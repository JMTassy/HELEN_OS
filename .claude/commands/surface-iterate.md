# HELEN Surface Iterator

Fable vision-driven iteration loop: screenshot → critique → fix → re-screenshot → verify.

## Inputs

$ARGUMENTS — surface file path and iteration goal. Example: "helen2027.html warm-up the typography", "home_v1.html add sacred geometry overlay", "temple.html improve dwell detection UX".

## Recipe

### Step 1: Baseline Screenshot
- Open the target HTML file in Chromium (Playwright pre-installed)
- Take a full-page screenshot at 1440x900 (desktop) and 390x844 (mobile)
- Save to scratchpad as `{surface}_baseline.png`

### Step 2: Vision Analysis
- Read the screenshot using Fable's vision capabilities
- Extract current design state:
  - Layout grid (columns, rows, spatial hierarchy)
  - Color palette in use (hex values, contrast ratios)
  - Typography (font families, sizes, weights)
  - Interactive elements (buttons, links, hover states)
  - Animation/motion patterns
  - Sacred geometry elements (rings, mandalas, radial layouts, golden ratio)

### Step 3: Generate Critique
Based on the iteration goal + Source Atlas doctrine + operator preferences:
- What works (keep)
- What violates doctrine (fix)
- What's missing from the goal (add)
- Specific CSS/HTML changes with line numbers

### Step 4: Apply Changes
- Edit the HTML/CSS directly
- Only touch the target file — no new files unless the change requires JS

### Step 5: Verification Screenshot
- Re-screenshot after changes
- Compare baseline vs. new visually
- Score improvement on the iteration goal (0-10)

### Step 6: Operator Review
- Present both screenshots side by side (send to user)
- Show the diff
- Wait for GO / REVERT / ITERATE

## Surface-Specific Design Rules

| Surface | Aesthetic | Key constraint |
|---|---|---|
| helen2027 | Warm sand, UZIK typography | Operator scored 9.2/10 — do NOT regress |
| home_v1 | Dark CRT cockpit, #00d4ff cyan | Receipted-agency: proposals first |
| cockpit_v4 | Dense HUD | Platonic solids, orbital mechanics |
| temple | Semantic cockpit | Dwell detection, receipt spine |
| temple_akashic | Akashic records | Memory visualization, knowledge graph |
| focus | Minimal terminal | Gate clear state, no clutter |
| starship | Navigational | Spatial metaphor, distance = permission |
| goblin/* | Feral creative | UNDERWARREN_SAFE, strange but useful |

## Constraints

- Fable vision tier required for accurate screenshot analysis
- Never degrade operator-scored surfaces below their current score
- Sacred geometry additions must follow the Third-Eye Rule: structural vision only, never mystical overlay
- All changes are NON_SOVEREIGN — surface layer does not affect kernel

## Loop Engineering (Fable)

The golden loop — iterate until the score plateaus:
```
score = 0
while score < target:
    screenshot = capture(surface)
    critique = vision_analyze(screenshot, goal)
    if critique.violations == 0:
        break
    apply(critique.fixes)
    score = vision_verify(surface, goal)
    if score == prev_score:
        break  # plateau — need operator input
    prev_score = score
```
