"""
cso_identity_contract.py — Executable Python contract for CSO Identity Laws V1
NON_SOVEREIGN · NO_SHIP · PROPOSAL
authority: NONE · mutation_rights: NONE · ledger_effect: NONE

Implements the 6 laws from docs/specs/CSO_IDENTITY_AND_NAMESPACE_RULES_V1.md.
Each law is a pure function. No side effects. No I/O.

Law 1: Identity Determinism       — id = H(namespace || canonical(payload))
Law 2: Namespace Isolation        — same local_id, different namespace → different object
Law 3: Immutability               — payload change → new object, never mutation
Law 4: Provenance Completeness    — chain must exist and every event must be receipted
Law 5: Federation Rule            — GlobalID = H(namespace || local_hash)
Law 6: Replay Identity Stability  — same events → same graph hash

Failure semantics: Φ(S, x) → ACCEPT | REJECT | DEGRADE | QUARANTINE
"""

import hashlib
import json
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# ── Exceptions ────────────────────────────────────────────────────────────────

class IdentityContractViolation(Exception):
    """A CSO identity law was violated."""

class NamespaceContractViolation(IdentityContractViolation):
    """Law 2: namespace isolation breached."""

class ImmutabilityContractViolation(IdentityContractViolation):
    """Law 3: in-place mutation attempted."""

class ProvenanceContractViolation(IdentityContractViolation):
    """Law 4: provenance chain missing or incomplete."""

class FederationContractViolation(IdentityContractViolation):
    """Law 5: cross-namespace identity merge without explicit bridge."""

class ReplayDivergenceViolation(IdentityContractViolation):
    """Law 6: same event sequence produced different graph hash."""


# ── Canonical serialization (shared by all laws) ──────────────────────────────

