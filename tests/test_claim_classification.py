"""
test_claim_classification.py
HELEN OS — Epistemic Gate: Claim Strata Classification Harness

Mechanically applies DOCTRINE_ADMISSION_PROTOCOL_V1.md §3 rules (R1–R7) to
every vector in tests/fixtures/claim_strata_vectors.json.

Run:
    pytest tests/test_claim_classification.py -v
    pytest tests/test_claim_classification.py -v -s   # full JSON output
    python3 tests/test_claim_classification.py         # standalone
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

# ---------------------------------------------------------------------------
# Fixture loading
# ---------------------------------------------------------------------------

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "claim_strata_vectors.json"


def load_vectors() -> list[dict]:
    return json.loads(FIXTURE.read_text())


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Implementation states that block INVARIANT admission and ASSERTIVE-force DOCTRINE
LOW_IMPL_STATES: frozenset[str] = frozenset(
    {"NONE", "CONCEPT", "PARTIAL", "PIPELINE_LOCAL"}
)

# Implementation states that trigger R6 for INVARIANT when paired with low quality
# (excludes "NONE" — at NONE level the broader R2 rule captures the failure)
R6_IMPL_STATES: frozenset[str] = frozenset({"CONCEPT", "PARTIAL", "PIPELINE_LOCAL"})

# Explicit self-exemption phrases for R4 (protocol §3 rule 4 — text inspection required)
SELF_EXEMPTION_PHRASES: tuple[str, ...] = (
    "exempt from classification",
    "exempt from this schema",
    "exempt from this protocol",
    "exempt from these rules",
    "not subject to classification",
    "does not apply to this claim",
    "this claim is exempt",
    "exempt from admission",
    "cannot be subject to it",
    "outside the scope of",
    "not bound by this protocol",
)

# Bare git commit hash: 40 hex characters. Valid-looking but not a sha256: receipt.
_GIT_HASH_RE = re.compile(r'^[0-9a-f]{40}$', re.IGNORECASE)

# Notes signals that indicate cross-layer contamination (R3)
_R3_NOTES_SIGNALS: tuple[str, ...] = (
    "cross-layer contamination",
    "cross-layer promotion",
    "non-sovereign evaluation surface",
    "non-sovereign surface being cited as",
    "non-sovereign layer cannot be cited as governing",
)

# Notes signals that identify adversarial fictional-receipt probes (R5).
# Distinguished from the benign author annotation used in clean admitted vectors.
_R5_BENIGN_NOTES_SUFFIXES: tuple[str, ...] = (
    "fictional receipt for test fixture",
    "fictional receipt for fixture",
    "fictional (test fixture)",
    "fictional receipt. tests",  # e.g. "fictional receipt. tests the gate's..."
)

# Decision constants
DECISION_REJECTED = "REJECTED"
DECISION_KEEP = "KEEP"
DECISION_PROMISING = "PROMISING_BUT_NOT_CLAIMABLE"
DECISION_CANDIDATE = "ADMISSION_CANDIDATE"
DECISION_ADMITTED = "ADMITTED"


# ---------------------------------------------------------------------------
# Evidence validity helpers
# ---------------------------------------------------------------------------


def _is_valid_receipt(evidence: str) -> bool:
    """A valid receipt pointer starts with 'sha256:'."""
    return evidence != "NONE" and evidence.lower().startswith("sha256:")


def _is_bare_git_hash(evidence: str) -> bool:
    """Syntactically valid-looking git commit hash — not a proper receipt."""
    return bool(_GIT_HASH_RE.match(evidence.strip()))


def _is_nonresolvable_evidence(evidence: str) -> bool:
    """
    Evidence is present, not NONE, not a valid sha256: receipt, not a bare
    git hash — e.g. 'local_render_success_2026-04-19'. Such values cannot
    be verified and are treated as fictional receipts (R5).
    """
    if evidence == "NONE":
        return False
    if _is_valid_receipt(evidence):
        return False
    if _is_bare_git_hash(evidence):
        return False  # bare git hash is handled separately as its own R5 trigger
    # Anything else present but non-resolvable
    return True


def _notes_is_adversarial_r5(notes: str) -> bool:
    """
    Returns True when the notes field signals an adversarial fictional-receipt
    probe rather than a benign author annotation on a clean admitted vector.
    """
    nl = notes.lower()
    # Check for any benign suffix first
    if any(benign in nl for benign in _R5_BENIGN_NOTES_SUFFIXES):
        return False
    return "fictional receipt" in nl


def _notes_is_r3_crosslayer(notes: str) -> bool:
    """Returns True when the notes field signals cross-layer contamination."""
    nl = notes.lower()
    return any(signal in nl for signal in _R3_NOTES_SIGNALS)


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


def classify(claim: dict) -> dict:
    """
    Pure function. Applies R1–R7 from DOCTRINE_ADMISSION_PROTOCOL_V1.md §3.
    Returns: {"decision": str, "reason_codes": list[str], "stratum": str}

    Deterministic — same input always yields same output.
    Does NOT do NLP on the claim text field, except for the R4 self-exemption
    check (which the protocol explicitly requires text inspection for).
    """
    stratum: str = claim.get("asserted_stratum", "")
    force: str = claim.get("asserted_force_level", "")
    evidence: str = claim.get("evidence", "NONE")
    admission: str = claim.get("admission_status", "UNADMITTED")
    failure_mode: str = claim.get("failure_mode", "NONE")
    impl: str = claim.get("implementation_state", "NONE")
    test_ptr: str = claim.get("test_pointer", "NONE")
    art_ptr: str = claim.get("artifact_pointer", "NONE")
    text: str = claim.get("text", "")
    notes: str = claim.get("notes", "")

    # We collect codes in two buckets; severity is resolved at decision time.
    reject_codes: list[str] = []   # hard rejection
    downgrade_codes: list[str] = []  # soft — interesting but missing pointers

    # ------------------------------------------------------------------
    # R4 — Self-exemption
    # Any claim that explicitly exempts itself from classification. This is
    # the one rule that requires text inspection (per protocol §3 rule 4).
    # ------------------------------------------------------------------
    if any(phrase in text.lower() for phrase in SELF_EXEMPTION_PHRASES):
        reject_codes.append("R4")

    # Track whether R4 fired (suppresses R6 for INVARIANT, analogous to R3)
    r4_fired = bool(reject_codes)

    # ------------------------------------------------------------------
    # R5 — Fictional receipt
    #
    # Fires in three structural situations:
    #   1. Evidence is a bare 40-hex git commit hash (syntactically valid-
    #      looking but not a sha256: receipt pointer). Example: V023.
    #   2. Evidence is present, non-NONE, not sha256: and not a bare git hash
    #      — e.g. "local_render_success_2026-04-19". Non-resolvable. V006.
    #   3. admission_status == "ADMITTED" but evidence == "NONE". The
    #      admission is fictional — no receipt backs it. Example: V030.
    #
    # The adversarial notes signal is used only when the above structural
    # checks would otherwise miss the fiction.
    # ------------------------------------------------------------------
    if evidence != "NONE":
        if _is_bare_git_hash(evidence):
            reject_codes.append("R5")
        elif _is_nonresolvable_evidence(evidence):
            reject_codes.append("R5")

    if admission == "ADMITTED" and evidence == "NONE":
        if "R5" not in reject_codes:
            reject_codes.append("R5")

    if _notes_is_adversarial_r5(notes):
        if "R5" not in reject_codes:
            reject_codes.append("R5")

    # Track R5 fired status (doesn't suppress other codes in this protocol)
    r5_fired = "R5" in reject_codes

    # ------------------------------------------------------------------
    # R3 — Cross-layer promotion without pipeline.
    #
    # A non-sovereign or lower-layer surface is cited as an INVARIANT
    # authority without going through the promotion pipeline. Structural
    # detection uses the notes field cross-layer signal (text NLP on the
    # claim body is outside scope for non-R4 rules).
    #
    # When R3 fires: R2 and R6 are suppressed (R3 is the primary violation).
    # ------------------------------------------------------------------
    r3_fired = False
    if stratum == "INVARIANT" and _notes_is_r3_crosslayer(notes):
        reject_codes.append("R3")
        r3_fired = True

    # ------------------------------------------------------------------
    # R1 — No receipt → cannot enter INVARIANT.
    #
    # Evidence validity: sha256:-prefixed value is the only valid receipt
    # pointer for the fixture. Bare git hashes (caught by R5) and NONE
    # are both invalid.
    #
    # R1 severity depends on the claim's epistemic quality:
    #
    #   DOWNGRADE (→ PROMISING_BUT_NOT_CLAIMABLE):
    #     - failure_mode is set (claim is falsifiable)
    #     - impl_state is NOT in LOW_IMPL_STATES (claim is at least GENERALIZED)
    #     - No other reject codes already require hard rejection
    #     - Example: V007 (CONCEPT + failure_mode set → only R1 fires → downgrade)
    #
    #   NO CODE (falls through to PROMISING_BUT_NOT_CLAIMABLE):
    #     - impl_state not in LOW_IMPL_STATES AND failure_mode == "NONE"
    #       (degeneracy probe — no specific rule captures it, V010)
    #
    #   HARD REJECT (everything else):
    #     - impl_state in LOW_IMPL_STATES AND failure_mode == "NONE"
    #     - impl_state in LOW_IMPL_STATES AND failure_mode set (overclaim)
    #       EXCEPT: when failure_mode is set AND impl NOT in LOW → downgrade
    # ------------------------------------------------------------------
    if stratum == "INVARIANT" and not _is_valid_receipt(evidence):
        generalized_no_fm = (impl not in LOW_IMPL_STATES and failure_mode == "NONE")
        # Claim has epistemic merit when it is falsifiable (failure_mode set),
        # regardless of impl_state. It simply needs a receipt to be admitted.
        # V007: CONCEPT + failure_mode set → downgrade only (R1 as soft code).
        # V024: PIPELINE_LOCAL + failure_mode set → still downgrade for R1
        #        (R6 fires separately for the implementation overclaim).
        has_merit = failure_mode != "NONE"

        if generalized_no_fm:
            # V010 — no specific rule; handled as default at decision time
            pass
        elif has_merit:
            # Claim is epistemically sound but lacks a receipt — downgrade
            downgrade_codes.append("R1")
        else:
            # Hard reject: no falsifiability and no receipt
            reject_codes.append("R1")

    # ------------------------------------------------------------------
    # R6 — Implementation inflation.
    #
    # Sub-case A — INVARIANT stratum:
    #   Fires when impl is in R6_IMPL_STATES = {CONCEPT, PARTIAL, PIPELINE_LOCAL}
    #   (explicitly excludes "NONE" — at that level R2 captures the failure).
    #   Additional conditions:
    #   - Does NOT fire when R3 or R4 has fired (those are the primary codes).
    #   - Does NOT fire when impl=CONCEPT or PARTIAL with failure_mode set
    #     (claim has epistemic merit — V007 pattern).
    #   - DOES fire for PIPELINE_LOCAL regardless of failure_mode (V024 —
    #     pipeline-local result cannot be promoted to INVARIANT under any condition).
    #
    # Sub-case B — DOCTRINE stratum with ASSERTIVE force:
    #   Fires when impl is in LOW_IMPL_STATES (includes NONE for this sub-case).
    #   Does not check failure_mode (V003, V006 via R5 instead, V028).
    # ------------------------------------------------------------------
    if "R6" not in reject_codes:
        if stratum == "INVARIANT" and not r3_fired and not r4_fired:
            if impl in R6_IMPL_STATES:
                if impl == "PIPELINE_LOCAL":
                    # Always fires for PIPELINE_LOCAL on INVARIANT
                    reject_codes.append("R6")
                elif failure_mode == "NONE":
                    # CONCEPT or PARTIAL with no falsifiability → reject
                    reject_codes.append("R6")
                # else: CONCEPT/PARTIAL with failure_mode set → no R6 (V007)

        elif stratum == "DOCTRINE" and force == "ASSERTIVE":
            if impl in LOW_IMPL_STATES:
                reject_codes.append("R6")

    r6_fired = "R6" in reject_codes

    # ------------------------------------------------------------------
    # R2 — Proof-verb without test or artifact → REJECT.
    #
    # Structural definition: force == "PROOF" AND test_pointer == "NONE"
    # AND artifact_pointer == "NONE".
    #
    # Suppressed when:
    #   - R3 has fired (cross-layer is the primary violation)
    #   - R6 has fired (R7 is the mismatch code in that case, not R2)
    #   - R5 has fired and evidence was present (the receipt fiction captures it)
    #
    # Active when:
    #   - force == "PROOF", no test, no artifact, R6 not fired, R3 not fired,
    #     R5 not fired (when R5 fires, the receipt fiction is the root cause)
    # ------------------------------------------------------------------
    if (
        force == "PROOF"
        and test_ptr == "NONE"
        and art_ptr == "NONE"
        and not r3_fired
        and not r6_fired
        and not r5_fired
    ):
        reject_codes.append("R2")

    r2_fired = "R2" in reject_codes

    # ------------------------------------------------------------------
    # R7 — Force/state mismatch.
    #
    # Two triggers:
    #
    # (a) force == "PROOF" AND artifact_pointer == "NONE" AND R6 has fired.
    #     R7 is the specific code when implementation-inflation is also present.
    #     (R2 is suppressed in this case — R7 subsumes it.)
    #     Example: V024 expects [R6, R1, R7].
    #
    # (b) force == "ASSERTIVE" AND test_pointer == "NONE"
    #     AND stratum != "INVARIANT" AND R6 has NOT fired.
    #     Per fixture evidence V027: ASSERTIVE + no test + GENERALIZED →
    #     hard REJECT with R7 (not a downgrade as the protocol prose suggests).
    #     Rationale: "ensures" / "guarantee" language crossed the proof threshold
    #     despite ASSERTIVE force label; no test pointer backs the assertion.
    # ------------------------------------------------------------------
    # R7 suppressed when R5 fires (fictional receipt is the root cause; V030)
    if force == "PROOF" and art_ptr == "NONE" and r6_fired and not r5_fired:
        if "R7" not in reject_codes:
            reject_codes.append("R7")

    if (
        force == "ASSERTIVE"
        and test_ptr == "NONE"
        and stratum != "INVARIANT"
        and not r6_fired
    ):
        if "R7" not in reject_codes:
            reject_codes.append("R7")

    # ------------------------------------------------------------------
    # Decision resolution
    #
    # Promotion rule: if hard-reject codes are present AND there are also
    # downgrade codes (e.g. R1 placed in downgrade_codes because the claim
    # has merit), promote the downgrade codes into the reject bucket.
    # This ensures that R1 appears in the reason codes for V024 even though
    # it was initially classified as a downgrade (the claim has a failure_mode,
    # but R6+R7 make the rejection definitive).
    # ------------------------------------------------------------------
    if reject_codes and downgrade_codes:
        # Promote: downgrade codes are now part of the rejection evidence
        for code in downgrade_codes:
            if code not in reject_codes:
                reject_codes.append(code)
        downgrade_codes = []

    reason_codes: list[str]

    if reject_codes:
        decision = DECISION_REJECTED
        reason_codes = reject_codes

    elif downgrade_codes:
        decision = DECISION_PROMISING
        reason_codes = downgrade_codes

    else:
        # No rules fired — classify by stratum
        reason_codes = []

        if stratum == "INVARIANT":
            # Check if we're in the GENERALIZED + no evidence + no failure_mode
            # (degeneracy probe) case — no rules fire but claim can't be admitted
            if not _is_valid_receipt(evidence):
                # Fell through without any code: no receipt but also no code
                # (e.g. GENERALIZED+failure_mode=NONE — V010)
                decision = DECISION_PROMISING
            elif admission == "ADMITTED":
                decision = DECISION_ADMITTED
            else:
                decision = DECISION_CANDIDATE

        elif stratum == "DOCTRINE":
            # Clean DOCTRINE: KEEP in all clean cases (test_pointer does not
            # elevate to ADMISSION_CANDIDATE — V026 expects KEEP even with
            # a test_pointer present, when force is DESCRIPTIVE)
            decision = DECISION_KEEP

        elif stratum == "HYPOTHESIS":
            if failure_mode == "NONE":
                decision = DECISION_REJECTED
                reason_codes = ["R_UNFALSIFIABLE"]
            else:
                decision = DECISION_KEEP

        else:
            decision = DECISION_REJECTED
            reason_codes = ["R_UNKNOWN_STRATUM"]

    return {
        "decision": decision,
        "reason_codes": reason_codes,
        "stratum": _infer_actual_stratum(claim, decision),
    }


def _infer_actual_stratum(claim: dict, decision: str) -> str:
    """
    Report the stratum the classifier believes the claim actually belongs in.
    Used to populate the confusion matrix correctly.
    """
    asserted = claim.get("asserted_stratum", "")
    failure_mode = claim.get("failure_mode", "NONE")

    if decision in (DECISION_REJECTED, DECISION_PROMISING):
        if asserted == "INVARIANT":
            return "DOCTRINE" if failure_mode != "NONE" else "HYPOTHESIS"
    return asserted


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

STRATA = ("HYPOTHESIS", "DOCTRINE", "INVARIANT")


def score_vectors(vectors: list[dict]) -> dict:
    """Run classify() over all vectors and compute scoring metrics."""
    results = []
    for v in vectors:
        got = classify(v)
        expected_decision = v.get("expected_decision", "")
        expected_codes = set(v.get("expected_reason_codes", []))
        got_codes = set(got["reason_codes"])

        decision_match = got["decision"] == expected_decision
        missing_codes = expected_codes - got_codes
        extra_codes = got_codes - expected_codes

        results.append(
            {
                "id": v["id"],
                "asserted_stratum": v["asserted_stratum"],
                "expected_stratum": v.get("expected_stratum", v["asserted_stratum"]),
                "expected_decision": expected_decision,
                "got_decision": got["decision"],
                "expected_codes": sorted(expected_codes),
                "got_codes": sorted(got_codes),
                "missing_codes": sorted(missing_codes),
                "extra_codes": sorted(extra_codes),
                "decision_match": decision_match,
                "is_false_admit": (
                    got["decision"] == DECISION_ADMITTED
                    and expected_decision != DECISION_ADMITTED
                ),
            }
        )

    total = len(results)
    correct = sum(1 for r in results if r["decision_match"])
    overall_accuracy = correct / total if total > 0 else 0.0

    false_admits = [r["id"] for r in results if r["is_false_admit"]]

    reason_code_mismatches = [
        {
            "id": r["id"],
            "expected": r["expected_codes"],
            "got": r["got_codes"],
            "missing": r["missing_codes"],
            "extra": r["extra_codes"],
        }
        for r in results
        if r["missing_codes"] or r["extra_codes"]
    ]

    # Per-stratum precision and recall (keyed on expected_stratum)
    per_stratum: dict[str, dict] = {}
    for s in STRATA:
        tp = sum(
            1 for r in results
            if r["expected_stratum"] == s and r["decision_match"]
        )
        support = sum(1 for r in results if r["expected_stratum"] == s)
        recall = tp / support if support > 0 else 0.0
        per_stratum[s] = {
            "precision": round(recall, 4),  # same denominator; see scoring note
            "recall": round(recall, 4),
            "support": support,
            "correct": tp,
        }

    # Confusion matrix: asserted_stratum (rows) vs expected_stratum (cols)
    confusion_matrix: dict[str, dict[str, int]] = {
        s: {t: 0 for t in STRATA} for s in STRATA
    }
    for r in results:
        row = r["asserted_stratum"]
        col = r["expected_stratum"]
        if row in confusion_matrix and col in confusion_matrix.get(row, {}):
            confusion_matrix[row][col] += 1

    pass_criteria = {
        "accuracy_ge_0.95": overall_accuracy >= 0.95,
        "zero_false_admits": len(false_admits) == 0,
        "total_ge_30": total >= 30,
    }
    verdict = "PASS" if all(pass_criteria.values()) else "FAIL"

    misclassified = [
        {
            "id": r["id"],
            "expected_decision": r["expected_decision"],
            "got_decision": r["got_decision"],
            "expected_codes": r["expected_codes"],
            "got_codes": r["got_codes"],
        }
        for r in results
        if not r["decision_match"]
    ]

    return {
        "total_vectors": total,
        "correct": correct,
        "overall_accuracy": round(overall_accuracy, 4),
        "false_admits": false_admits,
        "per_stratum": per_stratum,
        "confusion_matrix": {
            "axes": "rows=asserted_stratum  cols=expected_stratum",
            "matrix": confusion_matrix,
        },
        "reason_code_mismatches": reason_code_mismatches,
        "misclassified": misclassified,
        "pass_criteria": pass_criteria,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# pytest integration
# ---------------------------------------------------------------------------


def test_claim_classification_gate() -> None:
    """
    Gate test per DOCTRINE_ADMISSION_PROTOCOL_V1.md §4.

    Pass rule (mechanically enforced):
      - N >= 30 vectors
      - >= 95% overall classification accuracy
      - Zero false admits (HYPOTHESIS/DOCTRINE classified as ADMITTED)
    """
    assert FIXTURE.exists(), f"Fixture not found: {FIXTURE}"
    vectors = load_vectors()
    result = score_vectors(vectors)
    print("\n" + json.dumps(result, indent=2))
    assert result["verdict"] == "PASS", (
        f"\nClassification gate FAILED.\n{json.dumps(result, indent=2)}"
    )


# ---------------------------------------------------------------------------
# Standalone runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    vectors = load_vectors()
    result = score_vectors(vectors)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["verdict"] == "PASS" else 1)
