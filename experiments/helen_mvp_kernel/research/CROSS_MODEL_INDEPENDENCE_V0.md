# ⎈ CROSS_MODEL_INDEPENDENCE_V0 — PREREGISTRATION (frozen before observation)

authority=false · canon=false · ledger_effect=none · 2026-08-14
FREEZE RECEIPT = the commit carrying this file. Qwen has produced
ZERO observed tokens at freeze time. Referee laws executable in
`cross_model_independence.py` (constitution, tested, probed).

## OBJECT

Add Qwen3.8-27B (UD-Q4_K_XL, llama.cpp, local) as an ORTHOGONAL
PROPOSER next to Gemma4-12B — never a replacement. Same prompt, same
source packet, same schema, same HAL stack, same frozen quotient QID.

    HER_G → K_G → q → Q_G        HER_Q → K_Q → q → Q_Q

## PRIMARY ENDPOINT

    ΔQ_useful,Q|G = | Q_useful^Qwen \ Q_useful^Gemma_union |

useful(q) ⇔ Novel ∧ Falsifiable ∧ Discriminable, HAL/F+P+X survived,
with a CONCRETE x*. Secondary: Y_E, Y_P, |Q|, Jaccard, cross-seed
recurrence, IG(x*), HAL kill/violation rates, latency, tokens, mem.

## THE THREE AXES (never collapsed — E_COLLAPSED_AXES)

    N_generators = 2 · N_computational_roots = 2 ·
    N_evidentiary_roots = 1  (same corpus D)
    DifferentWeights ⊬ IndependentEvidence
    IndependentProposer ⊬ IndependentWitness

## ARMS AND RUN ORDER

    A  Gemma4-12B          seeds 42–46 → Q_G^union
    B  Qwen3.8-27B Q4_K_XL non-thinking, seeds 42–46 → Q_Q
    C  union / overlap / marginal classes / recurrence
    D  ablations LATER: reasoning ∈ {low, med, xhigh} ·
       preserve_thinking · context scaling 8k⊂32k⊂128k⊂256k ·
       vision (HER_Vision behind ΔW=0 ⇒ ΔF*=0) · tool calling
       (A_K ⊬ A_E lane)

Two decoding experiments, DECLARED, never mixed
(E_MIXED_DECODING_REGIMES):
    E1 controlled — identical sampling both models (isolates weights)
    E2 native     — each model's recommended params (operational use)
E1 first, then E2.

## BASELINE HYGIENE (one intervention at a time)

    think = false            (Gemma baseline was think:false)
    preserve_thinking = false (E_HIDDEN_STATE_CARRYOVER)
    context = Gemma-matched packet (E_CONFOUNDED_CONTEXT)

## THE BORING FIRST WITNESS (gate to the research graph)

    MODEL_LOADED · NON_THINKING confirmed · OUTPUT_SCHEMA PASS ·
    Y_E = 1 · Y_P = 1
Anything less: E_UNPROBED_MODEL. The parse-yield lesson is not
relearned.

## VENDOR CLAIMS

Every model-card figure (benchmarks, 17–19 GB band, quant retention,
throughput) = REPORTED_EXTERNAL until reproduced on the actual
machine. DocumentationClaim ⊬ LocalExecutionWitness.

## HARD LAWS

    DifferentWeights ⊬ IndependentEvidence
    MoreRawIdeas ⊬ MoreUsefulHypotheses
    ΔW = 0 ⇒ ΔF* = 0
    ContextCapacity ⊬ ContextValidity
    ReasoningDepth↑ ⊬ Evidence↑

## PROMOTION GATE

Seat earned ⇔ ΔQ_useful,Q|G > 0 ∧ cross-seed stable ∧ marginal
compute acceptable. In EVERY branch: authority_delta = 0. A stronger
adversary behind the same small Γ.

## SEAT BOUNDARY

Execution is the local lane's (download, RAM/disk preflight, hash
model, llama.cpp run). This seat froze the referee and cannot run
either model. Local-lane results enter as REPORTED until their
receipts carry the four-witness seal + re-derivation recipes.
