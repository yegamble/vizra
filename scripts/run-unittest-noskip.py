#!/usr/bin/env python3
"""Run unittest like `python3 -m unittest ARGS`, but fail on skips.

A required lane must not go green on tests that never ran: exit non-zero
if any test failed/errored, was skipped, was an expected failure (or an
unexpected success), or if zero tests ran. Usage:
  run-unittest-noskip.py discover -s DIR [-p PATTERN]
  run-unittest-noskip.py MODULE [MODULE ...]
"""
import os
import sys
import unittest


def main(argv):
    if not argv:
        print("usage: run-unittest-noskip.py discover ... | MODULE ...", file=sys.stderr)
        return 2
    sys.path.insert(0, os.getcwd())
    prog = unittest.main(module=None, argv=(["unittest", "discover", "-v", *argv[1:]] if argv[0] == "discover"
                                                else ["unittest", "-v", *argv]), exit=False)
    r = prog.result
    print(f"noskip: tests run {r.testsRun}, failures {len(r.failures)}, errors {len(r.errors)}, "
          f"skipped {len(r.skipped)}, expected failures {len(r.expectedFailures)}, "
          f"unexpected successes {len(r.unexpectedSuccesses)}")
    bad = []
    if r.testsRun == 0:
        bad.append("no tests ran")
    if not r.wasSuccessful():
        bad.append("failures or errors")
    for t, why in r.skipped:
        bad.append(f"skipped: {t.id()} ({why})")
    for t, _ in r.expectedFailures:
        bad.append(f"expected failure: {t.id()}")
    for t in r.unexpectedSuccesses:
        bad.append(f"unexpected success: {t.id()}")
    for b in bad:
        print(f"noskip: FAIL {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
