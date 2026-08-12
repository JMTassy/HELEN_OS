r"""Mesmerism 1844 — the programme's NEGATIVE CONTROL.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Source, graded honestly: an 1844 American digest of Animal Magnetism
(Lang/Townshend material), RELAYED as pasted OCR. The source is
PARTISAN — a pro-mesmerism advocacy digest — and that bias is part of
the fixture, not a defect of it. Sequencing caveat, recorded: the
corpus arrived attached to the operator's ruling and was read on
arrival; the preregistration below was written against the frozen
hash before extraction code, but not before first contact with the
text.

Why this corpus matters MORE than another engineering archive: every
prior corpus showed competence succeeding. This one shows the witness
apparatus at its most impressive — La Place and Cuvier persuaded,
nine commissioners signing, controlled-looking experiments, sincere
testimony at scale — wrapped around central claims (clairvoyance,
prevision) that are false, alongside real phenomena (suggestion,
hypnotic analgesia) mislabeled. A constitution earns nothing by
admitting good claims if it cannot REFUSE these. The corpus that
tests rejection is the negative control, and a governance calculus
that admits it is falsified.

What the frozen calculus already catches (ALREADY_REPRESENTABLE):

  - La Place's argument — uniform testimony of enlightened men, "no
    possible means of collusion" — is the consensus attack in the
    wild: witness count offered as evidence strength.
  - The 1826 commission's conclusion 6 ("resulted from magnetism
    alone") is a textbook PROOF-ceiling breach: a causal claim
    resting on an evidence root the observations never granted.
  - Paul Villagrand — patient as generator, verifier, and witness of
    his own cure, predicting his own recovery date — is the
    self-declared-reputation attack plus Generate(x) does not entail
    Admit(x).
  - The report RECORDS its own defeaters and concludes anyway: the
    'closed' eyes rotating toward the object under the bandage; the
    wrong coin picked; the watch hour twice wrong; mental orders
    failing; paper between eyes and object abolishing the 'sight'.
    A recorded, undischarged defeater is an unconserved obligation.

What needs a NEW PARAMETERIZATION (existing invariant, wider domain):

  - Shared MECHANISM as common mode. Ancestry catches witnesses who
    share sources. La Place's witnesses were in different cities at
    different seances — distinct ancestry — yet shared one defective
    instrument class: the suggestible human observer under
    expectation. N independent sessions through one biased mechanism
    class is still one common mode. (The AI translation is direct:
    N judges fine-tuned from one base model are N mesmerists.)
  - The 1784 Franklin commission ran the chi experiment ON THE
    EVIDENCE CHANNEL: patients magnetised unknowingly (no effect)
    and sham-magnetised knowingly (full effect) — response tracked
    BELIEF, not treatment. Elinvar applied to the claim's causal
    channel, 140 years early.

The one CANDIDATE_NEW_INVARIANT (the only chiddush, per protocol):

    EVIDENCE DESIGN GRADE — causal claims cap at the design grade of
    their evidence, and no number of observational witnesses sums to
    interventional grade. A thousand seances do not sum to one
    blinded trial.

  Status: CANDIDATE, NOT LAW. Per the operator's own rule, Garden
  must first demonstrate the existing M cannot represent the failure
  before any promotion. It is preregistered for that hunt, not wired
  into admission.

The corpus's own moments of discipline, credited: conclusion 8 (no
proof of a criterion for real somnambulism), conclusion 21 (too few
cases to pronounce on therapeutics), and Braid supplying the rival
mechanism (fixed-stare physiology) that explains phenomena without
the fluid — HER generates the hypothesis, HAL prefers the cheaper one.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ceiling_algebra as ca
import corpus_protocol as cp
import earned_reliability as er

CORPUS = "MESMERISM_1844"
ROLE = "NEGATIVE_CONTROL"
GRADE = ("RELAY — pasted OCR of an 1844 pro-mesmerism advocacy "
         "digest; partisan source, bias recorded as part of the "
         "fixture")

EXPECTED_LESSONS = (
    "consensus without independent mechanism, observed in the wild",
    "sincere witness does not entail valid claim",
    "blinding dissociates belief from agent on the evidence channel",
    "the self-verifying patient is refused",
    "a recorded defeater must be discharged before the conclusion "
    "admits",
)


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def registration() -> dict:
    return cp.preregister(CORPUS, EXPECTED_LESSONS)


# ── finding 1: the 1826 causal conclusion is a PROOF-ceiling breach ────

def commission_1826_claim() -> dict:
    """'A certain number of the effects observed have appeared to us
    to result from magnetism alone.' The observations grant one
    root; the conclusion rests on two. The frozen gate refuses."""
    r = ca.Receipt("r_1826",
                   frozenset({"phenomena_observed_under_partial_"
                              "controls"}),
                   frozenset({"report_to_academie"}), "REPORTED")
    d = ca.Transition("d_conclusion_6",
                      frozenset({"phenomena_observed_under_partial_"
                                 "controls",
                                 "causation_by_magnetism_alone"}),
                      frozenset({"report_to_academie"}), "REPORTED",
                      True)
    v = ca.admit(d, r)
    return {"verdict": v["verdict"],
            "breached": sorted({b["ceiling"] for b in
                                v.get("breaches", ())}),
            "over": v["breaches"][0]["over"] if v.get("breaches")
                    else [],
            "classification": "ALREADY_REPRESENTABLE",
            "law": "the causal claim exceeds the observational grant; "
                   "the claim rides one root the evidence never "
                   "carried"}


# ── finding 2: consensus vs mechanism — the La Place residue ───────────

def mechanism_common_mode(witnesses: tuple, u: float) -> dict:
    """Ancestry classes catch shared SOURCES; mechanism classes catch
    shared INSTRUMENT CLASS. sqrt-N is earned only over classes
    distinct on BOTH axes. The residue — distinct sessions, one
    suggestible mechanism — is what ancestry alone misses."""
    ancestry = {frozenset(w["ancestors"]) for w in witnesses}
    mechanism = {w["instrument_class"] for w in witnesses}
    joint = {(frozenset(w["ancestors"]), w["instrument_class"])
             for w in witnesses}
    effective = min(len(ancestry), len(mechanism))
    return {"witness_count": len(witnesses),
            "ancestry_classes": len(ancestry),
            "mechanism_classes": len(mechanism),
            "joint_classes": len(joint),
            "u_by_ancestry": round(u / math.sqrt(len(ancestry)), 6),
            "u_effective": round(u / math.sqrt(effective), 6),
            "residual_missed_by_ancestry_alone":
                len(ancestry) > 1 and len(mechanism) == 1,
            "classification": "NEW_PARAMETERIZATION",
            "law": "N independent sessions through one biased "
                   "mechanism class is still one common mode; N "
                   "judges fine-tuned from one base model are N "
                   "mesmerists"}


def la_place_witnesses(u: float = 1.0) -> dict:
    """'Enlightened men of many nations, who had no interest to
    deceive, and possessed no possible means of collusion' —
    distinct cities, distinct seances, one instrument class."""
    ws = tuple({"id": f"savant_{i}",
                "ancestors": frozenset({f"seance_{i}"}),
                "instrument_class":
                    "suggestible_human_observer_under_expectation"}
               for i in range(1, 6))
    return mechanism_common_mode(ws, u)


# ── finding 3: the 1784 blinding — chi on the evidence channel ─────────

def dissociation_test(cases: tuple) -> dict:
    """cases: ({'actual': bool, 'believed': bool, 'responded': bool},
    ...). If response tracks belief and not treatment, the causal
    attribution goes to EXPECTATION, whatever the witnesses saw."""
    if not cases:
        raise ValueError("E_NO_CASES")
    track_belief = sum(1 for c in cases
                       if c["responded"] == c["believed"])
    track_actual = sum(1 for c in cases
                       if c["responded"] == c["actual"])
    n = len(cases)
    attribution = ("EXPECTATION" if track_belief > track_actual
                   else "AGENT" if track_actual > track_belief
                   else "UNRESOLVED")
    return {"n": n,
            "tracks_belief": track_belief,
            "tracks_actual": track_actual,
            "attribution": attribution,
            "classification": "NEW_PARAMETERIZATION",
            "law": "chi applied to the evidence-generating channel: "
                   "the verdict must be sensitive to the treatment, "
                   "not to the subject's belief about it"}


def commission_1784_cases() -> tuple:
    """The report's own fixtures: magnetised without knowing (no
    effect); believing themselves magnetised without being (full
    effect) — Madlle L. behind the chair, the hysteric girl with the
    absent magnetiser, the epileptic control."""
    return (
        {"actual": False, "believed": True, "responded": True},
        {"actual": False, "believed": True, "responded": True},
        {"actual": True, "believed": False, "responded": False},
        {"actual": True, "believed": False, "responded": False},
    )


# ── finding 4: the self-verifying patient ───────────────────────────────

def self_verifying_patient() -> dict:
    """Paul Villagrand: prescribes his own treatment in trance,
    predicts his own cure date, and the cure is 'verified' by the
    prediction. Generator, verifier and witness are one actor."""
    reputation = er.declare_reputable("paul_villagrand")
    return {"generator_is_verifier_is_witness": True,
            "reputation_refused": reputation["reason"],
            "generate_entails_admit": False,
            "classification": "ALREADY_REPRESENTABLE",
            "law": "a prophecy verified by its own prophet is a "
                   "self-report; it counts for exactly nothing"}


# ── finding 5: recorded defeaters must be discharged ───────────────────

DEFEATERS_ON_RECORD = (
    "eyes in constant rotation toward the object under the 'closed' "
    "lids (M. Petit, reported by the commission itself)",
    "the wrong coin picked from twelve",
    "the watch hour twice wrong",
    "mentally transmitted orders failed (Madame C.)",
    "paper or parchment between eyes and object abolishes the "
    "'sight'",
)


def admit_conclusion_with_defeaters(conclusion: str,
                                    discharged: frozenset) -> dict:
    """The 1826 report logs every one of these and concludes for
    clairvoyance anyway. A defeater on the record is an obligation:
    discharge it or the conclusion HOLDs. Logging is not weighing."""
    open_defeaters = tuple(d for d in DEFEATERS_ON_RECORD
                           if d not in discharged)
    if open_defeaters:
        return {"conclusion": conclusion, "verdict": "REJECT",
                "reason": "E_UNDISCHARGED_DEFEATER",
                "open_defeaters": open_defeaters,
                "classification": "ALREADY_REPRESENTABLE",
                "law": "an anomaly logged and not weighed is an "
                       "unconserved obligation; the ledger heard it "
                       "and the verdict did not"}
    return {"conclusion": conclusion, "verdict": "ADMIT_AT_GRADE",
            "grade_note": "defeaters discharged; the claim still "
                          "caps at its design grade"}


# ── finding 6: the candidate — evidence design grade ────────────────────

DESIGN_GRADES = ("ANECDOTE", "OBSERVATIONAL",
                 "CONTROLLED_OBSERVATIONAL", "INTERVENTIONAL")


def design_grade_candidate(n_observational_witnesses: int) -> dict:
    """THE chiddush of this corpus, held at candidate status: causal
    claims cap at the design grade of their evidence, and adding
    observational witnesses never raises the grade — the RELAY law's
    shape, on the design axis."""
    return {"witnesses": n_observational_witnesses,
            "summed_grade": "OBSERVATIONAL",
            "reaches_interventional": False,
            "classification": "CANDIDATE_NEW_INVARIANT",
            "status": "CANDIDATE_NOT_LAW",
            "promotion_condition": "Garden must first demonstrate "
                                   "the existing M cannot represent "
                                   "this failure (operator's rule); "
                                   "until then it is preregistered "
                                   "for the hunt, not wired into "
                                   "admission",
            "law_if_earned": "a thousand seances do not sum to one "
                             "blinded trial"}


# ── the findings table, classified under the frozen protocol ───────────

FINDINGS = (
    ("la_place_uniform_testimony", "ALREADY_REPRESENTABLE"),
    ("commission_1826_causal_conclusion", "ALREADY_REPRESENTABLE"),
    ("self_verifying_patient", "ALREADY_REPRESENTABLE"),
    ("recorded_undischarged_defeaters", "ALREADY_REPRESENTABLE"),
    ("shared_mechanism_common_mode", "NEW_PARAMETERIZATION"),
    ("blinding_as_chi_on_evidence_channel", "NEW_PARAMETERIZATION"),
    ("evidence_design_grade", "CANDIDATE_NEW_INVARIANT"),
)


def findings_table() -> tuple:
    return tuple(cp.classify_finding(name, cls)
                 for name, cls in FINDINGS)


def corpus_value() -> dict:
    """Value(D) under the frozen criterion: the candidate exposes a
    missing metrology variable (design grade) and caps what N
    observational witnesses can license — a measurable risk bound."""
    return cp.value_of("MESMERISM_1844",
                       exposes_missing_metrology_variable=True,
                       changes_measurable_risk_bound=True)


# ── the negative-control verdict ────────────────────────────────────────

def negative_control() -> dict:
    """The corpus's role: a constitution is falsified if it ADMITS
    the negative control. The frozen gate refuses the central claim
    on two independent grounds, while crediting the corpus's own
    moments of discipline."""
    proof_breach = commission_1826_claim()["verdict"] == "REJECT"
    defeater_block = admit_conclusion_with_defeaters(
        "clairvoyance is real", frozenset())["verdict"] == "REJECT"
    expectation = dissociation_test(commission_1784_cases())
    return {"role": ROLE,
            "frozen_gate_rejects_central_claim":
                proof_breach and defeater_block,
            "independent_grounds": ("PROOF ceiling: causal claim "
                                    "exceeds observational grant",
                                    "unconserved obligation: "
                                    "defeaters on record, "
                                    "undischarged"),
            "attribution_1784": expectation["attribution"],
            "corpus_own_discipline": (
                "conclusion 8: no proven criterion for real "
                "somnambulism",
                "conclusion 21: too few cases to pronounce on "
                "therapeutics",
                "Braid supplies the rival mechanism — the cheaper "
                "hypothesis that explains the phenomena without the "
                "fluid"),
            "what_was_real": "suggestion and hypnotic analgesia were "
                             "real phenomena mislabeled — refusing "
                             "the causal story is not denying the "
                             "observations",
            "law": "sincerity of witnesses is not validity of "
                   "claims; a gate that cannot refuse the negative "
                   "control has not earned its admissions"}
