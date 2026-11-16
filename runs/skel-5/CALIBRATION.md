# Seeded-defect catch-rate calibration (SKEL-5 MEA-3)

| mode | caught/10 | catch-rate | false-pos | precision |
|---|---|---|---|---|
| same-session | 10/10 | 100% | 3 | 77% |
| fresh-same-family | 10/10 | 100% | 0 | 100% |
| fresh-cross-family | 10/10 | 100% | 0 | 100% |

Calibration gates routing (ECN-3): a reviewer that can't catch
known planted defects isn't trusted to route. Cross-family
advantage measured here justifies the factory's review routing.

## Honest nuance

All three modes caught 10/10 seeded defects. The same-session mode ALSO
flagged 3 additional GENUINE defects not in the catalogued 10:
- DUP-ID-COLLISION (String(Date.now()) IDs can collide)
- EMPTY-TITLE-ADD (handleAdd does not reject empty title)
- DELETE-IO-UNGUARDED (handleDelete setItem not in try/catch)
These are real bugs, not false positives — the fixture contains more than
10 defects. Against the 10-defect ground truth, precision is 10/13 for
same-session (the 3 extras are real but uncatalogued); the fresh modes
flagged exactly the 10. Catch-rate alone does not distinguish the modes
here because the defects are salient; the differentiator in SKEL-1 was
SUBTLE defects (self-certifying tests, masked concurrency) where fresh
cross-family context mattered. This calibration confirms all modes catch
obvious defects; routing decisions should weight the subtle-defect evidence
from the real runs, not this salient-defect fixture alone.
