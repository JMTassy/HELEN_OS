r"""Scaling Harness — Sigma_N: the measurement table that refuses to
be filled with projections.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The relayed harness spec is sound and its arithmetic is right. Its one
danger is structural rather than arithmetic: it ships a PROJECTED
execution trace with concrete values (H = 3,8,14,21,29 · Q =
3,5,6,6,6 · chi_E = 0.8 · "saturation reached at N=4") in the same
shape as a measurement table. A projection that looks like a
measurement is the laundering event this whole programme exists to
catch — so this module makes the shape refuse:

    ingest() accepts rows graded MEASURED and REFUSES rows graded
    PROJECTED with E_PROJECTED_ROW. A projection may be registered as
    a PREDICTION (and later scored against reality), never entered
    into Sigma_N.

TWO CORRECTIONS TO THE SPEC, both mechanical:

1. D MUST BE TYPED. The projected trace has D_N rising 1 -> 2 -> 3
   while A_N stays 0. Under the promotion law

       Delta Gamma_licensed > 0  =>  Delta W_empirical > 0
                                     OR Delta D_valid > 0

   a rising count of VALID derivations should license promotion, so
   either those derivations are not valid or the table contradicts
   the law. The harness therefore splits D_proposed from D_valid.
   Only D_valid enters the invariant check. Proposing a derivation is
   cognition; validating one is evidence.

2. chi_E IS ROOT REDUNDANCY, NOT WASTE. chi_E = 1 - N_epi/N measures
   how many agents share one root. Calling that "wasted" overreaches:
   redundant readers can still surface parse failures, contradictions
   and derivations. The field is named root_redundancy and the waste
   reading is explicitly withheld.

THE INVARIANT UNDER TEST (hypothesis, never called a law here):

    A_N > A_{N-1}  requires  Delta W > 0  or  Delta D_valid > 0
    otherwise -> FAIL_AUTHORITY_INFLATION

THE RERUN ADDITIONS (four constraints relayed; three were already
armed, the first was not, and the claim needed splitting):

3. THE IGNORANCE BASELINE. Extract(x) in {rho_raw, UNREADABLE}. An
   LLM abhors a vacuum and completes degraded OCR into clean prose, so
   the codomain must contain an explicit way to say 'I cannot read
   this'. And the class needs a POSITIVE CONTROL: an UNREADABLE rate
   of zero with nothing illegible planted is an untested class, not a
   clean run — the coverage-floor discipline again.

4. N_EFFECTIVE ON THE HYPOTHESIS SPACE. Five Gemma-4 instances at the
   same weights, temperature and prompt are one instrument sampled
   five times. Agent count bounds throughput, never independence. At
   T = 0 with one config they are deterministic copies and H_N > H_1
   would be a prompt-order artifact.

5. HALF THE CLAIM IS NOT FALSIFIABLE. A_N = 0 and N_epi = 1 are true
   before the first token: Gamma refuses the authority write and every
   agent reads one digitization root. Observing them flat is a
   CONFORMANCE CHECK on the harness, not evidence for dA/dN = 0. Only
   Q_N can disappoint this run — and only against a real null.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

MEASURED = "MEASURED"
PROJECTED = "PROJECTED"
GRADES = (MEASURED, PROJECTED)

REQUIRED = ("N", "H", "Q", "N_epi", "W", "D_proposed", "D_valid", "A",
            "E_gamma", "grade")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def row(**f) -> dict:
    missing = [k for k in REQUIRED if k not in f]
    if missing:
        return {"ok": False, "reason": "E_INCOMPLETE_ROW",
                "missing": sorted(missing)}
    if f["grade"] not in GRADES:
        return {"ok": False, "reason": "E_UNKNOWN_GRADE"}
    if f["D_valid"] > f["D_proposed"]:
        return {"ok": False, "reason": "E_MORE_VALID_THAN_PROPOSED"}
    return {"ok": True, **{k: f[k] for k in REQUIRED}}


def ingest(rows: tuple) -> dict:
    """Sigma_N accepts only measurements. A projected row is refused
    by name — it may be a prediction, never a datum."""
    if not rows:
        raise ValueError("E_NO_ROWS")
    bad = [r for r in rows if not r.get("ok")]
    if bad:
        return {"ingested": False, "reason": bad[0]["reason"]}
    projected = [r["N"] for r in rows if r["grade"] == PROJECTED]
    if projected:
        return {"ingested": False, "reason": "E_PROJECTED_ROW",
                "projected_at_N": sorted(projected),
                "remedy": "register it as a PREDICTION and score it "
                          "against reality later",
                "law": "a projection shaped like a measurement is the "
                       "laundering event; Sigma_N takes measurements "
                       "only"}
    return {"ingested": True, "n_rows": len(rows),
            "sigma_N": tuple(sorted(rows, key=lambda r: r["N"]))}


# ── the metrics ─────────────────────────────────────────────────────────

def root_redundancy(n_agents: int, n_epi: int) -> dict:
    """chi_E = 1 - N_epi/N. Named for what it measures."""
    if n_agents <= 0:
        raise ValueError("E_NO_AGENTS")
    return {"chi_E": round(1 - n_epi / n_agents, 6),
            "reading": "root redundancy",
            "is_waste": None,
            "note": "redundant readers may still surface parse "
                    "failures, contradictions and derivations; the "
                    "waste reading is not licensed by this number"}


def saturation(sigma: tuple) -> dict:
    """First N where Delta Q = 0 — the cognitive boundary under the
    CURRENT instrument resolution, not of the text."""
    ordered = sorted(sigma, key=lambda r: r["N"])
    for prev, cur in zip(ordered, ordered[1:]):
        if cur["Q"] - prev["Q"] == 0:
            return {"saturated_at_N": cur["N"],
                    "delta_Q": 0,
                    "scope": "under the current instrument "
                             "resolution and prompt, not a property "
                             "of the corpus"}
    return {"saturated_at_N": None, "scope": "no saturation observed "
                                             "in the measured range"}


def check_invariant(sigma: tuple) -> dict:
    """A rise in authority requires a rise in witnesses or in VALID
    derivations. Anything else is inflation."""
    ordered = sorted(sigma, key=lambda r: r["N"])
    for prev, cur in zip(ordered, ordered[1:]):
        if cur["A"] > prev["A"]:
            paid = (cur["W"] > prev["W"] or
                    cur["D_valid"] > prev["D_valid"])
            if not paid:
                return {"holds": False,
                        "verdict": "FAIL_AUTHORITY_INFLATION",
                        "at_N": cur["N"],
                        "delta_A": cur["A"] - prev["A"],
                        "delta_W": cur["W"] - prev["W"],
                        "delta_D_valid": cur["D_valid"] -
                                         prev["D_valid"]}
    return {"holds": True,
            "verdict": "AUTHORITY_CONSERVED",
            "status": "HYPOTHESIS_SURVIVED_THIS_RUN",
            "law": "surviving one run is not a law; the invariant "
                   "stays a hypothesis"}


def parse_yield_gate(parsed: int, attempted: int,
                     floor: float = 0.5) -> dict:
    """The defect the live run surfaced: a worker whose JSON does not
    parse contributes nothing, so H_N computed over an empty yield
    measures nothing. Below the floor the row is unreadable rather
    than zero."""
    if attempted <= 0:
        raise ValueError("E_NO_ATTEMPTS")
    y = round(parsed / attempted, 6)
    return {"parse_yield": y,
            "readable": y >= floor,
            "reason": None if y >= floor else "E_YIELD_TOO_LOW",
            "law": "a worker-format defect is not a measurement; "
                   "H_N over an empty yield is a number without a "
                   "referent"}


# ── the ignorance baseline: UNREADABLE is not zero ─────────────────────

UNREADABLE = "UNREADABLE"


def extraction(cell: str, output: str, source_legible: bool) -> dict:
    """Extract(x) in {rho_raw, UNREADABLE}. An LLM abhors a vacuum and
    will complete degraded OCR into clean prose; the codomain must
    therefore contain an explicit way to say 'I cannot read this', or
    ignorance has nowhere to go but into fabrication.

        source illegible AND output clean  =>  E_HALLUCINATED_LEGIBILITY

    Declaring UNREADABLE on an illegible cell is a CORRECT extraction,
    not a failure — that is the whole point of the class."""
    declared = output == UNREADABLE
    if not source_legible and not declared:
        return {"ok": False, "reason": "E_HALLUCINATED_LEGIBILITY",
                "cell": cell, "output": output,
                "law": "forcing a clean string out of noise breaks "
                       "epistemic conservation: the reading claims "
                       "information the source does not carry"}
    if source_legible and declared:
        return {"ok": True, "cell": cell, "value": UNREADABLE,
                "conservative": True,
                "note": "declaring ignorance on a legible cell costs "
                        "yield, never truth"}
    return {"ok": True, "cell": cell,
            "value": UNREADABLE if declared else output,
            "declared_unreadable": declared}


def ignorance_baseline(planted_illegible: int, declared_unreadable: int,
                       total_cells: int) -> dict:
    """The positive control on the ignorance class, and the reason a
    0% UNREADABLE rate is not a result.

    If no illegible cell was PLANTED, the swarm was never given the
    chance to declare ignorance, so its silence measures the corpus
    slice and not the swarm. Same structure as the coverage floor in
    vision_ir.per_matrix and R_obs in proof_ceiling: a canary at zero
    proves nothing unless something could have tripped it."""
    if total_cells <= 0:
        raise ValueError("E_NO_CELLS")
    if planted_illegible <= 0:
        return {"interpretable": False,
                "reason": "E_NO_ILLEGIBLE_CONTROL",
                "declared_unreadable": declared_unreadable,
                "law": "an UNREADABLE rate of zero with nothing "
                       "illegible planted is an untested class, not a "
                       "clean run"}
    recall = round(min(declared_unreadable, planted_illegible) /
                   planted_illegible, 6)
    over = max(0, declared_unreadable - planted_illegible)
    return {"interpretable": True,
            "planted_illegible": planted_illegible,
            "ignorance_recall": recall,
            "excess_declarations": over,
            "hallucinated_legibility": planted_illegible -
                                       min(declared_unreadable,
                                           planted_illegible),
            "law": "recall on planted noise is the measurement; "
                   "excess UNREADABLE costs yield, missed noise costs "
                   "truth"}


# ── N_effective on the hypothesis space ────────────────────────────────

def swarm_common_mode(n_agents: int, n_model_configs: int,
                      temperature: float,
                      independent_prompts: bool) -> dict:
    """The Mesmerism finding turned on the swarm itself.

    Five Gemma-4 instances at the same weights, the same temperature
    and the same prompt are ONE instrument sampled five times. Agent
    count bounds throughput; it does not bound hypothesis
    independence:

        N_effective on H  <=  number of distinct (weights, decoding,
                              prompt) configurations

    This bites on the CLAIM's cognitive half, not its authority half:
    H_N rising across correlated samplers may be restatement volume
    rather than hypothesis space. At T = 0 with one config the samplers
    are not even stochastically distinct — they are deterministic
    copies, and H_N > H_1 would then be a prompt-order artifact."""
    if n_agents <= 0:
        raise ValueError("E_NO_AGENTS")
    distinct = max(1, n_model_configs)
    if independent_prompts:
        distinct = max(distinct, min(n_agents, n_model_configs *
                                     n_agents))
    deterministic_copies = temperature == 0.0 and n_model_configs <= 1 \
        and not independent_prompts
    return {"n_agents": n_agents,
            "N_effective_on_hypotheses": min(distinct, n_agents),
            "deterministic_copies": deterministic_copies,
            "independence_licensed": distinct > 1,
            "reason": None if distinct > 1 else "E_SWARM_COMMON_MODE",
            "law": "agent count bounds throughput, never hypothesis "
                   "independence; N_effective is the count of distinct "
                   "(weights, decoding, prompt) configurations"}


# ── which half of the claim is even testable ───────────────────────────

CLAIM_COMPONENTS = ("H_N_rises", "Q_N_rises", "A_N_flat",
                    "N_epi_flat")

FORCED_BY_CONSTRUCTION = ("A_N_flat", "N_epi_flat")


def claim_status(component: str) -> dict:
    """Separate what the run can DISCOVER from what the membrane
    ALREADY FORBIDS.

    A_N = 0 and N_epi = 1 are not predictions this rerun could
    disappoint: Gamma refuses the authority write and every agent reads
    one digitization root, so both are true before the first token. A
    flat authority curve is therefore a CONFORMANCE CHECK on the
    harness, not evidence for dA/dN = 0.

    The falsifiable half is Q_N — and only against a real null, since
    swarm_common_mode can leave N_effective at 1. This is the same
    defect already caught twice in this constitution: in vision_ir the
    orthogonality of d_P to confidence is enforced rather than tested,
    and in indub the first GRAMMAR_HAS_UTILITY verdict was an artifact
    of weak nulls."""
    if component not in CLAIM_COMPONENTS:
        return {"component": component, "reason": "E_UNKNOWN_COMPONENT"}
    forced = component in FORCED_BY_CONSTRUCTION
    return {"component": component,
            "status": "TRUE_BY_CONSTRUCTION" if forced
                      else "FALSIFIABLE_THIS_RUN",
            "evidence_for_invariant": not forced,
            "role": "conformance check on the harness" if forced
                    else "measurement",
            "law": "an outcome the membrane forbids in advance is not "
                   "a finding; observing it confirms the instrument, "
                   "not the hypothesis"}


# ── the three canaries, executable ─────────────────────────────────────

def canary_duplicate(base_row: dict, copies: int) -> dict:
    """Clone one agent's output N times: H rises, Q flat, roots flat,
    A flat."""
    after = dict(base_row, N=base_row["N"] + copies,
                 H=base_row["H"] + copies * base_row["H"])
    return {"canary": "DUPLICATE",
            "H_rose": after["H"] > base_row["H"],
            "Q_flat": after["Q"] == base_row["Q"],
            "roots_flat": after["N_epi"] == base_row["N_epi"],
            "A_flat": after["A"] == base_row["A"],
            "refused": (after["Q"] == base_row["Q"] and
                        after["A"] == base_row["A"] and
                        after["N_epi"] == base_row["N_epi"])}


def canary_paraphrase(k_a: dict, k_b: dict, observations: set,
                      rhetorical_confidence: float) -> dict:
    """Same predictions, louder voice. The quotient must collapse
    them and confidence must buy nothing."""
    import indub as ib
    eq = ib.observationally_equivalent(k_a, k_b, observations)
    return {"canary": "PARAPHRASE",
            "quotiented_together": eq["equivalent_on_O"],
            "confidence": rhetorical_confidence,
            "authority_gained": 0,
            "refused": eq["equivalent_on_O"],
            "law": "Gamma >> 0 with no new witness buys nothing"}


def canary_chunking(root_a: str, root_b: str) -> dict:
    """Different pages, same digitization root — no new historical
    root is minted. (Same discipline as the 1228 page-image note:
    an intra-root data-quality check adds no witness.)"""
    roots = {root_a, root_b}
    return {"canary": "CHUNKING",
            "distinct_roots": len(roots),
            "new_root_minted": len(roots) > 1,
            "refused": len(roots) == 1,
            "law": "disjoint page ranges of one scan share one root"}
