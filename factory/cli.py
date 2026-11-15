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
from .spec import check_story
from .findings import FindingsLog
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


def cmd_log_finding(args) -> int:
    """Record one reviewer finding (called by the review loop each round)."""
    from .findings import Finding, classify
    import time
    log = FindingsLog(Path(args.log))
    log.append(Finding(
        ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        repo=args.repo, pr=args.pr, round=args.round, source=args.source,
        klass=args.klass or classify(args.summary, verified=args.verified),
        severity=args.severity, summary=args.summary, path=args.path,
        head_sha=args.head_sha, escaped_gate=args.escaped_gate,
        escaped_review=args.escaped_review, verified=args.verified,
        disposition=args.disposition, fix_sha=args.fix_sha,
        gate_check=args.gate_check))
    print(f"logged: {args.summary[:70]}")
    return 0


def cmd_findings(args) -> int:
    """Mine the review-findings log (Randy's idea, 2026-11-15)."""
    log = FindingsLog(Path(args.log))
    if args.recurring:
        for k, n in log.recurring(args.min_count):
            print(f"{n:3}  {k}")
        return 0
    if args.uncovered:
        for k in log.uncovered_classes():
            print(k)
        return 0
    text = log.render()
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
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
    for extra in (args.input or []):
        label, _, path = extra.partition("=")
        inputs[label] = Path(path).read_text(encoding="utf-8")
    if args.role == "coder" and args.story_file and not args.skip_spec_check:
        spec = check_story(Path(args.story_file).read_text(encoding="utf-8"))
        if not spec.passed:
            print(f"REFUSED: story spec fails planning checks: {spec.named_failures()}",
                  file=sys.stderr)
            return 2
        for w in spec.warnings:
            print(f"warning: {w}", file=sys.stderr)
    pkg = seal(story=args.story, role=args.role, model=args.model,
               instruction=args.instruction, inputs=inputs,
               expected_outputs=args.outputs.split(","),
               repo=args.repo, sha=args.sha,
               manifest=args.manifest.split(","))
    dispatch_dir = Path(args.dispatch_dir).resolve()
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
    # persist the dispatch transcript (reviewer verdicts live in stdout)
    out_path = dispatch_dir / f"{args.story}-{args.role}-{seq:02d}.output.txt"
    out_path.write_text(res.stdout + ("\n--- STDERR ---\n" + res.stderr if res.stderr else ""),
                        encoding="utf-8")
    led.append("dispatch_completed", story=args.story, role=args.role,
               model=res.model or args.model, tokens=res.tokens,
               cost_usd=res.cost_usd, wall_s=res.wall_s,
               outcome="ok" if res.ok else "fail",
               detail={"exit": res.exit_code, "usage": str(usage_path),
                       "output": str(out_path)})
    print(f"exit={res.exit_code} wall={res.wall_s:.1f}s "
          f"tokens={res.tokens} model={res.model}")
    if not res.ok:
        print(res.stderr[-1000:], file=sys.stderr)
    return 0 if res.ok else 1


def cmd_intake(args) -> int:
    """Guided intake state machine (SKEL-2 INT-1, harness-agnostic OC-7)."""
    from . import intake
    root = Path(args.root)
    try:
        if args.intake_cmd == "start":
            s = intake.start_session(root, description=args.description)
            print(json.dumps({"session_id": s.session_id, "status": s.status}))
        elif args.intake_cmd == "answer":
            answers = json.loads(args.answers)
            s = intake.answer_questions(root, args.session, answers)
            print(json.dumps({"session_id": s.session_id, "status": s.status}))
        elif args.intake_cmd == "generate":
            path = intake.generate_prd(root, args.session)
            print(json.dumps({"prd": str(path), "status": "prd_ready"}))
        elif args.intake_cmd == "status":
            s = intake.IntakeSession.load(root, args.session)
            print(json.dumps(s.to_dict(), indent=2))
    except intake.IntakeError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"REFUSED: --answers is not valid JSON: {exc}", file=sys.stderr)
        return 2
    return 0


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

    lf = sub.add_parser("log-finding", help="record one reviewer finding")
    lf.add_argument("--log", default="state/findings.jsonl")
    lf.add_argument("--repo", required=True); lf.add_argument("--pr", type=int, required=True)
    lf.add_argument("--round", type=int, required=True); lf.add_argument("--source", required=True)
    lf.add_argument("--summary", required=True); lf.add_argument("--klass", default=None)
    lf.add_argument("--severity", default="unknown"); lf.add_argument("--path", default=None)
    lf.add_argument("--head-sha", default=None); lf.add_argument("--verified", default="unverified")
    lf.add_argument("--disposition", default="open"); lf.add_argument("--fix-sha", default=None)
    lf.add_argument("--gate-check", default=None)
    lf.add_argument("--escaped-gate", action="store_true")
    lf.add_argument("--escaped-review", action="store_true")
    lf.set_defaults(fn=cmd_log_finding)

    fl = sub.add_parser("findings", help="mine the review-findings log")
    fl.add_argument("--log", default="state/findings.jsonl")
    fl.add_argument("--recurring", action="store_true")
    fl.add_argument("--uncovered", action="store_true")
    fl.add_argument("--min-count", type=int, default=2)
    fl.add_argument("--out", default=None)
    fl.set_defaults(fn=cmd_findings)

    dp = sub.add_parser("dispatch")
    dp.add_argument("--ledger", default=str(_default_ledger()))
    dp.add_argument("--story", required=True); dp.add_argument("--role", required=True)
    dp.add_argument("--model", required=True); dp.add_argument("--instruction", required=True)
    dp.add_argument("--story-file", default=None); dp.add_argument("--design-file", default=None)
    dp.add_argument("--input", action="append", default=None,
                    help="extra pinned input as label=path (repeatable)")
    dp.add_argument("--outputs", default="code committed,tests green")
    dp.add_argument("--repo", required=True); dp.add_argument("--sha", required=True)
    dp.add_argument("--manifest", required=True)
    dp.add_argument("--dispatch-dir", default="runs/todo-demo/dispatch")
    dp.add_argument("--workdir", required=True); dp.add_argument("--toolsets", default="terminal,file")
    dp.add_argument("--timeout", type=int, default=900); dp.add_argument("--dry-run", action="store_true")
    dp.add_argument("--skip-spec-check", action="store_true",
                    help="bypass planning checks (audited escape hatch)")
    dp.set_defaults(fn=cmd_dispatch)

    it = sub.add_parser("intake", help="guided intake state machine (SKEL-2, OC-7)")
    it.add_argument("--root", default="runs/intake",
                    help="directory holding intake sessions")
    itsub = it.add_subparsers(dest="intake_cmd", required=True)
    i_start = itsub.add_parser("start"); i_start.add_argument("--description", required=True)
    i_ans = itsub.add_parser("answer")
    i_ans.add_argument("--session", required=True)
    i_ans.add_argument("--answers", required=True, help="JSON object of category->answer")
    i_gen = itsub.add_parser("generate"); i_gen.add_argument("--session", required=True)
    i_stat = itsub.add_parser("status"); i_stat.add_argument("--session", required=True)
    it.set_defaults(fn=cmd_intake)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())