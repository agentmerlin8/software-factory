# Wireframe template (SKEL-2 INT-3)

Minimal Vite + React + Storybook workspace for intake wireframes. One
clickable mock-data story per screen; local URL only (OC-13: no
LIVE/SCREENSHOT tiers). The intake agent copies this template, swaps the
mock screens for the validated feature list, and serves it for the
engineer's approval pass.

## Run

    npm install
    npm run storybook      # serves http://localhost:6006

Stories live in `src/Wireframes.stories.tsx`; components in
`src/Wireframes.tsx`; theme in `src/wireframe.css` (literal hex +
rule-level dark overrides — the factory contrast gate resolves these,
AA in both themes).

## Gate

The wireframe CSS passes `factory` contrast audit (0 findings, both
themes). Focusable controls carry an opaque `:focus-visible` ring.
