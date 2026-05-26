# BOOTSTRAP_ELECTION_OPTIONS_V0.1 — Autoresearch Findings Amendment

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_APPLICABLE (findings amendment, not a mechanism)
**status:** Amendment — augments `BOOTSTRAP_ELECTION_OPTIONS_V0` with empirical findings from a 100-epoch autoresearch run
**origin_signal:** `BOOTSTRAP_ELECTION_OPTIONS_V0 §8 recommendation — operator chose to gather model-pressure evidence before deciding bootstrap path`
**amends:** `docs/proposals/BOOTSTRAP_ELECTION_OPTIONS_V0.md` (local commit `08f467b`)
**parent_synthesis:** `docs/proposals/BOOTSTRAP_ELECTION_OPTIONS_V0.md`, `docs/proposals/MAYOR_ADMISSION_PROTOCOL_V0.md`, `docs/proposals/RECEIPT_SAFE_MUTATION_PROTOCOL_V0.md`
**proposer:** claude-opus-4-7 (acting as GOBLIN doctrine drafter)
**attestor:** pending HER

---

## §0. Axiom

Carried forward:

> **NO VALID RECEIPT = NO TRUSTED STATE MUTATION.**
> **NO MAYOR SEAL = NO ADMITTED CANON.**
> **NO LEGITIMATE FIRST MAYOR = NO LEGITIMATE ADMISSION CHAIN.**

Extended by this amendment:

> **MODEL-MAJORITY ≠ OPERATOR JUDGMENT.**

A model converging on a structural framing is evidence of comprehensibility. A model failing to converge on a risk framing is evidence of the loop's limit, not of the risk's absence. Neither convergence nor non-convergence at autoresearch scale substitutes for operator decision on bootstrap authority.

---

## §1. Purpose

`BOOTSTRAP_ELECTION_OPTIONS_V0` compared the three bootstrap paths analytically. This amendment adds empirical signal from a 100-epoch autoresearch run in which `qwen3.5:9b` produced 100 RAW receipts in response to the parent doctrine.

### §1.1 Core conclusion

> **Autoresearch propagated bootstrap structure, but failed to propagate bootstrap risk. Therefore bootstrap authority cannot be selected by model-majority or autoresearch convergence.**

This is not a rejection of autoresearch as a method. It is a bound on what this method can decide.

---

## §2. Method (replayability)

The run is reproducible from the receipts on disk; this section pins the parameters so future analysis can verify findings against the same input.

| Parameter | Value |
|---|---|
| Tool | `tools/gemma_autonomous_loop.py` |
| Model | `qwen3.5:9b` (Ollama, local) |
| Iterations | 50 × 2 batches = 100 total |
| `--prompt-file` | `docs/proposals/BOOTSTRAP_ELECTION_OPTIONS_V0.md` |
| `--prompt-file-chars` | `1600` (truncated to fit `num_ctx=2048` constitutional guard) |
| Topic string | `"bootstrap election options for HELEN OS MAYOR admission"` |
| Halt discipline | `HALT logged, not human-reviewed per iteration` (49 newlines piped to stdin to advance past each pause) |
| Output destination | `GOVERNANCE/GEMMA_PROPOSALS/gemma_proposal_2026-05-26T00-*Z_iter*.json` |
| Lifecycle on every receipt | `RAW`, `auto_promotion_ceiling = RAW`, `authority = false` |
| Ledger writes | none |
| Admission actions | none |

Run 1 batch produced 50 receipts (8% envelope-incomplete). Run 2 batch produced 50 receipts (24% envelope-incomplete). The Run 2 envelope-failure rate exceeded the 20% threshold the operator set for proceeding to a longer 5-hour loop; **no 5-hour loop was launched**.

### §2.1 Scan methodology

Signal was extracted by scanning **only model-output fields** (`proposal_text`, `uncertainty_text`, `required_receipts`, `hal_questions`, `raw_response_text`) of each receipt. The `prompt_text` field was excluded because it contains the injected doctrine excerpt verbatim and would inflate any pattern match by construction. Match is case-insensitive substring containment; a receipt scores 1 per pattern regardless of how many times the pattern occurs. Per-pattern counts are out of 100 autoresearch receipts.

