"""NU_EXECUTION_EXHIBIT_V1 — the addressed Crystal Palace object.

NON_SOVEREIGN · authority=false · ledger_effect=none.

    A trace records what happened to be visible.
    An EXHIBIT records the conditions under which visibility was produced.
    A coverage witness determines what that visibility licenses us to say.

Five things that must never collapse:

    event != dependency != EXHIBIT != coverage verdict != transport

Laws implemented:

  ANTI-CIRCULARITY   H(Omega) is committed PRE-RUN. Every collector receipt
                     is stamped with that hash; a mismatch or a covered
                     surface outside the committed Omega is rejected
                     (the Texas Sharpshooter cannot draw the target after
                     the shots).

  CATALOGUE != JURY  The EXHIBIT has NO verdict field. `complete`, `pi_d`,
                     `verdict`, `authority`, `admit` are UNREPRESENTABLE —
                     the validator rejects them anywhere in I or C.
                     Judgment lives only in verify_coverage(), a pure
                     function the exhibit cannot call on itself.

  D- IS WITNESSED    A negative dependency is an EXECUTED discovery
                     obligation carrying a search receipt. Absence of an
                     event is never absence of a dependency: an entry in
                     discovery_minus without a receipt is rejected.

  UNOBSERVED => U    A relevant surface with no equipped collector lands
                     in the opacity manifest by DEFAULT. This is the
                     structural fix for the false-closure class the nu
                     adversaries demonstrated (os.stat silently dropping).

  DERIVE CLOSURE     There is no `closed` boolean. Run closure is DERIVED
                     from sequence integrity + a terminal event.

  id(E) = H(canon(E \\ id))    Identity binds the immutable observation
                     material and the observation contract, and ignores
                     downstream views/labels so a re-catalogued exhibit is
                     not new evidence.

Deterministic: sha256 over canonical JSON, no wall-time, no randomness.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

SCHEMA = "NU_EXECUTION_EXHIBIT_V1"

# Relevance of a surface to the property under evaluation.
REQUIRED = "required"
IRRELEVANT = "irrelevant"            # needs an irrelevance witness -> D-empty

# Fields that must NEVER appear anywhere in an exhibit: the exhibit is a
# catalogue, not a jury, and it carries no authority.
_UNREPRESENTABLE = frozenset({
    "complete", "closed", "pi_d", "verdict", "pass", "coverage_verdict",
    "authority", "admit", "valid_by_transport", "true_support",
})


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _h(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# ── the pre-run observation contract (anti-circularity) ─────────────────

@dataclass(frozen=True)
class ObservationContract:
    """Committed BEFORE the run. Omega is fixed here; the tracer cannot
    later redraw it around whatever it happened to see."""
    omega: tuple                      # ((surface_id, relevance, justification), ...)
    omega_hash: str

    @staticmethod
    def commit(surfaces: dict) -> "ObservationContract":
        """surfaces: {surface_id: relevance} or {surface_id: (relevance, why)}.
        Irrelevant surfaces MUST carry a justification (the irrelevance
        witness for D-empty)."""
        rows = []
        for sid in sorted(surfaces):
            v = surfaces[sid]
            relevance, why = (v if isinstance(v, tuple) else (v, ""))
            if relevance == IRRELEVANT and not why:
                raise ValueError(f"E_IRRELEVANCE_UNWITNESSED:{sid}")
            if relevance not in (REQUIRED, IRRELEVANT):
                raise ValueError(f"E_UNTYPED_RELEVANCE:{relevance}")
            rows.append((sid, relevance, why))
        rows = tuple(rows)
        return ObservationContract(omega=rows, omega_hash=_h(rows))

    def required(self) -> frozenset:
        return frozenset(s for s, r, _w in self.omega if r == REQUIRED)

    def irrelevant(self) -> frozenset:
        return frozenset(s for s, r, _w in self.omega if r == IRRELEVANT)

    def surfaces(self) -> frozenset:
        return frozenset(s for s, _r, _w in self.omega)


@dataclass(frozen=True)
class ExecutionEvent:
    seq: int
    surface: str
    detail: str


@dataclass(frozen=True)
class DiscoveryReceipt:
    """A WITNESSED search boundary: an executed obligation that bounds what
    could have happened on `surface` (e.g. a full dir traversal)."""
    surface: str
    method: str                       # e.g. "recursive_listdir", "ns_enumerate"
    result: str                       # what the search found (or "empty")
    omega_hash: str                   # stamped with the pre-run commitment


# ── the exhibit: catalogue only, NO verdict, NO authority, NO complete ──

@dataclass(frozen=True)
class NuExhibit:
    schema: str
    frame_manifest: dict              # F — interpreter + committed omega_hash
    event_manifest: tuple             # E — events, sequence-ordered
    dependency_plus: tuple            # D+ — positively witnessed surfaces
    discovery_minus: tuple            # D- — witnessed exclusions (with receipts)
    opacity_manifest: tuple           # U  — relevant surfaces left opaque
    coverage_manifest: dict           # Sigma — accounting, NOT a verdict
    merkle_root: str                  # integrity over events (!= completeness)
    exhibit_id: str = ""

    # NOTE what is absent: no `complete`, no `verdict`, no `pi_d`, no
    # `authority`. Those are structurally unrepresentable in this schema.

    def identity(self) -> str:
        """id(E) = H(canon(E \\ id)) — ignores exhibit_id and coverage
        VIEWS; re-labelling does not mint new evidence."""
        body = {
            "schema": self.schema, "frame_manifest": self.frame_manifest,
            "event_manifest": self.event_manifest,
            "dependency_plus": self.dependency_plus,
            "discovery_minus": self.discovery_minus,
            "opacity_manifest": self.opacity_manifest,
        }
        return _h(body)


def _merkle(events: tuple) -> str:
    if not events:
        return _h("EMPTY")
    layer = [_h((e.seq, e.surface, e.detail)) for e in events]
    while len(layer) > 1:
        layer = [_h((layer[i], layer[i + 1] if i + 1 < len(layer) else layer[i]))
                 for i in range(0, len(layer), 2)]
    return layer[0]


def derive_closure(events: tuple) -> dict:
    """Closure is DERIVED, never a trusted boolean. Requires contiguous
    sequence from 0 and a terminal marker event."""
    if not events:
        return {"closed": False, "reason": "E_NO_EVENTS"}
    seqs = [e.seq for e in events]
    if seqs != list(range(len(events))):
        return {"closed": False, "reason": "E_SEQUENCE_GAP"}
    if events[-1].surface != "__terminal__":
        return {"closed": False, "reason": "E_NO_TERMINAL"}
    return {"closed": True}


def build_exhibit(contract: ObservationContract, events: list,
                  equipped: frozenset, discovery: list | None = None) -> NuExhibit:
    """Assemble the catalogue. The dependency algebra:

        D+  : surfaces in Omega with >= 1 observed event
        D-  : witnessed exclusions carrying a DiscoveryReceipt
        U   : REQUIRED surfaces that are neither witnessed nor excluded —
              and CRUCIALLY, any required surface with no equipped
              collector defaults here (unobserved => U), never dropped
        D-empty : surfaces declared IRRELEVANT in the contract

    Anti-sharpshooter: an event on a surface OUTSIDE the committed Omega
    is a hard error, and every discovery receipt must be stamped with the
    committed omega_hash."""
    events = list(events)
    discovery = list(discovery or [])
    omega = contract.surfaces()

    for e in events:
        if e.surface not in omega and e.surface != "__terminal__":
            raise ValueError(f"E_SURFACE_OUTSIDE_OMEGA:{e.surface}")
    for r in discovery:
        if r.omega_hash != contract.omega_hash:
            raise ValueError("E_DISCOVERY_UNSTAMPED")   # drawn after the shots
        if r.surface not in omega:
            raise ValueError(f"E_DISCOVERY_OUTSIDE_OMEGA:{r.surface}")

    observed = {e.surface for e in events if e.surface != "__terminal__"}
    excluded = {r.surface for r in discovery}

    required = contract.required()
    d_plus = tuple(sorted(observed & required))
    d_minus = tuple(sorted((r.surface, r.method, r.result) for r in discovery))
    # unobserved => U by DEFAULT: any required surface not witnessed and
    # not witnessed-excluded is opaque. A surface with no equipped
    # collector CANNOT be witnessed, so it lands here structurally.
    opaque = tuple(sorted(
        s for s in required
        if s not in observed and s not in excluded
    ))
    d_empty = tuple(sorted(contract.irrelevant()))

    sigma = {
        "required_total": len(required),
        "d_plus": len(d_plus), "d_minus": len(d_minus),
        "opaque": len(opaque), "irrelevant": len(d_empty),
        "equipped": tuple(sorted(equipped)),
        "unequipped_required": tuple(sorted(required - equipped)),
        "closure": derive_closure(tuple(events)),
    }
    frame = {
        "python": None,   # stamped by caller if desired; identity-neutral
        "omega_hash": contract.omega_hash,
    }
    ev = tuple(events)
    ex = NuExhibit(
        schema=SCHEMA, frame_manifest=frame, event_manifest=ev,
        dependency_plus=d_plus, discovery_minus=d_minus,
        opacity_manifest=opaque, coverage_manifest=sigma,
        merkle_root=_merkle(ev),
    )
    return _finalize(ex)


def _finalize(ex: NuExhibit) -> NuExhibit:
    from dataclasses import replace
    return replace(ex, exhibit_id=ex.identity())


# ── the JURY, decomposed (per ruling): I_id, I_Omega, C_Omega never fuse ─
#
#   I_id    not implies  I_Omega  not implies  C_Omega  not implies  Pi_D
#
# V_I in {PASS, FAIL}   — structural/contract defect: the object is broken
# V_C in {PASS, UNKNOWN}— object sound but observation insufficient
# V_nu composes them; FAIL and UNKNOWN are DIFFERENT failure classes and
# must survive distinctly all the way into WVIS.

def verify_integrity(exhibit: NuExhibit, contract: ObservationContract) -> dict:
    """V_I -> PASS | FAIL. A FAIL means the evidence object is DEFECTIVE
    (contract/integrity/schema violation), not merely insufficient."""
    if exhibit.schema != SCHEMA:
        return {"verdict": "FAIL", "reason": "E_BAD_SCHEMA"}
    # I_id: identity binds the immutable observation body
    if exhibit.exhibit_id and exhibit.exhibit_id != exhibit.identity():
        return {"verdict": "FAIL", "reason": "E_IDENTITY_MISMATCH"}
    # I_Omega: pre-run commitment binding (anti-rewrite)
    if exhibit.frame_manifest.get("omega_hash") != contract.omega_hash:
        return {"verdict": "FAIL", "reason": "E_CONTRACT_MISMATCH"}
    # Merkle integrity (necessary, NOT sufficient — CT-style)
    if exhibit.merkle_root != _merkle(exhibit.event_manifest):
        return {"verdict": "FAIL", "reason": "E_INTEGRITY_BROKEN"}
    # partition well-formedness: no surface may occupy two classes
    d_plus = set(exhibit.dependency_plus)
    d_minus = {r[0] for r in exhibit.discovery_minus}
    opaque = set(exhibit.opacity_manifest)
    for a, b, nm in ((d_plus, d_minus, "PLUS_MINUS"),
                     (d_plus, opaque, "PLUS_OPAQUE"),
                     (d_minus, opaque, "MINUS_OPAQUE")):
        if a & b:
            return {"verdict": "FAIL", "reason": f"E_PARTITION_OVERLAP:{nm}",
                    "surfaces": sorted(a & b)}
    # NEGATIVE-BY-SILENCE guard: a D- entry must carry a witnessed method
    # and result; a bare surface claim is a contract violation, not an
    # observation gap.  not seen != shown absent.
    for surface, method, result in exhibit.discovery_minus:
        if not method or not result:
            return {"verdict": "FAIL", "reason": "E_NEGATIVE_WITHOUT_WITNESS",
                    "surface": surface}
    return {"verdict": "PASS"}


def verify_coverage(exhibit: NuExhibit, contract: ObservationContract) -> dict:
    """V_C -> PASS | UNKNOWN. Assumes integrity already PASSed; reasons
    ONLY about sufficiency.  Omega_opaque != {} => UNKNOWN. Never PASS
    while anything relevant remains opaque or uncovered."""
    required = contract.required()
    covered = set(exhibit.dependency_plus) | {r[0] for r in exhibit.discovery_minus}
    opaque = set(exhibit.opacity_manifest)
    uncovered = sorted(required - covered - opaque)
    if opaque:
        return {"verdict": "UNKNOWN", "reason": "E_OPACITY_NONEMPTY",
                "opaque": sorted(opaque), "pi_d": "NOT_EARNED"}
    if uncovered:
        return {"verdict": "UNKNOWN", "reason": "E_REQUIRED_UNCOVERED",
                "uncovered": uncovered, "pi_d": "NOT_EARNED"}
    return {"verdict": "PASS", "pi_d": "EARNED", "covered": sorted(covered)}


def verify_nu(exhibit: NuExhibit, contract: ObservationContract) -> dict:
    """The composed pipeline: VerifyIntegrity THEN VerifyCoverage.
        I=FAIL              -> V_nu = FAIL   (defective object)
        I=PASS, C=UNKNOWN   -> V_nu = UNKNOWN (sound but insufficient)
        I=PASS, C=PASS      -> V_nu = PASS
    Pi_D is EARNED only on PASS; V_nu != PASS => Pi_D NOT_EARNED => no
    transport. And even EARNED does not imply admission: E_nu !-> Gamma."""
    vi = verify_integrity(exhibit, contract)
    if vi["verdict"] == "FAIL":
        return {"v_nu": "FAIL", "class": "INTEGRITY", "detail": vi,
                "pi_d": "NOT_EARNED"}
    vc = verify_coverage(exhibit, contract)
    if vc["verdict"] == "UNKNOWN":
        return {"v_nu": "UNKNOWN", "class": "COVERAGE", "detail": vc,
                "pi_d": "NOT_EARNED"}
    return {"v_nu": "PASS", "class": "COVERAGE", "detail": vc,
            "pi_d": "EARNED", "admits": False}   # earned != admitted


# ── closed schema: `complete`/`verdict`/`authority` are UNREPRESENTABLE ──

def validate_exhibit_dict(d: dict) -> None:
    """A wire-level exhibit may not carry a self-verdict or authority
    field ANYWHERE. Rejects, never ignores."""
    def walk(o):
        if isinstance(o, dict):
            banned = set(k.lower() for k in o) & _UNREPRESENTABLE
            if banned:
                raise ValueError(f"E_UNREPRESENTABLE_FIELD:{','.join(sorted(banned))}")
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
    walk(d)
