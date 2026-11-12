#!/usr/bin/env python3
"""Build and check the deployment bundle `vizra-bundle_<tag>.tar.gz` (VZ-INSTALL-004).

Reproducible by construction rather than by tar flags: Python's tarfile writes
sorted entries in USTAR format with mtime = SOURCE_DATE_EPOCH, uid/gid 0, empty
owner names and mode 0644/0755; gzip carries mtime 0 and no file name. The same
inputs therefore give the same bytes on GNU and BSD hosts alike.

  bundle.py build --tag T --out DIR [--src ROOT] (--core-migrations DIR | --release-record FILE)
  bundle.py check BUNDLE [--core-migrations DIR] [--no-render]
"""
import argparse, glob, gzip, hashlib, io, json, os, re, shutil, subprocess, sys, tarfile, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT = "scripts/bundle-contents.json"
MIG = re.compile(r"^(\d+)_.+\.up\.sql$")


def fail(msg):
    print(f"bundle: FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def schema_from_migrations(d):
    nums = [int(m.group(1)) for f in os.listdir(d) if (m := MIG.match(f))]
    if not nums:
        fail(f"no *.up.sql migrations in {d}")
    return max(nums)


def schema_from_record(path):
    with open(path, encoding="utf-8") as fh:
        rec = json.load(fh)
    v = rec.get("components", {}).get("vizra-core", {}).get("schema_version")
    if not isinstance(v, int):
        fail(f"{path}: components.vizra-core.schema_version is not an integer")
    return v


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def source_date_epoch(src):
    v = os.environ.get("SOURCE_DATE_EPOCH")
    if v is None:
        v = subprocess.run(["git", "-C", src, "log", "-1", "--format=%ct"],
                           check=True, capture_output=True, text=True).stdout.strip()
    return int(v)


def build(a):
    src = os.path.abspath(a.src)
    with open(os.path.join(src, CONTRACT), encoding="utf-8") as fh:
        contract = json.load(fh)
    files = sorted(set(contract["include"]) | {CONTRACT})
    for rel in files:
        if not os.path.isfile(os.path.join(src, rel)):
            fail(f"missing: {rel} (in the include list, absent from {src})")
        for ex in contract["exclude"]:
            if rel == ex or rel.startswith(ex + "/"):
                fail(f"include list names excluded path {rel}")
    if a.core_migrations:
        schema, schema_src = schema_from_migrations(a.core_migrations), "core-migrations"
    else:
        schema, schema_src = schema_from_record(a.release_record), "release-record"
    epoch = source_date_epoch(src)
    manifest = {
        "bundle_format": 1,
        "tag": a.tag,
        "schema_version": schema,
        "schema_version_source": schema_src,
        "source_date_epoch": epoch,
        "files": {rel: sha256(os.path.join(src, rel)) for rel in files},
    }
    mbytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    root = f"vizra-bundle_{a.tag}"
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        def add(name, data, mode):
            ti = tarfile.TarInfo(f"{root}/{name}")
            ti.size, ti.mtime, ti.mode = len(data), epoch, mode
            ti.uid = ti.gid = 0
            ti.uname = ti.gname = ""
            tar.addfile(ti, io.BytesIO(data))
        entries = [(rel, os.path.join(src, rel)) for rel in files]
        for rel, path in sorted(entries + [("MANIFEST.json", None)]):
            if path is None:
                add(rel, mbytes, 0o644)
            else:
                with open(path, "rb") as fh:
                    data = fh.read()
                add(rel, data, 0o755 if os.access(path, os.X_OK) else 0o644)
    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, f"{root}.tar.gz")
    with open(out, "wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0, compresslevel=9) as gz:
            gz.write(raw.getvalue())
    print(f"bundle: built {out} ({len(files) + 1} files, schema_version {schema} from {schema_src})")


def bind_sources(compose_path):
    import yaml

    class Loader(yaml.SafeLoader):
        pass

    # Compose merge tags (!override, !reset) only change merging; keep the value.
    def any_tag(loader, suffix, node):
        if isinstance(node, yaml.MappingNode):
            return loader.construct_mapping(node, deep=True)
        if isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node, deep=True)
        return loader.construct_scalar(node)

    Loader.add_multi_constructor("!", any_tag)
    with open(compose_path, encoding="utf-8") as fh:
        doc = yaml.load(fh, Loader=Loader) or {}
    out = []
    for svc in (doc.get("services") or {}).values():
        for v in (svc or {}).get("volumes") or []:
            if isinstance(v, dict) and v.get("type") == "bind":
                out.append(v["source"])
            elif isinstance(v, str) and v.split(":")[0].startswith((".", "/")):
                out.append(v.split(":")[0])
    return out


