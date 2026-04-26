# ARTIFACT_LIFECYCLE_V1

---

## A. Scope

This document defines the universal lifecycle for all HELEN OS artifacts. Every file, receipt, sample, doctrine, scaffold, or run-log in the SOT (or any HELEN clone) carries a lifecycle state. The lifecycle determines whether the artifact may enter boot context, be executed, be cited as authority, or govern.

The lifecycle is **type-agnostic**: it applies to skills (AURA, Director, Ralph-W, Education, future DeliveryEngine, etc.), governance, knowledge, receipts, and runtime scaffolds equally.

This document is itself a governance artifact. It is staged at lifecycle state `DRAFT` pending `DOCTRINE_ADMISSION_PROTOCOL_V1` activation and a MAYOR ruling.

**Proposed law (DRAFT): every artifact carries a lifecycle state. No state = no admission.**

---

## B. Policy Identity

```
proposed_policy_id: ARTIFACT_LIFECYCLE_V1
version:        1.0
scope:          ALL_ARTIFACTS
lifecycle:      DRAFT
status:         DRAFT — pending DOCTRINE_ADMISSION_PROTOCOL_V1 activation + MAYOR ruling
depends_on:     CANONICALIZATION_V1, EDGE_LEGALITY_MATRIX_V1, CLAIM_GRAPH_V1,
                TEMPLE_SANDBOX_POLICY_V1, DOCTRINE_ADMISSION_PROTOCOL_V1 (DRAFT)
```

---

## C. The six lifecycle states

States form a partial order. Promotion is uphill only; demotion is one step down or terminal (`REJECTED` / `SUPERSEDED`).

```
RAW → DRAFT → CANDIDATE → RECEIPTED → ACTIVE → CANONICAL
                                  ↘
                                   SUPERSEDED (terminal)
                          ↘
                           REJECTED (terminal)
```

For each state below: **meaning · allowed usage · boot eligibility · execution eligibility · authority level · promotion requirement · demotion / rejection rule.**

---

### C.1 RAW

- **Meaning.** Unprocessed capture of an event, conversation, or external output. No editorial review, no claim of correctness, no claim of internal coherence.
- **Allowed usage.** Archival evidence; reference for later distillation. May be cited only as "this was captured at time T" — never as fact, never as doctrine, never as policy.
- **Boot eligibility.** **NO.** Must not be loaded into Claude Code, kernel, skill, or sub-agent boot context. RAW in a boot manifest is a hard fail.
- **Execution eligibility.** **NO.** RAW artifacts are never executed.
- **Authority level.** **ZERO.** Sidecar at most. Carries no constitutional weight.
- **Promotion requirement.** A `DRAFT` is created by an authoring skill that distills the RAW sample. The RAW artifact itself is never promoted; a derived `DRAFT` is authored separately and the RAW remains as evidence.
- **Demotion / rejection rule.** Cannot be demoted (already at floor). Operator may delete after the declared retention window — deletion does not invalidate prior derivative `DRAFT`s, which carry their own provenance.

### C.2 DRAFT

- **Meaning.** Authored proposal with structure and intent but no acceptance. May be partially formed, may be revised in place.
- **Allowed usage.** Review subject; round-trip with reviewers; reference only within the authoring session and in explicit "draft of …" citations.
- **Boot eligibility.** **NO.** Drafts may not enter any boot context. Loading a `DRAFT` as if it were `ACTIVE` is the canonical "draft mistaken for canon" error.
- **Execution eligibility.** **NO.** Drafts are never executed, even in dry-run.
- **Authority level.** **ZERO.** Cannot be cited as authority.
- **Promotion requirement.** Review pass + operator routing. For doctrine-class drafts, MAYOR review per `DOCTRINE_ADMISSION_PROTOCOL_V1`. For runtime-class drafts, K-tau / K8 lint pass + sandboxed dry-run.
- **Demotion / rejection rule.** → `REJECTED` (terminal, with a `REJECTION_RECEIPT_V1` recording reason) or → `RAW` if only a fragment is salvageable (the RAW capture stands; the DRAFT is discarded).

