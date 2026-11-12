"""Tests for gh_api() transient-failure retry in scripts/check-ledger-status-remote.py.

A fake `gh` on PATH replays a scripted sequence of replies, one per call.
"""
import contextlib
import importlib.util
import io
import os
import stat
import tempfile
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
SCRIPT = os.path.join(ROOT, "scripts", "check-ledger-status-remote.py")

spec = importlib.util.spec_from_file_location("check_ledger_status_remote", SCRIPT)
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)

FAKE_GH = r"""#!/bin/sh
# replies: one line per call in $FAKE_GH_DIR/replies: "ok" or "<exit>|<stderr text>"
n=$(cat "$FAKE_GH_DIR/count" 2>/dev/null || echo 0)
n=$((n+1)); echo "$n" > "$FAKE_GH_DIR/count"
line=$(sed -n "${n}p" "$FAKE_GH_DIR/replies")
[ -z "$line" ] && line=$(tail -n 1 "$FAKE_GH_DIR/replies")
if [ "$line" = ok ]; then echo '{"ok": true}'; exit 0; fi
echo "${line#*|}" >&2
exit "${line%%|*}"
"""

E503 = "1|gh: Service Unavailable (HTTP 503)"
E404 = "1|gh: Not Found (HTTP 404)"


class GhApiRetry(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        gh = os.path.join(self.dir, "gh")
        with open(gh, "w") as f:
            f.write(FAKE_GH)
        os.chmod(gh, os.stat(gh).st_mode | stat.S_IEXEC)
        self.old_path = os.environ["PATH"]
        os.environ["PATH"] = self.dir + os.pathsep + self.old_path
        os.environ["FAKE_GH_DIR"] = self.dir
        self.old_delays = getattr(remote, "RETRY_DELAYS", None)
        remote.RETRY_DELAYS = (0, 0)

    def tearDown(self):
        os.environ["PATH"] = self.old_path
        remote.RETRY_DELAYS = self.old_delays

    def run_api(self, replies):
        with open(os.path.join(self.dir, "replies"), "w") as f:
            f.write("\n".join(replies) + "\n")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = remote.gh_api("repos/x/y/pulls/1")
        with open(os.path.join(self.dir, "count")) as f:
            calls = int(f.read())
        return result, calls, [l for l in err.getvalue().splitlines() if l.strip()]

    def test_503_twice_then_success(self):
        (data, error), calls, lines = self.run_api([E503, E503, "ok"])
        self.assertIsNone(error)
        self.assertEqual(data, {"ok": True})
        self.assertEqual(calls, 3)
        self.assertEqual(len(lines), 2)
        self.assertTrue(all("retry" in l for l in lines), lines)

    def test_503_always_fails_with_original_error(self):
        (data, error), calls, lines = self.run_api([E503] * 4)
        self.assertIsNone(data)
        self.assertEqual(error, "gh api repos/x/y/pulls/1: exit 1: gh: Service Unavailable (HTTP 503)")
        self.assertEqual(calls, 3)
        self.assertEqual(len(lines), 2)

    def test_404_not_retried(self):
        (data, error), calls, lines = self.run_api([E404, "ok"])
        self.assertIsNone(data)
        self.assertEqual(error, "gh api repos/x/y/pulls/1: exit 1: gh: Not Found (HTTP 404)")
        self.assertEqual(calls, 1)
        self.assertEqual(lines, [])


if __name__ == "__main__":
    unittest.main()
