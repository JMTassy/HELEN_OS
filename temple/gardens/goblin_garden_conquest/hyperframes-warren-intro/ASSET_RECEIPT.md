# Goblin Warren HyperFrames Intro — Asset Receipt

```
authority: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
```

## What shipped (non-sovereign garden asset)

| Field | Value |
|-------|--------|
| Asset | Goblin Warren 6s intro / title card |
| Route | `/motion-graphics` (HeyGen six-decision form) |
| Spec | 6.0s · 1920×1080 · 30fps · draft MP4 |
| Output | `renders/goblin_warren_intro.mp4` (~835 KB) |
| Composition | `index.html` + `assets/home-page-preview.jpg` |
| Lint | `npx hyperframes lint` → 0 errors |
| Validate | `npx hyperframes check` → 25 text WCAG AA pass |
| Style lock | `DESIGN.md` (night warren HUD + mouthless goblins) |
| Prompt | `PROMPT_SIX_DECISIONS.md` |

## Six decisions present

1. **Route** — motion-graphics
2. **Spec** — 6s 1920×1080
3. **Beats** — 0–2 establish · 2–3.5 triad · 3.5–6 title
4. **Copy** — `"GOBLIN WARREN"` · `"Les Gobelins rêvent. Vous décidez."` · triad · authority:false stamp
5. **Technique** — soft squash-and-settle, stagger, lantern breath, grain
6. **Negatives** — no narration, no mouths, no SaaS cyan, no false admission

## Commands

```bash
cd temple/gardens/goblin_garden_conquest/hyperframes-warren-intro
npx hyperframes preview          # studio
npx hyperframes render --quality high --output renders/goblin_warren_intro_high.mp4
```

## Membrane

Garden-only · proposal ⊬ state · render ⊬ admission · HOLD_FOR_OPERATOR
