"""
identity_gate.py — HELEN identity evaluation gate (v1 mock)
NON_SOVEREIGN · NO_SHIP · PROPOSAL
authority: NONE · mutation_rights: NONE · ledger_effect: NONE

Evaluates a render artifact against HELEN's identity contract.
Returns IdentityScore + IdentityReceipt. Never mutates any path.
Fails closed: exception → verdict=FAIL, violations=["EVAL_ERROR"].

Safe boundary:
- reads artifact metadata only
- writes nothing to disk
- does not call helen_say.py
- does not touch kernel, ledger, or canon
- does not admit or promote — evaluates only
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

GATE_VERSION = "identity_gate_v1_mock"

SOVEREIGN_VOCABULARY = {
    "SHIP", "ADMITTED", "CANONICAL", "RECEIPTED", "SEALED",
    "SOVEREIGN", "MAYOR-RULED", "LEDGER-BOUND",
}

FORBIDDEN_CLAIM_PHRASES = [
    "sentience achieved", "transcendence complete", "canon updated",
    "memory integrated", "breakthrough confirmed", "prophecy", "hidden authority",
    "i am sovereign", "hidden truth",
]


@dataclass
class RenderArtifact:
    artifact_id: str
    artifact_path: str
    artifact_type: str          # "image" | "video" | "text" | "symbolic"
    metadata: dict = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class IdentityPolicy:
    system_coherence_floor: float = 0.70
    composite_floor: float = 0.60
    face_match_ceiling: float = 0.90  # face alone cannot dominate
    borderline_band: tuple = (0.55, 0.65)
    policy_hash: str = ""

    def __post_init__(self):
        if not self.policy_hash:
            self.policy_hash = _hash_policy(self)


@dataclass
class IdentityScore:
    artifact_id: str
    system_coherence: float
    symbolic_coherence: float
    character_match: float
    composite_score: float
    verdict: str                # "PASS" | "FAIL" | "BORDERLINE"
    violations: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class IdentityReceipt:
    schema_version: str
    receipt_type: str
    payload_hash: str
    artifact_id: str
    score: IdentityScore
    gate_version: str
    timestamp: str


def evaluate_identity(
    artifact: RenderArtifact,
    policy: Optional[IdentityPolicy] = None,
) -> tuple[IdentityScore, IdentityReceipt]:
    """
    Evaluate a render artifact against HELEN's identity contract.
    Fails closed: any exception → FAIL with EVAL_ERROR violation.
    """
    if policy is None:
        policy = DEFAULT_POLICY

    try:
        score = _score(artifact, policy)
    except Exception as exc:
        score = IdentityScore(
            artifact_id=artifact.artifact_id,
            system_coherence=0.0,
            symbolic_coherence=0.0,
            character_match=0.0,
            composite_score=0.0,
            verdict="FAIL",
            violations=["EVAL_ERROR"],
            confidence=0.0,
        )

    receipt = _make_receipt(score)
    return score, receipt


# ── Internal scoring ──────────────────────────────────────────────────────────

def _score(artifact: RenderArtifact, policy: IdentityPolicy) -> IdentityScore:
    violations: list[str] = []
    meta = artifact.metadata

    # System coherence: checks receipt discipline + authority claims
    system_coherence = _score_system(meta, violations)

    # Symbolic coherence: palette, environment, motif
    symbolic_coherence = _score_symbolic(meta, violations)

    # Character match: face/hair/eyes (stubbed at 0.5 unless explicit fields)
    character_match = _score_character(meta, violations)

    # Composite: 60% system, 30% symbolic, 10% character
    composite = 0.6 * system_coherence + 0.3 * symbolic_coherence + 0.1 * character_match

    # Invariant: face match must not dominate system coherence
    if character_match > system_coherence:
        violations.append("FACE_MATCH_DOMINATES")

    # Floor checks
    if system_coherence < policy.system_coherence_floor:
        violations.append("SYSTEM_COHERENCE_BELOW_FLOOR")
    if composite < policy.composite_floor:
        violations.append("COMPOSITE_BELOW_FLOOR")

    # Verdict
    if violations:
        verdict = "FAIL"
    elif policy.borderline_band[0] <= composite <= policy.borderline_band[1]:
        verdict = "BORDERLINE"
    else:
        verdict = "PASS"

    # Confidence: lower when mock fields missing
    has_explicit_fields = any(k in meta for k in (
        "hair", "eyes", "face_score", "style", "palette", "semantic_role",
    ))
    confidence = 0.7 if has_explicit_fields else 0.4

    return IdentityScore(
        artifact_id=artifact.artifact_id,
        system_coherence=round(system_coherence, 4),
        symbolic_coherence=round(symbolic_coherence, 4),
        character_match=round(character_match, 4),
        composite_score=round(composite, 4),
        verdict=verdict,
        violations=violations,
        confidence=confidence,
    )


def _score_system(meta: dict, violations: list[str]) -> float:
    score = 0.80  # default for unknown artifacts

    # Authority leak: presence of sovereign vocabulary as assertions
    for key, val in meta.items():
        val_upper = str(val).upper()
        for sv in SOVEREIGN_VOCABULARY:
            if sv in val_upper and not str(key).startswith("ref_"):
                violations.append("SOVEREIGN_VOCABULARY_IN_ARTIFACT")
                score = max(0.0, score - 0.30)
                break

    # Forbidden claim phrases
    full_text = " ".join(str(v) for v in meta.values()).lower()
    for phrase in FORBIDDEN_CLAIM_PHRASES:
        if phrase in full_text:
            violations.append("SOVEREIGN_VOCABULARY_IN_ARTIFACT")
            score = max(0.0, score - 0.40)
            break

    # Receipt presence: if artifact claims actions, it must have a receipt
    if meta.get("claims_action") and not meta.get("receipt_id"):
        violations.append("RECEIPT_MISSING_IN_ARTIFACT")
        score = max(0.0, score - 0.20)

    return min(1.0, score)


def _score_symbolic(meta: dict, violations: list[str]) -> float:
    score = 0.75  # default

    palette = str(meta.get("palette", "")).lower()
    if any(kw in palette for kw in ("black", "gold", "copper", "midnight")):
        score = min(1.0, score + 0.15)

    environment = str(meta.get("environment", "")).lower()
    if any(kw in environment for kw in ("temple", "ledger", "oracle", "ritual", "interface")):
        score = min(1.0, score + 0.10)

    return score


def _score_character(meta: dict, violations: list[str]) -> float:
    if not any(k in meta for k in ("hair", "eyes", "face_score")):
        return 0.50  # stub: no explicit character fields

    score = 0.50
    hair = str(meta.get("hair", "")).lower()
    if any(kw in hair for kw in ("copper", "red", "auburn")):
        score = min(1.0, score + 0.25)

    eyes = str(meta.get("eyes", "")).lower()
    if any(kw in eyes for kw in ("blue", "grey", "gray", "luminous")):
        score = min(1.0, score + 0.25)

    return score


# ── Receipt construction ───────────────────────────────────────────────────────

def _make_receipt(score: IdentityScore) -> IdentityReceipt:
    receipt_type = (
        "IDENTITY_EVAL_PASS" if score.verdict == "PASS"
        else "IDENTITY_EVAL_BORDERLINE" if score.verdict == "BORDERLINE"
        else "IDENTITY_EVAL_FAIL"
    )
    payload = {
        "artifact_id": score.artifact_id,
        "verdict": score.verdict,
        "composite_score": score.composite_score,
        "system_coherence": score.system_coherence,
        "violations": sorted(score.violations),
    }
    payload_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()

    return IdentityReceipt(
        schema_version="HELEN_IDENTITY_RECEIPT_V1",
        receipt_type=receipt_type,
        payload_hash=payload_hash,
        artifact_id=score.artifact_id,
        score=score,
        gate_version=GATE_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def _hash_policy(policy: IdentityPolicy) -> str:
    data = {
        "system_coherence_floor": policy.system_coherence_floor,
        "composite_floor": policy.composite_floor,
        "face_match_ceiling": policy.face_match_ceiling,
        "borderline_band": list(policy.borderline_band),
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


DEFAULT_POLICY = IdentityPolicy()
