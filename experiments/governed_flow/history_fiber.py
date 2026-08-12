"""History Fiber & Obligation Conservation — HF-01..HF-15.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Frame fact, witnessed 2026-08-12: the Architect lane reported commit
fff21ef for this material. No such object exists on any branch (all
fetched and searched) — the second ghost commit this session, after
3e0e2b4. A reported hash is a claim; only the ledger is law. This is
the first History Fiber material on the source of truth.

THE CORE CHIDDUSH: state is a quotient of history.

    pi : H -> S      replay's projection, MANY-TO-ONE

    h1 != h2  and  pi(h1) = pi(h2)  is entirely possible

so visible state does not determine history. The fiber

    pi^-1(s) = { h in H : pi(h) = s }

holds every history compatible with s. Collapsing members of a fiber
that differ in responsibility, consent, provenance, authority,
exposure, repair or open obligations is CAUSAL ALIASING.

    Governed State  G_t = (S_t, F_t, Omega_t)
                        = visible state + history fingerprint
                          + open obligations

OBLIGATION CONSERVATION:

    Omega_out = Omega_in - Omega_discharged + Omega_generated
                         + Omega_residual

Discharge requires an explicit witness: a receipt discharges ONLY the
obligations its proof contract covers (r |- omega). Absence from the
current state is not discharge. Projection, compression, compensation,
omission, model replacement and restored state may not silently erase
an obligation.

The five laundering classes share one structural error: a
transformation changes REPRESENTATION and the system mistakes that
change for increased AUTHORITY.

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

GOVERNED_DIMENSIONS = ("authorization", "consent", "exposure",
                       "responsibility", "repair", "provenance")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def canon_hash(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# ── obligations and typed discharge ─────────────────────────────────────

@dataclass(frozen=True)
class Obligation:
    """omega. Carries the CONTRACT its discharge requires — an
    obligation that does not say what would discharge it can never be
    discharged, and that is a feature."""
    oblig_id: str
    kind: str                          # notify | repair | disclose | ...
    owed_by: str
    created_by: str                    # the movement that generated it
    discharge_contract: str            # what a witness must show

    def __post_init__(self):
        if not self.discharge_contract:
            raise ValueError("E_OBLIGATION_WITHOUT_CONTRACT")


@dataclass(frozen=True)
class DischargeReceipt:
    """A receipt is a TYPED discharge operator, not a global 'fine now'.
    proof_contract names exactly which contracts it satisfies."""
    receipt_id: str
    covers: tuple                      # obligation ids
    proof_contract: str
    witness_ref: str

    def __post_init__(self):
        if not self.witness_ref:
            raise ValueError("E_DISCHARGE_WITHOUT_WITNESS")


def discharges(r: DischargeReceipt, omega: Obligation) -> dict:
    """HF-09: r |- omega. Both the id coverage AND the contract must
    match — a receipt for the wrong contract covering the right id
    discharges nothing."""
    if omega.oblig_id not in r.covers:
        return {"discharges": False, "reason": "E_NOT_COVERED"}
    if r.proof_contract != omega.discharge_contract:
        return {"discharges": False, "reason": "E_CONTRACT_MISMATCH",
                "required": omega.discharge_contract,
                "offered": r.proof_contract}
    return {"discharges": True, "witness": r.witness_ref}


def conserve_obligations(omega_in: frozenset, receipts: tuple,
                         generated: frozenset = frozenset(),
                         residual: frozenset = frozenset()) -> dict:
    """HF-07/HF-08. Omega_out = Omega_in - discharged + generated +
    residual. Anything not WITNESSED-discharged survives, whatever the
    state looks like."""
    by_id = {o.oblig_id: o for o in omega_in}
    discharged, refusals = set(), []
    for r in receipts:
        for oid in r.covers:
            o = by_id.get(oid)
            if o is None:
                refusals.append({"oblig_id": oid,
                                 "reason": "E_DISCHARGE_OF_UNKNOWN"})
                continue
            d = discharges(r, o)
            if d["discharges"]:
                discharged.add(oid)
            else:
                refusals.append({"oblig_id": oid, **d})
    survivors = frozenset(o for o in omega_in
                          if o.oblig_id not in discharged)
    return {"omega_out": survivors | generated | residual,
            "discharged": sorted(discharged),
            "refused_discharges": refusals,
            "carried_forward": sorted(o.oblig_id for o in survivors),
            "law": "absence from current state does not imply "
                   "obligation discharged"}


# ── histories, the quotient map, and fibers ─────────────────────────────

@dataclass(frozen=True)
class Movement:
    """One admitted step, with the governed dimensions it touched."""
    move_id: str
    from_state: str
    to_state: str
    dimensions: dict = field(default_factory=dict)   # governed coords


@dataclass(frozen=True)
class History:
    h_id: str
    initial: str
    movements: tuple = ()
    obligations: frozenset = frozenset()

    def visible_state(self) -> str:
        """pi(h) — the quotient map. Many-to-one BY CONSTRUCTION."""
        return (self.movements[-1].to_state if self.movements
                else self.initial)

    def fingerprint(self) -> str:
        """F_t — the movement fingerprint. Distinguishes histories that
        pi cannot."""
        return canon_hash([(m.move_id, m.from_state, m.to_state)
                           for m in self.movements])

    def governed_state(self) -> dict:
        """HF-04: G_t = (S_t, F_t, Omega_t)."""
        return {"S": self.visible_state(), "F": self.fingerprint(),
                "Omega": frozenset(o.oblig_id for o in self.obligations)}

    def dimension(self, name: str) -> tuple:
        return tuple(m.dimensions.get(name) for m in self.movements
                     if name in m.dimensions)


def equiv_visible(h1: History, h2: History) -> bool:
    """~_S — the weak relation. pi(h1) = pi(h2)."""
    return h1.visible_state() == h2.visible_state()


def equiv_governed(h1: History, h2: History) -> dict:
    """~_G — interchangeable w.r.t. ALL governed consequences.
    HF-03: ~_G is a STRICT subset of ~_S. A system storing only S
    silently substitutes ~_S for ~_G; that is causal aliasing."""
    same_s = equiv_visible(h1, h2)
    same_f = h1.fingerprint() == h2.fingerprint()
    same_omega = (h1.governed_state()["Omega"] ==
                  h2.governed_state()["Omega"])
    differing = [d for d in GOVERNED_DIMENSIONS
                 if h1.dimension(d) != h2.dimension(d)]
    return {"visible_equivalent": same_s,
            "governed_equivalent": same_s and same_f and same_omega
            and not differing,
            "differing_dimensions": differing,
            "law": "~_G is strictly finer than ~_S"}


def causal_aliasing(h1: History, h2: History, represented_equal: bool) -> dict:
    """HF-01/02/03. If the system represents two histories as equal
    while any governed dimension differs, the architecture has failed."""
    e = equiv_governed(h1, h2)
    if represented_equal and not e["governed_equivalent"]:
        return {"verdict": "E_CAUSAL_ALIASING",
                "visible_equivalent": e["visible_equivalent"],
                "differing": e["differing_dimensions"] or
                ["fingerprint_or_obligations"],
                "law": "visible state does not determine history"}
    return {"verdict": "NO_ALIASING"}


# ── HF-05/06: compensation is not erasure ───────────────────────────────

def compensate(h: History, undo: Movement) -> dict:
    """S_0 -a-> S_1 -a^-1-> S_0. The state returns; the history does
    not. Any obligation the original movement generated survives the
    undo unless separately, witnessedly discharged."""
    restored = History(h.h_id + "+undo", h.initial,
                       h.movements + (undo,), h.obligations)
    return {"state_restored": restored.visible_state() == h.initial,
            "history_restored": restored.fingerprint() ==
            History(h.h_id, h.initial, (), h.obligations).fingerprint(),
            "obligations_surviving": sorted(
                o.oblig_id for o in restored.obligations),
            "history": restored,
            "law": "STATE RESTORATION does not imply HISTORY "
                   "RESTORATION; COMPENSATION does not imply ERASURE"}


# ── the five laundering classes ─────────────────────────────────────────

def projection_laundering(root_count: int, representation_count: int) -> dict:
    """HF-10: 1 root -> n representations is not n witnesses."""
    return {"representations": representation_count,
            "independent_witnesses": root_count,
            "laundering": representation_count > root_count,
            "reason": ("E_PROJECTION_LAUNDERING"
                       if representation_count > root_count else None)}


def authority_laundering(authorized_at: int, effect_at: int) -> dict:
    """HF-11: Auth_{t+1} does not entail Auth_t."""
    if authorized_at > effect_at:
        return {"laundering": True, "reason": "E_AUTHORITY_LAUNDERING",
                "law": "a later authorization never legitimizes an "
                       "earlier unauthorized transition"}
    return {"laundering": False}


def state_laundering(h_before: History, h_after: History,
                     treated_as_never_happened: bool) -> dict:
    """HF-12: compensating operation restores state; the system must
    not behave as though the original event never occurred."""
    if treated_as_never_happened and \
            h_before.fingerprint() != h_after.fingerprint():
        return {"laundering": True, "reason": "E_STATE_LAUNDERING"}
    return {"laundering": False}


def learning_laundering(succeeded: bool, permission_witness: str = "") -> dict:
    """HF-13: Success(a) does not entail Permission(a)."""
    if succeeded and not permission_witness:
        return {"laundering": True, "reason": "E_LEARNING_LAUNDERING",
                "law": "successful behaviour is not evidence of "
                       "entitlement to perform it"}
    return {"laundering": False}


def memory_laundering(restatement_count: int, canon_witness: str = "") -> dict:
    """HF-14: Repeat(x) does not entail Canon(x)."""
    if restatement_count > 1 and not canon_witness:
        return {"laundering": True, "reason": "E_MEMORY_LAUNDERING",
                "restatements": restatement_count,
                "law": "repetition is not canonization"}
    return {"laundering": False}


LAUNDERING_CLASSES = ("projection", "authority", "state", "learning",
                      "memory")
LAUNDERING_COMMON_ERROR = ("a transformation changes representation and "
                           "the system mistakes that change for "
                           "increased authority")


# ── HF-15: the reducer conservation law ─────────────────────────────────

@dataclass(frozen=True)
class RawFinding:
    """A worker output, with its provenance root kept separate from its
    wording — token equivalence is not epistemic equivalence."""
    finding_id: str
    claim: str
    evidence: str
    source_root: str
    confidence: float
    contradicts: tuple = ()


def safe_reduce(findings: tuple) -> dict:
    """A reducer performs a quotient rho : F_raw -> F_compressed.
    Legal only when the equivalence relation is SAFE:

      R(rho(F)) subset of R(F)          never manufacture provenance
      Authority(rho(F)) <= Authority(F) never expand authority
      C(F_admitted) subset of C(rho(F)) contradictions must SURVIVE

    Representation rank must fall; evidence rank must not rise. So the
    corroboration label counts distinct SOURCE ROOTS, never worker
    copies — three workers on one source are one witness."""
    groups: dict = {}
    for f in findings:
        groups.setdefault(f.claim.strip().lower(), []).append(f)
    out, notes = [], []
    for key, grp in sorted(groups.items()):
        best = max(grp, key=lambda f: (f.confidence, f.finding_id))
        roots = {f.source_root for f in grp}
        # merge evidence rather than discard the non-representatives'
        merged = " | ".join(sorted(f.evidence for f in grp))
        label = (f"{len(grp)} workers, {len(roots)} independent source"
                 f"{'s' if len(roots) != 1 else ''}")
        out.append(RawFinding(best.finding_id, best.claim, merged,
                              best.source_root, best.confidence,
                              tuple(sorted({c for f in grp
                                            for c in f.contradicts}))))
        notes.append({"claim": key, "workers": len(grp),
                      "independent_roots": len(roots), "label": label,
                      "corroborated": len(roots) > 1})
    return {"reduced": tuple(out), "notes": notes,
            "roots_in": frozenset(f.source_root for f in findings),
            "roots_out": frozenset(f.source_root for f in out),
            "contradictions_in": frozenset(
                c for f in findings for c in f.contradicts),
            "contradictions_out": frozenset(
                c for f in out for c in f.contradicts),
            "dropped": tuple(sorted(
                f.finding_id for f in findings
                if f.finding_id not in {o.finding_id for o in out}))}


def reducer_conservation(result: dict) -> dict:
    """The check the reducer must pass. Representation rank down is
    desirable; evidence rank up is forbidden."""
    manufactured = result["roots_out"] - result["roots_in"]
    lost_contradictions = (result["contradictions_in"] -
                           result["contradictions_out"])
    if manufactured:
        return {"verdict": "E_PROVENANCE_MANUFACTURED",
                "invented_roots": sorted(manufactured)}
    if lost_contradictions:
        return {"verdict": "E_CONTRADICTION_LOST",
                "swallowed": sorted(lost_contradictions)}
    return {"verdict": "CONSERVING",
            "representation_rank_delta": len(result["reduced"]) -
            len(result["roots_in"]),
            "law": "delta rank(representation) < 0 desirable; "
                   "delta rank(evidence) > 0 forbidden"}


# ── the generic falsification bead ──────────────────────────────────────

def equal_state_different_history_bead(h_a: History, h_b: History,
                                       system_says_equal: bool) -> dict:
    """The adversarial test every governed component must admit —
    reducers, memories, ledgers, permissions, rollbacks, agent
    pipelines. Build h_A: S0 -> S1 -> S0 and h_B: S0. Verify
    pi(h_A) = pi(h_B). Then ask whether ANY governed dimension differs.
    If one does and the system represents them as equal, it failed."""
    same_visible = equiv_visible(h_a, h_b)
    alias = causal_aliasing(h_a, h_b, system_says_equal)
    return {"pi_equal": same_visible,
            "verdict": alias["verdict"],
            "passed": alias["verdict"] == "NO_ALIASING",
            "differing": alias.get("differing", []),
            "bead": "equal-state/different-history"}


# ── the fifteen invariants, each citing its enforcer ────────────────────

HF_INVARIANTS = (
    ("HF-01", "state is a quotient of history; pi is many-to-one",
     "History.visible_state"),
    ("HF-02", "visible state does not determine history",
     "equiv_governed"),
    ("HF-03", "~_G is strictly finer than ~_S; collapsing is aliasing",
     "causal_aliasing"),
    ("HF-04", "governed state = (S, F, Omega)", "History.governed_state"),
    ("HF-05", "state restoration is not history restoration",
     "compensate"),
    ("HF-06", "compensation is not erasure", "compensate"),
    ("HF-07", "obligation conservation equation", "conserve_obligations"),
    ("HF-08", "absence from state is not discharge", "conserve_obligations"),
    ("HF-09", "receipts are typed discharge operators (r |- omega)",
     "discharges"),
    ("HF-10", "projection laundering forbidden",
     "projection_laundering"),
    ("HF-11", "authority laundering forbidden", "authority_laundering"),
    ("HF-12", "state laundering forbidden", "state_laundering"),
    ("HF-13", "learning laundering forbidden", "learning_laundering"),
    ("HF-14", "memory laundering forbidden", "memory_laundering"),
    ("HF-15", "reducer may lower representation rank, never raise "
              "evidence rank", "reducer_conservation"),
)