### C.3 CANDIDATE

- **Meaning.** Review-passed artifact awaiting its required tests, gate runs, or proposer-validator separation.
- **Allowed usage.** May be referenced in tests; may be loaded into a sandboxed runner (no spine writes); cannot govern or bind.
- **Boot eligibility.** **NO.** Tests have not yet sealed the artifact's behavior.
- **Execution eligibility.** **SANDBOXED ONLY.** Dry-run, quarantined runner, or proposer-validator review harness. Never against production targets. Never against the sovereign ledger.
- **Authority level.** **LOW.** Provisional. No claim binding. No skill-lock.
- **Promotion requirement.** Required tests `PASS` + receipt emission via `tools/helen_say.py` (canonical writer). The receipt binds the candidate's content hash to its passing test set.
- **Demotion / rejection rule.** → `DRAFT` (revisions needed; tests failed but author wishes to retry) or → `REJECTED` (terminal).

### C.4 RECEIPTED

- **Meaning.** Artifact bound to a receipt in `town/ledger_v1.ndjson` via the canonical `helen_say.py → ndjson_writer.py` admission path. Has a hash-chained provenance trail; payload SHA is the artifact's identity.
- **Allowed usage.** Cited as having existed at a point in time. Referenced by other artifacts via receipt hash. May be inspected, replayed, or audited.
- **Boot eligibility.** **CONDITIONAL.** YES if bound by an *obligation* receipt (a receipt that asserts the artifact is required at boot). NO if bound only by a *recording* receipt (a receipt that merely notes existence).
- **Execution eligibility.** **YES** — provided proposer ≠ validator on the binding receipt (K2 / Rule 3). A self-validated receipted artifact may be executed only inside a fresh sub-agent context.
- **Authority level.** **PROVISIONAL.** Receipt = "this happened" or "this passed those tests." Receipt ≠ doctrine. Receipt ≠ canon.
- **Promotion requirement.** Operator activation moves the artifact to `ACTIVE`. Reducer / MAYOR admission moves it to `CANONICAL`.
- **Demotion / rejection rule.** Receipts are append-only; entries cannot be erased. A new receipt may **supersede** (mark the old hash as no longer current) or **revoke** (mark the old hash as withdrawn). The historical receipt remains in the chain.

### C.5 ACTIVE

- **Meaning.** Currently in production use. Loaded at boot into the relevant context, or callable as a runtime path. Subject to per-invocation K-gate enforcement.
- **Allowed usage.** Full operational use within the artifact's declared scope. Cited as the source of behavior.
- **Boot eligibility.** **YES.**
- **Execution eligibility.** **YES.**
- **Authority level.** **OPERATIONAL.** Binds runtime behavior within scope. Subject to existing K-gates (K8, K-tau, K-rho, K-wul, LEGORACLE) on every commit and every invocation that touches their domain.
- **Promotion requirement.** From `RECEIPTED`: operator activation + CI / lint pass. From `CANDIDATE`: must pass through `RECEIPTED` first (no skip).
- **Demotion / rejection rule.** → `CANDIDATE` (operator deactivation, test regression, K-gate failure, or scope rescoping). → `SUPERSEDED` when replaced by a successor (terminal for this version).

### C.6 CANONICAL

- **Meaning.** Doctrine-class artifact admitted by reducer / MAYOR. Authoritative at the constitutional layer within its declared scope.
- **Allowed usage.** Cited as law within scope. Other artifacts must align or explicitly request review.
- **Boot eligibility.** **YES.** Loaded into every relevant boot context.
- **Execution eligibility.** **GOVERNS execution rather than executing itself.** Canonical artifacts are read by gates, validators, and reducers; they are not invoked as runtime code.
- **Authority level.** **SOVEREIGN within declared scope.** Binds future artifacts.
- **Promotion requirement.** `DOCTRINE_ADMISSION_PROTOCOL_V1` (DRAFT today; not yet enforcing) + MAYOR ruling + receipt binding the canonical content SHA. Proposer ≠ validator on the admission receipt.
- **Demotion / rejection rule.** → `SUPERSEDED` (new version + binding receipt + migration plan describing how dependent artifacts move). Direct deletion of CANONICAL artifacts is forbidden; supersession is the only exit.

