"""Merge protocol — SKEL-4 MRG-1 (OC-15).

The platform's own guarantee IS the mechanism: strict "require branches up
to date" + a real required check refuses stale merges; GitHub's squash of
an up-to-date branch lands a tree equal to the reviewed head (EXP-1/3).
This module provides the operational logic around that guarantee:

- staleness detection (update-before-review is load-bearing)
- update-before-review (merge main into the story branch; the new head is
  the real commit CI + review run on)
- re-review decision (only when the story diff changed OR main's delta
  touches the story manifest — avoids quadratic re-review, MRG-5)
- squash-equivalence ALARM (post-merge compare; mismatch = alarm, NOT
  auto-revert — no identity was allowed to auto-revert, MRG-4)

Pure git logic on a local workdir; no live GitHub calls in the core.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


class MergeProtocolError(RuntimeError):
    """A merge-protocol operation failed (e.g. update conflict)."""


def _git(workdir: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(workdir),
                          capture_output=True, text=True, check=check)


def _out(workdir: Path, *args: str) -> str:
    return _git(workdir, *args).stdout.strip()


def is_stale(workdir: Path, branch: str, main: str = "main") -> bool:
    """True if `branch` does not contain the tip of `main` (behind main).

    Ancestry form: merge-base(main, branch) == main tip means the branch
    already includes everything on main. EXP-1 case B: a stale branch's
    squash differs from its reviewed head — this detects that condition.
    """
    main_tip = _out(workdir, "rev-parse", main)
    merge_base = _out(workdir, "merge-base", main, branch)
    return merge_base != main_tip


def update_before_review(workdir: Path, branch: str, main: str = "main") -> str:
    """Merge `main` INTO `branch` (update-before-review), return new head.

    The caller must be ON `branch`. On conflict the merge is aborted and
    MergeProtocolError raised — the working tree is left clean, the story
    is blocked for a human/agent resolution (never a silent partial merge).
    """
    current = _out(workdir, "rev-parse", "--abbrev-ref", "HEAD")
    if current != branch:
        raise MergeProtocolError(
            f"update_before_review must run ON {branch!r} (currently {current!r})")
    proc = _git(workdir, "merge", "--no-edit", main, check=False)
    if proc.returncode != 0:
        _git(workdir, "merge", "--abort", check=False)
        raise MergeProtocolError(
            f"update-before-review conflict merging {main} into {branch}: "
            f"{proc.stderr.strip()[:200] or proc.stdout.strip()[:200]}")
    return _out(workdir, "rev-parse", "HEAD")


def needs_rereview(*, story_diff_changed: bool, main_delta_paths: list[str],
                   story_manifest: list[str]) -> bool:
    """Re-review only when the story's own diff changed OR main's delta
    touches the story's manifest (MRG-5: avoids quadratic re-review).

    A disjoint main move (docs, another story's files) needs only the
    deterministic gates on the updated head, not a fresh LLM review.
    """
    if story_diff_changed:
        return True
    manifest = set(story_manifest)
    return any(p in manifest for p in main_delta_paths)


def main_delta_paths(workdir: Path, base_sha: str, main: str = "main") -> list[str]:
    """Files changed on main between base_sha and main's tip."""
    out = _out(workdir, "diff", "--name-only", base_sha, main)
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def trees_equal(workdir: Path, tree_a: str, tree_b: str) -> bool:
    """Post-merge ALARM comparison: are two tree hashes identical?

    Used to compare the landed squash tree against the reviewed head tree.
    A mismatch is an ALARM (investigate / prepared revert PR in the inbox),
    never an automatic revert (MRG-4).
    """
    return tree_a == tree_b


def head_tree(workdir: Path, ref: str = "HEAD") -> str:
    """The tree hash of a ref (for squash-equivalence comparison)."""
    return _out(workdir, "rev-parse", f"{ref}^{{tree}}")