def check(a):
    errors = []
    work = tempfile.mkdtemp(prefix="vizra-bundle-check-")
    try:
        with tarfile.open(a.bundle, "r:gz") as tar:
            for m in tar.getmembers():
                if not (m.isfile() or m.isdir()) or m.name.startswith("/") or ".." in m.name.split("/"):
                    fail(f"unsafe or non-regular tar entry: {m.name}")
            tar.extractall(work, filter="data") if hasattr(tarfile, "data_filter") else tar.extractall(work)
        roots = os.listdir(work)
        if len(roots) != 1:
            fail(f"expected one top-level directory, found {roots}")
        tree = os.path.join(work, roots[0])
        with open(os.path.join(tree, "MANIFEST.json"), encoding="utf-8") as fh:
            man = json.load(fh)
        with open(os.path.join(tree, CONTRACT), encoding="utf-8") as fh:
            contract = json.load(fh)
        shipped = set()
        for dp, _, fns in os.walk(tree):
            for f in fns:
                shipped.add(os.path.relpath(os.path.join(dp, f), tree))
        for rel, digest in man["files"].items():
            p = os.path.join(tree, rel)
            if not os.path.isfile(p):
                errors.append(f"manifest lists {rel}, absent from the bundle")
            elif sha256(p) != digest:
                errors.append(f"sha256 mismatch: {rel}")
        for rel in sorted(shipped - set(man["files"]) - {"MANIFEST.json"}):
            errors.append(f"unlisted file in bundle: {rel}")
        for ex in contract["exclude"]:
            for rel in shipped:
                if rel == ex or rel.startswith(ex + "/"):
                    errors.append(f"excluded path present: {rel}")
        for item, paths in contract["required"].items():
            if item in contract.get("not_yet_shipped", {}):
                print(f"bundle: not yet shipped: {item} — {contract['not_yet_shipped'][item]}")
                continue
            for p in paths:
                if p.replace("<tag>", man["tag"]) not in shipped:
                    errors.append(f"missing: {item} ({p})")
        # Every file a production shape renders with must ship: derived from the
        # shipped compose-shapes.json, so a new overlay cannot be left out silently.
        shapes_path = os.path.join(tree, "scripts/compose-shapes.json")
        if not os.path.isfile(shapes_path):
            errors.append("missing: scripts/compose-shapes.json")
        else:
            with open(shapes_path, encoding="utf-8") as fh:
                for shape in json.load(fh)["shapes"]:
                    if shape["kind"] != "production":
                        continue
                    for f in shape["files"]:
                        if f not in shipped:
                            errors.append(f"missing: production shape {shape['id']} needs {f}")
        gen = contract.get("generated_bind_sources", {})
        for cf in sorted(f for f in shipped if re.fullmatch(r"docker-compose[^/]*\.yml", f)):
            for s in bind_sources(os.path.join(tree, cf)):
                rel = os.path.normpath(s)
                if rel in gen:
                    continue
                if rel not in shipped and not os.path.isdir(os.path.join(tree, rel)):
                    errors.append(f"missing bind-mount source: {s} (referenced by {cf})")
        if a.core_migrations:
            want = schema_from_migrations(a.core_migrations)
            if man["schema_version"] != want:
                errors.append(f"schema_version {man['schema_version']} != migrations on disk {want}")
        if errors:
            for e in errors:
                print(f"bundle: FAIL: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"bundle: content ok ({len(man['files'])} files, tag {man['tag']}, schema_version {man['schema_version']})")
        if not a.no_render:
            with open(os.path.join(tree, "scripts/compose-shapes.json"), encoding="utf-8") as fh:
                shapes = [s["id"] for s in json.load(fh)["shapes"] if s["kind"] == "production"]
            for comp in ("vizra-core", "vizra-user", "vizra-search"):
                if os.path.exists(os.path.join(tree, comp)):
                    fail(f"component checkout {comp} present in the unpacked bundle")
            for sid in shapes:
                r = subprocess.run([sys.executable, os.path.join(tree, "scripts/compose-render.py"),
                                    "--shape", sid, "--out", os.path.join(work, "models")],
                                   cwd=tree, capture_output=True, text=True)
                if r.returncode != 0:
                    print(r.stdout + r.stderr, file=sys.stderr)
                    fail(f"render of production shape {sid} from the unpacked bundle failed")
                print(f"bundle: rendered {sid} from the unpacked bundle, no checkouts")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--tag", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--src", default=HERE)
    g = b.add_mutually_exclusive_group(required=True)
    g.add_argument("--core-migrations")
    g.add_argument("--release-record")
    c = sub.add_parser("check")
    c.add_argument("bundle")
    c.add_argument("--core-migrations")
    c.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    if a.cmd == "build":
        if not re.fullmatch(r"v?[0-9A-Za-z._-]+", a.tag):
            fail(f"bad tag {a.tag!r}")
        build(a)
    else:
        check(a)


if __name__ == "__main__":
    main()
