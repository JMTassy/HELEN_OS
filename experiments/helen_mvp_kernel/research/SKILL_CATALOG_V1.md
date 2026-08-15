# HELEN OS — Skill Catalog V1

authority=false · claim=NO_CLAIM · non-sovereign
Frozen 2026-08-15 from the operator's ruling ("SKILL the method").
Status column is law: only one skill is built; everything else is
specified, initiated, or candidate. Building a candidate requires an
operator GO.

## The governing law

    Few Skills outside. Rich HELEN machinery inside.

The same law as the enterprise architecture ("Applications outside.
HELEN inside") applied to the skill surface: internal modules are not
user-facing skills, and skill explosion is resisted for exactly the
reason agent explosion is. The membrane every skill respects:

    Skill = Method        Corpus = PrivateRuntimeData

No private material (emails, budgets, client names, consumer
datasets, invoices, HR comments, raw corpora) is ever packaged inside
a skill. Skills reach authorized material through connectors at
runtime.

## The seven primary skills

| # | skill | verb | status |
|---|---|---|---|
| 1 | `helen-institutional-archaeologist` | discover/reconstruct what happened (J1→J7) | **BUILT** — `.claude/skills/helen-institutional-archaeologist/`, this repo, this date |
| 2 | `helen-receipt-verifier` | determine what is actually proven (claim → required proof → earned state) | candidate |
| 3 | `helen-counterexample-hunter` | try to break the current theory (disconfirming evidence, edge cases, falsifiers) | candidate |
| 4 | `helen-account-archaeologist` | reconstruct an account longitudinally (people, opportunities, decisions, wins/losses, unresolved claims) | candidate |
| 5 | `helen-decision-gym` | convert earned evidence into governed training/evaluation episodes | initiated |
| 6 | `helen-institutional-simulator` | test decision-making on historical branches without future leakage | candidate / advanced |
| 7 | `helen-review-packet` | convert cognition/evidence into a bounded human/policy decision packet | candidate |

The two highest-value skills and their membrane:

    helen-institutional-archaeologist → helen-decision-gym
    ObservedHistory → GovernedTrainingProjection   (never RawArchive → Train)

The first determines what we legitimately know. The second determines
what we can legitimately learn from it.

## The pipeline the seven serve

    Discover → Verify → Reconstruct → Challenge → Admit → Learn → Test
       (1)      (2)        (4)          (3)      atomic    (5)    (6)

with (7) as the exit into human/policy decision at any stage.

## Atomic governance skills (composed INSIDE the seven, not exposed)

`draft_claim` · `compare_sources` · `build_receipt` ·
`summarize_ledger_window` · `prepare_review_packet` ·
`propose_experiment` · `temple_generate_artifact`
(TempleArtifact ⊬ Admission) · `oracle_evaluate_claim` ·
`autoresearch_generate_candidates` (authority=false, canon=false,
ledger_effect=none) · `validate_packet`.

## Internal motors (never standalone skills at this stage)

- **ACCOUNT ARCHAEOLOGY ENGINE** — root normalizer, role-edge
  auditor, temporal graph builder, edge resolver, attribution
  adversary, loss/re-entry mapper, recovery transition resolver,
  failure miner. Powers skill 1 (and eventually 4).
- **CAMPAIGN RECONSTRUCTION ENGINE** — Brief → Recommendation →
  Decision → Production → Deployment → Outcome, with the Pivot
  Realization Auditor (StrategicPivot ≠ OperationalRealization ≠
  Outcome).
- **DECISION BOUNDARY ENGINE** — when GO / PROBE / HOLD / REJECT /
  ESCALATE / STOP is right; kernel counterpart already committed as
  `constitution/decision_boundaries.py`.
- **GOLDEN DATA DECISION LAB** — root normalizer → role-edge auditor
  → temporal graph → decision branch miner → failure/counterexample
  miner → SOPHIA C/D/U → privacy projector → training shard →
  leakage auditor. Bigger than a skill; eventually a HELEN subsystem.
- **Existing named lanes** `SCANNER_CROSSING_V1` and
  `WORKSPACE_TRACE_V1` stay lanes until they earn skill status.

## What skill #1 shipped with (the packaging precedent)

- `SKILL.md` — contract (CORPUS_SCOPE/TARGET/QUESTION/DATE_RANGE/
  DEPTH_TARGET/MODE), 7 ground rules, 6-step workflow.
- `references/` — `epistemic-protocol.md` (access/claim states, the
  13 non-implications, role edges, commercial typing, non-absorbing
  temporal states, C/D/U), `depth-model.md` (J1→J7 + the earning
  rule), `output-contract.md` (17 mandatory sections, RECEIPT with
  DEPTH_LEVEL_TARGET vs DEPTH_LEVEL_EARNED, episode schemas,
  verifiers V1–V6).
- `scripts/` — `root_normalizer.py` (14 artifacts → 2 roots;
  Author(x) ≠ Root(x)), `claim_validator.py` (forbidden promotions;
  E_BLOCK_TREATED_AS_ABSORBING; figures never travel),
  `episode_validator.py` (episode schemas; V6 future-leakage fatal;
  restricted-material scan). All stdlib-only, deterministic, each
  with a `--selftest` mode (10+12+13 checks).

Future skills follow this shape: pushy description for triggering,
compact ground rules in SKILL.md, controlled vocabulary in
references, and everything not trusted to free-form reasoning as a
deterministic script with a selftest.

## Non-deltas

This catalog mints nothing: no skill beyond #1 exists by virtue of
being listed here; no atomic skill or motor gains an external
surface; no J-level, claim state, or authority is created by this
document. It is a REGISTERED agenda, not an admission.
