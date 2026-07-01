# HELEN Vision Audit

Use Fable 5's visual capabilities to audit HELEN's operator surfaces against the Source Atlas doctrine.

## Inputs

$ARGUMENTS — target surface(s). Options: "all", "helen2027", "home_v1", "cockpit_v4", "temple", "temple_akashic", "focus", "starship", "goblin", or a screenshot path.

## Recipe

### Mode 1: Live Surface Audit (HTML files)

1. **Start the dev server** or open the HTML file directly
2. **Screenshot** the surface using Playwright/browser automation
3. **Vision analysis** — evaluate the screenshot against Source Atlas doctrine:

   **Structural checks:**
   - Center = source object (is the primary artifact centered?)
   - Margins = commentary and objections (are they in orbit, not inline?)
   - Bottom rail = actions (are action buttons at the bottom?)
   - Top banner = governance state (is the status bar at top with correct palette?)

   **Palette compliance:**
   - Every governance color used correctly? (⚫🔵🟣🟠🟢🟡⚪🔴)
   - No green on non-admitted artifacts?
   - No decorative color substitution?
   - Background: black/parchment/graphite only?

   **Typography:**
   - SERIF = source text?
   - MONO = receipt/proof data?
   - HUMANIST = commentary?

   **Visual motif presence:**
   - Voxel Memory Mass (corpus as 3D terrain)?
   - Commentary Rings (Talmudic orbit)?
   - Wireframe Proof Chamber (deterministic test space)?
   - Floating Semantic Cubes (typed objects)?
   - CRT/Terminal Overlay (machine witness)?
   - Cathedral/Tower Verticality (build upward through receipts)?

   **Sacred geometry:**
   - Layered cosmology visible (center → orbit → periphery)?
   - Mandala/ring topology present where applicable?
   - Parchment/manuscript commentary layers?

4. **Diff against prior audit** (if exists in memory) — what changed, what regressed?

### Mode 2: Screenshot Comparison

When given a screenshot path:
1. Read the image using vision capabilities
2. Extract: layout structure, color usage, typography, spatial hierarchy
3. Compare against Source Atlas doctrine
4. Output: compliance score (0-10) with specific violations

### Mode 3: Design Iteration

When given a screenshot + "improve":
1. Analyze current state
2. Generate specific CSS/HTML fixes for each violation
3. Apply fixes
4. Re-screenshot and re-audit (the loop)

### Output

```yaml
surface: helen2027
compliance_score: 9.2
palette_violations: []
layout_violations:
  - "Action buttons in sidebar instead of bottom rail"
motif_coverage: 4/7
typography_compliance: PARTIAL  # humanist font missing
sacred_geometry: PRESENT  # warm sand palette evokes parchment layer
recommendations:
  - "Add mono font for receipt data in the queue items"
  - "Move action buttons to bottom rail per Source Atlas §center-orbit"
```

## Constraints

- Vision analysis is Fable-tier only (highest accuracy on dense technical images)
- Never auto-apply CSS changes without showing the diff first
- Screenshot comparison requires the image to be on disk (not a URL)
- Compliance score is descriptive, not sovereign — it doesn't change governance status

## Loop Engineering (Fable)

```
for surface in surfaces:
    score = vision_audit(surface)
    if score < 8.0:
        fixes = generate_fixes(surface, violations)
        apply(fixes)
        new_score = vision_audit(surface)  # re-audit after fix
        log(f"{surface}: {score} → {new_score}")
```
Fable's vision re-audits after each fix, creating a tightening loop.
