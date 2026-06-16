# CHRONOS_WUL_BRIDGE_SPEC_V1

```
MODE           = SANDBOX_TO_KERNEL
AUTHORITY      = false
CANON          = false
STATE_MUTATION = none
STATUS         = proposal
VERSION        = 1.0
```

---

## 1. Purpose

This spec defines a typed auditable bridge for transforming CHRONOS / Shigir / VOID mythic and poetic material into WUL-compliant claim objects. No raw narrative enters the kernel directly. The bridge is a filtration layer — not a governance decision engine.

---

## 2. Core split

| Type | Symbol | Meaning |
|---|---|---|
| NARRATIVE | 📜 | Mythic / poetic / simulator output |
| OBSERVATION | 👁️ | Directly attestable fact |
| HYPOTHESIS | ❓ | Possible interpretation |
| SPECULATION | 🌀 | Creative / unverified symbolic extension |
| CLAIM | 🧾 | Typed object with status + evidence |
| CONFIRMED | ✅ | Evidence-verified claim |
| RISK | ⚠️ | Escalation risk marker |
| FORBIDDEN | 🚫 | Illegal direct promotion |
| CLOSE | 🏁 | Seal |

---

## 3. Epistemic lattice

Allowed promotion path:

```
📜 ⟶ ❓ ⟶ 👁️ ⟶ ✅ 🏁
```

Rule: `status(c) = ✅ ⟹ E(c) ≠ ∅`

No evidence, no confirmation. Forbidden shortcut:

```
📜 ⟶ ✅ = 🚫 🏁
```

Narrative may generate hypotheses. Hypotheses require observation. Observations require evidence. Confirmation requires non-empty evidence set and risk ≠ HIGH.

---

## 4. Primitive glyph vocabulary

| Glyph | Primitive | Domain |
|---|---|---|
| 🗿 | Artifact | Physical object, idol, carved object |
| 📍 | Location | Geographic / site claim |
| ⏳ | Dating | Temporal / chronological claim |
| 🔺 | Geometry | Geometric marking, pattern, form |
| 👤 | Face | Anthropomorphic / facial feature |
| 🌊 | Water | Lake, sediment, aquatic context |
| 💾 | Memory | Information storage, encoding claim |
| ∅ | Null | Undefined / void state |
| ◯ | Potential | Latent / unactualized space |
| Ψ | Observer | Observing agent, consciousness |
| ↻ | Recursion | Self-referential / looping structure |
| ∆ | Transformation | State change, emergence |
| 🧪 | Test | Verification / experimental probe |
| 📸 | Image evidence | Visual / photographic source |
| 📚 | Source evidence | Textual / bibliographic source |
| 🧬 | Material evidence | Carbon dating / biological / physical |

---

## 5. Claim schema

```json
{
  "claim_id": "CLAIM_XXX",
  "source_zone": "CHRONOS_SANDBOX | SHIGIR_CORPUS | VOID_FORMALISM",
  "raw_text_hash": "sha256:<hash_placeholder>",
  "wul_graph": ["glyph", "relation", "glyph"],
  "epistemic_status": "OBSERVED | HYPOTHESIS | SPECULATION | SYMBOLIC_AXIOM_CANDIDATE | REJECTED",
  "evidence": [],
  "risk": "LOW | MEDIUM | HIGH",
  "kernel_admissible": false
}
```

Admissibility rule:

```
A(c) = 1
  iff  epistemic_status ∈ {OBSERVED, CONFIRMED}
  ∧    evidence ≠ []
  ∧    risk ≠ HIGH
```

WULmoji form:

```
A(🧾) = ✅ ⇔ (👁️ ∨ ✅) ⊗ evidence≠∅ ⊗ ⚠️≠HIGH 🏁
```

---

## 6. Math model

Let raw CHRONOS material be:

```
X = {x₁, …, xₙ}
```

Compiler `π`:

```
π : X → G
```

where `G = (V, E, τ, σ, ε)`:

```
V = glyph nodes
E = typed relations
τ = node types
σ = epistemic status function
ε = evidence set
```

Admissibility:

```
A(c) = 1  iff  σ(c) ∈ {OBSERVED, CONFIRMED}  ∧  |ε(c)| > 0  ∧  risk(c) ≠ HIGH
A(c) = 0  otherwise
```

---

## 7. Encoded claims

### 7.1 CLAIM_SHIGIR_GEOMETRY

