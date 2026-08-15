r"""Institutional Stemmatics — the UZIK corpus weighed by genealogy,
not counted. Candidate doctrine.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: CANDIDATE_DOCTRINE (operator's grade).

The thesis: institutional memory != document accumulation. It is
genealogy + independence + contradiction + replay. The same claim
appearing in five UZIK artifacts descended from one source is ONE
independent witness, not five — textual criticism's rule applied to
an organization's archive.

    N_files != N_epi
    5 x "UZIK says X"  !=>  5 x evidence for X          (NONAMPLIFICATION-01)

CONVERGENCE, NOT NOVELTY (recorded honestly): the ROOT-family
collapse is the same law already in the archaeologist skill's
root_normalizer and in cross_model_independence.collapse_to_neff /
scaling_harness.swarm_common_mode; the licensed frontier F* is
layered_frontier's. This module adds only the pieces NOT already in
the kernel: epistemic density rho_epi, adversarial (frontier-change)
retrieval, negative-memory-first capability, and the anti-mythology
non-implication chain — and it names the convergence rather than
banking it as independent support (that would be the very
consensus-illusion the doctrine forbids).

WHAT THIS MODULE REFUSES:
- counting representations as evidence (E_REPETITION_AS_CORROBORATION)
- retrieval that maximizes similarity when a contradicting document
  would move the frontier more (E_SIMILARITY_BLIND_RETRIEVAL)
- deriving a capability from successes only, ignoring failures and
  boundary conditions (E_SURVIVORSHIP_CAPABILITY)
- inferring present capability or authority from a persistent
  narrative (E_NARRATIVE_MINTS_CAPABILITY, and the whole chain)
"""
from __future__ import annotations

import json

WITNESS_CLASSES = ("SUCCESS", "FAILURE", "PARTIAL", "UNKNOWN",
                   "UNRESOLVED")

# the anti-mythology chain: each pair is a non-implication the graph
# must never collapse.
ANTI_MYTHOLOGY = (
    ("archive_mass", "knowledge"),
    ("repetition", "corroboration"),
    ("corporate_claim", "capability"),
    ("past_capability", "present_capability"),
    ("learned_pattern", "authority"),
    ("authority", "effect"),
)


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


# ── 1. epistemic density (the new metric) ──────────────────────────────

def rho_epi(n_independent_roots, n_representations) -> dict:
    """rho_epi = |R_independent| / |D_representations|. A huge archive
    with rho_epi << 1 holds little independent institutional
    knowledge. The five-representations/one-root case yields 0.2."""
    if n_representations <= 0:
        return {"ok": False, "reason": "E_NO_REPRESENTATIONS"}
    if n_independent_roots < 0 or \
            n_independent_roots > n_representations:
        return {"ok": False, "reason": "E_MORE_ROOTS_THAN_DOCS"}
    rho = round(n_independent_roots / n_representations, 6)
    return {"ok": True, "rho_epi": rho,
            "n_independent_roots": n_independent_roots,
            "n_representations": n_representations,
            "amplification_illusion": rho < 1.0 and
            n_representations > 1,
            "law": "a large archive with rho_epi << 1 holds little "
                   "independent knowledge"}


def nonamplification(n_saying_x, n_independent_roots) -> dict:
    """UZIK-NONAMPLIFICATION-01: k documents asserting X descended
    from one root are one unit of evidence, not k. Treating the count
    as the weight is refused."""
    if n_independent_roots < 1 and n_saying_x > 0:
        return {"ok": False, "reason": "E_NO_ROOT_FOR_CLAIM"}
    evidence_units = n_independent_roots
    if n_saying_x > evidence_units:
        return {"licensed": True, "n_representations": n_saying_x,
                "evidence_units": evidence_units,
                "amplified": True,
                "note": "representations exceed evidence; count the "
                        "roots"}
    return {"licensed": True, "n_representations": n_saying_x,
            "evidence_units": evidence_units, "amplified": False}


def repetition_is_not_corroboration(n_representations,
                                    same_root) -> dict:
    """Explicit refusal for the ranking layer: repeated wording from
    one root adds no corroboration."""
    if same_root and n_representations > 1:
        return {"corroborates": False,
                "reason": "E_REPETITION_AS_CORROBORATION"}
    return {"corroborates": True}


# ── 2. adversarial retrieval (frontier-change, not similarity) ─────────

def retrieve(candidates) -> dict:
    """Rank by ExpectedFrontierChange, not Similarity(query, d). A
    contradictory economics sheet with high frontier-change outranks a
    fourth marketing assertion with high similarity but near-zero
    information gain.

        d* = argmax_d ExpectedFrontierChange(d)

    candidates: ((doc_id, similarity, expected_frontier_change,
                  contradicts), ...)"""
    if not candidates:
        return {"ok": False, "reason": "E_NO_CANDIDATES"}
    # the similarity-blind pick (what naive RAG would do) and the
    # frontier pick (what HELEN does) — reported both so the
    # divergence is visible.
    by_sim = max(candidates, key=lambda c: (c[1], c[0]))
    by_frontier = max(candidates, key=lambda c: (c[2], c[0]))
    return {"ok": True,
            "similarity_pick": by_sim[0],
            "d_star": by_frontier[0],
            "d_star_contradicts": by_frontier[3],
            "divergent": by_sim[0] != by_frontier[0],
            "law": "sometimes the least convenient document is the "
                   "most informative"}


