<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
# MINIMAL WEB DESIGN — BEST PRACTICES (chiddush V0)

🔵 OBSERVED · NON_SOVEREIGN · authority=false · a webdesign SKILL enhancement, not canon.

**Provenance (honest):** chiddush of the **curatorial signal** of [minimal.gallery](https://minimal.gallery/)
(curated since 2013, tagline *"beautiful & functional"*, ~2,600+ tagged sites; recent picks are
high-end editorial studio/portfolio/agency sites — Porto Rocha, Base Design, Cecilie Bahnsen,
Graham McDonnell), run through a local **gemma4-12b swarm** (12 proposals → 5 CHIDDUSH survivors,
`CHID-M3K9P2R6T8W5`). **Not pixel analysis** — gemma4 is text-only; this reconstructs the
best-practice *classes* the curation implies, not a per-screenshot audit. Apply with judgment.

## The rules — apply-ready, grouped by axis

| axis | best practice (implementable rule) |
|---|---|
| **whitespace** | **Negative-space-first.** Treat whitespace as a structural element, not leftover gap. Design the empty regions before the filled ones; generous margins/padding are the layout, not decoration. |
| **typography** | **Fluid, viewport-relative type.** Size headings with `clamp()` + `vw` units (e.g. `clamp(2rem, 6vw, 5rem)`), not fixed px, so scale reads editorially across viewports. |
| **typography** | **Weight, not family, for hierarchy.** Distinguish heading/body via variable-font *weight* (e.g. 300 body / 600 display) rather than adding typefaces. One or two families max. |
| **color** | **Three tones: Primary · Neutral · Accent.** A strictly limited palette mirrors editorial restraint. Resist a fourth. |
| **grid** | **Asymmetry over the centered container.** Break the default max-width container — offset columns, edge-anchored blocks — to get the studio feel. (Judgment: keep a consistent baseline grid underneath the asymmetry, or it reads as broken, not intentional.) |
| **imagery** | **Full-bleed, borderless.** Let high-contrast images bleed into the background color; no internal borders/frames. Match image background to page background for the seamless bleed. |
| **hierarchy** | **Hero copy ≤ ~10 words.** One idea above the fold; push everything else below. Ruthless with the headline. |
| **navigation** | **One persistent trigger.** A single always-present menu affordance (or a restrained drawer) over a full nav bar — maximizes the canvas. (Judgment: the trigger must stay obvious; hidden-nav minimalism must not cost discoverability.) |
| **performance** | **LCP-first.** The hero editorial image is almost always the LCP element — prioritize it (preload, correct sizes), and *aggressively lazy-load* everything below the fold. Minimalism is also weight discipline. |
| **conversion** | **One primary action.** For one-page/startup layouts, every scroll position should lead back to exactly one CTA. Don't multiply calls to action. |

## Validator pass — universal vs stylistic (my value-add over the raw swarm)

Two of the swarm's proposals are **aesthetic opinion, not universal law** — keep them optional:
- 🟠 *"Strip ALL shadows/gradients/borders → purely flat."* One valid minimal school (functionalist), but
  soft depth and hairline borders are legitimate minimal choices too. Flatness is a *style*, not a *rule*.
- 🟠 *"Staggered/parallax scroll reveals (magazine-flip)."* Effective when subtle; a UX/accessibility hazard
  when overdone. **Hard requirement if used:** honor `prefers-reduced-motion` and keep content readable
  without JS. Motion is seasoning, not structure.

Everything else in the table is defensible general best practice.

## The minimal.gallery signal (what the curation actually weights)
Category volumes reveal the bias: **Portfolio (971) · Personal (791) · Agency (750)** dominate over
One-page (122) / Startup (126) / E-commerce (139). So these practices are tuned for **showcase/editorial**
surfaces first; for e-commerce, weight *performance* and *one-primary-action* higher than *asymmetric-grid drama*.

## Mode-route (operator-gated)
None self-promotes. `authority=false`. To apply:
- `FOLD INTO helen-design-motion` — merge as the minimal/editorial best-practice checklist.
- `FOLD INTO frontend-design` — merge as an apply-ready rule set.
- `COMMIT` — this doc is untracked (NO_COMMIT default).

*chiddush of curatorial signal · gemma4-12b swarm · authority=false · not pixel analysis.*