---

## §3. Finding I — Structural signal propagated

The model engaged strongly with the bootstrap problem as a structural question. Top patterns by per-receipt mention rate:

| Pattern | Receipts mentioning | Rate |
|---|---|---|
| `seal` | 96 / 100 | **96%** |
| `first mayor` | 54 / 100 | **54%** |
| `genesis` | 47 / 100 | **47%** |
| `MAYOR seal` | 30 / 100 | **30%** |
| `self-admission` | 22 / 100 | **22%** |

Reading: the model treats admission as a real problem with a named structural surface. The phrasing `first mayor` and `genesis` indicates the model independently reaches the bootstrap framing without those exact phrases appearing in the injected excerpt at the same density. The §0 axiom from the parent doctrine — that the first seal is the most consequential one — propagates as an engaged concept, not just an echoed phrase.

### §3.1 Implication

The doctrine's §0–§1 framing is *autoresearch-validated*: a model reading the doctrine in isolation reproduces the bootstrap question with high consistency. This is necessary but not sufficient for operator confidence.

---

## §4. Finding II — Risk signal did not propagate

The five most operationally-important threat concepts in `BOOTSTRAP_ELECTION_OPTIONS_V0 §2.3 / §3.3 / §4.3` received **zero** mentions across all 100 receipts:

| Pattern | Receipts mentioning | Rate |
|---|---|---|
| `operator capture` | 0 / 100 | **0%** |
| `quorum capture` | 0 / 100 | **0%** |
| `stale mandate` | 0 / 100 | **0%** |
| `identity binding` | 0 / 100 | **0%** |
| `key custody` | 0 / 100 | **0%** |
| `minimum bootstrap receipts` | 0 / 100 | **0%** |

Adjacent broader patterns were also weak or zero: `operator capture` 0%, `capture` (alone) 0%, `collusion` 4%, `single-operator` 3%, `revocation` 1%, `N-of-M` 0%, `founding authority` 0%.

### §4.1 The required-sentence finding

> **The absence of repeated model-generated risk language is not evidence that the risks are absent; it is evidence that the current autoresearch loop under-represents security/threat-model reasoning.**

This is the load-bearing observation of the amendment. The risks named in V0 §2.3 / §3.3 / §4.3 are real. They were articulated by the operator after considering capture, custody, succession, and audit topology — none of which the model exhibits attention to under this prompt configuration.

### §4.2 Possible mechanisms (not yet distinguished)

The risk-signal absence has at least three non-mutually-exclusive causes:

1. **Prompt truncation.** The 1600-char excerpt of `BOOTSTRAP_ELECTION_OPTIONS_V0` covers frontmatter + §0 + §1. The risk sections in §2.3 / §3.3 / §4.3 were never injected. The model could not echo what it never read.
2. **Model bias toward structural framing.** `qwen3.5:9b`'s training prior likely favours procedural-completeness reasoning over adversarial-threat reasoning. Even with the full doctrine injected, model output may concentrate on mechanism over failure mode.
3. **Topic-string anchoring.** The injected topic (`"bootstrap election options"`) is a structural framing. A topic phrased as `"what fails in HELEN bootstrap"` might elicit more risk language. This run did not test that variant.

This amendment does not resolve which cause dominates. **Until the cause is distinguished, autoresearch risk-mining is unreliable for bootstrap decisions.**

---

## §5. Interpretation

The combined findings produce an asymmetric verdict:

| Dimension | Autoresearch evidence |
|---|---|
| The bootstrap question is real | **Validated** (96% `seal`, 54% `first mayor`, 47% `genesis`) |
| The bootstrap is structurally specifiable | **Validated** (model reproduces seal / admission vocabulary) |
| The bootstrap has identified risk modes | **NOT validated** (zero hits on the five named risks) |
| Operator's §2.3 / §3.3 / §4.3 risk model | **Operator-derived, not corpus-derived** |
| Bootstrap path can be model-selected | **Refuted** — model did not engage with the comparison axes |

