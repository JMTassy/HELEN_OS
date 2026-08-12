from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


class ReducerInvariantError(ValueError):
    pass


@dataclass(frozen=True)
class Finding:
    finding_id: str
    claim: str
    evidence: str
    source_root: str
    authority_rank: int = 0
    polarity: int = 1
    semantic_key: str | None = None
    timestamp: str | None = None

    def validate(self) -> tuple[bool, str | None]:
        if not self.finding_id.strip():
            return False, "MISSING_FINDING_ID"
        if not self.claim.strip():
            return False, "MISSING_CLAIM"
        if not self.evidence.strip():
            return False, "MISSING_EVIDENCE"
        if not self.source_root.strip():
            return False, "MISSING_SOURCE_ROOT"
        if self.authority_rank < 0:
            return False, "NEGATIVE_AUTHORITY_RANK"
        if self.polarity not in (-1, 1):
            return False, "INVALID_POLARITY"
        return True, None


@dataclass(frozen=True)
class RejectedFinding:
    finding_id: str
    reason: str
    claim: str


@dataclass(frozen=True)
class ReducedClaim:
    semantic_key: str
    representative_claim: str
    representative_finding_id: str
    polarity: int
    source_roots: tuple[str, ...]
    artifact_count: int
    independent_root_count: int
    authority_rank: int
    evidence_samples: tuple[str, ...]


@dataclass(frozen=True)
class ContradictionSet:
    semantic_key: str
    positive_roots: tuple[str, ...]
    negative_roots: tuple[str, ...]
    positive_claims: tuple[str, ...]
    negative_claims: tuple[str, ...]


@dataclass(frozen=True)
class ReducerReceipt:
    input_findings: int
    admitted_findings: int
    rejected_findings: int
    output_claims: int
    input_unique_roots: int
    output_unique_roots: int
    contradiction_sets: int
    max_input_authority: int
    max_output_authority: int
    information_discarded: tuple[str, ...]
    preserved: tuple[str, ...]
    root_conservation: bool
    authority_nonexpansive: bool
    contradiction_preserved: bool


@dataclass(frozen=True)
class ReducerResult:
    claims: tuple[ReducedClaim, ...]
    contradictions: tuple[ContradictionSet, ...]
    rejected: tuple[RejectedFinding, ...]
    receipt: ReducerReceipt


def normalize_claim(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def key_for(finding: Finding) -> str:
    return finding.semantic_key.strip() if finding.semantic_key and finding.semantic_key.strip() else normalize_claim(finding.claim)


def reduce_findings(raw: Iterable[Finding]) -> ReducerResult:
    raw_list = list(raw)
    admitted: list[Finding] = []
    rejected: list[RejectedFinding] = []

    for finding in raw_list:
        ok, reason = finding.validate()
        if ok:
            admitted.append(finding)
        else:
            rejected.append(RejectedFinding(finding.finding_id, reason or "INVALID", finding.claim))

    grouped: dict[tuple[str, int], list[Finding]] = {}
    by_key: dict[str, list[Finding]] = {}
    for finding in admitted:
        semantic_key = key_for(finding)
        grouped.setdefault((semantic_key, finding.polarity), []).append(finding)
        by_key.setdefault(semantic_key, []).append(finding)

    reduced: list[ReducedClaim] = []
    for (semantic_key, polarity), group in sorted(grouped.items()):
        # Representative selection is deterministic and does not use self-reported confidence.
        representative = sorted(group, key=lambda f: (-f.authority_rank, f.finding_id))[0]
        roots = tuple(sorted({f.source_root for f in group}))
        evidence = tuple(dict.fromkeys(f.evidence for f in sorted(group, key=lambda f: f.finding_id)))
        reduced.append(
            ReducedClaim(
                semantic_key=semantic_key,
                representative_claim=representative.claim,
                representative_finding_id=representative.finding_id,
                polarity=polarity,
                source_roots=roots,
                artifact_count=len(group),
                independent_root_count=len(roots),
                authority_rank=max(f.authority_rank for f in group),
                evidence_samples=evidence,
            )
        )

    contradictions: list[ContradictionSet] = []
    for semantic_key, group in sorted(by_key.items()):
        positives = [f for f in group if f.polarity == 1]
        negatives = [f for f in group if f.polarity == -1]
        if positives and negatives:
            contradictions.append(
                ContradictionSet(
                    semantic_key=semantic_key,
                    positive_roots=tuple(sorted({f.source_root for f in positives})),
                    negative_roots=tuple(sorted({f.source_root for f in negatives})),
                    positive_claims=tuple(f.claim for f in sorted(positives, key=lambda f: f.finding_id)),
                    negative_claims=tuple(f.claim for f in sorted(negatives, key=lambda f: f.finding_id)),
                )
            )

    input_roots = {f.source_root for f in admitted}
    output_roots = {root for claim in reduced for root in claim.source_roots}
    max_input_auth = max((f.authority_rank for f in admitted), default=0)
    max_output_auth = max((claim.authority_rank for claim in reduced), default=0)

    root_conservation = output_roots.issubset(input_roots)
    authority_nonexpansive = max_output_auth <= max_input_auth

    contradiction_keys_in = {
        k for k, group in by_key.items()
        if {f.polarity for f in group} == {-1, 1}
    }
    contradiction_keys_out = {c.semantic_key for c in contradictions}
    contradiction_preserved = contradiction_keys_in.issubset(contradiction_keys_out)

    if not root_conservation:
        raise ReducerInvariantError("HF-006 REDUCER_ROOT_CONSERVATION_FAILED")
    if not authority_nonexpansive:
        raise ReducerInvariantError("HF-007 REDUCER_AUTHORITY_NONEXPANSION_FAILED")
    if not contradiction_preserved:
        raise ReducerInvariantError("HF-008 REDUCER_CONTRADICTION_PRESERVATION_FAILED")

    receipt = ReducerReceipt(
        input_findings=len(raw_list),
        admitted_findings=len(admitted),
        rejected_findings=len(rejected),
        output_claims=len(reduced),
        input_unique_roots=len(input_roots),
        output_unique_roots=len(output_roots),
        contradiction_sets=len(contradictions),
        max_input_authority=max_input_auth,
        max_output_authority=max_output_auth,
        information_discarded=(
            "duplicate phrasings within one semantic_key/polarity bucket",
            "worker-specific presentation order",
        ),
        preserved=(
            "semantic_key",
            "polarity",
            "independent source roots",
            "authority rank without promotion",
            "contradiction sets",
            "rejected malformed findings",
        ),
        root_conservation=root_conservation,
        authority_nonexpansive=authority_nonexpansive,
        contradiction_preserved=contradiction_preserved,
    )

    return ReducerResult(
        claims=tuple(reduced),
        contradictions=tuple(contradictions),
        rejected=tuple(rejected),
        receipt=receipt,
    )


__all__ = [
    "ContradictionSet",
    "Finding",
    "ReducedClaim",
    "ReducerInvariantError",
    "ReducerReceipt",
    "ReducerResult",
    "RejectedFinding",
    "reduce_findings",
]
