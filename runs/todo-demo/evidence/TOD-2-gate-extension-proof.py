# Fail-before / pass-after proof for the boundary_mutants gate check.
#
# Semantics: a claim is an UNMASKED malformed-entry payload. The real TOD-2
# pre-fix payload led with null, which throws into loadTasks' outer catch and
# masks the gap — that variant legitimately passes on the mutant and is
# reviewer-lens territory, NOT a deterministic claim (flagging it would be a
# false survivor). The fail-before fixture therefore uses an unmasked payload
# with a VACUOUS assertion: the self-certifying class in discoverable form.
import re
from pathlib import Path
import sys
sys.path.insert(0, '/home/merlin/Work/software-factory')
from factory.mutation import boundary_mutants

WORK = Path('/home/merlin/.hermes/cache/scratch/factory-exp/todo-demo')
TEST = WORK / 'src/App.test.tsx'
current = TEST.read_text(encoding='utf-8')
pre_fix = Path('/home/merlin/.hermes/cache/scratch/tod2-pre-fix-app-test.tsx').read_text(encoding='utf-8')

# Build the self-certifying fixture from the real malformed-entries test:
# unmask the payload, replace the strong assertions with a vacuous one.
m = re.search(r'it\("malformed array entries.*?\n  \}\);', pre_fix, re.S)
assert m, 'could not locate the malformed-entries test'
block = m.group(0)
weak_block = block.replace('[null, {}, 42, \\"str\\"]', '[{}, 42, \\"str\\"]')
weak_block = re.sub(
    r'expect\(screen\.getByTestId\("empty-state"\)\)\.toHaveTextContent\(\s*'
    r'/nothing here yet/i,\s*\);\s*'
    r'expect\(screen\.queryByRole\("listitem"\)\)\.toBeNull\(\);',
    'expect(screen.getByTestId("task-count")).toBeDefined();',
    weak_block)
assert weak_block != block and '[{}, 42' in weak_block, 'fixture build failed'
weak = pre_fix.replace(block, weak_block)

try:
    # 1. REAL pre-fix (masked): gate must NOT flag — false-survivor guard.
    TEST.write_text(pre_fix, encoding='utf-8')
    r = boundary_mutants(WORK, 'origin/main')
    print(f'REAL PRE-FIX (masked): verdict={r.verdict} ok={r.ok}\n  {r.detail}\n')
    assert r.ok, 'masked payload must not be flagged'

    # 2. FAIL-BEFORE: unmasked payload + vacuous assertion = self-certifying.
    TEST.write_text(weak, encoding='utf-8')
    r = boundary_mutants(WORK, 'origin/main')
    print(f'SELF-CERTIFYING: verdict={r.verdict} ok={r.ok}\n  {r.detail}\n')
    assert r.verdict == 'test-too-weak', 'gate must flag the self-certifying test'
finally:
    TEST.write_text(current, encoding='utf-8')

# 3. PASS-AFTER: the strengthened test at the fixed head.
r = boundary_mutants(WORK, 'origin/main')
print(f'FIXED: verdict={r.verdict} ok={r.ok}\n  {r.detail}')
assert r.ok, 'gate must pass the strengthened test'
assert TEST.read_text(encoding='utf-8') == current
print('tree restored to fixed head; proof complete')
