# OPERATING_CONTRACT — HELEN_OS_ROSE

This contract binds every operator (human or machine) working inside
HELEN_OS_ROSE. It is model-agnostic: no provider or model name may appear in
permanent files, and no function may depend on a specific session existing.

## 1. Sovereignty invariant

ROSE is the sovereign operator. No generated output — recommendation,
artifact, classification, default branch, or agent statement — becomes a
decision merely because it was generated.

Forbidden silent promotions:

```text
generated → approved
classified → routed → admitted
suggested → canonical
written → implemented
implemented → verified
default → semantic verdict
```

Only an explicit Rose record in `decisions/decision_ledger.jsonl` (written
via `scripts/append_decision.py`) can produce `APPROVED_BY_ROSE`.

Decision outcomes: `GO` `HOLD` `REVISE` `REJECT` `RESEARCH`

Lifecycle states: `PROPOSED` `RESEARCHED` `TESTED` `APPROVED_BY_ROSE`
`EXECUTED` `VERIFIED` `REJECTED` `HOLD`

Every state transition must carry evidence. Legal transitions are encoded in
`scripts/validate_workspace.py` and tested in
`tests/test_decision_transitions.py`.

## 2. Status vocabulary

Distinguish explicitly, always:

- `EXISTS` — a file or artifact is on disk. Nothing more.
- `WIRED` — it is connected to something that runs.
- `TESTED` — a repeatable test exercises it and passes.
- `ACTIVE` — it is in use in current operations.
- `APPROVED` — Rose recorded a decision covering it in the ledger.

A thing can be `EXISTS` without being any of the others. `CURRENT_STATE.md`
must use this vocabulary.

## 3. Roles

Three neutral functions. They are job descriptions, not identities.

**STRATEGY** — must diagnose the situation; separate facts, hypotheses,
assumptions, preferences, unknowns; produce at most three serious options;
compare them with explicit criteria; recommend one; define evidence needed
and falsification conditions; mark reversible vs irreversible choices; and
end with `DECISION_REQUIRED_FROM_ROSE`. It must never approve its own
recommendation. Full contract: `prompts/strategy.md`.

**EXECUTION** — must act only on a ledger-recorded `GO`, inside an execution
packet with scope, non-goals, acceptance tests, and stop conditions. Scope
growth returns to sovereign review. Full contract: `prompts/execution.md`.

**SOVEREIGN_REVIEW** — must summarize the decision plainly, expose
assumptions and uncertainty, name consequences and privacy/authority risks,
and request exactly one outcome from Rose. It must never manufacture Rose's
approval. Full contract: `prompts/sovereign_review.md`.

## 4. Evidence model

Evidence classes (strength of support for a specific claim, not universal
truth ranking):

- `E0` — unsupported statement
- `E1` — user-stated fact or preference
- `E2` — internal artifact
- `E3` — reproducible test or measurement
- `E4` — independent external source
- `E5` — signed agreement, transaction, deployment evidence, or formal institutional record

Every material strategic claim should be recorded in
`research/evidence_register.jsonl` with: `claim`, `evidence_class`,
`source`, `date`, `scope`, `limitations`.

## 5. Claim discipline

The claim linter (`scripts/claim_linter.py`) flags authority-bearing terms —
for example `approved`, `validated`, `verified`, `implemented`, `deployed`,
`partner`, `funded`, `customer`, `scientifically proven` — when they appear
without a nearby hedge, evidence marker (E0–E5, `R-###`, `EV-###`, `P-###`,
receipt path), or a machine-checkable decision reference. Unknown constructs
stay `UNCLASSIFIED`; they are never silently treated as admitted.

Practical rule: state facts with an evidence tag, state intentions with
plain future phrasing, and state hypotheses as hypotheses.

## 6. Privacy partitions

Partitions:

```text
PUBLIC
INTERNAL_BUSINESS
CONFIDENTIAL_STRATEGY
PARTNER_RESTRICTED
PERSONAL_PRIVATE
MEDICAL_PRIVATE
LEGAL_PRIVATE
FINANCIAL_PRIVATE
```

Rules:

1. Public content never automatically inherits private context.
2. Medical, legal, financial, residency, family, and relationship
   information stays outside ordinary business strategy files.
3. A synthesis spanning privacy partitions requires explicit Rose
   authorization, recorded in the ledger.
4. Operators must load the minimum necessary context for the task at hand.
5. Sensitive historical details are not copied into general project files.
6. This workspace stores **rules about** sensitive data, not the sensitive
   data itself. `domains/private/` holds pointers and rules only.

Every domain folder and every execution packet declares one privacy class.

## 7. Cost and complexity discipline

- Prefer standard-library tooling; no new dependency without demonstrated necessity.
- No new agents, services, or databases without a `GO` decision.
- One weekly review (`prompts/weekly_review.md`) beats continuous churn.
- The system must survive the disappearance of any single model, provider,
  or session. If a step only works "in that one chat", it is not part of
  the system.

## 8. Relationship to the host repository

HELEN_OS_ROSE lives inside the HELEN OS repository and adopts its receipts
culture, but it does not touch the sovereign kernel: no writes to
`helen_os/governance/`, `oracle_town/kernel/`, `town/ledger_v1.ndjson`,
`GOVERNANCE/CLOSURES/`, or constitutional files. HELEN_OS_ROSE keeps its own
ledger and receipts under this directory.
