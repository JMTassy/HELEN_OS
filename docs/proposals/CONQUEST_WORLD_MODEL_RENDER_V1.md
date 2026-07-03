# CONQUEST_WORLD_MODEL_RENDER_V1

```
status        : PROPOSAL · NON_SOVEREIGN · NO_CLAIM · render_only=true
authority     : false
sovereign     : false
canon         : false
ledger_effect : none
max_banner    : 🟣 CLAIM (per WULMOJI rendering rule)
JM_required   : true
```

Render-only doctrine for displaying the CONQUEST world model. A render describes;
it never admits. **Bloom ⊬ Admission.**

---

## 1 · The four layers (never merged)

```
LAYER 1 — WORLD MODEL          LAYER 2 — PROCESS
🜏 TERRARIUM                    🌀 DREAM
├─ 🜃 AVALON   fix·hold·shield      ↓
├─ ⚖️ CAMELOT  law·judge·ally    ⛧ SCHISM
└─ 🜍 MORGANA  mutate·probe         ↓
                                🎯 QUEST
LAYER 3 — GOVERNANCE_COLOR_V1      ↓
⚫🔵🟣🟠🟢🟡⚪🔴                 🧾 PROOF
                                    ↓
LAYER 4 — AGENTS                🗺️ TERRITORY
🧌🃏⚙️💫⏱️                          ↓
                                👑 POWER
```

**The canonical theorem:**

```
CONQUEST = 🌀 → ⛧ → 🎯 → 🧾 → 🗺️ → 👑
```

A dream does not become power directly. It must split, become a quest, produce
proof, stabilize territory — then empower. Épistemic conquest, not military.

---

## 2 · THE COLOR LAW — two namespaces, never one

The core correction this doctrine exists to lock: **GOVERNANCE_COLOR ≠ GARDEN_COLOR.**
The same glyph must never carry both a status meaning and a maturity meaning.

### GOVERNANCE_COLOR_V1 — "what is this object's epistemic/ledger status?"

| Glyph | Status |
|---|---|
| ⚫ | UNKNOWN |
| 🔵 | OBSERVED |
| 🟣 | CLAIM |
| 🟠 | REVIEW |
| 🟢 | ADMITTED (requires operator admission receipt) |
| 🟡 | SEALED (requires hash/version lock) |
| ⚪ | REPLAYABLE (requires replay validation) |
| 🔴 | BLOCKED |

### GARDEN_MATURITY_V1 — "how developed is this object?"

| Glyph | Maturity |
|---|---|
| 🌱 | SEED |
| 🌿 | SPROUT |
| 🌳 | GROWING |
| 🌸 | BLOOMING |
| 🍎 | FRUITING |

### Both must be rendered, side by side

A thing can be 🌸 BLOOMING but 🟠 REVIEW. A thing can be 🍎 FRUITING but 🔴 BLOCKED.
That tension is the point — beauty and status are orthogonal axes.

Example maturity/status table (honest, current):

| Object | Maturity | Status |
|---|---|---|
| Brume Engine | 🌱 SEED | 🔵 OBSERVED |
| Schism Detector | 🌿 SPROUT | 🟠 REVIEW |
| Terrarium World Model | 🌳 GROWING | 🟣 CLAIM |
| CONQUEST Core | 🌸 BLOOMING | 🟣 CLAIM (🟢 only with admission receipt) |
| Beginner Guide | 🍎 FRUITING | 🟣 CLAIM (⚪ only after replay validation) |

**Retired ladder:** the old garden color ladder (🔴 impulse → ⚪ law) collided with
governance colors (🔴 blocked, ⚪ replayable). It is superseded by GARDEN_MATURITY_V1
for maturity rendering. Where the seven-color *state* lattice is used inside game
simulation content (CONQUEST world sim internals), it must be explicitly namespaced
`SIM_STATE:` and never rendered beside governance colors.

---

## 3 · Forbidden collapses (render layer)

```
🌀 → 👑   ❌  dream → power directly
🜁 → 📜   ❌  symbol → ledger
🎯 → 👑   ❌  quest → power without proof
🧌 → 📜   ❌  goblin → ledger
candidate → ledger        ❌
rendered  → proven        ❌
blooming  → admitted      ❌
FABLE/goblin/local model → sovereign truth  ❌
GOVERNANCE_COLOR == GARDEN_MATURITY          ❌  (same glyph, two meanings)
```

---

## 4 · Tiny operator lock (canonical header for every render)

```
👁️ render only · 🌿 garden blooms · 🧮 math holds · 🜁 symbol stays symbol · 📜 ledger sleeps
authority=false · sovereign=false · canon=false · claim=NO_CLAIM
ledger_effect=none · commit=false · push=false · admission=false
```

Every CONQUEST render must end: `HOLD_FOR_OPERATOR`.

---

**Canonical boundary:** `Bloom ⊬ Admission.`
A render can be gorgeous and mean nothing constitutionally. That is by design.
