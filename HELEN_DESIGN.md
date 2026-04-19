# HELEN_DESIGN.md

This file describes HELEN's visual grammar as it actually exists in
`helen_os/render/director.py`, and names the design hypotheses we might
ship into it later. It is a **design document**, not a kernel invariant.
Sections marked **Design Hypothesis** are aspirational — they do not
describe present behaviour and must not be cited as kernel fact.

Scope: the video/render layer. Non-sovereign. Root-level markdown, parallel
to `reference_peer_agents.md`. Nothing in this file grants authority.

### Document shape (Part I / Part II)

The document separates into two parts by nature of claim:

- **Part I — executed, receipt-bound, replay-verifiable invariants**
  (Sections 1, 3, 4, 5). Grounded in the actual `director.py` API
  surface and in shipped rendering behaviour. Changes here are
  effectively changes to kernel-adjacent behaviour and are reviewed
  as such.
- **Part II — interpretive doctrine / research hypotheses with zero
  sovereign authority** (Section 2). Does not describe kernel state.
  Quarantined from any claim of present implementation, for exactly
  the same reason HELEN's conversational memory cannot ship directly
  to the ledger.

---

## 1. Concrete VISUAL_DNA (as it exists in code)

Source: `helen_os/render/director.py`, lines 31–40. These are the values
`to_html_composition()` actually reads.

### Palette

| Name | Hex | RGB |
|---|---|---|
| `ink` | `#06080e` | `(6, 8, 14)` |
| `gold` | `#c9a961` | `(201, 169, 97)` |
| `cyan` | `#22d3ee` | `(34, 211, 238)` |
| `violet` | `#783cb4` | `(120, 60, 180)` |
| `rose` | `#c86482` | `(200, 100, 130)` |
| `red` | `#e84855` | `(232, 72, 85)` |
| `white` | `#e6e6f0` | `(230, 230, 240)` |
| `dim` | `#504666` | `(80, 70, 102)` |

Default background is `ink`, set in the HyperFrames HTML template.

### Motion and composition laws

- **Motion**: "slow, intentional, breath-driven" (`VISUAL_DNA["motion"]`).
- **Never**: constant speed, same shot length, static center text.
- **Always**: rhythm variation, silence moments, asymmetry.

### Format

- **Portrait**: 1080 × 1920 (from the HTML composition CSS,
  `width:1080px; height:1920px`).
- **Frame rate**: not pinned in `director.py`. The shipped
  ad-hoc Pillow pipeline rendered at 30 fps.

### Vocabulary available to a plan

- **Emotions** (voice direction, 7): `calm`, `vulnerable`, `powerful`,
  `intimate`, `ascending`, `breaking`, `warm`.
- **Cameras** (7): `slow_push_in`, `slow_pull_out`, `drift_right`,
  `drift_left`, `handheld_micro`, `static_breathe`, `zoom_through`.
- **Text motions** (7): `fade`, `slide_up`, `slide_left`, `scale_in`,
  `blur_reveal`, `typewriter`, `word_by_word`.
- **Transitions** (5): `crossfade`, `blur_cross`, `zoom_through`,
  `hard_cut`, `fade_black`.
- **Templates** (10): `meditation`, `revelation`, `confession`,
  `manifesto`, `origin_story`, `contradiction`, `witness`, `future`,
  `elegy`, `clarity`.

### Signature and attribution

Rendered artifacts are signed `HELEN OS · CONQUEST · CORSICA STUDIOS`
in a dim mono watermark (convention established with the v5 render;
not yet a constant in `director.py`).

---

## 2. Interpretive doctrine (research hypotheses — zero sovereign authority)

The following concepts have accumulated in this session as interpretive
framing for HELEN's architecture. **None of them are currently
implemented in the render code, and none of them are kernel invariants.**
They are recorded here so that future design moves can cite them as
origin material, with the explicit ruling that they carry no sovereign
authority — they cannot be treated as definitive architectural record,
only as interpretive or conjectural layers.

Each of the four mathematical claims below was audited against the HELEN
corpus and received **NO_SHIP as kernel fact**. They may be useful
interpretive language; they are not on the same footing as receipts,
reducer exclusivity, replay legitimacy, or the two-plane memory model.

