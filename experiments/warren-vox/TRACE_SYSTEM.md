# WARREN VOX — Trace System

authority: false · claim: NO_CLAIM · paid_generation_calls: 0

Traces make **governed actions feel physical**. They never invent state.
If a meter moves, a reducer (or pure local garden sim) moved it first.
VOX only shows the aftermath.

## Trace kinds

| Kind | Trigger (game event) | Skin response |
|---|---|---|
| `enter` | start / wake | overlay dismiss; coach → first stamp |
| `propose` | pending proposal appears | card `.is-active`; speech bubble on goblin |
| `admit` | operator ADMIT | stage flash; `vox-popin` cutout; meter bars animate |
| `deny` | operator DENY | coach "Blocked."; no cutout |
| `compost` | operator COMPOST | optional 🍂 residue; coach "Buried soft." |
| `day_end` | turn budget complete | summary panel; primary "Next day" |
| `pulse` | MARK / attention | radial pulse FX on target (day1 lineage) |
| `shake` | failed FIX / too heavy | short CSS shake on prop |

## Timing budget (felt, not sovereign)

| Trace | Duration |
|---|---|
| flash | ~300–350ms |
| popin | ~450ms spring |
| coach swap | immediate text; optional 700ms busy lock |
| speech bubble | 1.2–1.8s then clear |
| meter bar | 400ms width ease |
| stamp busy lock | ≤700ms then re-enable or next propose |

Busy locks are UI-only. They must not desync from reducer results.

## Meter as Gauge (not Metric)

Meters render numbers already in state. VOX CSS:

```css
.vox-meter .bar > i { transition: width 0.4s ease; }
```

Forbidden: inventing meter values in CSS/animation alone.

## Coach as continuous trace

Coach is the always-on human-readable trace:

```
step: Turn 2 of 5
line: Stamp Snort's idea.
sub:  ADMIT grows · DENY blocks · COMPOST buries soft
```

If coach is blank while interactive, VOX fails QA.

## Log as midden (optional)

Last N skin events as short lines. Tags: admit / deny / compost / day.
Log is display of game events, not a second ledger.

## Reducer seam law

```
UI event → reducer function → new state → VOX render(state)
```

VOX files may never:

- write into `/* REDUCER-BEGIN */ … /* REDUCER-END */`
- edit `*_sim.js` / `*_test.js` logic
- call network image generators
- persist sovereign claims

## Verification hooks

`verify_vox.py` checks:

1. `tokens.css` has no `fetch(` / API hosts
2. apply tool refuses to modify files matching reducer markers / `*_sim.js`
3. demo HTML after apply still contains identical script hash (if any)
4. `paid_generation_calls: 0` in manifest
