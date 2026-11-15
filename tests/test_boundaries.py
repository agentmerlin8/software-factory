"""Boundary-check tests — the REAL round-3 crash regression."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.boundaries import check_file, check_tree

REPO = Path.home() / ".hermes/cache/scratch/factory-exp/todo-demo"

DEFECTIVE = '''
export function loadTasks(): Task[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as Task[]) : [];
  } catch {
    return [];
  }
}
'''

FIXED = '''
export function isTask(value: unknown): value is Task {
  if (typeof value !== "object" || value === null) return false;
  const t = value as Record<string, unknown>;
  return typeof t.id === "string" && typeof t.title === "string";
}
export function loadTasks(): Task[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    const out: Task[] = [];
    for (const entry of parsed) {
      if (!isTask(entry)) continue;
      out.push(entry);
    }
    return out;
  } catch {
    return [];
  }
}
'''


def test_defective_container_only_cast_is_flagged(tmp_path):
    p = tmp_path / "store.ts"
    p.write_text(DEFECTIVE)
    r = check_file(p)
    assert not r.passed
    assert "validate ELEMENTS" in r.named_failures()


def test_element_validated_version_passes(tmp_path):
    p = tmp_path / "store.ts"
    p.write_text(FIXED)
    assert check_file(p).passed


def test_no_parse_boundary_is_clean(tmp_path):
    p = tmp_path / "pure.ts"
    p.write_text("export const add = (a: number, b: number) => a + b;\n")
    assert check_file(p).passed


def test_test_files_are_skipped(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "store.test.ts").write_text(DEFECTIVE)
    assert check_tree(tmp_path).passed


@pytest.mark.skipif(not REPO.exists(), reason="product repo not cloned")
def test_real_prefix_store_is_flagged(tmp_path):
    """The actual pre-fix store.ts from commit 0ceb1d2."""
    old = subprocess.run(["git", "show", "0ceb1d2:src/store.ts"], cwd=REPO,
                         capture_output=True, text=True)
    if old.returncode != 0:
        pytest.skip("commit not available")
    p = tmp_path / "store.ts"
    p.write_text(old.stdout)
    assert not check_file(p).passed


@pytest.mark.skipif(not REPO.exists(), reason="product repo not cloned")
def test_real_fixed_store_passes():
    r = check_file(REPO / "src" / "store.ts")
    assert r.passed, r.named_failures()