The model gives a clean "yes the question exists" and is silent on "here is which option is safer." The decision remains operator-only.

### §5.1 Why §13.3 default strengthens, not weakens

Before the autoresearch, `§13.3 deferred / stay RAW` was a recommendation defended on prudence grounds. After the autoresearch, it is defended on the additional empirical ground that **the most accessible automated method for surfacing decision support did not produce decision support**. The operator who elects §13.1 or §13.2 today does so without model-corpus validation of either path's risk profile.

---

## §6. Implications for bootstrap election

The implications are constraints, not new options:

### §6.1 Bootstrap path remains an operator-only decision

No future autoresearch run at this scale should be cited as "the model preferred path X." The model under this configuration produced no preference signal.

### §6.2 The risk model is operator-canonical

`BOOTSTRAP_ELECTION_OPTIONS_V0 §2.3 / §3.3 / §4.3` should be treated as operator-canonical risk enumeration. Any future amendment that *removes* a risk from those sections requires explicit operator justification, not "the autoresearch loop didn't surface it."

### §6.3 The 5-hour loop is doubly gated

It was already gated by Run 2 envelope-failure rate (24% > 20%, blocked). It is now additionally gated by the risk-signal-absence finding: more receipts in this configuration will produce more structural pressure and the same risk silence. **Scaling the existing loop will not generate the missing signal.**

### §6.4 An autoresearch loop *could* be redesigned to surface risk

A useful future-protocol question, not actionable now: would a loop with `topic = "what fails in HELEN OS MAYOR bootstrap"` and `--prompt-file` injecting V0 §2.3 / §3.3 / §4.3 (the risk sections, not the framing) produce risk-language? That experiment is itself a doctrine task, not a code task; the prompt-file extraction would be an evidence-gathering tool, not an admission tool.

### §6.5 What this amendment does *not* license

- It does not license a §13.1 or §13.2 election. The risk model is unchanged and unmitigated.
- It does not license `mayor_admission.py` implementation.
- It does not license writing to `helensh/.state/admitted_canon.jsonl`.
- It does not license treating any of the 100 autoresearch receipts as ratified canon.

---

## §7. Defaults reaffirmed

> **Default remains §13.3 deferred bootstrap / stay RAW.**
> **No 5-hour loop.**
> **No MAYOR election.**
> **No admitted canon.**
> **No ledger mutation.**

The RAW control plane continues operating. The 100 autoresearch receipts join the existing corpus as `RAW` evidence with both lanes `null`. They are reviewable in the cockpit (`review_cockpit.py --source gemma --needs-hal`) but do not constitute a vote.

---

## §8. Resume conditions and halt boundary

GOBLIN halts here. This amendment is RAW. It documents what the autoresearch found and what it could not find. It elects nothing.

Resume conditions:

1. **HER attestation**: HER reviews §3–§6 against the actual receipt corpus to confirm the per-pattern counts are reproducible.
2. **HAL review (recorded)**: HAL receives this amendment as a M2 proposal envelope. `hal_verdict` ∈ {`PASS`, `FAIL`, `NEEDS_MORE_RECEIPTS`}.
3. **Operator decision (recorded)**: `APPROVED_FOR_SANDBOX_ONLY`, `REJECTED`, or `PENDING_REVIEW`.
4. **MAYOR admission (deferred)**: this amendment, like its parent, cannot be admitted to canon until MAYOR exists and a bootstrap path is elected. Under §13.3 default, that is indefinitely.
5. **Future autoresearch on risks**: §6.4 sketches a redesigned loop. Drafting that experiment is a separate doctrine task; running it is a separate operator decision.

The only action this document performs is **the act of being written and committed to the public branch**. It is an M5 derived artifact per `RECEIPT_SAFE_MUTATION_PROTOCOL_V0 §3` — not state, not canon, just evidence of what the 100-epoch run did and did not yield.

> NO MAYOR SEAL = NO ADMITTED CANON.
> MODEL-MAJORITY ≠ OPERATOR JUDGMENT.

Stand down preserved.