```json
{
  "claim_id": "CLAIM_SHIGIR_GEOMETRY",
  "source_zone": "SHIGIR_CORPUS",
  "raw_text_hash": "sha256:<placeholder_geometry>",
  "wul_graph": ["🗿", "⊗", "🔺"],
  "natural_text": "The Shigir Idol bears geometric carvings across its surface.",
  "epistemic_status": "OBSERVED",
  "evidence": ["📸 [Ekaterinburg Museum photographic record]", "📚 [Zhilin et al. 2018, Antiquity]"],
  "risk": "LOW",
  "kernel_admissible": true
}
```

WULmoji: `🕯️ CLAIM_SHIGIR_GEOMETRY 🔷 🗿⊗🔺 🔖 STATUS=OBSERVED 🔖 EVIDENCE=YES 🏁`

---

### 7.2 CLAIM_SHIGIR_AGE

```json
{
  "claim_id": "CLAIM_SHIGIR_AGE",
  "source_zone": "SHIGIR_CORPUS",
  "raw_text_hash": "sha256:<placeholder_age>",
  "wul_graph": ["🗿", "⊗", "⏳"],
  "natural_text": "The Shigir Idol is carbon-dated to approximately 12,500 years BP, making it the world's oldest known monumental wooden sculpture.",
  "epistemic_status": "OBSERVED",
  "evidence": ["🧬 [AMS radiocarbon dating, Zhilin et al. 2018]", "📚 [Antiquity 92/362, 2018]"],
  "risk": "LOW",
  "kernel_admissible": true
}
```

WULmoji: `🕯️ CLAIM_SHIGIR_AGE 🔷 🗿⊗⏳ 🔖 STATUS=OBSERVED 🔖 EVIDENCE=CARBON_DATED 🏁`

---

### 7.3 CLAIM_SHIGIR_MATERIAL

```json
{
  "claim_id": "CLAIM_SHIGIR_MATERIAL",
  "source_zone": "SHIGIR_CORPUS",
  "raw_text_hash": "sha256:<placeholder_material>",
  "wul_graph": ["🗿", "⊗", "🧬"],
  "natural_text": "The idol is carved from Kauri larchwood (Larix sibirica).",
  "epistemic_status": "OBSERVED",
  "evidence": ["🧬 [wood species analysis, Zhilin et al. 2018]", "📚 [Antiquity 92/362]"],
  "risk": "LOW",
  "kernel_admissible": true
}
```

WULmoji: `🕯️ CLAIM_SHIGIR_MATERIAL 🔷 🗿⊗🧬 🔖 STATUS=OBSERVED 🔖 EVIDENCE=SPECIES_ANALYSIS 🏁`

---

### 7.4 CLAIM_SHIGIR_ANTHROPOMORPHIC

```json
{
  "claim_id": "CLAIM_SHIGIR_ANTHROPOMORPHIC",
  "source_zone": "SHIGIR_CORPUS",
  "raw_text_hash": "sha256:<placeholder_faces>",
  "wul_graph": ["🗿", "⊗", "👤"],
  "natural_text": "The Shigir Idol has multiple carved faces and anthropomorphic features.",
  "epistemic_status": "OBSERVED",
  "evidence": ["📸 [museum photographic record]", "📚 [Zhilin et al. 2018, face count = 7–8 depending on reconstruction]"],
  "risk": "LOW",
  "kernel_admissible": true
}
```

WULmoji: `🕯️ CLAIM_SHIGIR_ANTHROPOMORPHIC 🔷 🗿⊗👤 🔖 STATUS=OBSERVED 🔖 EVIDENCE=YES 🏁`

---

### 7.5 CLAIM_SHIGIR_LOCATION

```json
{
  "claim_id": "CLAIM_SHIGIR_LOCATION",
  "source_zone": "SHIGIR_CORPUS",
  "raw_text_hash": "sha256:<placeholder_location>",
  "wul_graph": ["🗿", "⊗", "📍"],
  "natural_text": "The idol was found in the Shigir peat bog, Ural region, Russia, in 1890.",
  "epistemic_status": "OBSERVED",
  "evidence": ["📚 [Anuchin 1894, original discovery record]", "📍 [57.6°N 60.2°E, Kirovgrad district]"],
  "risk": "LOW",
  "kernel_admissible": true
}
```

WULmoji: `🕯️ CLAIM_SHIGIR_LOCATION 🔷 🗿⊗📍 🔖 STATUS=OBSERVED 🔖 EVIDENCE=ARCHIVE_RECORD 🏁`

---

