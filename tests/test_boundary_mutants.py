"""boundary_mutants gate — discovery helpers (TOD-2 round-1 class).

The end-to-end fail-before/pass-after proof runs on the real product tree
(scratch/prove-gate-extension.py); these unit tests pin the discovery logic
so a refactor cannot silently narrow the claim set.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.mutation import (
    _boundary_claims, _discover_boundary_guards, _vitest_counts,
)


def test_counts_parses_vitest_summary():
    assert _vitest_counts("Tests  1 passed | 54 skipped (55)") == (1, 0)
    assert _vitest_counts("Tests  1 failed | 2 passed (3)") == (2, 1)
    assert _vitest_counts("Tests  3 passed (3)") == (3, 0)


def test_counts_fail_closed_on_zero_selected():
    assert _vitest_counts("No test files found, exiting with code 1") is None
    assert _vitest_counts("Tests  55 skipped (55)") is None
    assert _vitest_counts("nothing here") is None


WEAK = r'''
it("malformed array entries render the empty state instead of crashing", () => {
  localStorage.setItem("todo-demo:tasks", "[{}, 42, \"str\"]");
  render(<App />);
});
'''

MASKED_NULL = r'''
it("renders the empty state when stored entries are null", () => {
  localStorage.setItem("todo-demo:tasks", "[null, {}, 42, \"str\"]");
  render(<App />);
});
'''

STRONG = '''
it("malformed array entries render the empty state instead of crashing", () => {
  localStorage.setItem(
    "todo-demo:tasks",
    '[{"id":"x"},{"id":"y","title":"no completed flag"}]',
  );
  render(<App />);
});
'''

PARSE_ONLY = '''
it("corrupt stored JSON renders the empty state instead of crashing", () => {
  localStorage.setItem("todo-demo:tasks", "{definitely not json");
  render(<App />);
});
'''

STRINGIFY = '''
it("drops entries missing required fields", () => {
  localStorage.setItem(
    "todo-demo:tasks",
    JSON.stringify([{ id: "x" }, { title: "no id" }, 42, "str", []]),
  );
  expect(loadTasks()).toEqual([]);
});
'''

VALID_ONLY = '''
it("keeps valid entries and drops only the malformed ones", () => {
  const good = { id: "ok", title: "keep", completed: false, createdAt: 5 };
  localStorage.setItem(
    "todo-demo:tasks",
    JSON.stringify([good, { id: "bad" }]),
  );
  expect(loadTasks()).toEqual([good]);
});
'''


def test_weak_payload_is_a_claim():
    claims = _boundary_claims("src/App.test.tsx", WEAK)
    assert claims == [("src/App.test.tsx",
                       "malformed array entries render the empty state instead of crashing")]


def test_strengthened_payload_is_still_a_claim():
    assert len(_boundary_claims("src/App.test.tsx", STRONG)) == 1


def test_parse_only_payload_is_not_an_element_claim():
    # Deleting the ELEMENT guard legitimately leaves the parse-boundary
    # test green — counting it would produce a false survivor.
    assert _boundary_claims("src/App.test.tsx", PARSE_ONLY) == []


def test_stringify_malformed_array_is_a_claim():
    assert len(_boundary_claims("src/store.test.ts", STRINGIFY)) == 1


def test_mixed_valid_and_malformed_is_a_claim():
    assert len(_boundary_claims("src/store.test.ts", VALID_ONLY)) == 1


def test_null_led_payload_is_masked_not_a_claim():
    # A leading null throws into the outer catch; later entries are
    # unreachable, so the test legitimately passes with the guard deleted.
    # That variant is reviewer-lens territory, not a deterministic claim.
    assert _boundary_claims("src/App.test.tsx", MASKED_NULL) == []


def test_claims_are_per_test_not_per_file():
    text = WEAK + PARSE_ONLY + STRINGIFY
    names = [n for _, n in _boundary_claims("f.ts", text)]
    assert len(names) == 2
    assert all("corrupt stored JSON" not in n for n in names)


GUARDED = '''
export function loadTasks() {
  const parsed = JSON.parse(raw);
  for (const entry of parsed) {
    if (!isTask(entry) || seen.has(entry.id)) continue;
    tasks.push(entry);
  }
}
'''


def test_guard_discovery_finds_loop_guard(tmp_path):
    p = tmp_path / "store.ts"
    p.write_text(GUARDED, encoding="utf-8")
    sites = _discover_boundary_guards(tmp_path, ["store.ts"])
    assert len(sites) == 1
    path, text, start, end, label = sites[0]
    assert label == "!isTask(entry)"
    mutant = text[:start] + text[end:]
    assert "!isTask(entry)" not in mutant
    assert "if (seen.has(entry.id)) continue;" in mutant  # still parseable


def test_guard_discovery_ignores_guards_outside_loops(tmp_path):
    p = tmp_path / "store.ts"
    p.write_text("if (!isTask(entry)) return;\n", encoding="utf-8")
    assert _discover_boundary_guards(tmp_path, ["store.ts"]) == []
