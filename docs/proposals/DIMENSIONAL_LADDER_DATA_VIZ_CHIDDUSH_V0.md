<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
<!-- CHIDDUSH_ARCHIVE output · 2026-08-22 · NON_SOVEREIGN · untracked (NO_COMMIT / NO_PUSH until operator verb) -->

# DIMENSIONAL_LADDER_DATA_VIZ — CHIDDUSH V0.2

A visual grammar for dimensional expansion in HELEN/Garden interfaces,
extracted from a dimensionally-confused source **without inheriting its
claims**. V0.1 adds the orthogonal **Scale** axis from a second fragment
(numeric 6ⁿ ladder), same firewall. Two core rules:

**Dimension exposes hidden variables. Scale exposes hidden organization.**

**Higher dimension = expose a variable that was previously collapsed.
When a visualization feels overloaded, don't add more marks to the same
dimension — promote the hidden variable into a new navigable axis.**

## Corpus status

| Layer | Item | Status |
|---|---|---|
| S | Spoken fragment on dimensions/time (operator relay, 2026-08-22) | `MYTHIC_SIGNAL` — "4th dimension = motion" is pedagogical metaphor, not mathematics; "all time exists simultaneously (music/physics)" is asserted eternalism, not a result. **Canon-ineligible; hypothesis-generator only.** |
| S | Upstream chiddush extraction (CHIDDUSH-prefixed relay, same day) | `REPORTED` — correctly self-bounded: "data-viz grammar, not science claim" |
| G | "New axis = previously entangled variable made explicit" | Concordant with established info-viz practice (Bertin retinal variables, faceting/small multiples, Shneiderman overview→zoom→filter) — `derived`, independently supported |
| ⚠ | Epistemic firewall | This doc's standing does **not** flow from the source's dimensional claims. Stream-adjacency to the Hopf corpus ⊬ epistemic adjacency (`G_R ⊬ G_E` applied to the relay channel). |
| S | Fragment #2: 6ⁿ numeric ladder (6→36→216→1296, "musical relationship", compass) | `MYTHIC_SIGNAL` — arithmetic verified (6ⁿ correct; cube face-angle sum 2160°; 1,296,000 arcseconds/circle) but every "appearance" is an artifact of base-10 padding + Babylonian sexagesimal conventions (360°, 3600″). Conventions ≠ constants. `NumericalCoincidence ⊬ PhysicalSignificance`. |
| S | Upstream chiddush extraction #2 (CHIDDUSH-prefixed relay, same day) | `REPORTED` — correctly self-bounded ("numeric scale ladder, not science claim") |
| G | "Zoom = semantic resolution transition, not camera movement" | Concordant with established practice — **semantic zooming** is a named technique (Perlin's Pad, Pad++, ZUI literature) — `derived`, independently supported |
| S | Fragment #3: "compass = best reference for measuring time?", 6⁵=7776, "hypercube in motion, multiple directions" | `MYTHIC_SIGNAL` — killed by unit analysis: 360°×60′×60″ = 1,296,000 **arcseconds**, not seconds of time. `1,296,000″ ≠ 1,296,000 s` ⇒ compass-as-clock does not follow. Cyclic-coordinate intuition rescued below. |
| S | Upstream analysis #3 (θ/orientation extension, same day) | `REPORTED` — carries the unit correction itself; middle of paste was a byte-duplicate of extraction #2, deduplicated (one root, one capture) |

## The ladder (HELEN mapping)

| D | Visual | HELEN object |
|---|---|---|
| D1 | position | EVENT (one receipt, one witnessed transition) |
| D2 | relation | LINEAGE (event → event edges) |
| D3 | enclosure | STATE / CAUSAL GRAPH |
| D4 | trajectory | REPLAY (σ₀ → σ₁ → σ₂ …) |
| D5 | parallel trajectories | BRANCHES (worktrees, candidate histories) |
| D6 | multi-state field | GOVERNED POSSIBILITY SPACE (branches + witnesses + authority + admission status) |

Compression: `• → — → ▢ → ↻ → ⫴ → ∞`
(event → relation → state → replay → parallel histories → possibility field)

## The genuinely good idea

"All of time simultaneously" is false as physics-by-assertion but **true by
construction of HELEN's ledger**: an append-only hash-chained history is a
block universe of institutional time. Every past state coexists and is
addressable; `Replay` is lawful traversal that never mutates
(`reversible cognition ≠ irreversible trust`). The replay lens moves through

    event-time × branch × state

so the operator is not trapped at "now" — they can see what happened, what
was proposed, what was rejected, what was HELD, what became admitted, and
where histories diverged. The mystic gestured at a capability HELEN
implements literally.

## V0.1 — The Scale axis (orthogonal to Dimension)

The second fragment adds a distinct operation:

    Dimension = variable exposure        (make a collapsed variable navigable)
    Scale     = aggregation depth        (make a local pattern aggregate)
    Dimension ⊥ Scale

A 2D view can traverse many scales; a 3D view can be stuck at one. The
zoom hierarchy `Resolutionₙ = bⁿ` (aesthetic seed b=6: 6 local anchors →
36 relation field → 216 subsystem → 1296 ecosystem) maps to HELEN as:

    EVENT → TASK → CAMPAIGN → INSTITUTION

one zoom gesture changing **semantic resolution** — density, rhythm,
label granularity, animation cadence, optionally sonification
("harmonic zoom": pulse → chord → phrase → composition) — never merely
magnification, and never losing lineage.

**Navigation tensor:** a HELEN view is addressed by

    View(d, s, t, b, p)
    d = dimensional axis exposed · s = aggregation scale
    t = temporal position · b = branch · p = provenance depth

replacing one overloaded dashboard with a navigable coordinate system.
The 6ⁿ motif is retained as a **Garden harmonic seed only** —
`bⁿ ⊬ natural dimension law`, `VisualHarmony ⊬ Truth`.

## V0.2 — The θ (orientation) axis

The compass fragment, unit-corrected, contributes one real structural move:

    linear coordinate → cyclic coordinate → multidirectional state space

A timeline is `t ∈ ℝ` (progression); a compass is `θ ∈ S¹` (orientation).
Neither substitutes for the other:

    Clock gives progression; compass gives orientation.

**State compass** — θ as the system's current *mode of change*, cyclic and
rotatable through time:

              EXPLORE
                 ↑
        REPAIR ← • → EXECUTE
                 ↓
               HOLD

The navigation tensor extends to **`View(d, s, t, θ, b, p)`**, and the
6ⁿ harmonic ladder gains a top rung: `6⁵ → branching trajectory field`
(one trajectory → many possible directions of motion — the honest reading
of "hypercube in motion").

Three-instrument rule:

    A timeline tells you when you are.
    A compass tells you how the state is oriented.
    A branch field tells you where it could go.

    Time × Orientation × Branch = navigable possibility geometry.

θ is a **render/navigation coordinate** (🌈): orientation displayed ⊬
transition permitted — mode changes still cross their typed gates
(EXPLORE→EXECUTE is a governed transition, not a dial turn).

## Required repair (counterexample lens, applied at capture)

**Navigable ≠ rendered-spatial.** Literal 3D dashboards reliably
underperform 2D (occlusion, perspective distortion, interaction cost). The
ladder is sound only if "promote to a new axis" means a *navigable* degree
of freedom — facet, filter, zoom scale, branch-lens, scrubber — not
necessarily a rendered spatial axis. D3 "volume" and beyond should default
to faceting and lenses; spatial 3D/4D rendering must earn its place per
view (e.g. the Hopf-fiber Garden view is an aesthetic choice, governed by
[HOPF_FIBRATION_GARDEN_VIZ_CHIDDUSH_V0](HOPF_FIBRATION_GARDEN_VIZ_CHIDDUSH_V0.md)).

## Axis-promotion table (design rule of thumb)

    too many events     → expose time
    too many timelines  → expose branch
    too many agents     → expose actor axis
    too many claims     → expose provenance axis
    too many statuses   → expose entitlement axis

Dimensionality as a **compression strategy**: an overloaded mark-set is a
signal that a variable is entangled and wants its own navigable axis.

## Laws carried over

    projection ≠ state · Delete(viz) ⇒ ΔLedger=0 (ontological test)
    depicted adjacency ⊬ permission (VISUAL_RELATION_NOT_AUTHORITY)
    branch shown ⊬ branch admitted · 🔵¹→🌈ⁿ ⊬ 🔵ⁿ
    MYTHIC_SIGNAL generates hypotheses; receipts decide

## Mode-route (operator-gated)

- Seed A — zoom-scale spec (RECEIPT → LINEAGE → TASK GRAPH → PROJECT SPACE → EXECUTION MOVIE → ALTERNATIVE HISTORIES) for the Garden UI: `NEEDS_OPERATOR` → design bead (`helen-design-motion`, never NEPTION).
- Seed B — replay-lens prototype over an existing spine (`event-time × branch × state` scrubber on `~/helensh/state/receipts/` as demo corpus): `NEEDS_OPERATOR`.
- Seed C — deletion-test falsifier for any built view (`Delete(viz) ⇒ ΔLedger=0`): `NEEDS_OPERATOR`, one-arm, cheap.
- Seed D — `View(d,s,t,b,p)` navigation spec + semantic-zoom prototype (scale axis over the same demo corpus as Seed B): `NEEDS_OPERATOR`.

None self-promotes. NEEDS_OPERATOR verb to move any seed anywhere.
