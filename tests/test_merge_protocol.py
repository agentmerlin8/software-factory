"""Merge-protocol tests — SKEL-4 MRG-1 (OC-15).

Pure logic on fixture git repos: staleness detection, update-before-review,
re-review decision, squash-equivalence alarm. No live GitHub calls.
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.merge_protocol import (
    is_stale, update_before_review, needs_rereview, trees_equal,
    main_delta_paths, MergeProtocolError,
)


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                          text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "base.txt").write_text("base\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-qm", "base")
    return tmp_path


def test_fresh_branch_not_stale(repo):
    git(repo, "checkout", "-q", "-b", "story")
    (repo / "story.txt").write_text("story\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "story")
    assert is_stale(repo, "story", "main") is False


def test_branch_behind_main_is_stale(repo):
    git(repo, "checkout", "-q", "-b", "story")
    (repo / "story.txt").write_text("story\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "story")
    git(repo, "checkout", "-q", "main")
    (repo / "main-move.txt").write_text("main moved\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "main move")
    assert is_stale(repo, "story", "main") is True


def test_update_before_review_merges_main(repo):
    git(repo, "checkout", "-q", "-b", "story")
    (repo / "story.txt").write_text("story\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "story")
    git(repo, "checkout", "-q", "main")
    (repo / "main-move.txt").write_text("main moved\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "main move")
    git(repo, "checkout", "-q", "story")
    new_head = update_before_review(repo, "story", "main")
    assert is_stale(repo, "story", "main") is False
    assert (repo / "main-move.txt").exists()  # main's change is now in story
    assert (repo / "story.txt").exists()      # story's change preserved
    assert new_head == git(repo, "rev-parse", "HEAD")


def test_update_before_review_conflict_raises(repo):
    git(repo, "checkout", "-q", "-b", "story")
    (repo / "base.txt").write_text("story version\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "story edit")
    git(repo, "checkout", "-q", "main")
    (repo / "base.txt").write_text("main version\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "main edit")
    git(repo, "checkout", "-q", "story")
    with pytest.raises(MergeProtocolError, match="conflict"):
        update_before_review(repo, "story", "main")
    # working tree must be clean after a refused update (abort the merge)
    assert git(repo, "status", "--porcelain") == ""


def test_needs_rereview_story_diff_changed():
    assert needs_rereview(story_diff_changed=True, main_delta_paths=[],
                          story_manifest=["src/a.ts"]) is True


def test_needs_rereview_main_touches_manifest():
    assert needs_rereview(story_diff_changed=False,
                          main_delta_paths=["src/a.ts", "README.md"],
                          story_manifest=["src/a.ts"]) is True


def test_no_rereview_disjoint_main_move():
    assert needs_rereview(story_diff_changed=False,
                          main_delta_paths=["docs/other.md"],
                          story_manifest=["src/a.ts"]) is False


def test_no_rereview_nothing_changed():
    assert needs_rereview(story_diff_changed=False, main_delta_paths=[],
                          story_manifest=["src/a.ts"]) is False


def test_trees_equal_same_tree(repo):
    t = git(repo, "rev-parse", "HEAD^{tree}")
    assert trees_equal(repo, t, t) is True


def test_trees_equal_different_tree(repo):
    t1 = git(repo, "rev-parse", "HEAD^{tree}")
    (repo / "new.txt").write_text("x\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "second")
    t2 = git(repo, "rev-parse", "HEAD^{tree}")
    assert trees_equal(repo, t1, t2) is False


def test_main_delta_paths(repo):
    base = git(repo, "rev-parse", "HEAD")
    (repo / "added.txt").write_text("x\n")
    (repo / "base.txt").write_text("changed\n")
    git(repo, "add", "-A"); git(repo, "commit", "-qm", "move")
    paths = main_delta_paths(repo, base, "main")
    assert set(paths) == {"added.txt", "base.txt"}
