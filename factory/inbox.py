"""Inbox — v1 = GitHub issues with a label + assignee (OC-13).

Escalations and human gates become labeled issues. The controller never
silently drops a blockage: every BLOCKED story gets an inbox issue linking
the evidence.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

INBOX_LABEL = "factory-inbox"


@dataclass
class InboxResult:
    ok: bool
    url: str | None = None
    error: str | None = None


def escalate(repo: str, *, story: str, reason: str, evidence: str,
             assignee: str | None = None,
             extra_labels: list[str] | None = None) -> InboxResult:
    """Create a labeled inbox issue. `repo` = owner/name."""
    title = f"[inbox] {story}: {reason}"
    body = (
        f"**Story:** {story}\n"
        f"**Reason:** {reason}\n\n"
        f"## Evidence\n{evidence}\n\n"
        f"---\n_Created by the factory controller (SKEL-1 v0)._ "
    )
    cmd = ["gh", "issue", "create", "--repo", repo,
           "--title", title, "--body", body, "--label", INBOX_LABEL]
    for label in (extra_labels or []):
        cmd += ["--label", label]
    if assignee:
        cmd += ["--assignee", assignee]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return InboxResult(ok=False, error="gh timeout")
    if p.returncode != 0:
        return InboxResult(ok=False, error=p.stderr.strip()[-500:])
    return InboxResult(ok=True, url=p.stdout.strip())


def ensure_label(repo: str) -> bool:
    """Idempotently create the inbox label (green)."""
    p = subprocess.run(
        ["gh", "label", "create", INBOX_LABEL, "--repo", repo,
         "--color", "D93F0B", "--description", "Factory inbox: needs a human",
         "--force"],
        capture_output=True, text=True, timeout=60)
    return p.returncode == 0