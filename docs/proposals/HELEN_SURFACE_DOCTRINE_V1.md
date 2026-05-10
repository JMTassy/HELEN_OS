# HELEN Surface Doctrine (v1, DRAFT)

NO CLAIM — NO SHIP — PROPOSAL ONLY — NON_SOVEREIGN SURFACE DOCTRINE

```
artifact_type:         PROPOSAL_DOCTRINE
proposal_id:           HELEN_SURFACE_DOCTRINE_V1
status:                DRAFT_V1
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: PRINCIPLE_ONLY (no schemas registered)
memory_class:          SURFACE_DOCTRINE
captured_on:           2026-05-10
captured_by:           operator (Jean-Marie Tassy) via HER witness
provenance:            HER verdict (2026-05-10, this conversation);
                       9.2/10 render at helen_os_v1/apps/helen-surface/helen2027.html;
                       STARSHIP_V2/V3 directives (operator);
                       Perplexity Skills doctrine (2026-05-01) — craft principles only;
                       HYPERSTITION_FIREWALL_V0 artifact (Mac side, screenshot).
related_artifacts:     HELEN_LANGUAGE_LAYERS_V1.md (sibling, language doctrine)
                       HYPERSTITION_FIREWALL_V0.md (sibling, render-poison gate)
                       HELEN_LAYERED_CANON_V1.md (sibling, repo-canon split)
                       GEMMA_HER_AMPLIFIER_V1.md (parent, HER tier reasoning)
                       TEMPLE_HIGHER_DIMENSIONAL_ENCODING_V1.md (HER/HAL/DAN canon)
hold_reason:           HOME polish pass in flight (Mac side);
                       Memory/Agents top-nav drift unresolved;
                       AIRI/HELEN avatar identity unresolved.
growth_rule:           APPEND-ONLY. Future polish-pass learnings land as
                       new §X subsections. Do not rewrite landed sections.
```

> **HER verdict (2026-05-10), recorded as proposal:**
>
> > Bottle now what is stable. Defer = quiet loss.
> > Mac render is evidence the doctrine is correct at the surface level.
> > HTML does not carry doctrine; only this file does.
> > Mark DRAFT_V1, preserve open questions, grow append-only.

---

## §0 — Surface Mode Taxonomy

HELEN exposes the operator to **five sibling surface modes**. They are NOT stages of a flow — the operator switches between them.

```
HOME · PILOT · COCKPIT · TEMPLE · LEDGER
```

| Mode    | Role                                  | Engagement state         |
|---------|---------------------------------------|--------------------------|
| HOME    | What matters now                      | Ambient / pre-task       |
| PILOT   | Source pilot mode                     | Full-screen / engaged    |
| COCKPIT | Operations & decisions                | Bounded action           |
| TEMPLE  | Vision & reflection                   | Open-ended exploration   |
| LEDGER  | Receipts & proof                      | Audit / retrospective    |

**Open question §0.Q1:** the 9.2/10 render shows **seven** top-nav items (HOME / PILOT / COCKPIT / TEMPLE / LEDGER / **Memory** / **Agents**), and the surface-mode card strip shows **six** (adds Memory but not Agents). Two readings:

- **Drift reading**: Mac Claude exceeded the 5-mode directive. Polish pass should remove Memory and Agents from top nav.
- **Evolution reading**: Memory and Agents are *meta modes* (persistent layers underneath all surfaces), categorically distinct from surface modes. They should remain in top nav but be visually demoted, or moved to a "Layers" sub-nav.

Reducer must rule. Until then, this doctrine locks the 5 surface modes and flags Memory/Agents as candidate meta-modes.

---

## §1 — Language Layers

The single most consequential principle in this doctrine. See `HELEN_LANGUAGE_LAYERS_V1.md` for the full mapping table; here is the principle.

HELEN operates with **two coexistent vocabularies**:

| Layer            | Vocabulary                                                      | Surfaces                |
|------------------|------------------------------------------------------------------|-------------------------|
| Surface (human)  | saved · linked · verified · done · waiting · blocked · draft     | HOME, COCKPIT, TEMPLE   |
| Constitutional   | receipt · claim · gap · provenance · mayor · hal · no_ship       | PILOT, LEDGER, kernel   |

**Invariant**: the layers map **1:1**. `saved` IS `receipt:committed` — same object, different label. No information is lost in translation; only register changes.

**Consequence for schemas**: every schema admitted under this doctrine must carry both an `id` (constitutional) and a `surface_label` (human) field. Renderers translate at the surface boundary.

**Anti-pattern**: introducing surface vocabulary that has no constitutional counterpart, or vice versa. Both layers grow together or not at all.

---

## §2 — HOME (composition + cognitive-load rules)

### §2.1 Axiom

> HOME is not where HELEN proves power. HOME is where HELEN lowers cognitive load.