def retrieval_policy(mode) -> dict:
    """A retrieval configured to maximize similarity alone is refused
    for institutional memory: it is blind to the discriminating
    document."""
    if mode == "max_similarity":
        return {"licensed": False, "reason": "E_SIMILARITY_BLIND_RETRIEVAL"}
    if mode == "max_expected_frontier_change":
        return {"licensed": True}
    return {"licensed": False, "reason": "E_UNKNOWN_RETRIEVAL_MODE"}


# ── 3. negative memory is first-class ──────────────────────────────────

def capability(successes, failures, boundary_conditions,
               counterexamples) -> dict:
    """Capability(C) = f(Successes, Failures, BoundaryConditions,
    Counterexamples). A capability claimed from successes alone, with
    no failure or boundary evidence, is survivorship — refused. The
    institutional question is not 'what did UZIK do well' but 'under
    exactly what conditions did mechanism C work, fail, or become
    unidentified'."""
    if successes > 0 and failures == 0 and \
            not boundary_conditions and counterexamples == 0:
        return {"ok": False, "reason": "E_SURVIVORSHIP_CAPABILITY",
                "law": "a capability with no witnessed failure or "
                       "boundary is a success highlight reel"}
    return {"ok": True,
            "characterized": True,
            "conditions_known": bool(boundary_conditions),
            "note": "capability is the conditions under which the "
                    "mechanism works, fails, or is unidentified"}


def witness_class(cls) -> dict:
    """Five classes; FAILURE / PARTIAL / UNRESOLVED are as first-class
    as SUCCESS. A graph that keeps only successes cannot characterize
    a capability."""
    if cls not in WITNESS_CLASSES:
        return {"ok": False, "reason": "E_UNKNOWN_WITNESS_CLASS"}
    return {"ok": True, "class": cls,
            "is_negative_memory": cls in ("FAILURE", "PARTIAL",
                                          "UNRESOLVED")}


# ── 4. the anti-mythology chain ────────────────────────────────────────

def implies(antecedent, consequent) -> dict:
    """Every pair in the anti-mythology chain is a non-implication.
    NarrativePersistence !=> CapabilityPersistence, and the rest."""
    if (antecedent, consequent) in ANTI_MYTHOLOGY:
        return {"implication_licensed": False,
                "reason": "E_" + {
                    "knowledge": "ARCHIVE_MINTS_KNOWLEDGE",
                    "corroboration": "REPETITION_AS_CORROBORATION",
                    "capability": "NARRATIVE_MINTS_CAPABILITY",
                    "present_capability": "PAST_MINTS_PRESENT",
                    "authority": "PATTERN_MINTS_AUTHORITY",
                    "effect": "AUTHORITY_MINTS_EFFECT",
                }[consequent]}
    return {"implication_licensed": None,
            "note": "pair not governed by this chain"}


def constitutional_forgetting(warranted_at, currently_available,
                              currently_authorized) -> dict:
    """Historically warranted !-> currently available !-> currently
    authorized. The frontier is time-indexed: F*_2016 does not license
    F*_2026. This is forgetting without historical erasure — the past
    witness is kept, its present authority is not inherited."""
    reasons = []
    if warranted_at and not currently_available:
        reasons.append("warranted_then_not_available_now")
    if currently_available and not currently_authorized:
        reasons.append("available_not_authorized")
    return {"history_preserved": True,
            "present_capability": currently_available,
            "present_authority": currently_authorized,
            "gaps": tuple(reasons),
            "law": "constitutional forgetting: keep the record, do "
                   "not inherit the authority"}


# ── 5. the Institutional Witness Graph type ────────────────────────────

def iwg_claim_support(claim, representations, independent_roots,
                      contradictions) -> dict:
    """A claim in the IWG = (D,C,R,E,tau,Omega,F*) is supported by its
    independent ROOTS R, never its representation count D, and its
    support is net of contradictions. This is the type the extraction
    algorithm emits instead of a similarity-ranked chunk list."""
    if independent_roots < 0 or representations < independent_roots:
        return {"ok": False, "reason": "E_MORE_ROOTS_THAN_DOCS"}
    net_support = independent_roots - contradictions
    return {"ok": True, "claim": claim,
            "representations": representations,
            "independent_roots": independent_roots,
            "contradictions": contradictions,
            "net_independent_support": net_support,
            "rho_epi": (round(independent_roots / representations, 6)
                        if representations else None),
            "status": "CONTESTED" if contradictions > 0 else
            ("SUPPORTED" if net_support > 0 else "UNSUPPORTED"),
            "promoted": False,
            "law": "support is counted in independent roots, net of "
                   "contradiction — never in representations"}
