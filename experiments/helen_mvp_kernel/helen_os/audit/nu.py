"""ν — the execution-exhibit tracer (NU_EXECUTION_EXHIBIT_V1). 🔵 OBSERVED · authority=0.

ν sits UNDER C17: it mints an addressed EXHIBIT of a run's observability, and a pure VerifyCoverage
turns that EXHIBIT into a coverage verdict which C17 then consumes. The canonical chain:

    Execution → typed Events → (D⁺, D⁻, 𝒰) → E_ν → VerifyCoverage → PASS | UNKNOWN | FAIL

with NO reverse shortcuts:
    E_ν ⊬ Π_D=PASS      many events ⊬ stronger evidence      valid structure ⊬ adequate coverage
    Σ (coverage accounting) ≠ Π_D (the verdict)

Three separated objects (Catalogue ≠ Jury):
    a trace says what was VISIBLE · an EXHIBIT says HOW that visibility was produced ·
    a coverage verdict says what that visibility LICENSES.

Anti-circularity: Ω is committed PRE-RUN (omega_pre_hash), so the tracer cannot define success after
seeing its own blind spots. Pessimistic law: d ∉ D⁺ ⊬ d ∈ D⁻ — negative knowledge needs its own
witnessed discovery obligation. sys.addaudithook is only ONE collector, never ν itself; any class
with no defended collector lands in 𝒰. The EXHIBIT cannot even CARRY a verdict coordinate (closed
verdict surface, like WVIS): complete / pi_d_pass / admit / authority / ledger_append ∉ Fields(E_ν).
Determinism: pure functions over injected events; canon reuses the ledger hash_chain.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from helen_os.ledger.hash_chain import canonical_json, sha256_hex


def h_v(x) -> str:
    return sha256_hex(canonical_json(x))


class ObsClass(Enum):                  # Ω/python-v1 — the observation universe
    FILE_READ = "FILE_READ"
    FILE_METADATA = "FILE_METADATA"
    IMPORT = "IMPORT"
    ENV_READ = "ENV_READ"
    CONFIG = "CONFIG"
    CWD = "CWD"
    ARGUMENT = "ARGUMENT"
    DYNAMIC_CODE = "DYNAMIC_CODE"
    NAMESPACE_DISCOVERY = "NAMESPACE_DISCOVERY"
    SUBPROCESS = "SUBPROCESS"
    NATIVE_BOUNDARY = "NATIVE_BOUNDARY"      # ctypes / C-ext — no defended collector → 𝒰
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"


class Disposition(Enum):
    COVERED = "COVERED"
    NOT_APPLICABLE = "NOT_APPLICABLE"        # needs a justification witness, never an escape hatch


@dataclass(frozen=True)
class ExecutionEvent:
    seq: int
    event_type: ObsClass
    source: str                 # e.g. "CPYTHON_AUDIT"
    object_ref: str             # content ref of the object (file:sha…, module:…, env:KEY)
    locator: str
    operation: str
    raw_event_hash: str = ""


@dataclass(frozen=True)
class ObservationContract:       # Ω — precommitted before collection
    omega_id: str
    classes: tuple               # tuple[ObsClass] — the RELEVANT observation classes
    policy_id: str
    collectors: tuple = ()       # tuple[str]

    def omega_hash(self) -> str:
        return h_v({"omega_id": self.omega_id,
                    "classes": sorted(c.value for c in self.classes),
                    "policy_id": self.policy_id,
                    "collectors": sorted(self.collectors)})


@dataclass(frozen=True)
class PositiveDep:               # d ∈ D⁺ ⟺ ∃ events ⊢ d (with concrete event refs)
    dep_id: str
    cls: ObsClass
    resource: str
    evidence_events: tuple       # tuple[int] — seq refs that justify this dep
    derivation_rule: str


@dataclass(frozen=True)
class NegativeDep:
    """d ∈ D⁻ — a PROOF-CARRYING exclusion. Absence-of-event is NOT enough (Negative-by-Silence).
    Each exclusion IS its own single-subject witness (cls = subject), so one witness can never launder
    another subject's exclusion. ValidNegativeWitness = ValidStructure ∧ ValidBinding ∧ Executed."""
    cls: ObsClass               # subject: the class proven absent (binding)
    scope: str                  # search domain that was enumerated
    discovery_rule: str         # the discovery obligation
    enumerated_count: int
    manifest_hash: str          # hash of the enumeration RESULT
    executed: bool = False      # was the obligation actually RUN? (a described obligation is not a witness)