### 7.6 CLAIM_SHIGIR_PRESERVATION_CONTEXT

```json
{
  "claim_id": "CLAIM_SHIGIR_PRESERVATION_CONTEXT",
  "source_zone": "SHIGIR_CORPUS",
  "raw_text_hash": "sha256:<placeholder_peat>",
  "wul_graph": ["🗿", "⊗", "🌊"],
  "natural_text": "Preservation was enabled by anaerobic peat bog conditions, preventing wood decay.",
  "epistemic_status": "OBSERVED",
  "evidence": ["📚 [Peat bog preservation archaeology, general literature]", "🧬 [Zhilin 2018 wood integrity analysis]"],
  "risk": "LOW",
  "kernel_admissible": true
}
```

WULmoji: `🕯️ CLAIM_SHIGIR_PRESERVATION_CONTEXT 🔷 🗿⊗🌊 🔖 STATUS=OBSERVED 🔖 EVIDENCE=GEOLOGY 🏁`

---

### 7.7 CLAIM_SHIGIR_ENCODING

```json
{
  "claim_id": "CLAIM_SHIGIR_ENCODING",
  "source_zone": "SHIGIR_CORPUS",
  "raw_text_hash": "sha256:<placeholder_encoding>",
  "wul_graph": ["🗿", "⊗", "🔺", "⟶", "❓", "💾"],
  "natural_text": "The geometric patterns on the Shigir Idol may encode semantic information — a proto-symbolic system.",
  "epistemic_status": "HYPOTHESIS",
  "evidence": [],
  "risk": "MEDIUM",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_SHIGIR_ENCODING 🔷 🗿⊗🔺⟶❓💾 🔖 STATUS=HYPOTHESIS 🔖 EVIDENCE=∅ 🔖 KERNEL=🚫_UNTIL_SOURCE 🏁`

---

### 7.8 CLAIM_SHIGIR_PROTO_LANGUAGE

```json
{
  "claim_id": "CLAIM_SHIGIR_PROTO_LANGUAGE",
  "source_zone": "SHIGIR_CORPUS",
  "raw_text_hash": "sha256:<placeholder_protolang>",
  "wul_graph": ["🔺", "⟶", "❓", "💾", "⊗", "👤"],
  "natural_text": "The geometric marking system represents a coherent proto-language, not decorative pattern.",
  "epistemic_status": "HYPOTHESIS",
  "evidence": [],
  "risk": "MEDIUM",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_SHIGIR_PROTO_LANGUAGE 🔷 🔺❓💾⊗👤 🔖 STATUS=HYPOTHESIS 🔖 EVIDENCE=∅ 🏁`

---

### 7.9 CLAIM_OBSERVER_COLLAPSE

```json
{
  "claim_id": "CLAIM_OBSERVER_COLLAPSE",
  "source_zone": "VOID_FORMALISM",
  "raw_text_hash": "sha256:<placeholder_observer>",
  "wul_graph": ["Ψ", "⊗", "◯", "⟶", "∆"],
  "natural_text": "The act of observation (Ψ) collapses potential space (◯) into transformation (∆).",
  "epistemic_status": "HYPOTHESIS",
  "evidence": [],
  "risk": "MEDIUM",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_OBSERVER_COLLAPSE 🔷 Ψ⊗◯⟶∆ 🔖 STATUS=HYPOTHESIS 🔖 EVIDENCE=∅ 🏁`

---

### 7.10 CLAIM_HYDROMEMORY ⚠️ SANDBOX_ONLY

```json
{
  "claim_id": "CLAIM_HYDROMEMORY",
  "source_zone": "CHRONOS_SANDBOX",
  "raw_text_hash": "sha256:<placeholder_hydro>",
  "wul_graph": ["🌊", "⊗", "💾"],
  "natural_text": "Water remembers — aquatic medium stores and transmits symbolic or energetic information.",
  "epistemic_status": "SPECULATION",
  "sandbox_only": true,
  "evidence": [],
  "risk": "HIGH",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_HYDROMEMORY 🔷 🌊⊗💾 🔖 STATUS=🌀SPECULATION 🔖 SANDBOX_ONLY=TRUE 🔖 KERNEL=🚫 🏁`

---

### 7.11 CLAIM_ELDER_TRANSMISSION ⚠️ SANDBOX_ONLY

