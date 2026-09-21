# Component configuration-key snapshots

Each `<component>.json` records the configuration keys a component repository
declares, **at a named commit of that repository**. They exist because the
coverage check must work in the shape that matters most — the deployment bundle,
where the component checkouts are absent — and because this repository's CI has
no token to check out a private sibling repository.

That is a real limit and it is stated rather than papered over:

| Check | Where it runs | What it proves |
|---|---|---|
| snapshot ⟷ compose `environment:` maps | every `validate` run, from the rendered model | every key a component declares is delivered to it, and no key is delivered that nothing declares |
| snapshot ⟷ template | every `validate` run | every operator-settable key has a template entry, and every template entry has a consumer |
| snapshot ⟷ the component's live source | **only where the checkout is present** (a developer's machine, and the future `bundle` lane) | the snapshot is not stale |

So a green `validate` does **not** prove the snapshots are current. It proves the
topology is consistent with them. `./scripts/check-config-coverage.py --drift`
is the check that proves currency, and it reports BLOCKED — never a pass — when
a checkout is missing.

`source_commit` is the component commit the keys were read from. Update the
snapshot and the commit in the same edit, or the drift check will say so.