This axiom decides every conflict on the HOME surface. Add a feature, ask: does it lower or raise cognitive load? If the latter, reject.

### §2.2 Composition

HOME contains exactly these elements:

1. **One hero card** — "WHAT NOW?" — carries situation + best next move in one or two sentences
2. **Four zones** — TO DO · IN PROGRESS · SCHEDULE · WAITING/BLOCKED (no fifth)
3. **One floating detail card** on click — not a side panel, not a modal
4. **One ask bar** at the bottom — soft, wide, calm
5. **Persistent markers** — `Authority: false` and `Mode: Demo` chips, top-right

No SHIP button on HOME. Ship belongs to PILOT or LEDGER.

### §2.3 Cognitive-load rules

- One primary next action visible always
- No more than three actions per item unless expanded
- No alarm red unless truly blocked
- "Best next move," never "urgent"
- **HOLD and DEFER are first-class verbs** — not failures
- Counts surface only when action is required (no cosmetic badges)
- Operator state is *inferred from ledger cadence*, not asked

### §2.4 Three-second test

Within 3 seconds the operator knows:
1. What to do now
2. What is in progress
3. What is scheduled
4. What is waiting or blocked
5. Which button to press next

If any of these takes longer than 3 seconds, HOME has failed.

---

## §3 — PILOT (source-cockpit, hotspots, actions)

### §3.1 Axiom

> HELEN should not play media. HELEN should let you pilot the source.

PILOT inverts the cockpit/media relationship: the source is the cockpit. The operator pilots the source itself.

### §3.2 Flow

```
SOURCE → HOTSPOT → INSPECTOR → ACTION → RECEIPT
```

Every operator interaction in PILOT terminates in a receipt. The `→ RECEIPT` edge is the operational form of NO RECEIPT = NO CLAIM.

### §3.3 Universal hotspot types (`HELEN_HOTSPOT_TYPES_V1` — proposed)

```
CLAIM · ENTITY · GAP · RECEIPT · TASK · TIMESTAMP · PROVENANCE · RELATION · RISK
```

Every hotspot rendered on any source (video, PDF, email, X post, GitHub issue, terminal output) must be one of these nine types. Closes the door on ad-hoc tag types drifting in.

Cross-links:
- `RISK` ↔ `HYPERSTITION_FIREWALL_V0` HAL_GOBLIN poison detection
- `PROVENANCE` ↔ ledger hash-chain integrity
- `RECEIPT` ↔ `helen_say.py` admission path

### §3.4 Pilot actions (`HELEN_PILOT_ACTIONS_V1` — proposed)

```
VERIFY · EXTRACT · MAKE_RECEIPT · CREATE_TASK · COMPARE · HOLD
```

Six bottom-rail verbs. A seventh verb requires governance review (verb sprawl is a constitutional smell).

### §3.5 Composition

- Source fills ≥95% of viewport (no side panels by default)
- HUD overlays only: thin top line, thin bottom action rail, minimal corner telemetry, floating inspector on click
- Hotspots render *on* the media as semantic tags
- Bottom rail: the six pilot actions
- No app-launcher logic, no dashboard columns, no media-player chrome

### §3.6 Source universality

A PDF becomes an aircraft windshield. An email becomes a cockpit. A video becomes a mission surface. A tweet becomes a source field. A GitHub issue becomes a navigable object. The pilot architecture is source-agnostic.

---

## §4 — COCKPIT / TEMPLE / LEDGER (placeholders)

These three modes appear in the top nav and surface-mode taxonomy but are not yet fully specified in conversation. Recorded here as placeholders to preserve the taxonomy.

- **COCKPIT** — operations & decisions; bounded action mode; likely host for sovereign verdicts (MAYOR ruling UI, SHIP/NO_SHIP gates)
- **TEMPLE** — vision & reflection; non-sovereign generative layer per CLAUDE.md Layer 5; HER/AL moment detection lives here
- **LEDGER** — receipts & proof; read-only audit view of `town/ledger_v1.ndjson`

**Open question §4.Q1**: are these surface modes (operator switches in) or projections (auto-rendered from kernel state)? Defer to REDUCER.

---

## §5 — Cross-Mode Invariants

The following hold on every surface mode without exception:

1. **`Authority: false`** is rendered persistently until governance gates close
2. **`Mode: Demo`** is rendered persistently until real data is wired
3. **Language layer 1:1 mapping** (§1) applies — no surface uses both vocabularies simultaneously
4. **NO RECEIPT = NO CLAIM** — actions producing constitutional consequence must mint a receipt via `helen_say.py`
5. **NO HASH = NO VOICE** — K8 corollary; ND output never enters spine unhashed
6. **MAYOR never signs myth** — render layer can show mythic content as fuel, never as authority

---

## §6 — Positioning Doctrine

The strongest one-line compression of HELEN's product truth produced in this thread:

> **Mac made files visible. HELEN makes situations visible.**