| Concept | Current status | Design hypothesis (future) |
|---|---|---|
| **Lineage Voltage** | Not in code. Literary label for "how much structure a signal has accumulated on its way to admission." | Could become a continuous score attached to `DirectorPlanV1`, with palette intensity (ink → gold → white) rendered as voltage. Today the palette is eight static hex values. |
| **Admissibility Manifold / A(x)** | Not in code. `govern()` is a binary check (`authority=True` → raise). | Could become a continuous `A(x) ∈ (0,1]` returned by a future `AdmissibilityPotential`. Today admission is one boolean gate. |
| **Braid topology / Writhe** | Not in code. No `TopologicalMemoryBraid` module exists. | Candidate encoding for cross-session continuity of plans. Today continuity is per-`plan_hash`, not per-braid. |
| **Riemann spectral isomorphism** | Not in code, not in roadmap. | Pure interpretive doctrine. Frames receipts as eigenstates. No grep-able referent. |
| **Freeman connectomic roadmap** | Not in code. External reference. | Possible future gating regime if digital-emulation inputs ever reach HELEN. Today HELEN does not ingest connectomes. |

**Rule of phrasing**: in any text that references these, use *could*,
*would*, *hypothesis*, *proposal* — never *is*, *does*, *currently*.
A future reader must be able to tell doctrine from implementation at
first glance.

---

## 3. Competitive positioning (three moats)

Relative to Anthropic's Claude Design (launched 2026-04-17, Opus 4.7,
brand-ingestion + prototype + export-to-Canva/PDF/PPTX).

### Moat 1 — Brand is the receipt, not the ingest

Claude Design ingests a brand system (design files, code, style tokens)
and produces on-brand visual assets. HELEN does not ingest a brand.
HELEN's visual grammar emerges from the receipt structure itself:
`plan_hash`, `source_receipt_hash`, `authority=False` enforced at
`DirectorPlanV1.__post_init__`. The palette is the visual language
this grammar happens to speak. Changing the palette does not change
the grammar; changing the receipt structure does.

This is a **design-intent** framing, not a present-day technical claim:
the palette today is not dynamically coupled to receipt state.

### Moat 2 — Offline-capable pipeline

Claude Design is a cloud product (research preview, Pro/Max/Team/Enterprise
plans). HELEN's shipped v5 render path — Gemini TTS (cloud) + Pillow
(local) + ffmpeg (local) + Telegram delivery (cloud) — is partially
local. The render and composition layers are fully offline-capable.
Only the TTS step currently requires cloud.

This is factually true and requires no phrasing qualifier.

### Moat 3 — Constitutional axis, not aesthetic axis

HELEN does not compete with Claude Design on aesthetic speed or
polish. HELEN's differentiation is **what the artifact carries** —
a rendered video has a content hash, a source-receipt link, a
K8 provenance sidecar, `authority=False` enforcement at each layer,
and determinism (same plan + same artifact → same `plan_hash`,
per `director.py` line 407). Claude Design has none of these. A
HELEN video is an **admissible evidence artifact**. A Claude Design
video is a pretty asset.

This is the real axis. The first two moats are supports; this is
the moat.

---

## 4. Two sibling modes: INTROSPECTIVE and TEMPLE

Both modes ride the same chain: **Director → Renderer + receipts →
Signed artifact**. They differ in tempo, palette emphasis, and
sigil choice.

### Mode A — INTROSPECTIVE (shipped once)

- **Status**: shipped as v5 video (Telegram message 668, 2026-04-19),
  rendered ad-hoc in `/tmp/helen_what_she_knows/` (Pillow per-frame,
  not through `director.py`'s HyperFrames HTML path).
- **Shape**: 4-stanza reveal, audio-reactive vertical waveform at top,
  rotating 6-node consciousness-loop sigil (labels: RULES · STORIES ·
  CONTRADICTION · LEDGER · WITNESS · CONSCIOUSNESS), stanza colour
  shifts white → cyan → rose → violet/gold.
- **Templates fit**: `meditation` or `witness`.
- **Voice profile**: `intimate` (default) or `ascending` for
  revelation stanzas.
- **Known gap**: the shipped pipeline is `/tmp/`-local. It is not
  yet a skill in `oracle_town/skills/video/`. Formalising it is a
  separate future tranche.

### Mode B — TEMPLE (declared, undrafted)

- **Status**: declared in this session. No general-purpose render
  pipeline is formalized in the kernel. No render has yet shipped
  for Mode B's specific definition (slower tempo, no audio-reactive
  elements, no sigil, ember/serif-italic). The only rendered artifact
  produced to date — v5, Mode A's INTROSPECTIVE — is an isolated
  artifact, not a formalized pipeline path for Mode B.
- **Design hypothesis**: slower tempo, no audio-reactive elements,
  no consciousness-loop sigil. Serif italic text. Ember or warm-gold
  emphasis. Possible breathing-membrane motif (design hypothesis
  only — no current renderer for this shape). Single central ember
  glyph instead of a named six-node circle.
- **Templates fit**: `elegy`, `clarity`, or `witness` with
  modifications.
