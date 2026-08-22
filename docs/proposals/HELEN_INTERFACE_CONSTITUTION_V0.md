<!--
authority=false · canon=false · claim=NO_CLAIM · ledger_effect=none · SPEC_CANDIDATE / NON_AUTHORITATIVE
A UI constitutional layer between typed application state and component recipes. Does NOT change the semantic-color
SOT, the Anti-ADHD Color WULmath policy, Source Atlas, or WULmoji semantics — it binds them. None self-promotes.
NEEDS_OPERATOR verb to promote any rule. Companion executable: experiments/helen_mvp_kernel/fable_lean_v0/ui_invariant_lint_v0.py
-->

# HELEN_INTERFACE_CONSTITUTION_V0 — SPEC_CANDIDATE · NON_AUTHORITATIVE · NO_CLAIM

The layer between typed state and pixels:

    Typed State → Semantic Tokens → UI Constitution → Component Recipe → Render

It is not a design system and not a skin. It is the **non-interference contract for surfaces**: the rules under which
presentation may become richer *without* presentation ever gaining semantic or constitutional power. It is SPNI, lowered
to the interface.

## 1 · Core separation (the non-collapse law)

    Presentation  ≠  Semantics  ≠  Authority
    TypedState > ColorProjection · ImportedDesignSkill ⊬ Override(HELENCanon) · DesignInvariant ≠ DesignPreference

    Color renders state.        Color does not mint state.
    Typography gives hierarchy. Motion gives continuity.
    WULmath gives relation.     Typed state carries meaning.

Direction is one-way:

    REJECT(state) → --color-status-danger          (typed state → semantic token → rendered colour)
    rendered_red  ⊬ REJECT                          (seeing red never mints REJECT — Perception ⊥ Entitlement)

## 2 · Precedence lattice (the deterministic conflict resolver)

    Accessibility > Typed Semantics > HELEN Governance > Interface Invariants > Imported Recipe / OA Design > Decorative Styling

Any lower layer that conflicts with a higher layer **loses automatically**. This replaces aesthetic negotiation with a
decision procedure: OA recipes and decoration sit below governance and typed semantics, so they can never override the
colour law or a typed state. It is why importing oa-design/net-art skins is safe — they enter *below* the line that
protects meaning.

## 3 · Semantic colour (preserve the existing SOT — do not fork it)

The fixed SemanticColor SOT (Source Atlas ⚫🔵🟣🟠🟢🟡⚪🔴, one-meaning-per-colour) and the Anti-ADHD two-layer palette
(SEMANTIC frozen · PRESENTATION accents) are **preserved and placed at the top of the lattice**. This document adds no
colours and changes no meanings.

    Require:   TypedState → semantic projection → semantic token → rendered colour
    Prohibit:  a second semantic-colour ontology · primitive colour used as state authority · state inferred from colour alone
    Accents 🌈🧬🔥💎🛡 = ATTENTION ONLY:   accent ⊬ state · accent ⊬ evidence · accent ⊬ authority

## 4 · Visual grammar (typography carries hierarchy *because* it no longer carries authority)

| register | use | INVARIANT / PREFERENCE |
|---|---|---|
| DISPLAY / SERIF | concepts, chapter transitions, Garden titles, major state transitions | PREFERENCE (face) |
| SANS | operational prose, controls, navigation, explanatory UI | PREFERENCE (face) |
| MONO / TABULAR | receipts, hashes, timestamps, IDs, WULmath, metrics, diffs | **INVARIANT** (tabular-nums on changing numerics) |

Typography rules, classified:
- **INVARIANT**: `tabular-nums` on changing numeric/data values · accessible truncation (full value retrievable) ·
  `overflow-wrap: break-word` where IDs/URLs can escape · root-level font smoothing only.
- **PREFERENCE** (never linted): serif-vs-sans, `.woff2` packaging, 60–75ch measure, `text-wrap: balance/pretty`,
  natural-case source + presentational `text-transform`, smart punctuation.

## 5 · Motion (communicates causality, never entitlement)

    INVARIANT:  forbid `transition: all` (name exact properties) · non-essential motion MUST have a prefers-reduced-motion guard ·
                theme switch must not animate · `will-change` only for transform/opacity/filter and only when justified
    LAW:        ΔMotion ⊬ ΔEntitlement — a state transition may animate; scanning stays still; motion never changes what is admitted.

## 6 · Accessibility floor (top of the lattice — non-negotiable)

    INVARIANT:  native semantic interactive elements · :focus-visible required · no positive tabindex ·
                icon-only control requires accessible name · no aria-hidden=true on a focusable control ·
                real labels for inputs · colour is never the sole status carrier · role=status routine / role=alert urgent ·
                skip-to-content first · prefers-reduced-motion respected · documented touch hit-area floor · paste not blocked

## 7 · Layout (mostly design rules; one lintable)

    DESIGN RULE (DOCUMENT_ONLY): concentric radii on nested surfaces · optical > geometric alignment ·
                group gap ≥ 2× internal gap · logical CSS properties · quiet nested surfaces
    INVARIANT (lintable-partial): no fixed dimensions on text containers

## 8 · Writing (interface language, not epistemic state)

    verb-first action labels · confirmation repeats the consequence · one term per flow · destination-bearing links ·
    sentence-case default · toggle label describes the ENABLED state · empty state = orientation + one action · address the reader as "you"
    (These are interface-language constraints; they carry NO epistemic authority.)

## 9 · SPNI binding (the theorem this whole layer instantiates)

For any renderer / style transform `p`:

    ΔPresentation ≠ 0  ⇒  ΔLoadBearingSemantics = 0

A UI transform MAY alter: typography · spacing · density · motion · decorative colour · wording surface.
It MAY NOT alter: Decision · ReasonCode · Authority · Admission · Warrant · Receipt semantics · Replay outcome.

## 10 · Executable subset (the point — a quality floor, not a style guide)

Only the mechanically-checkable invariants are linted (`ui_invariant_lint_v0.py`), classified honestly:

    ENFORCED       UI001 transition:all · UI003 outline suppression w/o focus-visible · UI004 positive tabindex ·
                   UI006 non-essential motion w/o reduced-motion guard · UI009 aria-hidden on focusable
    PARTIAL        UI002 primitive state-colour in components · UI005 clickable non-semantic div/span · UI010 icon-only button w/o name
    DOCUMENT_ONLY  UI007 dynamic metric w/o tabular-nums · UI008 hardcoded state-colour bypassing token (semantics not statically decidable)

The required non-interference property of the linter itself:

    InvariantViolation ⇒ Reject      ∧      PreferenceVariation ⇒ Permit      ⇒      StyleDifference ⊬ Violation

Taste stays in GARDEN. The gate enforces invariants, never preferences.

---
authority=false · canon=false · claim=NO_CLAIM · ledger_effect=none · a reading, not a ruling · NEEDS_OPERATOR verb to promote