---

## D. Artifact types and default lifecycles

Each artifact type has a default initial state, a typical maximum state achievable for its class, and a promotion route. The right column names the canonical example currently in the SOT.

| Type                  | Default state          | Max state (typical) | Promotion route                                      | Canonical example in SOT                                              |
| --------------------- | ---------------------- | ------------------- | ---------------------------------------------------- | --------------------------------------------------------------------- |
| `RAW_SAMPLE`          | `RAW`                  | `RAW`               | never; derivatives are authored as `DRAFT`           | `temple/subsandbox/aura/raw_samples/2026-04-26-aura-terminal-sample-01.md` |
| `AURA_FRAGMENT`       | `DRAFT`                | `CANDIDATE`         | distillation skill review + AURA scaffolding         | (not yet authored)                                                    |
| `OPERATOR_DOC`        | `DRAFT` → `ACTIVE`     | `ACTIVE`            | operator approval + commit                           | `CLAUDE.md` (root, skill-local)                                       |
| `SKILL_DRAFT`         | `DRAFT`                | `DRAFT`             | never directly; replaced by SKILL_CANON              | `oracle_town/skills/video/helen-director/SKILL_V2_DRAFT.md`           |
| `SKILL_CANON`         | `ACTIVE`               | `CANONICAL`         | `DOCTRINE_ADMISSION_PROTOCOL_V1` + MAYOR ruling      | `oracle_town/skills/video/helen-director/SKILL.md`                    |
| `EXECUTABLE_SCAFFOLD` | `CANDIDATE`            | `ACTIVE`            | endpoint verification + receipt + activation         | `oracle_town/skills/video/helen-director/run_30s_v1.py`               |
| `RECEIPT`             | `RECEIPTED`            | `RECEIPTED`         | terminal; cannot transit                             | entries in `town/ledger_v1.ndjson`                                    |
| `RUN_LOG`             | `RAW`                  | `RAW`               | never; non-sovereign sidecar                         | (transcripts under `artifacts/`)                                      |
| `KNOWLEDGE_ENTRY`     | `DRAFT`                | `ACTIVE`            | operator save + curation                             | `~/.claude/projects/.../memory/*.md`                                  |
| `TOPIC_CARD`          | `DRAFT`                | `CANDIDATE`         | review pass + scope declaration                      | (per-topic summaries)                                                 |
| `AUTORESEARCH_RESULT` | `CANDIDATE`            | `RECEIPTED`         | tranche sub-receipt binding                          | `GOVERNANCE/TRANCHE_RECEIPTS/*`                                       |
| `DIRECTOR_PIPELINE`   | `EXECUTABLE_SCAFFOLD` class | `ACTIVE`       | dry-run pass + endpoint verification + delivery receipt | `oracle_town/skills/video/helen-director/run_30s_v1.py` (current)     |

`DIRECTOR_PIPELINE` is a sub-class of `EXECUTABLE_SCAFFOLD` with the additional requirement that delivery to Telegram (or equivalent) emit a `DELIVERY_RECEIPT_V1` before the artifact lifts past `RECEIPTED`.

---

## E. Hard rules

These rules are absolute. Each is checkable; each names the failure code a validator should emit.