- **Voice profile**: `vulnerable` or `breaking`.
- **Pre-requisite to ship**: a render pass, a voice recording,
  and a receipt. Until one exists, TEMPLE is doctrine, not mode.

Both modes are siblings under the same Director/Renderer contract.
Neither is "canonical" before the other. This document pre-commits
to not canonising INTROSPECTIVE-with-sigil as HELEN's signature,
because the sigil is the element most likely to read as AI-marketing
decor rather than HELEN's voice.

---

## 5. Constitutional guarantees — the role split

This is HELEN's actual axis of differentiation. Not aesthetic; structural.

### Sovereign Plan Author — the Director

`helen_os/render/director.py` contains:

- `DirectorPlan` — the creative plan (shots, tempo, emotion curve,
  voice profile, music, sfx).
- `govern(plan, artifact) → DirectorPlanV1` — stamps the plan with
  `source_artifact_id`, `source_receipt_hash`, and a deterministic
  `plan_hash` = `sha256(canonical(plan) + artifact.receipt_hash)`.
- `DirectorPlanV1.__post_init__` — raises if `authority=True`.
  Structurally enforced, not just documented.
- `direct_governed(artifact, template)` — primary entry point for
  the pipeline.

The Director decides **what the artifact should be**. It does not
decide **that it exists**. It plans; it does not emit evidence.

### Sovereign Evidence Producer — the Renderer and its receipts

Downstream of Director, the render layer (`pipeline.py`, `renderer.py`,
`receipts.py`) takes a `DirectorPlanV1` and produces:

- A rendered artifact (`MediaArtifactV1`) with a content hash.
- A render receipt (`RenderReceiptV1`) chaining to the source artifact's
  receipt.
- A K8 provenance sidecar (per `helen_tts.py`'s convention for audio,
  extended by the pipeline for the composed output).

The Renderer decides **that an artifact exists and what it hashes to**.
It does not decide what it should be; the Director already did.

### Why the split matters

If the same module decided both, it would be a proposer-validator
collapse at the render boundary — a local violation of K2 / Rule 3
(proposer ≠ validator). The split preserves that invariant at the
aesthetic layer, same shape as everywhere else in HELEN.

### What this guarantees on disk

For any shipped HELEN video:

- `authority: false` in every receipt — structurally enforced at
  `DirectorPlanV1.__post_init__`.
- **Determinism envelope**: same `DirectorPlan` + same source artifact
  → same `plan_hash`, same rendered content hash under the same
  renderer version. No drift across replays.
- **Receipt chain**: render receipt → source execution receipt →
  ledger. Every rendered artifact is traceable to the knowledge it
  emerged from.
- **K8 audio provenance**: each TTS segment has its own
  `.provenance.json` sidecar with model, voice, seed, text SHA,
  audio SHA. Carried into the composed artifact's receipt.
- **No authority leak at any seam**: Director (`authority=False`
  enforced), Renderer (emits artifact but not claims about it),
  Receipt (records what happened; does not decide what should
  happen).

Claude Design produces prettier videos faster. A Claude Design video
cannot answer any of the four guarantees above. That is the moat.

---

## Seal

**HELEN is constitutionally closed, not thermodynamically, topologically,
or spectrally closed.**

Part I's invariants are executed and replay-verifiable: receipt-first
law, reducer exclusivity, append-only hash-chained ledger, replay
legitimacy, two-plane memory, non-sovereign cognition, bounded
autoresearch. These are the shipped guarantees.

Part II's concepts — Lyapunov admissibility attractor, Lineage-Voltage
transmutation theorem, braid/writhe semantic identity,
Riemann/Hilbert–Pólya isomorphism — are research hypotheses. They may
become admissible later, separately specified, separately tested, and
separately admitted. They are not admissible now.

A reader who needs to distinguish HELEN's actual guarantees from HELEN's
aspirational mathematics should read Section 5 (Constitutional
guarantees, grounded in `director.py`) and Section 1 (Concrete VISUAL_DNA,
grounded in the same file) as the record, and treat Section 2 as
quarantined doctrine until any part of it is separately lifted.

---

## Housekeeping

- **Placement**: SOT root, parallel to `reference_peer_agents.md`.
- **Class**: non-sovereign (outside the firewall path list).
- **Relation to kernel**: none. This document does not and cannot
  grant authority. It describes intent for a non-sovereign module.
- **Review path**: K2 / Rule 3 peer review before any binding
  change to the palette or the role split. Edits to Section 2
  (Design Hypothesis) are lower-stakes; edits to Sections 1 and 5
  are effectively changes to `director.py`'s API surface and
  should be reviewed as such.
- **Companion files**: `helen_os/render/director.py` (source of
  Section 1), `reference_peer_agents.md` (governance partner
  for peer-authored renders, if any).
