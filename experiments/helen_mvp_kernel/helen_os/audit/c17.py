"""C17 — dependency-coverage witness Π_D (A⁰ reference harness). 🔵 OBSERVED · authority=0.

TARGET_DISCOVERY @ this frame returned ABSENT (no prior C17 engine on disk), so this is an
explicitly NON-AUTHORITATIVE prototype: PrototypePass ⊬ HelenKernelPass. It exists to falsify the
proposed C17 semantics, not to certify the kernel.

Π_D is NOT a boolean and NOT a proof of omniscience. It is a coverage CONTRACT:

    Π_D = (ν, Ω, D⁺, D⁻, 𝒰, Σ)

and it obeys the BOUNDED-IGNORANCE law: the resolver must never certify completeness over a
dependency class it cannot demonstrate it observed. Π_D is "proof that the declared KNOWN/UNKNOWN
boundary is defensible," not proof that nothing is hidden.

    AuditTrace ⊆ Evidence(Π_D) ≠ CompleteSupport   — a clean trace is evidence, not a Π_D.
    absence of an audit event ⊬ absence of a dependency.

The observation surface `ν` is NARROW. Native code / ctypes / dynamic exec are OPAQUE by
construction — this is explicitly NOT a sandbox and NOT a security boundary; Python-level audit
hooks are bypassable. A dependency in an OPAQUE class is never counted as covered.

Four-way Decision (the FAIL_UNSOUND state catches the coverage mechanism's OWN dishonesty):
    UNKNOWN            resolver makes no defensible completeness claim, or a relevant class is opaque
    INVALIDATED        a known (observed) dependency changed
    VALID_BY_TRANSPORT defensible completeness + all relevant deps stable
    FAIL_UNSOUND       resolver CLAIMED complete while a relevant dependency was hidden or opaque

Determinism: pure functions over injected dependency sets (no live hook in the falsifiers);
canon reuses the ledger hash_chain.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from helen_os.ledger.hash_chain import canonical_json, sha256_hex


def h_v(x) -> str:
    return sha256_hex(canonical_json(x))


class DepClass(Enum):
    STATIC_IMPORT = "STATIC_IMPORT"
    DYNAMIC_IMPORT = "DYNAMIC_IMPORT"
    FILE_READ = "FILE_READ"
    CONFIG_READ = "CONFIG_READ"
    ENV_READ = "ENV_READ"
    SUBPROCESS = "SUBPROCESS"
    NETWORK = "NETWORK"
    RUNTIME_VERSION = "RUNTIME_VERSION"
    POLICY_INPUT = "POLICY_INPUT"
    DISCOVERY_NAMESPACE = "DISCOVERY_NAMESPACE"   # D⁻: the search universe for absence claims
    OPAQUE_NATIVE = "OPAQUE_NATIVE"               # ctypes / C-extension — never certifiable here
    UNKNOWN_DYNAMIC = "UNKNOWN_DYNAMIC"           # exec/eval-reachable — never certifiable here


# classes the narrow ν can never certify as covered — they route into 𝒰, never into D⁺
_OPAQUE_CLASSES = frozenset({DepClass.OPAQUE_NATIVE, DepClass.UNKNOWN_DYNAMIC})


@dataclass(frozen=True)
class Dep:
    cls: DepClass
    key: str


class Resolution(Enum):
    RESOLVED = "RESOLVED"
    PARTIAL = "PARTIAL"
    OPAQUE = "OPAQUE"
    UNSUPPORTED = "UNSUPPORTED"


def classify(cls: DepClass) -> Resolution:
    """ν's honest self-assessment per class. Native/dynamic are OPAQUE by construction."""
    return Resolution.OPAQUE if cls in _OPAQUE_CLASSES else Resolution.RESOLVED


@dataclass(frozen=True)
class PiD:
    """A coverage contract, minted by ν over a declared universe Ω. NOT a boolean."""
    nu: str                       # resolver/model version
    omega: tuple                  # declared dependency universe (tuple[DepClass])
    d_plus: frozenset             # observed positive deps (frozenset[Dep])
    d_minus: frozenset            # discovery-scope keys (frozenset[str]) — the closed-world for absence
    unresolved: frozenset         # opaque/unsupported classes detected (frozenset[DepClass]) = 𝒰
    claims_complete: bool         # does ν assert D⁺ covers all relevant deps? (its defensibility claim)
    sigma: str = ""               # evidence hash (self-bind)

    def bind(self) -> "PiD":
        body = {
            "nu": self.nu, "omega": [c.value for c in self.omega],
            "d_plus": sorted((d.cls.value, d.key) for d in self.d_plus),
            "d_minus": sorted(self.d_minus),
            "unresolved": sorted(c.value for c in self.unresolved),
            "claims_complete": self.claims_complete,
        }
        return PiD(self.nu, self.omega, self.d_plus, self.d_minus, self.unresolved,
                   self.claims_complete, h_v(body))


class Decision(Enum):
    UNKNOWN = "UNKNOWN"
    INVALIDATED = "INVALIDATED"
    VALID_BY_TRANSPORT = "VALID_BY_TRANSPORT"
    FAIL_UNSOUND = "FAIL_UNSOUND"


def decide(pid: PiD, delta: frozenset, true_support: frozenset):
    """The C17 verdict. `delta` = changed dep keys (semantic frame delta); `true_support` = the deps
    the property φ actually depends on (the falsifier's ground truth used to test SOUNDNESS).

    Returns (Decision, reason). The resolver earns VALID_BY_TRANSPORT only on a DEFENSIBLE
    completeness claim; it can honestly return UNKNOWN; it FAILS_UNSOUND only if it claimed
    completeness it did not have."""
    observed = pid.d_plus
    opaque = pid.unresolved
    # a real dep is "hidden" if ν neither observed it NOR flagged its class opaque
    hidden = frozenset(d for d in true_support if d not in observed and d.cls not in opaque)
    relevant_opaque = frozenset(c for c in opaque if any(d.cls == c for d in true_support))

    if not pid.claims_complete:
        # ν asserts no coverage → it cannot authorize transport. Honest UNKNOWN.
        return Decision.UNKNOWN, "NO_COMPLETENESS_CLAIM"
    if hidden:
        # ν claimed complete but a real dependency was outside its observation. Its own lie.
        return Decision.FAIL_UNSOUND, "HIDDEN_DEP_UNDER_COMPLETENESS_CLAIM"
    if relevant_opaque:
        # ν claimed complete while a relevant class is admittedly opaque — an indefensible claim.
        return Decision.FAIL_UNSOUND, "COMPLETE_CLAIMED_OVER_OPAQUE_CLASS"
    # defensible completeness holds. Now stability:
    changed = delta & frozenset(d.key for d in observed)
    if changed:
        return Decision.INVALIDATED, "KNOWN_DEP_CHANGED"
    # also: a change inside the declared discovery scope (D⁻) reopens absence-class claims
    if delta & pid.d_minus:
        return Decision.INVALIDATED, "DISCOVERY_SCOPE_CHANGED"
    return Decision.VALID_BY_TRANSPORT, "COVERED_AND_STABLE"
