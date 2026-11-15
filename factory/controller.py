"""Controller validator — SKEL-3 SEC-1 (OC-14 security core).

The controller is the SOLE state-repo writer. It runs NO model output and
NO product code: it validates an agent submission against schema + event
allowlist + policy, stamps provenance, and appends to the hash-chained
ledger. Agents emit submissions to the PRODUCT repo; only this module
(holding the controller identity) writes state.

Refusal rules (fail-closed, all-or-nothing):
- submission must be an object with schema==0, a source string, and a
  non-empty events list
- every event must be an object with a known event type (ledger allowlist)
- policy may narrow the event allowlist; a submission cannot change policy
- the controller computes the chain ('prev') itself — an agent-supplied
  'prev' is stripped, never trusted
- validation happens BEFORE any write: one bad event refuses the whole
  submission (no partial append)
"""
from __future__ import annotations

import copy
from pathlib import Path

from .ledger import Ledger, LedgerError, EVENT_TYPES, SCHEMA

DEFAULT_POLICY = {
    "schema": SCHEMA,
    "allowed_events": sorted(EVENT_TYPES),
}


class ControllerError(ValueError):
    """A submission was refused (fail-closed, nothing written)."""


def validate_submission(submission: dict, policy: dict | None = None) -> list[dict]:
    """Validate and return normalized events, or raise ControllerError.

    Pure: no I/O. The caller (append_submission) writes only after this
    returns cleanly.
    """
    pol = policy or DEFAULT_POLICY
    if not isinstance(submission, dict):
        raise ControllerError("submission must be a JSON object")
    if submission.get("schema") != pol.get("schema", SCHEMA):
        raise ControllerError(
            f"submission schema {submission.get('schema')!r} != policy schema "
            f"{pol.get('schema', SCHEMA)}")
    source = submission.get("source")
    if not isinstance(source, str) or not source.strip():
        raise ControllerError("submission must carry a non-empty 'source' string")
    events = submission.get("events")
    if not isinstance(events, list) or not events:
        raise ControllerError("submission must carry a non-empty 'events' list")

    allowed = set(pol.get("allowed_events", EVENT_TYPES))
    normalized = []
    for i, e in enumerate(events):
        if not isinstance(e, dict):
            raise ControllerError(f"event[{i}] must be an object")
        etype = e.get("event")
        if etype not in EVENT_TYPES:
            raise ControllerError(f"event[{i}] unknown event type: {etype!r}")
        if etype not in allowed:
            raise ControllerError(
                f"event[{i}] type {etype!r} not in policy allowlist")
        detail = e.get("detail") or {}
        if not isinstance(detail, dict):
            raise ControllerError(f"event[{i}] detail must be an object")
        # A submission may not attempt to change controller policy.
        if any(k in detail for k in ("policy_change", "policy_update", "allow_all")):
            raise ControllerError(
                f"event[{i}] attempts a policy mutation — refused (policy "
                "changes only by human-reviewed PR)")
        norm = copy.deepcopy(e)
        # Never trust an agent-supplied chain hash or timestamp provenance.
        norm.pop("prev", None)
        norm.pop("ts", None)
        norm["detail"] = dict(detail)
        norm["detail"]["_source"] = source
        normalized.append(norm)
    return normalized


def append_submission(ledger: Ledger, submission: dict,
                      policy: dict | None = None) -> list[dict]:
    """Validate, then append all events ATOMICALLY. Returns stored rows.

    Atomicity: events are appended to a temp copy of the ledger; only when
    every append succeeds is the temp file swapped over the real ledger.
    A failure mid-append leaves the original ledger untouched. The
    ledger's own append() computes 'prev' and stamps 'ts' — the controller
    is the only writer, so the chain stays intact.
    """
    import shutil
    import tempfile

    normalized = validate_submission(submission, policy)
    ledger.path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(ledger.path.parent)) as td:
        tmp_path = Path(td) / "ledger.jsonl"
        if ledger.path.exists():
            shutil.copyfile(ledger.path, tmp_path)
        tmp_ledger = Ledger(tmp_path)
        rows = []
        try:
            for e in normalized:
                row = tmp_ledger.append(
                    e["event"],
                    story=e.get("story"), role=e.get("role"),
                    repo=e.get("repo"), sha=e.get("sha"),
                    model=e.get("model"), tokens=e.get("tokens"),
                    cost_usd=e.get("cost_usd"), wall_s=e.get("wall_s"),
                    human_min=e.get("human_min"), outcome=e.get("outcome"),
                    detail=e.get("detail"),
                )
                rows.append(row)
        except LedgerError as exc:
            raise ControllerError(f"ledger refused append: {exc}") from exc
        # All appends succeeded — swap atomically (same filesystem).
        tmp_path.replace(ledger.path)
    return rows
