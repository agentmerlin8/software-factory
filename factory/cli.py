"""Factory CLI — `python -m factory <cmd>` (v0).

Commands: status, doctor, dispatch, gate, inbox, metrics.
Read path is fail-closed: a missing ledger is an error, never empty BACKLOG.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__
from .ledger import Ledger, LedgerError
from . import gates, inbox, metrics
from .dispatch import seal
from .adapters import hermes


def _default_ledger() -> Path:
    return Path("runs/todo-demo/ledger.jsonl")


def cmd_status(args) -> int:
    path = Path(args.ledger)
    if not path.exists():
        print(f"REFUSED: no ledger at {path} (fail-closed, not BACKLOG)",
              file=sys.stderr)
        return 2
    led = Ledger(path)
    try:
        rows = led.read()
    except LedgerError as exc:
        print(f"REFUSED: invalid ledger: {exc}", file=sys.stderr)
        return 2
    if not rows:
        print("ledger present but empty — no run started")
        return 0
    stories: dict[str, list[str]] = {}
    for r in rows:
        if r.get("story"):
            stories.setdefault(r["story"], []).append(r["event"])
    print(f"run events: {len(rows)}")
    print(f"last event: {rows[-1]['event']} @ {rows[-1]['ts']}")
    for s, evs in sorted(stories.items()):
        print(f"  {s}: {len(evs)} events, last={evs[-1]}")
    return 0


def cmd_doctor(args) -> int:
    checks: dict[str, bool] = {}
    checks["gh_auth"] = subprocess.run(
        ["gh", "auth", "status"], capture_output=True).returncode == 0
    checks["node"] = shutil.which("node") is not None
    checks["npm"] = shutil.which("npm") is not None
    checks["hermes"] = shutil.which("hermes") is not None
    checks["git"] = shutil.which("git") is not None
    if args.repo:
        checks["repo_reachable"] = subprocess.run(
            ["gh", "repo", "view", args.repo, "--json", "name"],
            capture_output=True).returncode == 0
    ok = all(checks.values())
    for name, passed in checks.items():
        print(f"  {'PASS' if passed else 'FAIL'}  {name}")
    print("doctor:", "OK" if ok else "FAIL")
    return 0 if ok else 1


def cmd_gate(args) -> int:
    res = gates.pre_review(Path(args.workdir), base=args.base,
                           manifest=args.manifest.split(","),
                           test_filter=args.test_filter)
    print(json.dumps({"passed": res.passed, "checks": res.checks,
                      "failures": res.failures}, indent=2))
    return 0 if res.passed else 1


def cmd_inbox(args) -> int:
    res = inbox.escalate(args.repo, story=args.story, reason=args.reason,
                         evidence=args.evidence, assignee=args.assignee)
    if res.ok:
        print(res.url)
        return 0
    print(f"REFUSED: {res.error}", file=sys.stderr)
    return 1


def cmd_metrics(args) -> int:
    fac = metrics.harvest(Ledger(Path(args.factory_ledger)))
    ctl = (metrics.harvest(Ledger(Path(args.control_ledger)))
           if args.control_ledger and Path(args.control_ledger).exists() else {})
    text = metrics.render_comparison(fac, ctl)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


def cmd_dispatch(args) -> int:
    """Seal a package and (unless --dry-run) run it via the Hermes adapter."""
    led = Ledger(Path(args.ledger))
    inputs = {}
    if args.story_file:
        inputs["story"] = Path(args.story_file).read_text(encoding="utf-8")
    if args.design_file:
        inputs["design"] = Path(args.design_file).read_text(encoding="utf-8")
    pkg = seal(story=args.story, role=args.role, model=args.model,
               instruction=args.instruction, inputs=inputs,
               expected_outputs=args.outputs.split(","),
               repo=args.repo, sha=args.sha,
               manifest=args.manifest.split(","))
    dispatch_dir = Path(args.dispatch_dir)
    seq = len(list(dispatch_dir.glob(f"{args.story}-{args.role}-*.md"))) + 1 \
        if dispatch_dir.exists() else 1
    path = pkg.write(dispatch_dir, seq)
    led.append("dispatch_sealed", story=args.story, role=args.role,
               repo=args.repo, sha=args.sha, model=args.model,
               detail={"package": str(path), "sha256": pkg.sha256})
    print(f"sealed {path} (sha256 {pkg.sha256[:12]}…)")
    if args.dry_run:
        print("dry-run: not executing")
        return 0
    usage_path = dispatch_dir / f"{args.story}-{args.role}-{seq:02d}.usage.json"
    led.append("dispatch_started", story=args.story, role=args.role,
               model=args.model, detail={"package": str(path)})
    res = hermes.run(path, model=args.model, workdir=Path(args.workdir),
                     usage_path=usage_path, toolsets=args.toolsets,
                     timeout_s=args.timeout)
    led.append("dispatch_completed", story=args.story, role=args.role,
               model=res.model or args.model, tokens=res.tokens,
               cost_usd=res.cost_usd, wall_s=res.wall_s,
               outcome="ok" if res.ok else "fail",
               detail={"exit": res.exit_code, "usage": str(usage_path)})
    print(f"exit={res.exit_code} wall={res.wall_s:.1f}s "
          f"tokens={res.tokens} model={res.model}")
    if not res.ok:
        print(res.stderr[-1000:], file=sys.stderr)
    return 0 if res.ok else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="factory", description="SKEL-1 control plane")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status"); s.add_argument("--ledger", default=str(_default_ledger()))
    s.set_defaults(fn=cmd_status)

    d = sub.add_parser("doctor"); d.add_argument("--repo", default=None)
    d.set_defaults(fn=cmd_doctor)

    g = sub.add_parser("gate")
    g.add_argument("--workdir", required=True); g.add_argument("--base", default="origin/main")
    g.add_argument("--manifest", required=True); g.add_argument("--test-filter", default=None)
    g.set_defaults(fn=cmd_gate)

    i = sub.add_parser("inbox")
    i.add_argument("--repo", required=True); i.add_argument("--story", required=True)
    i.add_argument("--reason", required=True); i.add_argument("--evidence", default="")
    i.add_argument("--assignee", default=None)
    i.set_defaults(fn=cmd_inbox)

    m = sub.add_parser("metrics")
    m.add_argument("--factory-ledger", default=str(_default_ledger()))
    m.add_argument("--control-ledger", default=None); m.add_argument("--out", default=None)
    m.set_defaults(fn=cmd_metrics)

    dp = sub.add_parser("dispatch")
    dp.add_argument("--ledger", default=str(_default_ledger()))
    dp.add_argument("--story", required=True); dp.add_argument("--role", required=True)
    dp.add_argument("--model", required=True); dp.add_argument("--instruction", required=True)
    dp.add_argument("--story-file", default=None); dp.add_argument("--design-file", default=None)
    dp.add_argument("--outputs", default="code committed,tests green")
    dp.add_argument("--repo", required=True); dp.add_argument("--sha", required=True)
    dp.add_argument("--manifest", required=True)
    dp.add_argument("--dispatch-dir", default="runs/todo-demo/dispatch")
    dp.add_argument("--workdir", required=True); dp.add_argument("--toolsets", default="terminal,file")
    dp.add_argument("--timeout", type=int, default=900); dp.add_argument("--dry-run", action="store_true")
    dp.set_defaults(fn=cmd_dispatch)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())