```json
{
  "claim_id": "CLAIM_ELDER_TRANSMISSION",
  "source_zone": "CHRONOS_SANDBOX",
  "raw_text_hash": "sha256:<placeholder_elder>",
  "wul_graph": ["👤", "⟶", "💾", "⟶", "👤"],
  "natural_text": "Ancestral knowledge was directly transmitted across 12,000 years through living elder lineage.",
  "epistemic_status": "SPECULATION",
  "sandbox_only": true,
  "evidence": [],
  "risk": "HIGH",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_ELDER_TRANSMISSION 🔷 👤⟶💾⟶👤 🔖 STATUS=🌀SPECULATION 🔖 SANDBOX_ONLY=TRUE 🔖 KERNEL=🚫 🏁`

---

### 7.12 CLAIM_REALITY_BREACH ⚠️ SANDBOX_ONLY

```json
{
  "claim_id": "CLAIM_REALITY_BREACH",
  "source_zone": "CHRONOS_SANDBOX",
  "raw_text_hash": "sha256:<placeholder_breach>",
  "wul_graph": ["◯", "⟶", "∆", "⊗", "🚫"],
  "natural_text": "A reality breach event collapsed the boundary between simulation and governed state.",
  "epistemic_status": "SPECULATION",
  "sandbox_only": true,
  "evidence": [],
  "risk": "HIGH",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_REALITY_BREACH 🔷 ◯⟶∆⊗🚫 🔖 STATUS=🌀SPECULATION 🔖 SANDBOX_ONLY=TRUE 🔖 KERNEL=🚫 🏁`

---

### 7.13 CLAIM_TEMPORAL_SYNC ⚠️ SANDBOX_ONLY

```json
{
  "claim_id": "CLAIM_TEMPORAL_SYNC",
  "source_zone": "CHRONOS_SANDBOX",
  "raw_text_hash": "sha256:<placeholder_temporal>",
  "wul_graph": ["⏳", "⊗", "↻", "⟶", "Ψ"],
  "natural_text": "A temporal synchronization event aligned archaic consciousness with present observation.",
  "epistemic_status": "SPECULATION",
  "sandbox_only": true,
  "evidence": [],
  "risk": "HIGH",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_TEMPORAL_SYNC 🔷 ⏳⊗↻⟶Ψ 🔖 STATUS=🌀SPECULATION 🔖 SANDBOX_ONLY=TRUE 🔖 KERNEL=🚫 🏁`

---

### 7.14 CLAIM_NULL_SOURCE ⚠️ SANDBOX_ONLY

```json
{
  "claim_id": "CLAIM_NULL_SOURCE",
  "source_zone": "VOID_FORMALISM",
  "raw_text_hash": "sha256:<placeholder_null>",
  "wul_graph": ["∅", "⟶", "◯", "⟶", "∆", "⟶", "Ψ"],
  "natural_text": "NULL is the source — void precedes all actualized form.",
  "epistemic_status": "SYMBOLIC_AXIOM_CANDIDATE",
  "sandbox_only": true,
  "evidence": [],
  "risk": "HIGH",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_NULL_SOURCE 🔷 ∅⟶◯⟶∆⟶Ψ 🔖 STATUS=SYMBOLIC_AXIOM_CANDIDATE 🔖 SANDBOX_ONLY=TRUE 🔖 KERNEL=FORMALISM_ONLY 🏁`

---

### 7.15 CLAIM_VOID_RECURSION ⚠️ SANDBOX_ONLY

```json
{
  "claim_id": "CLAIM_VOID_RECURSION",
  "source_zone": "VOID_FORMALISM",
  "raw_text_hash": "sha256:<placeholder_recursion>",
  "wul_graph": ["∅", "⊗", "↻", "⟶", "◯"],
  "natural_text": "The void recursively generates potential: ∅ applied to itself produces ◯.",
  "epistemic_status": "SYMBOLIC_AXIOM_CANDIDATE",
  "sandbox_only": true,
  "evidence": [],
  "risk": "HIGH",
  "kernel_admissible": false
}
```

WULmoji: `🕯️ CLAIM_VOID_RECURSION 🔷 ∅⊗↻⟶◯ 🔖 STATUS=SYMBOLIC_AXIOM_CANDIDATE 🔖 SANDBOX_ONLY=TRUE 🔖 KERNEL=FORMALISM_ONLY 🏁`

---

## 8. Safety law

```
No CHRONOS poetic output enters MAYOR directly.
No simulator warning becomes fact.
No "ancient transmission" becomes evidence.
No metaphysical claim ships without explicit status = SPECULATION.
```

Compressed:

