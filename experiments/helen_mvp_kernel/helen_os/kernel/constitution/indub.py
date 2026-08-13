r"""indub(p) — inverse grammar induction, with the held-out falsifier
that can demote it.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
T-INDUB-01, per operator ruling: run induction before FETCH 1851, so
that 1851 later becomes an out-of-distribution VALIDATION corpus
rather than undirected collection growth.

    indub :  O_ATF  ->  (K_hat, W, U)

    K_hat = candidate generative rule set
    W     = supporting witnesses per rule
    U     = unresolved structure (honestly carried, never smoothed)

    then test:  Generate(K_hat)  ~=?  O_heldout

THE CRITICAL FALSIFIABLE QUESTION (the operator's, kept verbatim in
spirit): does a finite family of observed specimens permit recovery
of a COMPACT generative rule set that predicts held-out specimens
BETTER THAN DESCRIPTIVE MEMORIZATION? If it cannot predict held-out
structure, the 'grammar' reading is demoted to DESCRIPTIVE_TAXONOMY.

Three verdicts, and the middle one is the honest one most inducers
skip:

    SUPPORTED  — predicts held-out AND compresses
    HOLD       — predicts held-out but does NOT compress: memorization
                 cannot be ruled out, so no grammar claim is licensed
    REFUTED    — fails to predict held-out -> DESCRIPTIVE_TAXONOMY

The inducer generalizes ONLY where a second dimension is witnessed: a
pattern seen in >= 2 states and >= 2 sizes licenses a product rule;
anything else is enumerated as a literal. That restraint is what
makes the REFUTED verdict reachable — an inducer that always
generalizes can never fail, and an experiment that cannot fail is
theatre.

ACCESS LIMIT, stated not hidden: the verified ATF corpus (1267pp PDF
+ OCR text layer, hashed) lives in the local corpus/runtime lane and
is NOT reachable from this seat. This module therefore delivers the
machinery and its discrimination proof; the run against real ATF
specimens must execute where the corpus is. Nothing here claims to
have read the Desk Book.

AUDIT CORRECTION carried (operator): the ATF string verification
supports the specific historical border claim under the reported
corpus/hash workflow. It does NOT prove the architecture's epistemic
conservation law. It is a successful INSTANCE of the mechanism, not a
THEOREM about the architecture — see instance_is_not_theorem().

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

VERDICTS = ("SUPPORTED", "HOLD", "REFUTED")
COMPRESSION_FLOOR = 0.5      # legacy ratio, reported not decisive

# ── the explicit complexity penalty (operator constraint on stage 1) ───
# A description-length criterion replaces the magic threshold. A
# grammar must STRICTLY beat the cost of listing the observations, and
# it pays for what it over-generates: a rule that predicts far more
# than was seen must encode the exclusions.
ENCODER_VERSION = "mdl-v1"   # nu: the coding convention is PINNED.
# A MDL law is reproducible only under a stable code. Without a pinned
# nu, a grammar can "win" by silently changing how symbols are counted.
SYM_LITERAL = 3        # (pattern, size, state)
SYM_RULE_OVERHEAD = 3  # rule structure
SYM_SPURIOUS = 3       # each over-generated item must be excluded


def description_length(k_hat: dict, observed: set) -> dict:
    """L(K) + L(O|K) against the memorization baseline L(O). Strictly
    less, or the 'grammar' is not paying for itself."""
    l_rules = sum(SYM_RULE_OVERHEAD + len(r["sizes"]) + len(r["states"])
                  for r in k_hat.get("rules", ()))
    l_literals = SYM_LITERAL * len(k_hat.get("literals", ()))
    gen = generate(k_hat)
    missing = observed - gen
    spurious = gen - observed
    l_exceptions = (SYM_LITERAL * len(missing) +
                    SYM_SPURIOUS * len(spurious))
    total = l_rules + l_literals + l_exceptions
    baseline = SYM_LITERAL * len(observed)
    return {"nu": ENCODER_VERSION,
            "L_K": l_rules + l_literals,
            "L_exceptions": l_exceptions,
            "over_generated": len(spurious),
            "total": total, "baseline_memorization": baseline,
            "beats_memorization": total < baseline,
            "margin": baseline - total,
            "law": "a grammar must cost strictly less than the list it "
                   "replaces, and must pay for what it invents"}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _triples(specimens: tuple) -> set:
    return {(s["pattern"], s["size"], s["state"]) for s in specimens}


# ── the inducer ─────────────────────────────────────────────────────────

def indub(specimens: tuple) -> dict:
    """Recover (K_hat, W, U). A product rule is licensed for a pattern
    only when a SECOND dimension is witnessed (>=2 sizes and >=2
    states); otherwise the specimens are carried as literals and the
    pattern is logged in U as unresolved structure."""
    if not specimens:
        raise ValueError("E_NO_SPECIMENS")
    obs = _triples(specimens)
    patterns = sorted({p for p, _, _ in obs})

    rules, literals, witnesses, unresolved = [], [], {}, []
    for p in patterns:
        sizes = sorted({s for pp, s, _ in obs if pp == p})
        states = sorted({st for pp, _, st in obs if pp == p})
        if len(sizes) >= 2 and len(states) >= 2:
            rid = f"R::{p}"
            rules.append({"rule_id": rid, "pattern": p,
                          "sizes": sizes, "states": states,
                          "form": "PRODUCT"})
            witnesses[rid] = sorted(t for t in obs if t[0] == p)
        else:
            literals.extend(sorted(t for t in obs if t[0] == p))
            unresolved.append(
                {"pattern": p, "sizes": sizes, "states": states,
                 "why": "second dimension not witnessed; no "
                        "generalization licensed"})

    k_size = len(rules) + len(literals)
    return {"K_hat": {"rules": rules, "literals": literals},
            "W": witnesses,
            "U": unresolved,
            "k_size": k_size,
            "n_observed": len(obs),
            "compression": round(1 - k_size / len(obs), 6)}


def generate(k_hat: dict) -> set:
    """Expand K_hat into the specimen set it predicts.

    A rule may name one pattern or carry an explicit `patterns` list.
    A wildcard pattern with no expansion list is REFUSED rather than
    emitted literally: the first version emitted ('*', size, state)
    tuples, which silently poisoned every downstream consumer that
    compared generated sets. Found by composing the stages, not by
    testing them one at a time."""
    out = set(tuple(t) for t in k_hat.get("literals", ()))
    for r in k_hat.get("rules", ()):
        pats = r.get("patterns")
        if pats is None:
            if r.get("pattern") == "*":
                raise ValueError("E_UNEXPANDED_WILDCARD")
            pats = [r["pattern"]]
        for p in pats:
            for s in r["sizes"]:
                for st in r["states"]:
                    out.add((p, s, st))
    return out


# ── the held-out falsifier ──────────────────────────────────────────────

def heldout_test(train: tuple, heldout: tuple) -> dict:
    """Induce on train, predict held-out. Compression AND prediction
    are reported separately so memorization is visible rather than
    laundered into a grammar claim."""
    if not heldout:
        raise ValueError("E_EMPTY_HELDOUT")
    fit = indub(train)
    predicted = generate(fit["K_hat"])
    target = _triples(heldout)
    hit = sorted(target & predicted)
    miss = sorted(target - predicted)
    coverage = round(len(hit) / len(target), 6)
    mdl = description_length(fit["K_hat"], _triples(train))

    tr = _triples(train)
    in_support = all(any(p == tp for tp, _, _ in tr) and
                     any(s == ts for _, ts, _ in tr) and
                     any(st == tst for _, _, tst in tr)
                     for p, s, st in target)
    regime = "INTERPOLATION" if in_support else "EXTRAPOLATION"

    if coverage < 1.0:
        verdict, demoted = "REFUTED", "DESCRIPTIVE_TAXONOMY"
    elif not mdl["beats_memorization"]:
        verdict, demoted = "HOLD", None
    else:
        verdict, demoted = "SUPPORTED", None

    return {"verdict": verdict,
            "demoted_to": demoted,
            "heldout_coverage": coverage,
            "heldout_regime": regime,
            "regime_note": ("a REFUTED verdict under EXTRAPOLATION "
                            "means the split asked for a dimension "
                            "value never witnessed — a different "
                            "experiment from interpolation, and not "
                            "the same failure"),
            "predicted_heldout": hit,
            "missed_heldout": miss,
            "mdl": mdl,
            "compression": fit["compression"],
            "compresses": mdl["beats_memorization"],
            "k_size": fit["k_size"],
            "unresolved": fit["U"],
            "law": "a grammar must predict what it never saw AND beat "
                   "the memorization baseline under an explicit "
                   "complexity penalty; predicting without paying for "
                   "itself licenses no grammar claim"}


def compare_mdl(a: dict, b: dict) -> dict:
    """J_nu(h) < J_nu(K_mem), strictly and under the SAME nu. Comparing
    description lengths computed by different encoders is meaningless
    and is refused rather than silently ranked."""
    if a.get("nu") != b.get("nu"):
        return {"comparable": False, "reason": "E_ENCODER_MISMATCH",
                "nu": (a.get("nu"), b.get("nu")),
                "law": "a MDL victory is only reproducible under a "
                       "pinned coding convention"}
    return {"comparable": True, "nu": a["nu"],
            "a_wins": a["total"] < b["total"],
            "strict": a["total"] != b["total"],
            "margin": b["total"] - a["total"]}


# ── observational equivalence: what is learned is a CLASS ──────────────

def observationally_equivalent(k1: dict, k2: dict,
                               observations: set) -> dict:
    """K1 ~_O K2 iff they agree on every observation. Grammars that
    differ only OUTSIDE the observed corpus are indistinguishable by
    that corpus — the object recovered is [K_hat]_O, never a uniquely
    identified historical generator."""
    g1, g2 = generate(k1), generate(k2)
    disagree = sorted((g1 ^ g2) & observations)
    outside = len(g1 ^ g2) - len(disagree)
    return {"equivalent_on_O": not disagree,
            "relative_to": "the finite corpus O",
            "equivalent_on_X": None,
            "disagreements_inside_O": disagree,
            "differences_outside_O": outside,
            "learned_object": "[K_hat]_O — an equivalence class "
                              "RELATIVE TO O, not simpliciter",
            "reason_if_claimed_globally": "E_LOCAL_EQUIVALENCE_"
                                          "GENERALIZED",
            "law": "K1 ~_O K2 does not entail K1 ~_X K2; agreement on "
                   "a finite corpus says nothing outside it — which "
                   "is exactly what DISCRIMINATE exists to exploit"}


def reconstructs_corpus_is_not_historically_used(k_id: str,
                                                 reconstructs: bool
                                                 ) -> dict:
    """ReconstructsCorpus(K) does not entail HistoricallyUsed(K).
    Distinct from the specimen-level law: this one is about the
    GENERATOR. A grammar that rebuilds every surviving artefact is
    observationally adequate; the designers may have used another
    member of the same equivalence class."""
    return {"grammar": k_id,
            "reconstructs_corpus": reconstructs,
            "historically_used": None,
            "licensed": "observational adequacy",
            "reason": "E_ADEQUACY_IS_NOT_IDENTITY"}


# ── the negative controls: an experiment needs a stupid opponent ───────

def k_memorizer(train: tuple) -> dict:
    """K_mem — memorizes the training set. Predicts nothing unseen."""
    return {"rules": [], "literals": sorted(_triples(train))}


def k_random(train: tuple, seed_index: int = 0) -> dict:
    """K_random — capacity roughly matched to the induced grammar but
    structurally arbitrary. Deterministic: the 'randomness' is a
    fixed rotation of the observed values, not a PRNG."""
    obs = _triples(train)
    patterns = sorted({p for p, _, _ in obs})
    sizes = sorted({s for _, s, _ in obs})
    states = sorted({st for _, _, st in obs})
    if not patterns:
        raise ValueError("E_NO_SPECIMENS")
    k = seed_index % len(patterns)
    rotated = patterns[k:] + patterns[:k]
    return {"rules": [{"rule_id": f"R::rand{i}", "pattern": p,
                       "sizes": sizes[:max(1, len(sizes) // 2)],
                       "states": states[:1], "form": "PRODUCT"}
                      for i, p in enumerate(rotated)],
            "literals": []}


def k_matched(train: tuple) -> dict:
    """K_matched — same rule count and roughly the same description
    length as K_hat, but with the size/state relations PERMUTED across
    patterns. Without it a good score may only mean the null models
    were too stupid to be informative."""
    fit = indub(train)
    rules = fit["K_hat"]["rules"]
    if len(rules) < 2:
        return {"rules": list(rules), "literals":
                list(fit["K_hat"]["literals"]), "degenerate": True}
    rot = rules[1:] + rules[:1]          # deterministic permutation
    return {"rules": [{"rule_id": f"R::m{i}", "pattern": r["pattern"],
                       "sizes": rot[i]["sizes"],
                       "states": rot[i]["states"], "form": "PRODUCT"}
                      for i, r in enumerate(rules)],
            "literals": list(fit["K_hat"]["literals"])}


def against_controls(train: tuple, heldout: tuple) -> dict:
    """The result is meaningful only if the induced grammar beats BOTH
    controls on genuinely unseen structure. Beating neither means the
    'induction' discovered nothing."""
    target = _triples(heldout)
    if not target:
        raise ValueError("E_EMPTY_HELDOUT")

    def cover(k):
        return round(len(target & generate(k)) / len(target), 6)

    p_induced = cover(indub(train)["K_hat"])
    p_mem = cover(k_memorizer(train))
    p_rand = cover(k_random(train))
    p_match = cover(k_matched(train))
    beats_both = (p_induced > p_mem and p_induced > p_rand and
                  p_induced > p_match)
    outperformed = [n for n, p in (("K_memorizer", p_mem),
                                   ("K_random", p_rand),
                                   ("K_matched", p_match))
                    if p > p_induced]
    if beats_both:
        verdict = "GRAMMAR_HAS_UTILITY"
    elif outperformed:
        verdict = "CONTROL_OUTPERFORMED_INDUCTION"
    else:
        verdict = "NO_UTILITY_DEMONSTRATED"
    return {"P_induced": p_induced, "P_memorizer": p_mem,
            "P_random": p_rand, "P_matched": p_match,
            "beats_both_controls": beats_both,
            "outperformed_by": outperformed,
            "verdict": verdict,
            "beats_all_three": beats_both,
            "law": "testing grammar utility, not grammar existence; "
                   "a win over stupid nulls only means the nulls were "
                   "stupid — K_matched is the one that can hurt"}


# ── DISCRIMINATE: disagreement becomes experimental design ─────────────

def discriminate(k1: dict, k2: dict, cost=None) -> dict:
    """x* = the observation that would most strongly separate two
    surviving grammars. Turns disagreement into information
    acquisition instead of averaging it away. This is the research
    verb that replaces MORE_SWARM and MORE_CORPUS."""
    g1, g2 = generate(k1), generate(k2)
    only1 = sorted(g1 - g2)
    only2 = sorted(g2 - g1)
    candidates = only1 + only2
    if not candidates:
        return {"discriminating_observation": None,
                "verdict": "OBSERVATIONALLY_IDENTICAL",
                "note": "no experiment separates them; the corpus "
                        "cannot decide between these grammars"}
    x_star = min(candidates, key=cost) if cost else candidates[0]
    return {"discriminating_observation": x_star,
            "selection_rule": "cheapest separating observation"
                              if cost else "first separating "
                              "observation (no cost model given)",
            "predicted_by": "K1" if x_star in only1 else "K2",
            "refutes_if_absent": "K1" if x_star in only1 else "K2",
            "n_discriminating_candidates": len(candidates),
            "verdict": "EXPERIMENT_DESIGNED",
            "law": "do not average disagreeing hypotheses; find the "
                   "observation that decides between them"}


# ── swarm laws: search power is not authority ──────────────────────────

def swarm_scaling(n_agents: int, hypotheses: int,
                  new_independent_witnesses: int,
                  new_valid_derivations: int,
                  roots_genuinely_independent: bool = True) -> dict:
    """CORRECTION to an overclaim this module shipped: dA/dN = 0 was
    written as an absolute law. It is CONDITIONAL —

        (dA/dN) | rho, Gamma, E, D  =  0

    i.e. holding provenance, admission rules, evidence roots and
    derivations FIXED, adding agents adds no authority. But if 32
    agents run 32 genuinely independent experiments, N raises E
    indirectly and A may become promotable. Headcount never creates
    authority; the new evidence they produced does.

        N up  does not entail  A up
        N up  =>  E_independent up  =>  A may become promotable
                  (iff the roots are genuinely independent)
    """
    delta_licensed = (new_independent_witnesses +
                      new_valid_derivations)
    counted = delta_licensed if roots_genuinely_independent else 0
    return {"n_agents": n_agents,
            "proposal_capacity": hypotheses,
            "claimed_evidence_delta": delta_licensed,
            "counted_evidence_delta": counted,
            "roots_genuinely_independent": roots_genuinely_independent,
            "authority_from_headcount": 0,
            "promotion_licensed": counted > 0,
            "law": "swarm scale buys hypothesis diversity, not "
                   "epistemic credit; N may raise A only THROUGH new "
                   "independent evidence, never directly"}


def research_state(n_agents: int, hypotheses: tuple,
                   equivalence_classes: int,
                   independent_roots: int) -> dict:
    """R_t = (K_t, E_t, D_t, U_t, X*_t). The fundamental object is no
    longer the grammar but the research state.

    CORRECTION to the proposed hierarchy, forced by the operator's own
    reported figures (32 agents, 43 hypotheses): the chain was stated
    as

        N_agents >> N_hypotheses >> N_equiv >> N_roots

    but the first link does NOT hold and should not — agents are
    GENERATORS, each producing many hypotheses across epochs, so
    N_hypotheses exceeding N_agents is health, not pathology. The
    load-bearing claim is the COLLAPSE chain, which starts one link
    later:

        N_hypotheses >= N_equivalence_classes >= N_independent_roots

    Agent -> hypothesis is amplification (expected). Hypothesis -> class
    -> root is collapse (the diagnostic). Distributed intelligence is
    counted in falsifiable distinctions and independent roots, never
    in agents or ideas."""
    n_h = len(hypotheses)
    chain = (n_h, equivalence_classes, independent_roots)
    collapse_holds = all(chain[i] >= chain[i + 1] for i in range(2))
    return {"N_agents": n_agents, "N_hypotheses": n_h,
            "N_equivalence_classes": equivalence_classes,
            "N_independent_roots": independent_roots,
            "amplification_agents_to_hypotheses": round(
                n_h / n_agents, 6) if n_agents else None,
            "collapse_hierarchy_holds": collapse_holds,
            "diversity_collapse": round(
                1 - equivalence_classes / n_h, 6) if n_h else None,
            "evidential_collapse": round(
                1 - independent_roots / n_h, 6) if n_h else None,
            "effective_witnesses": independent_roots,
            "law": "agent -> hypothesis is amplification and expected; "
                   "hypothesis -> class -> root is collapse and is the "
                   "diagnostic"}


def grammar_space(specimens: tuple) -> dict:
    """G(p) = {g : g ~> p}. Inverse reconstruction is NON-UNIQUE, and
    the first version of this module got it wrong: it returned a
    single K_hat, which hallucinates a unique historical production
    process. Several grammars generate the same specimens and differ
    only in what they predict BEYOND them.

        g1 ~> p  and  g2 ~> p  does not entail  g1 = g2

    Three canonical candidates are enumerated per family:
      LITERAL        exact, zero generalization, zero compression
      PER_PATTERN    generalize within a pattern (the indub default)
      GLOBAL_PRODUCT generalize across all patterns — maximal
                     compression, maximal over-generation
    Over-generation is reported, never hidden: it is the measure of
    how much history a grammar would invent."""
    if not specimens:
        raise ValueError("E_NO_SPECIMENS")
    obs = _triples(specimens)
    patterns = sorted({p for p, _, _ in obs})
    sizes = sorted({s for _, s, _ in obs})
    states = sorted({st for _, _, st in obs})

    literal = {"rules": [], "literals": sorted(obs)}
    per_pattern = indub(specimens)["K_hat"]
    global_product = {"rules": [{"rule_id": "R::*", "pattern": "*",
                                 "patterns": patterns,
                                 "sizes": sizes, "states": states,
                                 "form": "PRODUCT"}], "literals": []}

    cands = []
    for name, k in (("LITERAL", literal),
                    ("PER_PATTERN", per_pattern),
                    ("GLOBAL_PRODUCT", global_product)):
        gen = generate(k)
        k_size = len(k["rules"]) + len(k["literals"])
        cands.append({
            "grammar_id": name,
            "k_size": k_size,
            "covers_observed": obs <= gen,
            "over_generation": len(gen - obs),
            "compression": round(1 - k_size / len(obs), 6)})

    consistent = [c for c in cands if c["covers_observed"]]
    return {"G_of_p": cands,
            "consistent_with_observation": [c["grammar_id"]
                                            for c in consistent],
            "n_consistent": len(consistent),
            "unique": len(consistent) == 1,
            "law": "recover a SPACE of candidate explanations; a "
                   "single reconstruction presented as the historical "
                   "process is laundering"}


def select_unique(space: dict, discriminating_evidence: bool) -> dict:
    """Collapsing G(p) to one grammar requires evidence that
    ELIMINATES the rivals. Without it the honest output is
    UNDERDETERMINED — naming a winner would convert a modelling
    choice into a historical claim."""
    if space["n_consistent"] > 1 and not discriminating_evidence:
        return {"selected": None, "verdict": "UNDERDETERMINED",
                "reason": "E_NON_UNIQUE_RECONSTRUCTION",
                "survivors": space["consistent_with_observation"],
                "law": "g1 ~> p and g2 ~> p does not entail g1 = g2; "
                       "picking one without discriminating evidence "
                       "is historical laundering"}
    return {"selected": space["consistent_with_observation"][0]
                        if space["consistent_with_observation"] else None,
            "verdict": "DETERMINED" if discriminating_evidence
                       else "SINGLETON"}


def reconstructible_is_not_used(p: str, reconstructible: bool) -> dict:
    """The invariant that keeps reconstruction out of history:

        Reconstructible(p)  does not entail  HistoricallyUsed(p)

    distinct from Generable -> HistoricallyObserved: that one is
    about what the catalogue afforded, this one about what our own
    inference machinery can rebuild. Our ability to rebuild a
    specimen is a fact about US, not about the past."""
    return {"specimen": p,
            "reconstructible": reconstructible,
            "historically_used": None,
            "reason": "E_RECONSTRUCTION_IS_NOT_HISTORY",
            "law": "reconstructibility is a property of the inference "
                   "machinery, not evidence about production"}


def completion_is_not_validation(run: str, exit_code: int) -> dict:
    """The swarm reported exit code 0. That licenses 'the run
    completed' and nothing else — not convergence, not a validated
    grammar, not an admitted result."""
    return {"run": run, "exit_code": exit_code,
            "completed": exit_code == 0,
            "grammar_validated": False,
            "licensed": "the run completed",
            "reason": "E_COMPLETION_IS_NOT_VALIDATION",
            "next": ("inspect outputs for convergence, competing "
                     "grammars, reconstruction accuracy, and "
                     "epistemic over-promotion")}


def instance_is_not_theorem(mechanism: str, instance_verified: bool,
                            claimed_law: str) -> dict:
    """One mechanism firing successfully licenses a claim about THAT
    instance, never a theorem about the architecture. The ATF string
    verification is the live example: it grounds the border claim, not
    the epistemic conservation law."""
    return {"mechanism": mechanism,
            "instance_verified": instance_verified,
            "claimed_law": claimed_law,
            "law_proven": False,
            "licensed": (f"the specific claim, under the reported "
                         f"corpus/hash workflow"),
            "reason": "E_INSTANCE_IS_NOT_THEOREM",
            "note": "a successful instance of the mechanism is not a "
                    "theorem about the architecture"}


def corpus_status() -> dict:
    """Honest access state for this seat."""
    return {"corpus": "ATF_DESK_BOOK_1900",
            "reachable_from_this_seat": False,
            "held_by": "local corpus/runtime lane",
            "machinery_ready": True,
            "claims_made_about_corpus_content": None,
            "law": "the run against real specimens must execute where "
                   "the corpus is; nothing here claims to have read "
                   "it"}


def next_corpus_role() -> dict:
    """Per ruling: 1851 becomes validation, not expansion."""
    return {"corpus": "1851",
            "role": "OUT_OF_DISTRIBUTION_VALIDATION",
            "not": "collection_expansion",
            "sequence": "ATF 1900 --indub--> K_hat --test--> 1851",
            "precondition": "T-INDUB-01 returns SUPPORTED or HOLD; a "
                            "REFUTED grammar has nothing to validate"}


def selection_is_not_promotion(winner: str, benchmark_score: float
                               ) -> dict:
    """A candidate may win the benchmark and remain a CLAIM.
    K_{t+1} >_predictive K_t does not entail E(K_{t+1}) > E(K_t):
    model improvement and epistemic promotion are orthogonal."""
    return {"selected": winner, "score": benchmark_score,
            "epistemic_phase": "claim",
            "promoted": False,
            "reason": "E_SELECTION_IS_NOT_PROMOTION",
            "law": "search may be arbitrarily powerful while the "
                   "promotion seam stays small and deterministic"}


# ── the audit correction ────────────────────────────────────────────────

def grammar_space(specimens: tuple) -> dict:
    """G(p) = {g : g ~> p}. Inverse reconstruction is NON-UNIQUE, and
    the first version of this module got it wrong: it returned a
    single K_hat, which hallucinates a unique historical production
    process. Several grammars generate the same specimens and differ
    only in what they predict BEYOND them.

        g1 ~> p  and  g2 ~> p  does not entail  g1 = g2

    Three canonical candidates are enumerated per family:
      LITERAL        exact, zero generalization, zero compression
      PER_PATTERN    generalize within a pattern (the indub default)
      GLOBAL_PRODUCT generalize across all patterns — maximal
                     compression, maximal over-generation
    Over-generation is reported, never hidden: it is the measure of
    how much history a grammar would invent."""
    if not specimens:
        raise ValueError("E_NO_SPECIMENS")
    obs = _triples(specimens)
    patterns = sorted({p for p, _, _ in obs})
    sizes = sorted({s for _, s, _ in obs})
    states = sorted({st for _, _, st in obs})

    literal = {"rules": [], "literals": sorted(obs)}
    per_pattern = indub(specimens)["K_hat"]
    global_product = {"rules": [{"rule_id": "R::*", "pattern": "*",
                                 "patterns": patterns,
                                 "sizes": sizes, "states": states,
                                 "form": "PRODUCT"}], "literals": []}

    cands = []
    for name, k in (("LITERAL", literal),
                    ("PER_PATTERN", per_pattern),
                    ("GLOBAL_PRODUCT", global_product)):
        gen = generate(k)
        k_size = len(k["rules"]) + len(k["literals"])
        cands.append({
            "grammar_id": name,
            "k_size": k_size,
            "covers_observed": obs <= gen,
            "over_generation": len(gen - obs),
            "compression": round(1 - k_size / len(obs), 6)})

    consistent = [c for c in cands if c["covers_observed"]]
    return {"G_of_p": cands,
            "consistent_with_observation": [c["grammar_id"]
                                            for c in consistent],
            "n_consistent": len(consistent),
            "unique": len(consistent) == 1,
            "law": "recover a SPACE of candidate explanations; a "
                   "single reconstruction presented as the historical "
                   "process is laundering"}


def select_unique(space: dict, discriminating_evidence: bool) -> dict:
    """Collapsing G(p) to one grammar requires evidence that
    ELIMINATES the rivals. Without it the honest output is
    UNDERDETERMINED — naming a winner would convert a modelling
    choice into a historical claim."""
    if space["n_consistent"] > 1 and not discriminating_evidence:
        return {"selected": None, "verdict": "UNDERDETERMINED",
                "reason": "E_NON_UNIQUE_RECONSTRUCTION",
                "survivors": space["consistent_with_observation"],
                "law": "g1 ~> p and g2 ~> p does not entail g1 = g2; "
                       "picking one without discriminating evidence "
                       "is historical laundering"}
    return {"selected": space["consistent_with_observation"][0]
                        if space["consistent_with_observation"] else None,
            "verdict": "DETERMINED" if discriminating_evidence
                       else "SINGLETON"}


def reconstructible_is_not_used(p: str, reconstructible: bool) -> dict:
    """The invariant that keeps reconstruction out of history:

        Reconstructible(p)  does not entail  HistoricallyUsed(p)

    distinct from Generable -> HistoricallyObserved: that one is
    about what the catalogue afforded, this one about what our own
    inference machinery can rebuild. Our ability to rebuild a
    specimen is a fact about US, not about the past."""
    return {"specimen": p,
            "reconstructible": reconstructible,
            "historically_used": None,
            "reason": "E_RECONSTRUCTION_IS_NOT_HISTORY",
            "law": "reconstructibility is a property of the inference "
                   "machinery, not evidence about production"}


def completion_is_not_validation(run: str, exit_code: int) -> dict:
    """The swarm reported exit code 0. That licenses 'the run
    completed' and nothing else — not convergence, not a validated
    grammar, not an admitted result."""
    return {"run": run, "exit_code": exit_code,
            "completed": exit_code == 0,
            "grammar_validated": False,
            "licensed": "the run completed",
            "reason": "E_COMPLETION_IS_NOT_VALIDATION",
            "next": ("inspect outputs for convergence, competing "
                     "grammars, reconstruction accuracy, and "
                     "epistemic over-promotion")}


def instance_is_not_theorem(mechanism: str, instance_verified: bool,
                            claimed_law: str) -> dict:
    """One mechanism firing successfully licenses a claim about THAT
    instance, never a theorem about the architecture. The ATF string
    verification is the live example: it grounds the border claim, not
    the epistemic conservation law."""
    return {"mechanism": mechanism,
            "instance_verified": instance_verified,
            "claimed_law": claimed_law,
            "law_proven": False,
            "licensed": (f"the specific claim, under the reported "
                         f"corpus/hash workflow"),
            "reason": "E_INSTANCE_IS_NOT_THEOREM",
            "note": "a successful instance of the mechanism is not a "
                    "theorem about the architecture"}


def corpus_status() -> dict:
    """Honest access state for this seat."""
    return {"corpus": "ATF_DESK_BOOK_1900",
            "reachable_from_this_seat": False,
            "held_by": "local corpus/runtime lane",
            "machinery_ready": True,
            "claims_made_about_corpus_content": None,
            "law": "the run against real specimens must execute where "
                   "the corpus is; nothing here claims to have read "
                   "it"}


def next_corpus_role() -> dict:
    """Per ruling: 1851 becomes validation, not expansion."""
    return {"corpus": "1851",
            "role": "OUT_OF_DISTRIBUTION_VALIDATION",
            "not": "collection_expansion",
            "sequence": "ATF 1900 --indub--> K_hat --test--> 1851",
            "precondition": "T-INDUB-01 returns SUPPORTED or HOLD; a "
                            "REFUTED grammar has nothing to validate"}