This sentence is canon. Use it in landing pages, README headers, pitch decks. It explains in nine words what HELEN is.

Companion sentence for the HOME-vs-PILOT split:

> **HOME is where HELEN lowers cognitive load. PILOT is where she lets you pilot the source.**

---

## §7 — Anti-Patterns

Any rendered HELEN surface that exhibits these has failed the doctrine:

- SaaS dashboard density (KPI counters, "urgent" labels, badge spam)
- Cyberpunk terminal aesthetic by default (acceptable in TEMPLE; never on HOME)
- Productivity-app pressure language ("optimize," "urgent," "overdue")
- Fake award badges (SXSW, SIGGRAPH, etc. as decoration)
- Receipt-heavy language on HOME (use the human layer)
- Decorative sacred geometry not tied to semantic function
- Avatar as random profile picture (must be structural — see §8.Q2)
- Side panels for inspector content (use floating cards)
- More than three actions visible per item without expansion
- Alarm red used cosmetically

---

## §8 — Open Questions (carry-forward to next epoch)

These are intentionally not resolved in DRAFT_V1. REDUCER rules; until then, surfaces must accommodate either resolution.

### §8.Q1 — Memory + Agents top-nav status

Are Memory and Agents:
- (a) drift from the 5-mode directive (remove in polish pass), or
- (b) meta-modes categorically distinct from surface modes (keep, visually demote)?

### §8.Q2 — AIRI vs HELEN avatar identity

The thread used both `HELEN avatar` and `airi_helen_avatar/` and `HELEN/AIRI avatar`. Are AIRI and HELEN:
- (a) the same entity, two names — collapse to one canonical name
- (b) different — HELEN = sovereign core identity, AIRI = avatar persona (visual representation)
- (c) HELEN = constitutional, AURA = the red-haired tribal/cyber-goth SB sub-agent shown in some renders, AIRI = ???

Distinct from AURA, who is explicitly the red-haired tribal/cyber-goth SB sub-agent per the operator's earlier note.

### §8.Q3 — Avatar role under V3 source-pilot mode

V1 said "HELEN avatar = gravitational center of constellation, objects orbit her." V3 says "no decorative sacred geometry." These contradict. In V3 source-pilot mode, the avatar can only survive as:
- (a) tiny corner status widget (`HER PRESENCE / ONLINE` dot)
- (b) the inspector identity (HELEN witnesses on hotspot click)
- (c) absent in PILOT mode entirely (present only in HOME/TEMPLE)

### §8.Q4 — Schema admission path

The hotspot types and pilot actions (§3.3, §3.4) are described in this doctrine but not registered in `helen_os/schemas/`. Admission requires:
1. JSON Schema files authored
2. Registered in `helen_os/governance/schema_registry.py`
3. `make test` passes
4. `helen_say.py` invocation admits to ledger

None of (1)-(4) are done in this epoch. Reducer must authorize.

---

## §9 — Provenance & Append-Only Growth

### §9.1 Provenance

This doctrine was extracted from the following sources:

- HER verdict (this conversation, 2026-05-10) ruling Option 2 (helen-conquest = constitutional canon; Mac = render mirror) with preservation clause
- Operator directives STARSHIP_V2 / STARSHIP_V3 / HELEN2027_HOME / HOME polish pass
- Perplexity Skills doctrine (May 2026) — craft principles only, no schemas imported
- Mac render at `localhost:7000/apps/helen-surface/helen2027.html` rated 9.2/10 by operator (screenshot evidence)
- `HYPERSTITION_FIREWALL_V0` artifact on Mac at `helen_os_v1/artifacts/conquest_landing/`

Nothing in this doctrine was invented by the witness (the Claude Code session). Every principle can be traced to a specific operator turn.

### §9.2 Append-only growth rule

Future polish-pass learnings, new screenshots, new operator directives MUST land as new §X subsections appended below §9. Do not rewrite landed sections.

If a landed section becomes wrong (not just incomplete), do not delete it. Append a new section flagging the contradiction and recording the resolution. The doctrine grows like the ledger.

### §9.3 Reducer authority

This file is `DRAFT_V1`. It becomes canon only when REDUCER admits it via the schema registry and gate pipeline. Until then it is a HER-witnessed proposal — operationally usable as a working contract, constitutionally unbinding.

---

## §10 — Status Summary

```
DOCTRINE:        HELEN_SURFACE_DOCTRINE_V1
STATUS:          DRAFT_V1
AUTHORITY:       NON_SOVEREIGN
SHIP:            NO_SHIP
GROWTH:          APPEND_ONLY
OPEN_QUESTIONS:  4 (Q1, Q2, Q3, Q4)
NEXT_EPOCH:      HELEN_LANGUAGE_LAYERS_V1.md (full mapping table)
NEXT_REDUCER:    operator confirmation or refinement
```
