#!/usr/bin/env python3
"""Backfill the findings log from the REAL PR #1 review history.

Grounded in the actual reviews/comments, not memory. Idempotent: rebuilds the
log from scratch each run so re-running never duplicates rows.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "Work/software-factory"))
from factory.findings import Finding, FindingsLog, classify

R = "agentmerlin8/factory-todo-demo"
LOG = Path.home() / "Work/software-factory/state/findings.jsonl"

# The verified per-round record (each was executed before fixing).
# (round, head, summary, path, severity, verified, disposition, fix_sha, gate_check)
ROUNDS = [
    (2, "04428d6", "Storage failure aborts task submission without accessible feedback",
     "src/App.tsx", "major", "executed", "fixed", "0ceb1d2", None),
    (2, "04428d6", "Light-theme secondary text below minimum contrast (2.61-2.92:1)",
     "src/index.css", "major", "executed", "fixed", "0ceb1d2", "contrast"),
    (2, "04428d6", "Dark-theme secondary text below minimum contrast (3.27-3.82:1)",
     "src/index.css", "major", "executed", "fixed", "0ceb1d2", "contrast"),
    (2, "04428d6", "Light-mode eyebrow contrast 3.68:1 below 4.5:1",
     "src/index.css", "major", "executed", "fixed", "0ceb1d2", "contrast"),
    (3, "0ceb1d2", "Validate stored task entries before rendering: [null] crashes mount",
     "src/App.tsx", "major", "executed", "fixed", "89a491b", "boundaries"),
    (3, "0ceb1d2", "Add label contrast in light-mode hover states on gradient (measured 15/18 combos failing)",
     "src/index.css", "major", "executed", "fixed", "89a491b", "contrast"),
    (4, "89a491b", "Selected task text contrast 4.04:1 in light mode (::selection)",
     "src/index.css", "major", "executed", "fixed", "259eceb", "contrast"),
    (4, "89a491b", "Button keyboard-focus outline 1.61:1 light / 2.11:1 dark, below 3:1",
     "src/index.css", "major", "executed", "fixed", "259eceb", "contrast"),
    (5, "259eceb", "Successful task additions are not announced to screen-reader users",
     "src/App.tsx", "major", "executed", "fixed", "80a79b0", "announcements"),
    (6, "80a79b0", "Repeated task titles do not trigger a new live-region announcement",
     "src/App.tsx", "major", "executed", "fixed", "2e954fc", "announcements"),
]

# Our own cross-family reviewer's round-1 findings (2 were refuted by execution).
OWN_REVIEW = [
    (1, "ba6580c", "Missing subscriber notification breaks the test suite",
     "src/store.ts", "blocker", "refuted", "rejected", None, None),
    (1, "ba6580c", "Double-submit hazard allows duplicate tasks",
     "src/App.tsx", "major", "refuted", "rejected", None, None),
    (1, "ba6580c", "Enter-submits test does not assert input clearing",
     "src/App.test.tsx", "minor", "executed", "fixed", "04428d6", None),
    (1, "ba6580c", "Large theme addition exceeds the functional brief (unrequested CSS)",
     "src/index.css", "nit", "reasoned", "deferred", None, None),
]

TIMESTAMPS = {1: "2026-11-14T21:10:00Z", 2: "2026-11-15T13:59:26Z",
              3: "2026-11-15T14:30:02Z", 4: "2026-11-15T14:56:39Z",
              5: "2026-11-15T15:11:11Z", 6: "2026-11-15T15:18:54Z"}


def main():
    if LOG.exists():
        LOG.unlink()  # rebuild: idempotent backfill
    log = FindingsLog(LOG)

    for rnd, head, summary, path, sev, verified, disp, fix, gate in ROUNDS:
        log.append(Finding(
            ts=TIMESTAMPS[rnd], repo=R, pr=1, round=rnd, source="copilot",
            klass=classify(summary, verified=verified), severity=sev, summary=summary, path=path,
            head_sha=head, escaped_gate=True, escaped_review=True,
            verified=verified, disposition=disp, fix_sha=fix, gate_check=gate))

    for rnd, head, summary, path, sev, verified, disp, fix, gate in OWN_REVIEW:
        log.append(Finding(
            ts=TIMESTAMPS[rnd], repo=R, pr=1, round=rnd, source="cross-family",
            klass=classify(summary, verified=verified), severity=sev, summary=summary, path=path,
            head_sha=head, escaped_gate=False, escaped_review=False,
            verified=verified, disposition=disp, fix_sha=fix, gate_check=gate))

    rows = log.read()
    print(f"backfilled {len(rows)} findings -> {LOG}")
    print("\nclass distribution:")
    for k, n in log.by_class().most_common():
        print(f"  {k}: {n}")
    print("\nuncovered classes:", log.uncovered_classes())


if __name__ == "__main__":
    main()