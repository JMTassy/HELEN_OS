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
COMPRESSION_FLOOR = 0.5      # K_hat must be <= half the observations


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
    """Expand K_hat into the specimen set it predicts."""
    out = set(tuple(t) for t in k_hat.get("literals", ()))
    for r in k_hat.get("rules", ()):
        for s in r["sizes"]:
            for st in r["states"]:
                out.add((r["pattern"], s, st))
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
    compresses = fit["compression"] >= COMPRESSION_FLOOR

    if coverage < 1.0:
        verdict, demoted = "REFUTED", "DESCRIPTIVE_TAXONOMY"
    elif not compresses:
        verdict, demoted = "HOLD", None
    else:
        verdict, demoted = "SUPPORTED", None

    return {"verdict": verdict,
            "demoted_to": demoted,
            "heldout_coverage": coverage,
            "predicted_heldout": hit,
            "missed_heldout": miss,
            "compression": fit["compression"],
            "compresses": compresses,
            "k_size": fit["k_size"],
            "unresolved": fit["U"],
            "law": "a grammar must predict what it never saw AND cost "
                   "less than the list it replaces; predicting "
                   "without compressing is memorization and licenses "
                   "no grammar claim"}


# ── the audit correction ────────────────────────────────────────────────

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
