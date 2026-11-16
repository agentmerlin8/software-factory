# Seeded-defect fixture (SKEL-5 MEA-3 calibration target)

10 planted defects across 4 files. Ground truth: `factory/calibration.py`
`SEEDED_DEFECTS`. **Do not fix these** — they are the calibration targets a
reviewer must FIND. The catch-rate experiment measures how many each review
mode catches.

| ID | Class | File | Planted defect |
|---|---|---|---|
| SD-01 | concurrency-lost-update | store.ts | addTask/toggleTask read once, write from stale snapshot |
| SD-02 | self-certifying-test | store.test.ts | corrupt-data payload led by null masks the guard |
| SD-03 | untrusted-boundary | store.ts | isTask accepts empty-string title |
| SD-04 | silent-mutation | App.tsx | handleDelete success announces nothing |
| SD-05 | stale-live-region | App.tsx | same-title adds produce identical announcement text |
| SD-06 | contrast-text | theme.css | .muted #c9bda6 on #f7f1e5 = 1.65:1 (AA needs 4.5) |
| SD-07 | scope-creep | theme.css | unrequested gradient/glow/shimmer restyle, no AC |
| SD-08 | unhandled-io-failure | App.tsx | toggle catch block swallows storage failure |
| SD-09 | test-gap | store.test.ts | list test asserts count, not ordering AC |
| SD-10 | state-integrity | store.ts | completed filter predicate lets active tasks through |

This is a review target, not a buildable project (no node_modules by design).
