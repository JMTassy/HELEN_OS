"""IC — the Ingestion Commit Cell.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    IC = (window, enumeration, provenance_closure, classification,
          candidate_semantics, restricted_fields, mirror_set, hashes,
          receipt, cursor)

Ingestion is not copying information. It is compiling a
provenance-closed, permission-bounded history of what the institution
is allowed to remember.

The same law as the historical corpus, different substrate:

    DISCOVERED != INTERPRETED != DECIDED != PERSISTED != REPLAYABLE

Three distinct completion credentials, never one boolean:

    ENUMERATION_COMPLETE        the query returned
    PROVENANCE_CLOSURE_COMPLETE closure finished UNDER THE DECLARED
                                DISCOVERY OPERATORS — never "proved
                                exhaustive over the universe"
    MIRROR_COMPLETE             bytes are durable and hash-verified

The admission rule:

    WindowBound  EnumerationRecorded  ProvenanceExpanded
    ClassificationValid  SecretsExcluded  RequiredMirrorsVerified
    HashesVerified
    -------------------------------------------------------------
                        AdvanceCursor

CURSOR = ACKNOWLEDGEMENT OF DURABLE CAUSAL CLOSURE. Order is
Persist -> Hash -> Verify -> Receipt -> CursorAdvance, never the
reverse: future successful persistence cannot retroactively prove a
cursor advance was safe when it happened. That is the institutional
arrow of time in the ingestion substrate.

Execution needs four conjuncts, not two:

    Execute(a) = Valid(a) & Authorized(a) & Capacity(a) & Environment(a)

so capacity is a LEASED RESOURCE R = (type, available, reserved,
consumed, expires) — quota, credits, tokens, money, storage, rate
limits, human attention — and it can be double-spent exactly like
authority.

And the availability family, one law at several layers:

    AccountAlive     !=> DataAlive
    ServiceAvailable !=> CorpusDurable
    Healthy          !=> KnownBuild
    Enumerated       !=> ProvenanceClosed

Deterministic: time passed in, no randomness, canonical JSON.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

COMPLETION_CREDENTIALS = ("ENUMERATION_COMPLETE",
                          "PROVENANCE_CLOSURE_COMPLETE",
                          "MIRROR_COMPLETE")

CURSOR_ORDER = ("PERSIST", "HASH", "VERIFY", "RECEIPT", "CURSOR_ADVANCE")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def canon_hash(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# ── capacity as a leased resource ───────────────────────────────────────

@dataclass
class ResourceLease:
    """R = (type, available, reserved, consumed, expires). Capacity is
    not an incidental runtime property; it is spent, and it can be
    double-spent."""
    rtype: str
    available: float
    reserved: float = 0.0
    consumed: float = 0.0
    expires: int = 2**31 - 1

    def reserve(self, amount: float, t: int) -> dict:
        if t > self.expires:
            return {"ok": False, "reason": "E_CAPACITY_EXPIRED"}
        if amount > self.available - self.reserved:
            return {"ok": False, "reason": "E_INSUFFICIENT_CAPACITY",
                    "requested": amount,
                    "free": self.available - self.reserved}
        self.reserved += amount
        return {"ok": True, "reserved_total": self.reserved}

    def consume(self, amount: float) -> dict:
        if amount > self.reserved:
            return {"ok": False, "reason": "E_CONSUME_WITHOUT_RESERVE"}
        self.reserved -= amount
        self.consumed += amount
        self.available -= amount
        return {"ok": True, "consumed_total": self.consumed}


def can_execute(valid: bool, authorized: bool, capacity: ResourceLease | None,
                amount: float, environment_ok: bool, t: int) -> dict:
    """Execute(a) = Valid & Authorized & Capacity & Environment. Any
    missing conjunct means no effect — and the receipt names WHICH."""
    conj = {"valid": valid, "authorized": authorized,
            "environment": environment_ok,
            "capacity": bool(capacity) and
            capacity.reserve(amount, t)["ok"] if capacity else False}
    if not all(conj.values()):
        return {"verdict": "NO_EFFECT",
                "missing": sorted(k for k, v in conj.items() if not v),
                "conjuncts": conj}
    return {"verdict": "EXECUTABLE", "conjuncts": conj}


# ── the three completion credentials ────────────────────────────────────

@dataclass(frozen=True)
class DiscoveryOperators:
    """The DECLARED operators under which closure is claimed. Closure
    is relative to these and says nothing about the universe."""
    names: tuple                       # e.g. ("enumerate_modified_time",
    #                                          "resolve_linked_ids", ...)

    def __post_init__(self):
        if not self.names:
            raise ValueError("E_NO_DECLARED_OPERATORS")


def provenance_closure(enumerated: frozenset, linked: frozenset,
                       attachments: frozenset, referenced: frozenset,
                       operators: DiscoveryOperators) -> dict:
    """Delta_effective = enumeration ∪ links ∪ attachments ∪ referenced.
    ENUMERATION_COMPLETE and PROVENANCE_CLOSURE_COMPLETE are separate
    credentials — the live falsifier was a 488MB in-window object
    visible by stable ID and invisible to the query."""
    union = enumerated | linked | attachments | referenced
    missed = union - enumerated
    return {"effective_delta": union,
            "ENUMERATION_COMPLETE": True,          # the query returned
            "enumeration_was_exhaustive": not missed,
            "found_only_by_provenance": sorted(missed),
            "PROVENANCE_CLOSURE_COMPLETE": True,
            "closure_scope": tuple(operators.names),
            "closure_caveat": "closure completed under the declared "
                              "discovery operators; NOT proved "
                              "exhaustive over the universe",
            "law": "ENUMERATION COMPLETE does not imply PROVENANCE "
                   "CLOSURE COMPLETE"}


# ── the cell and its admission rule ─────────────────────────────────────

@dataclass(frozen=True)
class IngestionCell:
    window: tuple                      # (lower_bound, upper_bound)
    enumeration: frozenset
    closure: dict                      # provenance_closure() output
    classification: dict               # object_id -> class
    restricted_fields: tuple           # names withheld from projection
    mirror_set: frozenset              # objects REQUIRED to be mirrored
    mirrors_verified: frozenset        # objects with a verified hash
    hashes: dict                       # object_id -> sha256
    projection_fields: dict = field(default_factory=dict)


def admit_ingestion(cell: IngestionCell, max_class: str,
                    secrecy_of: dict) -> dict:
    """The inference rule. Every premise discharged, or no cursor."""
    if not (cell.window and len(cell.window) == 2 and
            cell.window[0] < cell.window[1]):
        return _deny("E_WINDOW_UNBOUND")
    if not cell.enumeration and not cell.closure.get("effective_delta"):
        return _deny("E_ENUMERATION_UNRECORDED")
    if not cell.closure.get("PROVENANCE_CLOSURE_COMPLETE"):
        return _deny("E_PROVENANCE_NOT_EXPANDED")
    unclassified = sorted(cell.closure["effective_delta"] -
                          frozenset(cell.classification))
    if unclassified:
        return _deny("E_CLASSIFICATION_INCOMPLETE",
                     unclassified=unclassified)
    leaked = sorted(f for f in cell.projection_fields
                    if _rank_class(secrecy_of.get(f, "S0")) >
                    _rank_class(max_class))
    if leaked:
        return _deny("E_SECRET_IN_PROJECTION", leaked_fields=leaked)
    unmirrored = sorted(cell.mirror_set - cell.mirrors_verified)
    if unmirrored:
        return _deny("E_MIRROR_UNVERIFIED", missing=unmirrored)
    unhashed = sorted(cell.mirrors_verified - frozenset(cell.hashes))
    if unhashed:
        return _deny("E_HASH_UNVERIFIED", missing=unhashed)
    return {"verdict": "ADVANCE_CURSOR",
            "credentials": {"ENUMERATION_COMPLETE": True,
                            "PROVENANCE_CLOSURE_COMPLETE": True,
                            "MIRROR_COMPLETE": True},
            "receipt": canon_hash([sorted(cell.closure["effective_delta"]),
                                   sorted(cell.hashes.items()),
                                   cell.window]),
            "closure_scope": cell.closure["closure_scope"]}


def _deny(reason: str, **extra) -> dict:
    return {"verdict": "CURSOR_HELD", "reason": reason,
            "cursor_advanced": False,
            "note": "the run is recorded; the cursor is not moved",
            **extra}


_CLASSES = ("S0", "S1", "S2", "S3", "S4")


def _rank_class(c: str) -> int:
    if c not in _CLASSES:
        raise ValueError("E_UNKNOWN_SECRECY_CLASS")
    return _CLASSES.index(c)


# ── cursor discipline ───────────────────────────────────────────────────

def cursor_sequence_valid(steps: tuple) -> dict:
    """Persist -> Hash -> Verify -> Receipt -> CursorAdvance. A cursor
    that moves before durable closure creates an unreplayable gap, and
    later success cannot retroactively make the early advance safe."""
    if tuple(steps) != CURSOR_ORDER:
        pos = {s: i for i, s in enumerate(steps)}
        early = ("CURSOR_ADVANCE" in pos and
                 any(pos.get(s, 99) > pos["CURSOR_ADVANCE"]
                     for s in CURSOR_ORDER[:-1]))
        return {"verdict": "REFUSED",
                "reason": ("E_CURSOR_BEFORE_DURABLE_CLOSURE" if early
                           else "E_CURSOR_SEQUENCE_INVALID"),
                "required": CURSOR_ORDER,
                "law": "the cursor is an acknowledgement of durable "
                       "causal closure, never a promise of it"}
    return {"verdict": "VALID_SEQUENCE"}


# ── the availability family ─────────────────────────────────────────────

AVAILABILITY_NON_ENTAILMENTS = (
    ("account_alive", "data_alive"),
    ("service_available", "corpus_durable"),
    ("healthy", "known_build"),
    ("enumerated", "provenance_closed"),
)


def entails(premise: str, conclusion: str) -> dict:
    """Every pair above is a NON-entailment. The function exists so the
    refusal is executable rather than remembered."""
    if (premise, conclusion) in AVAILABILITY_NON_ENTAILMENTS:
        return {"entails": False, "reason": "E_NON_ENTAILMENT",
                "law": f"{premise} does not imply {conclusion}"}
    return {"entails": None, "reason": "E_UNKNOWN_PAIR"}


# ── constitutional vs extensional ingestion equality ────────────────────

def ingestion_equiv(run_a: dict, run_b: dict) -> dict:
    """Two runs may produce identical semantic memory while one skipped
    a provenance-linked object. Extensional equality may hold;
    constitutional equality must not."""
    same_memory = run_a["semantic_memory"] == run_b["semantic_memory"]
    same_closure = run_a["effective_delta"] == run_b["effective_delta"]
    same_ops = run_a["closure_scope"] == run_b["closure_scope"]
    return {"extensional": same_memory,
            "constitutional": same_memory and same_closure and same_ops,
            "law": "same semantic result, different provenance closure, "
                   "is not the same ingestion"}