def _normalize_str(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def canonicalize(obj: Any) -> str:
    """
    C(payload): stable_sort(keys) + NFC(strings) + no whitespace outside strings.
    Timestamps are NOT in the canonical domain — omit them before calling.
    """
    if isinstance(obj, dict):
        return "{" + ",".join(
            f"{json.dumps(_normalize_str(k))}:{canonicalize(v)}"
            for k, v in sorted(obj.items())
        ) + "}"
    if isinstance(obj, list):
        return "[" + ",".join(canonicalize(i) for i in obj) + "]"
    if isinstance(obj, str):
        return json.dumps(_normalize_str(obj))
    return json.dumps(obj)


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


# ── Law 1: Identity Determinism ───────────────────────────────────────────────

def law_1_identity_determinism(namespace: str, payload: dict) -> str:
    """
    id(o) = H(namespace || C(payload))
    Identity is a pure function of namespace + canonical payload. Always.
    Invariant: same (namespace, payload) → same id. Different payload → different id.
    """
    canonical = canonicalize(payload)
    return _sha256(f"{namespace}|{canonical}")


# ── Law 2: Namespace Isolation ────────────────────────────────────────────────

def law_2_namespace_isolation(ns_a: str, local_id: str, ns_b: str) -> bool:
    """
    (ns_a, local_id) ≢ (ns_b, local_id) when ns_a ≠ ns_b.
    Returns True if the two global_ids are distinct (they must be when namespaces differ).
    Raises NamespaceContractViolation if called with ns_a == ns_b (not an isolation check).
    """
    if ns_a == ns_b:
        raise NamespaceContractViolation(
            f"Both namespaces are '{ns_a}' — this is not a cross-namespace check."
        )
    return f"{ns_a}/{local_id}" != f"{ns_b}/{local_id}"


def make_global_id(namespace: str, local_id: str) -> str:
    """global_id = namespace/local_id (separator: /)"""
    return f"{namespace}/{local_id}"


# ── Law 3: Immutability ───────────────────────────────────────────────────────

def law_3_immutability_check(
    existing_hash: str,
    new_payload: dict,
    namespace: str,
    local_id: str = "__check__",
) -> bool:
    """
    payload' ≠ payload ⟹ id' ≠ id (mutation is structurally impossible).
    Returns True if the new payload produces a different hash (correct: new object).
    Returns False if the new payload produces the same hash (same content — idempotent no-op).
    Never raises: this is a pure check, not an enforcement gate.
    """
    new_hash = law_1_identity_determinism(namespace, new_payload)
    return new_hash != existing_hash


# ── Law 4: Provenance Completeness ────────────────────────────────────────────

def law_4_provenance_check(provenance: dict) -> str:
    """
    Returns 'ADMIT' or 'QUARANTINE'.
    QUARANTINE if: chain absent, chain empty, or any event missing receipt_hash.
    ADMIT if: chain non-empty and every event carries a receipt_hash.
    """
    chain = provenance.get("chain", [])
    if not chain:
        return "QUARANTINE"
    for event in chain:
        if not event.get("receipt_hash"):
            return "QUARANTINE"
    return "ADMIT"


# ── Law 5: Federation Rule ────────────────────────────────────────────────────

def law_5_federation_global_id(namespace: str, local_hash: str) -> str:
    """
    GlobalID = H(namespace || local_hash)
    Cross-system identity requires explicit bridging, not hash-equality merge.
    """
    return _sha256(f"{namespace}|{local_hash}")


def make_bridge_relation(
    ns_a: str, id_a: str, ns_b: str, id_b: str, receipt: str
) -> dict:
    """
    Explicit BRIDGE_RELATION — the only admissible federation link.
    Both namespace origins and a receipt are mandatory.
    """
    if not receipt:
        raise FederationContractViolation("BRIDGE_RELATION requires a receipt.")
    return {
        "type": "BRIDGE",
        "ns_a": ns_a,
        "id_a": id_a,
        "ns_b": ns_b,
        "id_b": id_b,
        "receipt": receipt,
    }


# ── Law 6: Replay Identity Stability ─────────────────────────────────────────

def law_6_replay_stability(
    events: list,
    replay_fn: Callable[[list], Any],
    project_hash_fn: Optional[Callable[[Any], str]] = None,
) -> bool:
    """
    Replay(events) twice → same graph hash. No exceptions.
    If project_hash_fn is None, falls back to repr-based hash (for testing).
    Raises ReplayDivergenceViolation on mismatch.
    """
    g1 = replay_fn(events)
    g2 = replay_fn(events)

    if project_hash_fn is not None:
        h1 = project_hash_fn(g1)
        h2 = project_hash_fn(g2)
    else:
        h1 = _sha256(repr(sorted(str(g1))))
        h2 = _sha256(repr(sorted(str(g2))))

    if h1 != h2:
        raise ReplayDivergenceViolation(
            f"Replay divergence detected: {h1[:16]} ≠ {h2[:16]}"
        )
    return True


# ── Failure semantics: Φ(S, x) ───────────────────────────────────────────────

ADMIT = "ACCEPT"
REJECT = "REJECT"
QUARANTINE = "QUARANTINE"
DEGRADE = "DEGRADE"

_STATUS = {ADMIT, REJECT, QUARANTINE, DEGRADE}


@dataclass
class AdmissionResult:
    status: str      # ACCEPT | REJECT | QUARANTINE | DEGRADE
    global_id: str
    reason: str
    hash: Optional[str] = None


def admit_cso(
    namespace: str,
    local_id: str,
    payload: dict,
    receipts: list,
    provenance: dict,
    existing_graph: Optional[dict] = None,  # global_id → hash
) -> AdmissionResult:
    """
    Φ(S, x) — total function over all inputs.
    Returns AdmissionResult with status ACCEPT | REJECT | QUARANTINE | DEGRADE.
    Never raises (fails closed → REJECT).
    """
    try:
        gid = make_global_id(namespace, local_id)

        # Receipt gate
        if not receipts:
            return AdmissionResult(REJECT, gid, "NO RECEIPT = NO CLAIM")

        # Namespace gate
        if not namespace or "/" in namespace:
            return AdmissionResult(REJECT, gid, "Namespace missing or malformed")

        # Provenance gate
        prov_status = law_4_provenance_check(provenance)
        if prov_status == "QUARANTINE":
            return AdmissionResult(QUARANTINE, gid, "Provenance chain incomplete or unreceipeted")

        # Compute hash
        h = law_1_identity_determinism(namespace, payload)

        if existing_graph is not None:
            existing_hash = existing_graph.get(gid)

            if existing_hash is not None:
                if existing_hash == h:
                    # Duplicate — idempotent no-op
                    return AdmissionResult(ADMIT, gid, "Duplicate — idempotent no-op", h)
                else:
                    # Same global_id, different hash — mutation attempt
                    return AdmissionResult(REJECT, gid, "Mutation attempt: payload changed, same global_id", h)

        return AdmissionResult(ADMIT, gid, "Valid", h)

    except Exception as exc:
        return AdmissionResult(REJECT, "__unknown__", f"EVAL_ERROR: {exc}")
