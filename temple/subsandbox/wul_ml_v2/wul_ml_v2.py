"""
🧾 WUL-ML V2 MINIMAL CORE — TEMPLE SANDBOX · authority=NONE · CANON=FALSE
Compiler membrane MVP: whitelist morphisms + REJECT default + authority monotonicity.

Two independent judgments:
  1. Morphism legality:  (sources, target) ∉ E_LEGAL  ⇒ REJECT (forbidden coercion named).
  2. Authority monotonicity: A may rise 0→1 only across a B_Γ bridge — even if the
     whitelist itself is corrupted (extra_legal audit hook), authority cannot bootstrap.

ExternalTruth exists as a sort and is deliberately UNREACHABLE: no morphism may
name it as source or target. Receipt ≠ Attestation ≠ ExternalTruth.
"""

from typing import Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------- sorts

CORE_SORTS = frozenset({
    "GardenSeed", "Candidate", "WitnessedCandidate", "HALResult",
    "AdmissionDecision", "Capability", "Effect", "Receipt", "ReplayState",
    "ExternalTruth",
})

EXTENSION_SORTS = frozenset({"FailureReceipt", "Projection", "Diagnosis", "Consequence"})

SORTS = CORE_SORTS | EXTENSION_SORTS


def parse_sort(s: str) -> Tuple[str, Optional[str]]:
    """'AdmissionDecision[ADMIT]' -> ('AdmissionDecision', 'ADMIT'); 'Receipt' -> ('Receipt', None)."""
    if "[" in s and s.endswith("]"):
        base, tag = s[:-1].split("[", 1)
        return base, tag
    return s, None


# ---------------------------------------------------------------- legal morphisms
# Entry: (tuple of required source specs, target spec). A source spec is a
# (base, required_tag) pair; required_tag None matches any tag.
# 'Receipt*' (one-or-more receipts) is modelled by star_source below.

E_LEGAL: List[Tuple[Tuple[Tuple[str, Optional[str]], ...], str]] = [
    ((("GardenSeed", None),), "Candidate"),
    ((("Candidate", None),), "WitnessedCandidate"),
    ((("WitnessedCandidate", None),), "HALResult"),
    ((("WitnessedCandidate", None), ("HALResult", None)), "AdmissionDecision"),
    ((("AdmissionDecision", "ADMIT"),), "Capability"),
    ((("Capability", None), ("AdmissionDecision", "ADMIT")), "Effect"),
    ((("Effect", None),), "Receipt"),
]
STAR_MORPHISM = ("Receipt", "ReplayState")  # Receipt+ -> ReplayState

# Authority: can the sort participate in governed mutation?
A: Dict[str, int] = {s: 0 for s in SORTS}
for s in ("Capability", "Effect", "Receipt", "ReplayState"):
    A[s] = 1
A["ExternalTruth"] = 0  # outside governance entirely; unreachable regardless

# The only bridges across which authority may rise.
B_GAMMA = [((("AdmissionDecision", "ADMIT"),), "Capability")]

# ---------------------------------------------------------------- unreachability (import-time law)

_all_rule_sorts = set()
for _srcs, _tgt in E_LEGAL:
    _all_rule_sorts.add(_tgt)
    _all_rule_sorts.update(b for b, _ in _srcs)
_all_rule_sorts.update(STAR_MORPHISM)
assert "ExternalTruth" not in _all_rule_sorts, "ExternalTruth must stay unreachable"


# ---------------------------------------------------------------- typecheck

def _sources_match(rule_srcs, step_srcs) -> bool:
    if len(rule_srcs) != len(step_srcs):
        return False
    remaining = list(step_srcs)
    for base, tag in rule_srcs:
        hit = None
        for i, s in enumerate(remaining):
            sb, st = parse_sort(s)
            if sb == base and (tag is None or st == tag):
                hit = i
                break
        if hit is None:
            return False
        remaining.pop(hit)
    return True


def _is_legal(step_srcs: Sequence[str], target: str, extra_legal=None) -> bool:
    tb, _ = parse_sort(target)
    if tb == STAR_MORPHISM[1]:
        bases = [parse_sort(s)[0] for s in step_srcs]
        if len(bases) >= 1 and all(b == STAR_MORPHISM[0] for b in bases):
            return True
    for rule_srcs, rule_tgt in list(E_LEGAL) + list(extra_legal or []):
        if parse_sort(rule_tgt)[0] == tb and _sources_match(rule_srcs, step_srcs):
            return True
    return False


def _crosses_bridge(step_srcs: Sequence[str], target: str) -> bool:
    for rule_srcs, rule_tgt in B_GAMMA:
        if parse_sort(rule_tgt)[0] == parse_sort(target)[0] and _sources_match(rule_srcs, step_srcs):
            return True
    return False


def typecheck(program: List[dict], extra_legal=None) -> Tuple[str, List[str]]:
    """program: [{'from': ['SortA', 'SortB[TAG]'], 'to': 'SortC'}, ...]
    Returns ('ACCEPT'|'REJECT', reasons). Default is REJECT: anything not
    whitelisted is a forbidden coercion. Authority judgment is independent."""
    reasons: List[str] = []
    for step in program:
        srcs, tgt = step["from"], step["to"]
        for s in list(srcs) + [tgt]:
            if parse_sort(s)[0] not in SORTS:
                reasons.append(f"UNKNOWN SORT: {s}")
        arrow = f"{' + '.join(srcs)} -> {tgt}"
        if not _is_legal(srcs, tgt, extra_legal):
            reasons.append(f"FORBIDDEN COERCION: {arrow} (not in E_LEGAL; default = REJECT)")
            continue
        src_auth = max((A.get(parse_sort(s)[0], 0) for s in srcs), default=0)
        tgt_auth = A.get(parse_sort(tgt)[0], 0)
        if tgt_auth > src_auth and not _crosses_bridge(srcs, tgt):
            reasons.append(f"AUTHORITY BOOTSTRAP: {arrow} raises A outside B_Γ")
    return ("REJECT", reasons) if reasons else ("ACCEPT", [])
