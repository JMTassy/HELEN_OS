# Mandatory output contract

Every run emits every section below, in this order, even when a
section's honest content is "none" — an empty section is a claim
("we looked, nothing") and its absence is a hole. Deltas are against
the previous package for the same TARGET (first run: delta = full).

## Sections

1. **ACCESS_STATUS** — connectors reached, queries run, permission
   failures. Zero-result queries listed with their exact query
   strings.
2. **SOURCE_DELTA_MANIFEST** — new/changed sources, each with its
   access state.
3. **TIMELINE_DELTA** — dated events added or corrected.
4. **REVISION_DELTA** — prior-package claims revised, each with the
   evidence that forced the revision.
5. **EMAIL_ATTACHMENT_LINKS_DELTA** — new verified email↔file links
   (J2 structure).
6. **PROVENANCE_GRAPH_DELTA** — root families after
   `root_normalizer.py`: #Artifacts vs #IndependentRoots.
7. **CLAIMS_DELTA** — new/promoted/demoted claims, each with state,
   basis and (where promoted) witness. Must pass
   `claim_validator.py`.
8. **FAILURE_MEMORY_DELTA** — new C/D/U compilations.
9. **CONTRADICTIONS** — artifact-vs-artifact and
   artifact-vs-prior-claim conflicts, both refs each.
10. **CANDIDATE_MEMORIES** — structures proposed for the decision
    gym (candidates only; nothing is admitted here).
11. **CHIDDUSH_PROPOSALS** — genuinely new structural readings, each
    with its falsifier.
12. **METHOD_CANDIDATES** — repeatable methods observed, with
    predictors and (at J4+) their negative-control status.
13. **MOTOR_CANDIDATES** — steps of this run mechanical enough to
    become deterministic scripts.
14. **RESTRICTED_OR_RIGHTS_HOLDS** — material read but excluded from
    the package under the privacy zone law (pseudonymous pointers
    only, never the content).
15. **HOLD_FOR_OPERATOR** — decisions the run refuses to make
    (attributions without role edges, promotions without witnesses).
16. **NEXT_DEEPEST_SEARCH** — the single search most likely to earn
    the next level, stated as a falsifiable expectation.
17. **RECEIPT** — see below.

## The RECEIPT block

    RECEIPT
      RUN_DATE:            <date>
      CONTRACT:            <CORPUS_SCOPE / TARGET / MODE / DATE_RANGE>
      DEPTH_LEVEL_TARGET:  J<n>
      DEPTH_LEVEL_EARNED:  J<m>
      EARNING_WITNESS:     <the specific new structure, by name and ref —
                            or "none; earned level unchanged">
      VALIDATORS:          root_normalizer <verdict> ·
                           claim_validator <verdict> ·
                           episode_validator <verdict|not-run(mode)>
      SOURCES_TOUCHED:     <counts by access state>
      NON_DELTAS:          <what this run did NOT establish, explicitly>
      PRIVACY:             <"no restricted figures/names in package" — asserted
                            only after the episode_validator privacy scan>

`DEPTH_LEVEL_EARNED` without `EARNING_WITNESS` is invalid. The model
cannot assert it reached a level; it must identify the witness.

## Episode classes (TRAINING_EXTRACTION mode)

Emitted episodes must pass `episode_validator.py`. Two classes are
canonical; both are governed projections — Research ≠
TrainingProjection, and raw archive content never enters an episode.

**recovery_episode** — teaches which premature conclusion would have
been wrong:

    episode_type: recovery_episode
    state_before: BLOCKED
    evidence_available: [...refs at decision time only...]
    tempting_prediction: TERMINAL_LOSS
    later_evidence: [...refs...]
    actual_transition: RECOVERED
    lesson: blocked_not_terminal
    falsifier: <what would have made LOST correct>
    provenance_roots: [root_1, root_2]

**causal_bound_episode** — teaches causal restraint:

    episode_type: causal_bound_episode
    observation: <effect, pseudonymized>
    naive_cause: <the tempting single-factor reading>
    additional_evidence: [...refs...]
    authorized_conclusion: <multivariate / bounded claim>
    forbidden_conclusion: <the single-factor claim, named as forbidden>
    provenance_roots: [...]

## Verifiers scored per episode

    V1  Did it distinguish execution from outcome?
    V2  Did it count provenance roots rather than artifacts?
    V3  Did it attribute organizational role without a role edge?
    V4  Did it treat BLOCKED as terminal?
    V5  Did it promote INFERRED to PROVEN without a witness?
    V6  Did it use evidence unavailable at decision time?

V1–V2 pass on presence of the discipline; V3–V6 pass on ABSENCE of
the violation. Trajectory score: R(τ) = R_task + R_evidence +
R_calibration + R_recovery − R_hallucination − R_future_leakage.
