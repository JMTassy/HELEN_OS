r"""CROSS_MODEL_INDEPENDENCE_V0 — the benchmark's laws, frozen before
Qwen produces a single token.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: PREREGISTERED — the commit carrying this file is the freeze
receipt. Execution belongs to the local lane (Gemma4-12B + Qwen3.8-
27B UD-Q4_K_XL under llama.cpp); this module is the referee that
refuses the known ways the experiment can lie.

    Different model lineage  does not entail  N_eff = 2

Qwen is added as an ORTHOGONAL PROPOSER, never a replacement:
HER_G (Gemma) and HER_Q (Qwen) feed the SAME frozen quotient q. The
question is never "which model is smarter" — it is marginal quotient
discovery:

    Delta Q_useful,Q|G = | Q_useful^Qwen \ Q_useful^Gemma_union |

where a class is USEFUL only if Novel AND Falsifiable AND
Discriminable — HAL/F, HAL/P, HAL/X survived, with a concrete
discriminator x*. Ten novel unfalsifiable abstractions lose to one
excellent discriminator.

THE THREE AXES ARE NEVER COLLAPSED:

    N_generators != N_computational_roots != N_evidentiary_roots

Gemma(D) and Qwen(D) share the corpus D: two proposers, one witness.
Independent computation is not independent evidence — the HAL/P
distinction, kept structural.

THE TWO DECODING EXPERIMENTS ARE NEVER SILENTLY MIXED:

    E1 controlled decoding   identical sampling for both models
    E2 native decoding       each model's recommended parameters

E1 isolates the weights; E2 asks which model is useful when
correctly operated. Different experiments, declared as such.

BASELINE HYGIENE: non-thinking first (the Gemma baseline was
think:false) · preserve_thinking=false (hidden-state carryover
contaminates seeds, fresh-context HAL, novelty, independence and
replication) · SAME bounded context packet as Gemma (otherwise Qwen
gets two interventions at once and nothing is causal).

THE BORING FIRST WITNESS gates entry into the research graph:
MODEL_LOADED, non-thinking confirmed, schema PASS, Y_E = 1, Y_P = 1.
The instrumentation lesson (parse_yield 0 at T=0) is not relearned.

VENDOR CLAIMS ARE REPORTED_EXTERNAL: benchmark scores, the 17-19 GB
band, quant retention, throughput — expectations until reproduced on
the actual machine. DocumentationClaim !=> LocalExecutionWitness
(receipt_integrity, applied to model cards).

PROMOTION GATE: Qwen earns a HELEN seat only on Delta Q_useful > 0
with cross-seed stability at acceptable marginal compute. And in
every branch, capability buys ZERO authority — a stronger adversary
behind the same small Gamma is exactly what HELEN wants.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

STATUS = "PREREGISTERED"

AXES = ("N_generators", "N_computational_roots", "N_evidentiary_roots")

ARMS = ("A_gemma_seeds_42_46", "B_qwen_nonthink_seeds_42_46",
        "C_union", "D_ablations_later")

ABLATIONS_LATER = ("reasoning_low", "reasoning_medium",
                   "reasoning_xhigh", "preserve_thinking",
                   "context_scaling", "vision", "tool_calling")

FIRST_WITNESS = ("model_loaded", "non_thinking_confirmed",
                 "output_schema_pass", "execution_yield_1",
                 "parse_yield_1")

USEFUL_PARTS = ("novel", "falsifiable", "discriminable")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the three axes, never collapsed ────────────────────────────────────

def independence_axes(n_generators: int, n_computational_roots: int,
                      n_evidentiary_roots: int) -> dict:
    """Two proposers over one corpus: N_gen=2, N_evid=1. Both true at
    once; neither is 'N_eff'."""
    if min(n_generators, n_computational_roots,
           n_evidentiary_roots) < 0:
        raise ValueError("E_NEGATIVE_COUNT")
    return {"N_generators": n_generators,
            "N_computational_roots": n_computational_roots,
            "N_evidentiary_roots": n_evidentiary_roots,
            "independent_proposers": n_generators > 1,
            "independent_witnesses": n_evidentiary_roots > 1,
            "law": "independent computation is not independent "
                   "evidence"}


def collapse_to_neff(_axes: dict) -> dict:
    """The move the ruling forbids by name."""
    return {"collapsed": False, "reason": "E_COLLAPSED_AXES",
            "law": "never collapse generators, computational roots "
                   "and evidentiary roots into one N_eff"}


# ── usefulness and the primary endpoint ────────────────────────────────

def useful(novel: bool, falsifiable: bool, discriminable: bool,
           x_star: str | None) -> dict:
    """Useful = Novel AND Falsifiable AND Discriminable, with the
    discriminator NAMED. HAL survival without an x* is admiration,
    not usefulness."""
    parts = {"novel": novel, "falsifiable": falsifiable,
             "discriminable": discriminable}
    missing = sorted(k for k, v in parts.items() if not v)
    if missing:
        return {"useful": False, "missing": tuple(missing),
                "reason": "E_NOT_USEFUL"}
    if not x_star:
        return {"useful": False, "reason": "E_NO_DISCRIMINATOR",
                "law": "a surviving class without a concrete x* "
                       "cannot be acquired against"}
    return {"useful": True, "x_star": x_star}


def delta_q_useful(q_qwen_useful: frozenset,
                   q_gemma_union: frozenset) -> dict:
    """The primary endpoint. Magnificent prose with
    Q_Q subset-of Q_G buys nothing."""
    marginal = q_qwen_useful - q_gemma_union
    inter = q_qwen_useful & q_gemma_union
    union = q_qwen_useful | q_gemma_union
    return {"delta_Q_useful_Q_given_G": len(marginal),
            "marginal_classes": tuple(sorted(marginal)),
            "jaccard": round(len(inter) / len(union), 6) if union
                       else None,
            "verdict": "COVERAGE_BOUGHT" if marginal else
                       "NO_COVERAGE_BOUGHT",
            "law": "the endpoint is marginal quotient discovery, "
                   "never raw candidate counts"}


# ── the two decoding experiments, never mixed ──────────────────────────

def decoding_regime(gemma_params: dict, qwen_params: dict,
                    declared: str) -> dict:
    """E1 = identical sampling (isolates weights). E2 = each model's
    native recommendation (asks operational usefulness). A run whose
    declaration does not match its parameters is refused."""
    identical = gemma_params == qwen_params
    if declared == "E1_controlled":
        ok = identical
    elif declared == "E2_native":
        ok = not identical
    else:
        return {"ok": False, "reason": "E_UNKNOWN_REGIME"}
    return {"ok": ok, "declared": declared,
            "params_identical": identical,
            "reason": None if ok else "E_MIXED_DECODING_REGIMES",
            "law": "controlled and native decoding are different "
                   "experiments; mixing them silently answers "
                   "neither question"}


# ── baseline hygiene ───────────────────────────────────────────────────

def baseline_config(think: bool, preserve_thinking: bool,
                    context_matched_to_gemma: bool) -> dict:
    problems = []
    if think:
        problems.append("E_THINKING_AT_BASELINE")
    if preserve_thinking:
        problems.append("E_HIDDEN_STATE_CARRYOVER")
    if not context_matched_to_gemma:
        problems.append("E_CONFOUNDED_CONTEXT")
    return {"ok": not problems, "refusals": tuple(problems),
            "law": "one intervention at a time: different weights, "
                   "same everything else — thinking, hidden memory "
                   "and context width are their own later ablations"}


def first_witness(results: dict) -> dict:
    """The boring gate. Qwen enters the research graph only after
    all five, and the first witness SHOULD be boring."""
    missing = sorted(set(FIRST_WITNESS) - {k for k, v
                                           in results.items() if v})
    return {"enters_research_graph": not missing,
            "missing": tuple(missing),
            "reason": None if not missing else "E_UNPROBED_MODEL",
            "law": "the parse-yield lesson is not relearned; "
                   "instrument first, hypothesize second"}


# ── vendor claims and the promotion gate ───────────────────────────────

def vendor_claim(claim: str) -> dict:
    """Model-card figures are motivation, never local evidence."""
    return {"claim": claim, "grade": "REPORTED_EXTERNAL",
            "observed_local": False,
            "law": "DocumentationClaim does not entail "
                   "LocalExecutionWitness; the memory band, quant "
                   "retention and benchmark scores are expectations "
                   "until reproduced on the actual machine"}


def promotion_gate(delta_q: int, cross_seed_stable: bool,
                   marginal_cost_acceptable: bool) -> dict:
    """A seat is earned by coverage, held to cost — and capability
    buys zero authority in every branch."""
    earned = delta_q > 0 and cross_seed_stable and \
        marginal_cost_acceptable
    return {"seat_earned": earned,
            "authority_delta": 0,
            "reason": None if earned else (
                "E_NO_MARGINAL_COVERAGE" if delta_q <= 0 else
                "E_UNSTABLE_ACROSS_SEEDS" if not cross_seed_stable
                else "E_MARGINAL_COST_TOO_HIGH"),
            "law": "Qwen can enlarge HELEN's cognition space; it "
                   "gets zero additional authority by being more "
                   "capable"}