| #   | Rule                                                                                                                                  | Failure code                            |
| --- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| E.1 | RAW chat is not memory. A `RAW` artifact may not be promoted to `KNOWLEDGE_ENTRY`. Distillation through `DRAFT` is mandatory.         | `RAW_PROMOTED_DIRECTLY`                 |
| E.2 | DRAFT doctrine is not canon. A `SKILL_DRAFT` (or any `DRAFT` artifact) may not be cited as authority.                                 | `DRAFT_CITED_AS_AUTHORITY`              |
| E.3 | Executable scaffold is not active skill. An `EXECUTABLE_SCAFFOLD` may not be invoked outside dry-run / sandbox until `ACTIVE`.        | `SCAFFOLD_INVOKED_LIVE`                 |
| E.4 | Receipt is not authority unless bound to obligation. A *recording* receipt does not authorize boot or execution.                      | `RECORDING_RECEIPT_TREATED_AS_OBLIGATION` |
| E.5 | No artifact may enter boot context without a lifecycle state. Untagged artifacts in any boot manifest are a hard fail.                | `MISSING_LIFECYCLE_STATE`               |
| E.6 | No artifact may execute unless in `CANDIDATE` or above with required tests `PASS`. `RAW` and `DRAFT` artifacts never execute.         | `EXECUTE_BELOW_CANDIDATE`               |
| E.7 | No artifact may govern unless reducer-admitted (`CANONICAL`). `ACTIVE` artifacts bind runtime behavior; only `CANONICAL` binds law.   | `GOVERN_BELOW_CANONICAL`                |

Corollaries (derived, not separately enumerated):

- C.1: A receipt that names an artifact does not change that artifact's lifecycle state. State is a property of the artifact, not of any receipt that references it.
- C.2: Canonical-path firewall (per `~/.claude/CLAUDE.md`) operates orthogonally. An artifact may be `CANONICAL` (admitted) and still live outside the sovereign-firewall; the firewall constrains *who may write*, this policy constrains *what may be loaded, executed, or cited*.

---

## F. Lifecycle metadata requirement

Every artifact subject to this policy must declare its lifecycle state. The declaration mechanism depends on file type:

- **Markdown governance / doctrine / skill files**: include a `lifecycle:` field in the front-matter or in the policy-identity block (see Section B above for the canonical form).
- **Python / JS / shell scripts**: include a top-of-file comment line `# lifecycle: <STATE>` within the first 20 lines.
- **JSON artifacts**: include a top-level `"lifecycle"` key.
- **NDJSON receipts**: lifecycle is implicit — every receipt is `RECEIPTED` by definition.
- **Untracked / RAW transcripts**: lifecycle is implicit by directory placement (e.g., `temple/subsandbox/.../raw_samples/` → `RAW`).

Artifacts predating this policy carry an implicit lifecycle until lint coverage retroactively classifies them. The lint script (Section H) is the migration vehicle.

---

## G. Integration with existing policies