```
📜🌀 ⟶ ⚖️ = 🚫
📜🌀 ⟶ 🧾❓ = ✅
👁️ + 📚 + 📸 ⟶ 🧾✅ = ✅
🏁
```

---

## 9. Claim summary table

| claim_id | status | sandbox_only | kernel_admissible |
|---|---|---|---|
| CLAIM_SHIGIR_GEOMETRY | OBSERVED | false | true |
| CLAIM_SHIGIR_AGE | OBSERVED | false | true |
| CLAIM_SHIGIR_MATERIAL | OBSERVED | false | true |
| CLAIM_SHIGIR_ANTHROPOMORPHIC | OBSERVED | false | true |
| CLAIM_SHIGIR_LOCATION | OBSERVED | false | true |
| CLAIM_SHIGIR_PRESERVATION_CONTEXT | OBSERVED | false | true |
| CLAIM_SHIGIR_ENCODING | HYPOTHESIS | false | false |
| CLAIM_SHIGIR_PROTO_LANGUAGE | HYPOTHESIS | false | false |
| CLAIM_OBSERVER_COLLAPSE | HYPOTHESIS | false | false |
| CLAIM_HYDROMEMORY | SPECULATION | **true** | false |
| CLAIM_ELDER_TRANSMISSION | SPECULATION | **true** | false |
| CLAIM_REALITY_BREACH | SPECULATION | **true** | false |
| CLAIM_TEMPORAL_SYNC | SPECULATION | **true** | false |
| CLAIM_NULL_SOURCE | SYMBOLIC_AXIOM_CANDIDATE | **true** | false |
| CLAIM_VOID_RECURSION | SYMBOLIC_AXIOM_CANDIDATE | **true** | false |

**Claims encoded:** 15
**Sandbox-only:** 6
**Kernel-admissible:** 6
**Hypothesis (pending evidence):** 3

---

## 10. WULmoji receipt candidates

```
🕯️ CLAIM_SHIGIR_GEOMETRY       🔷 🗿⊗🔺        🔖 STATUS=OBSERVED      🔖 EVIDENCE_REQUIRED=YES 🏁
🕯️ CLAIM_SHIGIR_AGE            🔷 🗿⊗⏳         🔖 STATUS=OBSERVED      🔖 EVIDENCE=CARBON_DATED 🏁
🕯️ CLAIM_SHIGIR_MATERIAL       🔷 🗿⊗🧬         🔖 STATUS=OBSERVED      🔖 EVIDENCE=SPECIES_ANALYSIS 🏁
🕯️ CLAIM_SHIGIR_ANTHROPOMORPHIC 🔷 🗿⊗👤        🔖 STATUS=OBSERVED      🔖 EVIDENCE=YES 🏁
🕯️ CLAIM_SHIGIR_LOCATION       🔷 🗿⊗📍         🔖 STATUS=OBSERVED      🔖 EVIDENCE=ARCHIVE_RECORD 🏁
🕯️ CLAIM_SHIGIR_PRESERVATION   🔷 🗿⊗🌊         🔖 STATUS=OBSERVED      🔖 EVIDENCE=GEOLOGY 🏁
🕯️ CLAIM_SHIGIR_ENCODING       🔷 🗿⊗🔺⟶❓💾   🔖 STATUS=HYPOTHESIS    🔖 EVIDENCE=∅ 🔖 KERNEL=🚫 🏁
🕯️ CLAIM_HYDROMEMORY           🔷 🌊⊗💾         🔖 STATUS=🌀SPECULATION 🔖 SANDBOX_ONLY 🔖 KERNEL=🚫 🏁
🕯️ CLAIM_NULL_SOURCE           🔷 ∅⟶◯⟶∆⟶Ψ   🔖 STATUS=SYMBOLIC_AXIOM 🔖 SANDBOX_ONLY 🔖 FORMALISM_ONLY 🏁
🕯️ CLAIM_VOID_RECURSION        🔷 ∅⊗↻⟶◯        🔖 STATUS=SYMBOLIC_AXIOM 🔖 SANDBOX_ONLY 🔖 FORMALISM_ONLY 🏁
```

---

## 11. Final seal

```
📜🌀 ⟶ 🧾❓
👁️📚 ⟶ 🧾✅
∅◯∆Ψ ⟶ 🧠FORMALISM
⚖️ only after evidence
🏁
```

```
AUTHORITY      = false
CANON          = false
STATE_MUTATION = none
PROMOTION      = forbidden until reducer passage
```