def valid_negative_witness(d: NegativeDep) -> bool:
    """ValidNegativeWitness = ValidStructure ∧ ValidBinding ∧ Executed. A declared obligation_id is not
    a witness until it is executed and bound to its subject — else negative-by-unexecuted-description."""
    valid_structure = bool(d.scope) and bool(d.discovery_rule) and bool(d.manifest_hash)
    valid_binding = isinstance(d.cls, ObsClass)        # subject present and typed
    return valid_structure and valid_binding and bool(d.executed)


@dataclass(frozen=True)
class OpaqueClass:               # 𝒰 — relevance possible, no defended observation mechanism
    cls: ObsClass
    reason: str
    relevance: str = "POSSIBLY_RELEVANT"
    disposition: str = "BLOCK_COVERAGE"


@dataclass(frozen=True)
class ClassDisposition:          # explicit NA classification (must carry a justification)
    cls: ObsClass
    disposition: Disposition
    justification: str = ""


@dataclass(frozen=True)
class NuExhibit:
    schema_version: str
    omega: ObservationContract
    omega_pre_hash: str          # BOUND before the run — verified against omega.omega_hash()
    events: tuple                # tuple[ExecutionEvent]
    d_plus: tuple                # tuple[PositiveDep]
    d_minus: tuple               # tuple[NegativeDep]
    opaque: tuple                # tuple[OpaqueClass]
    dispositions: tuple = ()     # tuple[ClassDisposition] — NA justifications
    collector_failures: tuple = ()
    views: tuple = ()            # rendering views — EXCLUDED from content identity

    def identity_body(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "omega_hash": self.omega.omega_hash(),
            "omega_pre_hash": self.omega_pre_hash,
            "events": [[e.seq, e.event_type.value, e.object_ref] for e in self.events],
            "d_plus": sorted((d.dep_id, d.cls.value, d.resource) for d in self.d_plus),
            "d_minus": sorted((d.cls.value, d.scope, d.manifest_hash) for d in self.d_minus),
            "opaque": sorted(o.cls.value for o in self.opaque),
            "dispositions": sorted((c.cls.value, c.disposition.value) for c in self.dispositions),
        }   # views deliberately excluded: a new view is not a new evidence identity

    def exhibit_id(self) -> str:
        return h_v(self.identity_body())


# closed VERDICT surface — the EXHIBIT cannot even carry a downstream judgment coordinate
_FORBIDDEN = frozenset({"complete", "pi_d_pass", "admit", "authority",
                        "ledger_append", "valid_by_transport"})
assert _FORBIDDEN.isdisjoint(NuExhibit.__dataclass_fields__)


def mint(omega: ObservationContract, events, d_plus, d_minus, opaque,
         dispositions=(), collector_failures=(), views=()) -> NuExhibit:
    """Construct an EXHIBIT, binding the pre-run Ω hash. (In a live run, omega_pre_hash would be
    committed before the first event; here mint binds it, and verify recomputes/checks it.)"""
    return NuExhibit("NU_EXECUTION_EXHIBIT_V1", omega, omega.omega_hash(),
                     tuple(events), tuple(d_plus), tuple(d_minus), tuple(opaque),
                     tuple(dispositions), tuple(collector_failures), tuple(views))


class Coverage(Enum):
    PASS = "PASS"
    UNKNOWN = "UNKNOWN"
    FAIL = "FAIL"


