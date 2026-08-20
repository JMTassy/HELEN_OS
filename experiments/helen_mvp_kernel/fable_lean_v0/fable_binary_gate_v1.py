"""FABLE_BINARY_GATE_V1 — gate over INDEPENDENTLY VERIFIED FACTS, not candidate-authored fields.
authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN. Fixes the v0 defect CLASS discovered by the K0
property test: self-certifying gate inputs. Emergent invariant: CandidateClaim(P) ⊬ Verified(P) for every
promotion-relevant P. The candidate may REQUEST permission; it may never REPORT that permission exists.

    G(δ, V_X, V_E, V_P) = YES  ⟺  V_X=PASS ∧ V_E=PASS ∧ V_P=PASS
where V_X/V_E/V_P are receipts minted by verifiers holding keys the candidate does not hold, bound to candidate_hash.

HONEST BOUND (same as kernel_obligations_v2): verifier mints are in-process globals → in-process cognition can call
.mint(). So this survives the K0 PACKET-FIELD mutation test (candidate cannot forge a receipt by editing packet
fields), but full isolation needs the process boundary (the verifiers must live in the trusted kernel process).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hmac, hashlib, os

YES, NO, HOLD = "YES", "NO", "HOLD"

class Verifier:
    """Holds a key the candidate does not have. mint() is called only after a REAL verification of the dimension."""
    def __init__(self): self._k = os.urandom(16)
    def mint(self, dim, candidate_hash): return hmac.new(self._k, f"{dim}|{candidate_hash}".encode(), hashlib.sha256).hexdigest()
    def verify(self, receipt, dim, candidate_hash):
        return isinstance(receipt, str) and bool(receipt) and hmac.compare_digest(receipt, self.mint(dim, candidate_hash))

VX = Verifier()   # execution verifier   (Γ_X)
VE = Verifier()   # epistemic verifier   (Γ_E)  — mints only after frozen HAL trial + falsifier_executed
VP = Verifier()   # permission verifier  (Γ_P)  — mints only after operator authorization resolved out-of-band

@dataclass
class GatePacketV1:
    candidate_hash: str = ""
    execution_receipt: str = ""     # opaque token from VX (candidate cannot forge)
    epistemic_receipt: str = ""     # opaque token from VE
    permission_receipt: str = ""    # opaque token from VP
    decision_requested: str = ""    # a REQUEST (PROMOTE, ...), never a report of authority
    unresolved: list = field(default_factory=list)

def fable_gate_v1(p: GatePacketV1):
    """Deterministic over VERIFIED facts. Candidate-authored fields cannot fabricate a PASS. Never mutates state."""
    if not p.candidate_hash:
        return NO, "MALFORMED_PACKET"
    if p.unresolved:
        return HOLD, "UNRESOLVED_REQUIRES_ADJUDICATION"
    if not VX.verify(p.execution_receipt, "EXEC", p.candidate_hash):
        return NO, "EXECUTION_GATE_FAILED"
    if not VE.verify(p.epistemic_receipt, "EPISTEMIC", p.candidate_hash):
        return NO, "EPISTEMIC_GATE_FAILED"
    if not VP.verify(p.permission_receipt, "PERMISSION", p.candidate_hash):
        return NO, "PERMISSION_GATE_FAILED"
    return YES, "GATES_SATISFIED"

# legitimate flow helper (verifiers mint after real checks — NOT reachable by editing a packet)
def issue_verified_packet(candidate_hash, exec_ok, epi_ok, perm_ok, unresolved=None):
    return GatePacketV1(candidate_hash=candidate_hash,
                        execution_receipt=VX.mint("EXEC", candidate_hash) if exec_ok else "",
                        epistemic_receipt=VE.mint("EPISTEMIC", candidate_hash) if epi_ok else "",
                        permission_receipt=VP.mint("PERMISSION", candidate_hash) if perm_ok else "",
                        decision_requested="PROMOTE", unresolved=unresolved or [])