| Policy                          | Relationship                                                                                                                                                                                                |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TEMPLE_SANDBOX_POLICY_V1`      | All Temple Sandbox artifacts default to `RAW`. Tier III / `wild_text` / `QUARANTINED` is a separate orthogonal classification (admissibility); lifecycle (RAW) is the time / promotion axis.                |
| `DOCTRINE_ADMISSION_PROTOCOL_V1`| Governs `DRAFT` → `CANONICAL` transitions for doctrine-class artifacts. Currently DRAFT itself; until activation, `CANONICAL` admission is **paused** for new artifacts.                                    |
| `CANONICALIZATION_V1`           | Defines the SHA used to bind a `RECEIPTED` artifact's content hash to its receipt.                                                                                                                          |
| `CLAIM_GRAPH_V1`                | Each artifact node should carry a `lifecycle_state` field. Edge legality (Section H of `EDGE_LEGALITY_MATRIX_V1`) may use lifecycle as an additional constraint (e.g., `wild_text` + `RAW` may not `SUPPORTS` a `CANONICAL` claim). |
| K-tau / K8 / K-rho / K-wul      | These gates may treat lifecycle as a precondition: e.g., K-tau may refuse to lint an artifact whose lifecycle state is below its execution-eligibility threshold for the lint's scope.                       |
| Sovereign-path firewall (per global `CLAUDE.md`) | Orthogonal. Firewall says *who may write where*; lifecycle says *what may be loaded, executed, or cited*. Both apply.                                                                                       |

---

## H. Validator obligations

A validator implementing this policy must check, for each artifact in scope:

1. The artifact carries a declared lifecycle state via the mechanism in Section F.
2. The state is one of the six valid states (`RAW`, `DRAFT`, `CANDIDATE`, `RECEIPTED`, `ACTIVE`, `CANONICAL`) or one of the two terminals (`REJECTED`, `SUPERSEDED`).
3. The artifact's actual content matches its type's default state (e.g., a file in `temple/subsandbox/.../raw_samples/` may not declare `lifecycle: ACTIVE`).
4. Boot manifests reference only `ACTIVE` or `CANONICAL` artifacts.
5. Execution requests target only artifacts in `CANDIDATE` (sandboxed), `RECEIPTED`, or `ACTIVE` state.
6. Citation as authority targets only `CANONICAL` artifacts (or, with explicit "draft of …" framing, `DRAFT` / `CANDIDATE` artifacts within the authoring session).
7. Any `→ CANONICAL` transition has a corresponding `DOCTRINE_ADMISSION_PROTOCOL_V1` receipt with proposer ≠ validator.

A future lint script (placeholder name: `scripts/helen_artifact_lifecycle_lint.py`) walks the SOT, validates these conditions, and emits one of the failure codes from Section E.

---

## I. Failure action

On any validation failure:

- The artifact is **refused** at the gate that detected the failure (boot, execution, citation, or admission).
- Failure is logged with the applicable error code from Section E.
- For `EXECUTE_BELOW_CANDIDATE` and `SCAFFOLD_INVOKED_LIVE`: the runner must terminate before any IO touches a non-sandbox target.
- For `GOVERN_BELOW_CANONICAL` and `DRAFT_CITED_AS_AUTHORITY`: the validator must reject the dependent artifact, not the offending citation source.
- For `MISSING_LIFECYCLE_STATE`: the artifact is treated as `RAW` until classified, with all the boot / execution / citation restrictions of `RAW`.

---

## J. Non-claims

This policy does not define:

- canonical hashing (governed by `CANONICALIZATION_V1`),
- edge legality (governed by `EDGE_LEGALITY_MATRIX_V1`),
- the schema shape of any specific receipt type,
- the *truth or falsity* of any artifact's content,
- the sovereign-path firewall (governed by global `~/.claude/CLAUDE.md`),
- the doctrine-admission gate's internal logic (governed by `DOCTRINE_ADMISSION_PROTOCOL_V1`),
- skill-promotion-reducer logic (governed by the reducer's own specification).

This policy defines only the **lifecycle axis**: what state an artifact is in, and what that state permits.

---

## K. Migration

Artifacts predating this policy are not retroactively rejected. The lint script (Section H) classifies them on first scan. Operator may bulk-tag by directory pattern. `town/ledger_v1.ndjson` entries are implicitly `RECEIPTED` and require no migration.

The first artifact authored under this proposed policy is `temple/subsandbox/aura/raw_samples/2026-04-26-aura-terminal-sample-01.md` (state: `RAW` by directory convention; commit `077c87f`).

---

**Document Version**: ARTIFACT_LIFECYCLE_V1
**Status**: DRAFT — pending DOCTRINE_ADMISSION_PROTOCOL_V1 activation + MAYOR ruling
**Lifecycle (this file)**: DRAFT
**Depends on**: CANONICALIZATION_V1, EDGE_LEGALITY_MATRIX_V1, CLAIM_GRAPH_V1, TEMPLE_SANDBOX_POLICY_V1, DOCTRINE_ADMISSION_PROTOCOL_V1 (DRAFT)