def verify_coverage(E: NuExhibit):
    """Pure judgment. FAIL = exhibit/contract inconsistency; UNKNOWN = sound but relevant opacity
    remains; PASS = every relevant class covered or validly NA. Σ ≠ Π_D — this is the verdict."""
    # 1. contract integrity — reject retrospective Ω substitution
    if E.omega_pre_hash != E.omega.omega_hash():
        return Coverage.FAIL, "INVALID_CONTRACT"
    # 2. event-ref integrity — every D⁺ must cite real, non-empty evidence
    seqs = {e.seq for e in E.events}
    for d in E.d_plus:
        if not d.evidence_events:
            return Coverage.FAIL, f"COVERED_WITHOUT_EVIDENCE:{d.dep_id}"
        if not set(d.evidence_events) <= seqs:
            return Coverage.FAIL, f"FORGED_EVENT_REF:{d.dep_id}"
    # 3. NA must be justified — never an escape hatch
    for c in E.dispositions:
        if c.disposition == Disposition.NOT_APPLICABLE and not c.justification:
            return Coverage.FAIL, f"NA_WITHOUT_JUSTIFICATION:{c.cls.value}"
    # 3b. D⁻ must be PROOF-CARRYING — silence cannot enter D⁻ (Negative-by-Silence). Pointwise: EVERY
    #     declared exclusion needs its own valid, executed, bound witness; one witness cannot launder
    #     another subject's exclusion (d∉D⁺ ⊬ d∈D⁻).
    for d in E.d_minus:
        if not valid_negative_witness(d):
            return Coverage.FAIL, f"UNWITNESSED_EXCLUSION:{d.cls.value}"
    # partition sets
    covered = {d.cls for d in E.d_plus} | {d.cls for d in E.d_minus}   # witnessed positively or by discovery
    opaque = {o.cls for o in E.opaque}
    na = {c.cls for c in E.dispositions if c.disposition == Disposition.NOT_APPLICABLE}
    relevant = set(E.omega.classes)
    # 4. conservation: each relevant class classified exactly once (no silent disappearance)
    for w in relevant:
        m = sum([w in covered, w in opaque, w in na])
        if m == 0:
            return Coverage.FAIL, f"UNCLASSIFIED_CLASS:{w.value}"   # d∉D⁺ ⊬ d∈D⁻: needs a witness
        if m > 1:
            return Coverage.FAIL, f"OVERLAP_CLASS:{w.value}"
    # 5. relevant opacity ⇒ UNKNOWN (never PASS, never masquerade as FAIL)
    if opaque & relevant:
        return Coverage.UNKNOWN, "RELEVANT_OPACITY"
    # 6. every relevant class defensibly covered or validly NA
    return Coverage.PASS, "ALL_RELEVANT_COVERED_OR_NA"


class NuIntegrityError(ValueError):
    """Raised at the wire boundary when an externally-supplied payload violates a ν-integrity invariant
    (not merely a JSON-shape error). typed-constructor safety ≠ wire-format safety."""


def validate_exhibit_payload(raw: dict) -> bool:
    """Wire-boundary SEMANTIC gate. A well-formed, schema-shaped JSON payload can still violate ν
    integrity — this enforces the SAME invariants as the constructor on raw external input:
        JSON well-formed ⊬ schema valid ⊬ ν-integrity valid.
    Rejects forbidden verdict coordinates AND the Negative-by-Silence path on the wire."""
    if not isinstance(raw, dict):
        raise NuIntegrityError("PAYLOAD_NOT_OBJECT")
    leaked = _FORBIDDEN & set(raw.keys())
    if leaked:
        raise NuIntegrityError(f"FORBIDDEN_VERDICT_FIELD:{sorted(leaked)}")   # closed verdict surface
    for d in raw.get("d_minus", []) or []:
        subj = d.get("cls") or d.get("subject")
        if not subj:
            raise NuIntegrityError("NEGATIVE_WITHOUT_SUBJECT")
        if not (d.get("scope") and d.get("discovery_rule") and d.get("manifest_hash")):
            raise NuIntegrityError(f"UNWITNESSED_EXCLUSION_WIRE:{subj}")       # structure/binding
        if not d.get("executed"):
            raise NuIntegrityError(f"UNEXECUTED_EXCLUSION_WIRE:{subj}")        # described ≠ executed
    return True
