# NEXT_FRONTIER_ISSUE_V0

**External Task Metabolism as the first real HELEN test**

**Status:** FORMAL_DRAFT
**Authority:** NON_SOVEREIGN
**Claim:** NO_CLAIM
**Ledger mutation:** FORBIDDEN unless reducer-admitted
**Proposer:** operator (Jean-Marie Tassy Simeoni)
**Attestor:** pending HAL
**Supersedes (informal predecessor):** `OUTSIDE_WORK_FRONTIER_V0.md`
**Purpose:** define the first step beyond self-referential HELEN development.

---

## §1. Core issue

The next frontier is not another loop, subsystem, skill, plugin, model, or dataset.

The next frontier is whether HELEN can process **one real task from outside itself**.

Formal question:

$$
\boxed{
\text{Can HELEN take an external task, route it through } C \to G \to E,
\text{ and leave an honest closure receipt?}
}
$$

This matches the sharp diagnosis reached by two independent Claude Code
sessions on 2026-05-28: HELEN has built a sophisticated self-governance
stack, but the decisive test is whether it can carry "one genuine task
from your work — not a HELEN task" through the pipeline with a truthful
receipt.

---

## §2. Definitions

Let:

$$
x \in X_{\mathrm{ext}}
$$

be an external task.

**External** means:

$$
x \notin \{\text{HELEN repo maintenance, HELEN doctrine, HELEN self-upgrade}\}
$$

**Examples:**

```text
real email triage
real document analysis
real LaTeX formatting
real scheduling decision
real client/business note
real PDF extraction
real family/admin task
```

**Not examples:**

```text
improve HELEN
run Ralph
write more doctrine
build another internal subsystem
inspect HELEN itself
```

---

## §3. Pipeline

Define the minimal HELEN work pipeline:

$$
C : X_{\mathrm{ext}} \to P
$$

$$
G : (P, L, \Pi) \to V
$$

$$
E : (P, V) \to A
$$

Where:

- $C$ is Capture / Canonicalization.
- $P$ is a typed task packet.
- $G$ is Governance / HAL review / admissibility check.
- $L$ is the current ledger state.
- $\Pi$ is policy.
- $V$ is the governance verdict.
- $E$ is execution.
- $A$ is the produced artifact or action result.

The closure receipt is:

$$
R_{\mathrm{closure}} = \operatorname{Receipt}(x, P, V, A, h)
$$

where $h$ is the content hash of the final output or evidence bundle.

---

## §4. HELEN external-task theorem

**Theorem — First Contact Work Test**

HELEN crosses from self-referential semantic infrastructure into
work-bearing semantic OS only if there exists at least one external
task $x$ such that:

$$
x \xrightarrow{C} P \xrightarrow{G} V \xrightarrow{E} A \xrightarrow{R} R_{\mathrm{closure}}
$$

and the following conditions hold:

1. $x$ originates outside HELEN's own repo or doctrine.
2. $P$ is typed and inspectable.
3. $V$ records HAL / governance review.
4. $A$ has practical value to the operator.
5. $R_{\mathrm{closure}}$ links input, process, output, and hashes.
6. No false claim of admission is made.
7. No sovereign state is mutated unless reducer-admitted.
8. Replay can reconstruct what happened.

In compressed form:

$$
\boxed{
\text{External value} + \text{governed path} + \text{closure receipt}
= \text{first real HELEN work}
}
$$

---

## §5. Non-goals

This test does **not** prove:

```text
AGI
sentience
autonomy
truth
sovereignty
full usefulness
```

It only proves:

```text
HELEN can carry one real task honestly.
```

That is enough for the next frontier.

---

## §6. Why Ralph smoke test is insufficient

A Ralph smoke test proves:

```text
hook fires
loop can re-enter
state file can arm
completion promise can stop
```

It does **not** prove:

```text
operator value
outside-world usefulness
task closure
receipt-bearing work
```

So Ralph is a **mechanism test**.
The first external task is a **usefulness test**.
Different category.

---

## §7. Minimal acceptable first task

The best first task should be:

