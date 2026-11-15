# Review findings — mined view

14 findings · 1 repo(s) · 1 PR(s)

## Recurring classes (what keeps coming back)

| class | count | meaning |
|---|---|---|
| `contrast-text` | 3 | Text below WCAG AA 4.5:1 against its background |
| `false-positive` | 2 | Reviewer claim refuted by execution (not a real defect) |
| `unhandled-io-failure` | 1 | I/O failure uncaught: action aborts, no feedback |
| `untrusted-boundary` | 1 | External data parsed without element validation |
| `contrast-gradient-state` | 1 | Text on a gradient/interactive state below 4.5:1 |
| `contrast-selection` | 1 | ::selection text below 4.5:1 |
| `contrast-focus-indicator` | 1 | Focus indicator below the 3:1 non-text minimum |
| `silent-mutation` | 1 | State change not announced to assistive tech |
| `stale-live-region` | 1 | Live region text unchanged, so no re-announcement |
| `test-gap` | 1 | Named test does not assert the acceptance criterion |
| `scope-creep` | 1 | Unrequested work shipped without its own ACs |

## Escape rate by round (are we improving?)

| round | findings | escaped gate | escaped review | fixed |
|---|---|---|---|---|
| 1 | 4 | 0 | 0 | 1 |
| 2 | 4 | 4 | 4 | 4 |
| 3 | 2 | 2 | 2 | 2 |
| 4 | 2 | 2 | 2 | 2 |
| 5 | 1 | 1 | 1 | 1 |
| 6 | 1 | 1 | 1 | 1 |

## Classes with NO deterministic check yet

- `scope-creep` — Unrequested work shipped without its own ACs
- `test-gap` — Named test does not assert the acceptance criterion
- `unhandled-io-failure` — I/O failure uncaught: action aborts, no feedback

_Each of these is a gate-extension candidate: the next occurrence is preventable, not just fixable._

## Who catches what (and how often they are wrong)

| source | real defects | refuted by execution | precision |
|---|---|---|---|
| copilot | 10 | 0 | 100% |
| cross-family | 2 | 2 | 50% |

_Precision here means 'survived execution', not 'was useful' — a refuted claim still costs a verification cycle._
