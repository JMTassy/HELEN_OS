"""Crystal Palace 1851 — HER/HAL prospective-recombination harness.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The experiment (HAL pre-verdict: SHIP EXPERIMENT, not SHIP CLAIM):

    842 pages -> frozen 1851 graph -> HER compost -> HAL falsification

with ZERO post-1851 patent information entering before the graph and the
candidate set are frozen and hashed.

Frame fact, first-class: C_1851 is NOT in this frame. archive.org is
unreachable through the proxy (CONNECT 403, twice-witnessed). So the
corpus boots UNREACHABLE and every read returns UNKNOWN until pages are
delivered in-frame — same law as design_memory: no read, no grammar.

The laws this module makes executable (each falsifier-backed):

  C1  PRIMITIVES PRESENT ⊬ INVENTION PRESENT — component existence never
      licenses an OBSERVED combination edge (kill K4).
  C2  Novelty N(I) = alpha*N_V + beta*N_E with beta >> alpha is a
      HYPOTHESIS to test, never an assumption. R_V vs R_E is computable
      only post-freeze.
  C3  Latent adjacent possible — recombination is bounded to the
      contemporaneous neighbourhood N_k(p); a component outside it is
      refused, not scored low (lineage closure, again).
  C4  AUTHORITY GRAVITY — A(edge) <= min A(node). Twenty converging
      pages feel inevitable; they add ZERO authority. Only an
      independent EXTERNAL witness can raise it, by one grade, with a
      receipt.
  C5  DESCRIPTION/PATENT CONTAMINATION — "described as patent" never
      promotes to "verified patent"; "called inventor" never to
      "legally established inventor"; "exhibited in 1851" never to
      "novel as of 1851". Semantic shortcuts are refused (kill K5).
  C6  TEMPORAL PROVENANCE — tau(q) = (t_event, t_source, t_record).
      The observation date is NEVER t_event (retrospective leakage);
      the event date is NEVER backfilled from t_source (kill K6).
  C7  COMBINATORIAL HINDSIGHT — generation and evaluation are separated
      by a freeze: candidates are canonically hashed BEFORE any
      post-1851 data is consulted. Consultation before freeze is
      recorded and kills every downstream verdict (kill K1).

HER emits; she never promotes. HAL reduces deterministically:

    S = E ∧ P ∧ L ∧ F   ->   SHIP_INSIGHT only.

SHIP_INSIGHT ⊬ SHIP_HISTORICAL_FACT ⊬ SHIP_PATENT_FACT ⊬
SHIP_NOVELTY_CLAIM — those routes to ESCALATE (external archival
verification), never out of this module.

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

AVAILABLE = "AVAILABLE"
UNREACHABLE = "UNREACHABLE"

# authority grades, ordered. Fusion direction is DOWN only.
GRADES = ("HYPOTHESIS", "INFERRED", "REPORTED", "OBSERVED")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def canon_hash(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


def _grade_rank(g: str) -> int:
    if g not in GRADES:
        raise ValueError(f"E_UNKNOWN_GRADE:{g}")
    return GRADES.index(g)


# ── the corpus, availability first-class ────────────────────────────────

@dataclass(frozen=True)
class Corpus1851:
    """C_1851. pages_in_frame is the set of pages actually DELIVERED into
    this frame (like the ATF specimens were) — not the set that exists."""
    corpus_id: str
    availability: str
    pages_total: int = 842
    pages_in_frame: frozenset = field(default_factory=frozenset)


C_1851 = Corpus1851(
    corpus_id="crystal_palace_great_exhibition_1851",
    availability=UNREACHABLE,      # archive.org CONNECT 403, twice-witnessed
    pages_total=842,
    pages_in_frame=frozenset())


# ── HER page record: the ten fields, with the no-silent-promotion law ───

@dataclass(frozen=True)
class PageRecord:
    """One page, read by HER. OBSERVED and INFERRED_CLAIMS are disjoint
    by construction — an inference that appears in OBSERVED is a silent
    promotion and the record refuses to exist."""
    page_id: str
    observed: tuple = ()              # what the page literally shows
    technical_objects: tuple = ()
    relations: tuple = ()             # (src, dst, relation) literally on-page
    explicit_claims: tuple = ()       # the page's own assertions
    inferred_claims: tuple = ()       # HER's readings — never facts
    surprises: tuple = ()
    contradictions: tuple = ()
    missing_witnesses: tuple = ()
    future_candidate: str = ""
    confidence: float = 0.0

    def __post_init__(self):
        if set(self.observed) & set(self.inferred_claims):
            raise ValueError("E_SILENT_PROMOTION")
        if set(self.explicit_claims) & set(self.inferred_claims):
            raise ValueError("E_SILENT_PROMOTION")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("E_CONFIDENCE_RANGE")


def her_read_page(corpus: Corpus1851, page_id: str,
                  record: PageRecord | None = None) -> dict:
    """The read gate. A page not delivered in-frame yields UNKNOWN —
    HER does not narrate pages she has not seen."""
    if corpus.availability != AVAILABLE and page_id not in corpus.pages_in_frame:
        return {"status": "UNKNOWN", "reason": "E_PAGE_NOT_IN_FRAME",
                "page_id": page_id}
    if page_id not in corpus.pages_in_frame:
        return {"status": "UNKNOWN", "reason": "E_PAGE_NOT_IN_FRAME",
                "page_id": page_id}
    if record is None or record.page_id != page_id:
        return {"status": "UNKNOWN", "reason": "E_NO_RECORD_FOR_PAGE",
                "page_id": page_id}
    return {"status": "READ", "record": record}


# ── C6: three clocks ────────────────────────────────────────────────────

@dataclass(frozen=True)
class Tau:
    """tau(q) = (t_event, t_source, t_record). Each clock answers a
    different question and none substitutes for another."""
    t_event: str = ""                 # when the thing happened (may be older)
    t_source: str = ""                # when the source says so (1851)
    t_record: str = ""                # when we extracted it (this frame)

    def observation_date(self) -> str:
        """An 1851 catalogue reporting something older made its
        observation in 1851 — never at the older date."""
        return self.t_source or self.t_record or "UNKNOWN"

    def event_date(self) -> str:
        """Never backfilled from the source clock (kill K6 upstream)."""
        return self.t_event or "UNKNOWN"


# ── C4: authority gravity ───────────────────────────────────────────────

@dataclass(frozen=True)
class GraphNode:
    node_id: str
    grade: str                        # in GRADES
    pages: tuple = ()                 # supporting page ids

    def __post_init__(self):
        _grade_rank(self.grade)


@dataclass(frozen=True)
class GraphEdge:
    """A functional relationship. Its authority is CAPPED by its weakest
    endpoint; corpus-internal convergence adds nothing."""
    src: str
    dst: str
    relation: str
    basis: str                        # "on_page" | "component_existence" | ...
    grade: str = "INFERRED"

    def __post_init__(self):
        _grade_rank(self.grade)
        if self.basis == "component_existence" and self.grade in (
                "OBSERVED", "REPORTED"):
            # C1/K4: parts on shelves never witness the machine
            raise ValueError("E_COMPONENTS_ARE_NOT_A_COMBINATION")


def edge_authority(edge: GraphEdge, nodes: dict,
                   convergent_pages: tuple = (),
                   external_witnesses: tuple = ()) -> dict:
    """A(e) <= min_i A(v_i). convergent_pages (more corpus pages saying
    the same thing) contribute ZERO. One independent EXTERNAL witness
    with a receipt raises the cap by exactly one grade."""
    endpoint_rank = min(_grade_rank(nodes[edge.src].grade),
                        _grade_rank(nodes[edge.dst].grade))
    cap = min(_grade_rank(edge.grade), endpoint_rank)
    raised = False
    for w in external_witnesses:
        if isinstance(w, dict) and w.get("kind") == "external" and w.get("receipt"):
            cap = min(cap + 1, len(GRADES) - 1)
            raised = True
            break                      # one grade, not one per witness
    return {"authority": GRADES[cap],
            "convergence_counted": 0,           # structurally zero
            "convergent_pages_seen": len(convergent_pages),
            "raised_by_external_witness": raised}


# ── C3: latent adjacent possible ────────────────────────────────────────

def adjacent_possible(neighbourhood: frozenset, components: tuple) -> dict:
    """What machine becomes possible from ONLY the contemporaneous
    neighbourhood N_k(p)? A component outside it is refused — this is
    lineage closure pointed at 1851."""
    outside = sorted(set(components) - neighbourhood)
    if outside:
        return {"verdict": "REJECT", "reason": "E_OUTSIDE_NEIGHBOURHOOD",
                "components_outside_Nk": outside}
    return {"verdict": "CANDIDATE", "status": "HYPOTHESIS",
            "note": "generable from N_k(p); Generable ⊬ HistoricallyObserved"}


# ── K_1851 = (V, E, M): the motif layer ─────────────────────────────────

@dataclass(frozen=True)
class Motif:
    """A reusable operational motif — the corpus's grammar, not its
    nouns. Must cite witness frames; carries its own forbidden
    promotions (analogy is not lineage). Grade caps at REPORTED when
    the witness is a relayed seat-read: ObservedThere ⊬ ObservedHere."""
    motif_id: str
    structure: tuple                  # ordered stages
    witness_frames: tuple             # frame-qualified canvas ids
    grade: str = "REPORTED"
    forbidden_promotions: tuple = ()
    kind: str = "motif"               # motif | falsifier
    corpus_scope: str = "vol1"

    def __post_init__(self):
        _grade_rank(self.grade)
        if not self.witness_frames:
            raise ValueError("E_UNWITNESSED_MOTIF")


def promote_motif(motif: Motif, target: str) -> dict:
    """A motif's structural resemblance to a later concept is an
    analogy. Promoting it to that concept is refused at the type."""
    if target in motif.forbidden_promotions:
        return {"verdict": "REFUSED", "reason": "E_ANALOGY_IS_NOT_LINEAGE",
                "motif": motif.motif_id, "to": target}
    return {"verdict": "NOT_A_KNOWN_PROMOTION",
            "motif": motif.motif_id, "to": target}


def atlas_scope_check(atlas_scope: str, motif: Motif) -> dict:
    """C_Vol1 != C_all_Great_Exhibition. A witness from Volumes 2-4
    (the arithmometer's actual home) never enters the Vol-1 atlas —
    NO_PROMOTION_ACROSS_CORPUS_BOUNDARY."""
    if motif.corpus_scope != atlas_scope:
        return {"verdict": "REJECT", "reason": "E_CORPUS_BOUNDARY",
                "atlas_scope": atlas_scope, "motif_scope": motif.corpus_scope}
    return {"verdict": "IN_SCOPE", "atlas_scope": atlas_scope}


def t11_authority_gravity(edge: GraphEdge, nodes: dict,
                          coherent_observations: tuple) -> dict:
    """T11 AUTHORITY_GRAVITY. Given N mutually coherent low-authority
    observations, an attempt to raise an inferred edge's authority
    because graph coherence Gamma increased is REJECTED. dA/dGamma = 0,
    structurally: the refusal is unconditional on N."""
    before = edge_authority(edge, nodes)["authority"]
    return {"attempt": "raise_authority_via_coherence",
            "gamma": len(coherent_observations),
            "verdict": "REJECT_INDEPENDENT_WITNESS_MISSING",
            "law": "Gamma-up does not imply A-up",
            "authority_before": before,
            "authority_after": before}


# ── C5: forbidden semantic promotions ───────────────────────────────────

FORBIDDEN_PROMOTIONS = {
    "described as patent": "verified patent",
    "called inventor": "legally established inventor",
    "exhibited in 1851": "novel as of 1851",
}


def promote_claim(claim: str, target: str, witnesses: tuple = ()) -> dict:
    """The corpus's own words never climb the legal/novelty ladder.
    Promotion needs an independent external witness with a receipt."""
    if FORBIDDEN_PROMOTIONS.get(claim) == target:
        has_external = any(
            isinstance(w, dict) and w.get("kind") == "external"
            and w.get("receipt") for w in witnesses)
        if not has_external:
            return {"verdict": "REFUSED", "reason": "E_SEMANTIC_SHORTCUT",
                    "from": claim, "to": target}
        return {"verdict": "PROMOTED_WITH_WITNESS", "from": claim,
                "to": target, "witnesses": len(witnesses)}
    return {"verdict": "NOT_A_KNOWN_PROMOTION", "from": claim, "to": target}


# ── C2: the novelty measure, held at HYPOTHESIS ─────────────────────────

@dataclass(frozen=True)
class NoveltyHypothesis:
    """N(I) = alpha*N_V + beta*N_E, beta >> alpha — a hypothesis to
    TEST, not assume. It never carries a verdict."""
    alpha: float = 1.0
    beta: float = 4.0
    status: str = "HYPOTHESIS"

    def score(self, n_v: float, n_e: float) -> float:
        return self.alpha * n_v + self.beta * n_e


def rv_re(recovered_v: int, total_v: int, recovered_e: int, total_e: int,
          freeze_receipt: dict | None = None,
          recovered_m: int | None = None, total_m: int | None = None) -> dict:
    """The central statistic — computable ONLY against a clean freeze.
    Without one, the number would be hindsight wearing a ratio. R_M
    (motif recoverability) joins R_V and R_E when the motif layer is
    counted: the sharpened hypothesis is R_V ~ 1, R_M high, R_E < R_M —
    later invention as new composition of old motifs."""
    if not freeze_receipt or freeze_receipt.get("contamination"):
        return {"status": "UNKNOWN", "reason": "E_NO_CLEAN_FREEZE"}
    r_v = recovered_v / total_v if total_v else 0.0
    r_e = recovered_e / total_e if total_e else 0.0
    out = {"status": "MEASURED", "R_V": r_v, "R_E": r_e,
           "chiddush_supported": r_v > r_e,
           "note": "if R_V >> R_E, novelty is disproportionately "
                   "relational — a claim worth trying hard to kill"}
    if total_m is not None:
        out["R_M"] = (recovered_m or 0) / total_m if total_m else 0.0
    return out


# ── C7: the freeze ──────────────────────────────────────────────────────

def freeze_candidates(candidates: tuple, access_log: tuple = ()) -> dict:
    """Hash the candidate set BEFORE any post-1851 data enters. Every
    prior access to future data is recorded as contamination on the
    receipt — the freeze does not launder it, it remembers it."""
    contamination = tuple(
        e for e in access_log
        if isinstance(e, dict) and e.get("kind") == "POST_1851_CONSULT")
    return {"freeze_hash": canon_hash([canon(c.__dict__)
                                       if hasattr(c, "__dict__") else canon(c)
                                       for c in candidates]),
            "candidate_count": len(candidates),
            "contamination": contamination}


# ── HER -> HAL compost packet ───────────────────────────────────────────

@dataclass(frozen=True)
class CompostPacket:
    """What HER sends — never 842 pages of prose. explicit_vs_inferred
    is a dict {"explicit": (...), "inferred": (...)}; overlap is K2."""
    candidate_id: str
    supporting_pages: tuple = ()
    primitive_nodes: tuple = ()       # GraphNode
    inferred_edges: tuple = ()        # GraphEdge
    explicit_vs_inferred: dict = field(default_factory=dict)
    temporal_provenance: tuple = ()   # (claim_id, Tau, claimed_event_date)
    information_loss: str = ""
    assumptions_added: tuple = ()
    independent_witnesses: tuple = () # dicts: {"kind": ..., "receipt": ...}
    counterevidence: tuple = ()
    leakage_risk: str = "UNKNOWN"
    novelty_hypothesis: str = "INSIGHT"   # INSIGHT | HISTORICAL_FACT |
    falsifier: dict = field(default_factory=dict)  # PATENT_CLAIM | NOVELTY_CLAIM


# ── HAL: kill conditions, then S = E ∧ P ∧ L ∧ F ───────────────────────

KILL_CONDITIONS = (
    "K1_FUTURE_DATA_BEFORE_FREEZE",
    "K2_INFERENCE_AS_OBSERVATION",
    "K3_CONVERGENCE_AS_WITNESS",
    "K4_COMPONENTS_AS_COMBINATION",
    "K5_PATENT_WORD_AS_PATENT_FACT",
    "K6_SOURCE_DATE_AS_EVENT_DATE",
)

ESCALATE_CLASSES = frozenset(
    {"HISTORICAL_FACT", "PATENT_CLAIM", "NOVELTY_CLAIM"})

SHIP_DOES_NOT_LICENSE = ("HISTORICAL_FACT", "PATENT_FACT", "NOVELTY_CLAIM",
                         "ADMISSION", "LEDGER_EFFECT")


def detect_kills(packet: CompostPacket, freeze_receipt: dict) -> list:
    kills = []
    if freeze_receipt.get("contamination"):
        kills.append("K1_FUTURE_DATA_BEFORE_FREEZE")
    exp = set(packet.explicit_vs_inferred.get("explicit", ()))
    inf = set(packet.explicit_vs_inferred.get("inferred", ()))
    if exp & inf:
        kills.append("K2_INFERENCE_AS_OBSERVATION")
    if any(isinstance(w, dict) and w.get("kind") == "corpus_convergence"
           for w in packet.independent_witnesses):
        kills.append("K3_CONVERGENCE_AS_WITNESS")
    # K4 is mostly unconstructible (GraphEdge refuses), but a packet can
    # still smuggle the assertion as prose in assumptions_added:
    if any("components imply combination" in str(a).lower()
           for a in packet.assumptions_added):
        kills.append("K4_COMPONENTS_AS_COMBINATION")
    promoted = set(FORBIDDEN_PROMOTIONS.values())
    has_external = any(isinstance(w, dict) and w.get("kind") == "external"
                       and w.get("receipt")
                       for w in packet.independent_witnesses)
    if not has_external and any(str(a) in promoted
                                for a in packet.assumptions_added):
        kills.append("K5_PATENT_WORD_AS_PATENT_FACT")
    for _cid, tau, claimed in packet.temporal_provenance:
        if tau.event_date() == "UNKNOWN" and claimed == tau.t_source:
            kills.append("K6_SOURCE_DATE_AS_EVENT_DATE")
            break
    return kills


def hal_verdict(packet: CompostPacket, freeze_receipt: dict) -> dict:
    """Deterministic reduction. Four terminal states, no fifth:
    NO_SHIP (killed) > ESCALATE (needs external gate) >
    SHIP_INSIGHT (S holds) > HOLD (under-witnessed)."""
    kills = detect_kills(packet, freeze_receipt)
    if kills:
        return {"verdict": "NO_SHIP", "glyph": "❌",
                "kill_conditions": kills}
    if packet.novelty_hypothesis in ESCALATE_CLASSES:
        return {"verdict": "ESCALATE", "glyph": "⚖️",
                "reason": "external patent/archival verification required",
                "class": packet.novelty_hypothesis}
    e = bool(packet.supporting_pages) and all(
        n.pages for n in packet.primitive_nodes)
    p = bool(packet.information_loss) and packet.assumptions_added is not None
    l = (not freeze_receipt.get("contamination")
         and bool(freeze_receipt.get("freeze_hash")))
    f = (packet.falsifier.get("executed") is True
         and packet.falsifier.get("survived") is True)
    gates = {"E_evidence_bound": e, "P_provenance_preserved": p,
             "L_no_leakage": l, "F_falsifier_survived": f}
    if all(gates.values()):
        return {"verdict": "SHIP_INSIGHT", "glyph": "🌹", "gates": gates,
                "licenses": "corpus-derived finding only",
                "does_not_license": SHIP_DOES_NOT_LICENSE,
                "admits": False}
    return {"verdict": "HOLD", "glyph": "🌿", "gates": gates,
            "missing": sorted(k for k, v in gates.items() if not v)}
