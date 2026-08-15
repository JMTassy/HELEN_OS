# Epistemic protocol

The controlled vocabulary for every source and every claim a run
produces. These states are the law of the package: a source or claim
carrying a state outside these sets fails `claim_validator.py`.

## Access states (one per source)

What YOU did with the artifact — never what you believe about it.

| state | meaning |
|---|---|
| `METADATA_SEEN` | listed in a search result / directory; title, sender, date only |
| `CONTENT_OPENED` | body actually retrieved and read in this run |
| `CONTENT_EXTRACTED` | specific facts pulled out with location references |
| `CONTENT_CROSS_CORROBORATED` | the same fact confirmed from a second INDEPENDENT root |
| `NO_ACCESS` | retrieval attempted and failed (permission, deletion, format); the failure is itself a receipt |

`METADATA_SEEN` licenses claims about existence and timing only.
Title ≠ content: nothing about what a document says may be claimed
from its name. A search that returns zero results is an observation
(`NO_ACCESS` never applies to it — record the query and the zero).

## Claim states (one per claim)

| state | earned by |
|---|---|
| `OBSERVED` | direct reading of a primary artifact (`CONTENT_OPENED`+) |
| `REPORTED` | someone in the corpus asserts it; you observed only the assertion |
| `INFERRED` | licensed deduction from OBSERVED/PROVEN premises, derivation shown |
| `HYPOTHESIZED` | candidate explanation; carries its falsifier or it is not a hypothesis |
| `PROVEN` | OBSERVED on ≥ 2 independent roots, or re-derivable mechanically |
| `CONTRADICTED` | a primary artifact conflicts with it; both refs recorded |
| `NO_RECEIPT` | asked, searched, not found — a first-class lawful outcome, not an embarrassment |

Legal promotions move only through evidence: REPORTED→OBSERVED needs
the primary artifact; INFERRED/HYPOTHESIZED→PROVEN needs the
corroborating root. Repetition, confidence, or narrative coherence
promote nothing. DIAGNOSIS is a kind of INFERRED that never becomes
OBSERVED by any path.

## The invariant non-implications

Each line is a distinct error class observed in real archives. Read
`⊬` as "never implies without a separate witness":

    title                ⊬ content
    proposal             ⊬ execution
    requested            ⊬ approved
    approved             ⊬ contracted
    contracted           ⊬ invoiced
    invoiced             ⊬ paid
    complaint            ⊬ responsibility
    archive presence     ⊬ authorship
    copy                 ⊬ independent root
    forward              ⊬ independent witness
    strategic decision   ⊬ execution
    execution            ⊬ outcome
    blocked              ⊬ terminal loss

## Role edges (mandatory before institutional attribution)

An organization's archive containing x proves only custody. Assign
one edge per (organization, artifact) pair before attributing
anything: `AUTHOR · EXECUTOR · CLIENT · SUPPLIER · RECIPIENT ·
REFERENCE_ONLY · UNKNOWN`. The canonical trap (abstract pattern, no
private data): document found in org archive → attribution tempting →
role-edge search → no execution evidence → **HOLD**. UNKNOWN is a
lawful edge; a guessed edge is not.

## Commercial number typing

Every amount travels with a state from the seven-chain — `ESTIMATE →
REQUESTED → LIKELY → APPROVED → CONTRACTED → INVOICED → PAID` — plus
a date and a provenance ref. Transitions advance one arrow at a time,
each with a witness; regressions (bad news) need no permission.
"Budget" with no state is an untyped amount and is refused.

## Temporal states are not absorbing

Track opportunities/projects on: `DISCOVERED · QUALIFYING · PROBE ·
GO · BLOCKED · HOLD · RECOVERED · EXECUTING · COMPLETED · LOST ·
UNKNOWN`. `BLOCKED → RECOVERED` is explicitly permitted and is the
single most valuable transition a run can witness. Only a closure
receipt makes `LOST` terminal; an announced cancellation is an
intent, never an outcome. Without an outcome receipt a block stays
`OPEN_BLOCKED` — reading it as loss is the false-terminal-causality
error this protocol exists to prevent.

## Failure compilation (SOPHIA C/D/U)

Every failure compiles to exactly three registers, kept separate:

- **C** — licensed Consequence: what OBSERVED evidence entails.
- **D** — abductive Diagnosis: best current explanation, tagged as
  such forever. A diagnosis never becomes a fact by repetition.
- **U** — Unresolved proof obligation: what measurement or search
  would settle it.