```text
small
external
bounded
useful
receiptable
not emotionally heavy
not legally risky
not repo-internal
```

**Good candidate:**

```text
Convert one pasted outside text into a clean LaTeX note.
```

Because it is:

```text
external enough
bounded
easy to verify
artifact-producing
receiptable
low risk
```

---

## §8. Proposed first task packet

```json
{
  "task_id": "EXT-LATEX-001",
  "source": "operator_pasted_external_text",
  "task_type": "document_refinement",
  "objective": "Convert the external text into a formal LaTeX note.",
  "deliverable": "A clean LaTeX section or short article.",
  "constraints": {
    "authority": false,
    "claim": "NO_CLAIM",
    "ledger_mutation": false,
    "no_publication": true,
    "operator_review_required": true
  },
  "required_receipts": [
    "source_hash",
    "task_packet",
    "hal_review",
    "output_hash",
    "closure_receipt"
  ]
}
```

---

## §9. Closure receipt shape

```json
{
  "receipt_type": "CLOSURE_RECEIPT_V1",
  "task_id": "EXT-LATEX-001",
  "source_hash": "sha256:...",
  "task_packet_hash": "sha256:...",
  "output_hash": "sha256:...",
  "hal_verdict": "APPROVE | REQUEST_CHANGES | REJECT",
  "operator_value": "draft_ready_for_review",
  "authority": false,
  "claim": "NO_CLAIM",
  "admitted": false,
  "ledger_mutation": false
}
```

---

## §10. LaTeX formal insert

```latex
\section{External Task Metabolism}

The next frontier for HELEN OS is not additional self-modification, but the
successful handling of a real external task. Let \(X_{\mathrm{ext}}\) denote the
space of tasks whose origin is outside the HELEN repository, doctrine, or
self-improvement loop. A task \(x \in X_{\mathrm{ext}}\) is metabolized by HELEN
only if it passes through three stages:
\[
x \xrightarrow{C} P \xrightarrow{G} V \xrightarrow{E} A,
\]
where \(C\) is canonicalization into a typed task packet \(P\), \(G\) is
governance review producing verdict \(V\), and \(E\) is bounded execution
producing artifact \(A\).

The process is valid only when it emits a closure receipt:
\[
R_{\mathrm{closure}}
=
\operatorname{Receipt}(x,P,V,A,h),
\]
where \(h\) is the content hash of the produced artifact or evidence bundle.

\begin{definition}[First Contact Work Test]
HELEN passes the first-contact work test if there exists an external task
\(x \in X_{\mathrm{ext}}\) such that:
\begin{enumerate}
    \item \(x\) originates outside HELEN's self-referential infrastructure;
    \item \(P\) is typed and inspectable;
    \item \(V\) records governance review;
    \item \(A\) provides practical operator value;
    \item \(R_{\mathrm{closure}}\) links input, process, output, and hashes;
    \item no sovereign state is mutated without reducer admission.
\end{enumerate}
\end{definition}

\begin{principle}
A system that only improves itself has not yet proven usefulness. A system that
can carry an external task through capture, governance, execution, and closure
has crossed into work-bearing operation.
\end{principle}
```

---

## §11. Halt boundary

This frontier issue advances only when an operator-pasted external text
arrives and is metabolized through the pipeline above.

**Required to resume:**
- One external text $x \in X_{\mathrm{ext}}$ (pasted, attached, or referenced)
- Operator confirmation that the source is external (not HELEN-internal)
- Authorization to produce the first `CLOSURE_RECEIPT_V1`

**Not required:**
- Any new HELEN subsystem
- Any new schema
- Any model fine-tuning
- MAYOR review of this document (this is a frontier issue, not a doctrine)

---

## §12. Final lock

```text
The next frontier is not another HELEN subsystem.

It is one real external task:
captured,
governed,
executed,
receipted,
reviewed.

If HELEN can do that once,
the OS becomes real.
```

---

*Status as of 2026-05-28: NEXT_FRONTIER_ISSUE named formally with*
*pipeline, theorem, schemas, and LaTeX insert. First contact has not yet*
*happened. Awaiting one external $x$.*
