"""UZIK_DEEP_EXTRACTION_V1 — the ORGANE (generic epistemic-memory machinery).

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Separation law (upgrade 9): this module is ORGANE — it contains no
UZIK/Calvi/Manucurist facts. INSTANCE evidence lives in fixtures; GARDEN
nutrients are derived; KERNEL admission has no path through this file
(there is no admit surface, and nutrients are constructed admission=False
by a frozen dataclass).

Governing theorem (upgrade 10): HELEN does not learn by swallowing the
corpus; it learns by preserving the distinctions the corpus forces:
  typed relation ≠ RELATED_TO            contact ≠ influence
  UNKNOWN ≠ ABSENT_AFTER_SEARCH          instances ≠ corroborations
  resemblance ≠ authorship               shape preserved ≠ identity preserved
  generated ≠ canonical                  garden ≠ kernel

Deterministic: sha256 over canonical JSON; no wall-time, no randomness.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace

# --- typed relations (upgrade 1): no generic edges -----------------------

EDGE_TYPES = frozenset({
    "ORGANIZED", "COFOUNDED_REPORTED", "PARTNER_OF", "CREATIVE_CREDIT",
    "CORPORATE_ROLE", "CANCELLED", "TRANSFORMED_INTO",
    "VISUAL_SIMILARITY_CANDIDATE", "DERIVED_FROM",
})

# GLYPH_TRAP (upgrade 6): claims visual evidence may never mint.
GLYPH_TRAP_FORBIDDEN = frozenset({"SAME_DESIGNER", "UZIK_SIGNATURE",
                                  "CAUSAL_LINEAGE", "CREATIVE_CREDIT"})

# Evidence-class rank: a direct documentary credit outranks resemblance.
EVIDENCE_RANK = {"documentary": 2, "visual": 1}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def h(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# --- source registry + replayable chain (upgrade 2) ----------------------

@dataclass(frozen=True)
class Source:
    source_id: str
    family: str                      # press | registry | social | synthetic_fixture ...
    locator: str
    retrieval_receipt: str           # hash of retrieval evidence
    content_hash: str
    derived_from: str = ""           # lineage pointer for repost clustering


@dataclass(frozen=True)
class Claim:
    claim_id: str
    subject: str
    relation: str
    obj: str
    time_span: str
    status: str                      # REPORTED | DISPUTED
    evidence_class: str              # documentary | visual
    source_ids: tuple


class EvidenceGraph:
    def __init__(self):
        self.sources: dict[str, Source] = {}
        self.claims: dict[str, Claim] = {}

    def register_source(self, **kw) -> Source:
        s = Source(**kw)
        self.sources[s.source_id] = s
        return s

    def add_claim(self, subject, relation, obj, time_span, source_ids,
                  evidence_class="documentary", status="REPORTED") -> Claim:
        if relation not in EDGE_TYPES:
            raise ValueError(f"E_UNTYPED_RELATION:{relation}")
        if evidence_class == "visual" and relation != "VISUAL_SIMILARITY_CANDIDATE":
            raise ValueError(f"E_GLYPH_TRAP:{relation}")   # resemblance ≠ authorship
        missing = [s for s in source_ids if s not in self.sources]
        if missing:
            raise ValueError(f"E_UNREGISTERED_SOURCE:{missing[0]}")
        c = Claim(h((subject, relation, obj, time_span, tuple(source_ids)))[:16],
                  subject, relation, obj, time_span, status, evidence_class,
                  tuple(source_ids))
        self.claims[c.claim_id] = c
        return c

    # -- replay (upgrade 2): "why do you know this?" as an executable path
    def replay(self, claim_ids: tuple) -> dict:
        path, ok = [], True
        for cid in claim_ids:
            c = self.claims.get(cid)
            if c is None:
                return {"verdict": "UNKNOWN", "reason": f"E_NO_CLAIM:{cid}", "path": path}
            step = {"claim": cid, "sources": []}
            for sid in c.source_ids:
                s = self.sources.get(sid)
                if s is None or not s.retrieval_receipt:
                    ok = False
                    step["sources"].append({"source": sid, "receipt": "MISSING"})
                else:
                    step["sources"].append({"source": sid,
                                            "receipt": s.retrieval_receipt,
                                            "content_hash": s.content_hash})
            path.append(step)
        return {"verdict": "REPLAYED" if ok else "UNKNOWN", "path": path}

    # -- independence (upgrade 4): instances ≠ corroborations
    def independent_origins(self, claim: Claim) -> int:
        roots = set()
        for sid in claim.source_ids:
            s = self.sources[sid]
            seen = set()
            while s.derived_from and s.derived_from in self.sources and s.source_id not in seen:
                seen.add(s.source_id)
                s = self.sources[s.derived_from]
            roots.add(s.content_hash if not s.derived_from else s.derived_from)
        return len(roots)

    # -- authorship ranking (upgrade 6): credit outranks resemblance
    def authorship_verdict(self, subject, obj) -> str:
        best = None
        for c in self.claims.values():
            if {c.subject, c.obj} == {subject, obj}:
                rank = EVIDENCE_RANK.get(c.evidence_class, 0)
                if best is None or rank > best[0]:
                    best = (rank, c)
        if best is None:
            return "UNKNOWN"
        rank, c = best
        if c.evidence_class == "documentary" and c.relation == "CREATIVE_CREDIT":
            return "CREDITED"
        return "VISUAL_SIMILARITY_CANDIDATE"   # never silently SAME_DESIGNER


# --- coverage-aware UNKNOWN (upgrade 3) ----------------------------------

@dataclass(frozen=True)
class Census:
    """PUBLIC_CORPUS_CENSUS(v, t, C): declared coverage cells."""
    version: str
    as_of: str
    cells: frozenset                 # {(entity, year_range, family, relation)}

    def covers(self, entity, year_range, family, relation) -> bool:
        return (entity, year_range, family, relation) in self.cells


def absence_verdict(graph: EvidenceGraph, census: Census,
                    entity, relation, year_range, family) -> dict:
    for c in graph.claims.values():
        if c.subject == entity and c.relation == relation and c.time_span == year_range:
            return {"verdict": "PRESENT", "claims": [c.claim_id]}
    if census.covers(entity, year_range, family, relation):
        return {"verdict": "ABSENT_AFTER_SEARCH",
                "coverage": {"census": census.version, "as_of": census.as_of,
                             "cell": [entity, year_range, family, relation]}}
    return {"verdict": "UNKNOWN", "reason": "E_NO_COVERAGE"}


# --- ETA transformation receipts (upgrade 7) -----------------------------

def eta_receipt(input_bytes: bytes, operation: str, params: dict,
                software: str, output_bytes: bytes) -> dict:
    return {"input_hash": hashlib.sha256(input_bytes).hexdigest(),
            "operation": operation, "params": params, "software": software,
            "output_hash": hashlib.sha256(output_bytes).hexdigest()}


def verify_eta_chain(original: bytes, final: bytes, receipts: list[dict]) -> dict:
    """Shape preservation proves nothing; only an unbroken receipt chain
    binds an output to its source identity."""
    if not receipts:
        return {"verdict": "UNKNOWN", "reason": "E_NO_RECEIPTS"}
    cur = hashlib.sha256(original).hexdigest()
    for i, r in enumerate(receipts):
        if r["input_hash"] != cur:
            return {"verdict": "UNKNOWN", "reason": f"E_CHAIN_BROKEN:{i}"}
        cur = r["output_hash"]
    if cur != hashlib.sha256(final).hexdigest():
        return {"verdict": "UNKNOWN", "reason": "E_FINAL_MISMATCH"}
    return {"verdict": "BOUND", "steps": len(receipts)}


# --- temporal chiddush (upgrade 5) ---------------------------------------

def transition_report(graph: EvidenceGraph, stages: list[str],
                      entity: str) -> list[dict]:
    """Each transition t_i -> t_{i+1} must name its supporting claims;
    an unsupported transition is UNKNOWN, never narrated as known."""
    out = []
    for a, b in zip(stages, stages[1:]):
        support = [c.claim_id for c in graph.claims.values()
                   if c.relation == "TRANSFORMED_INTO"
                   and c.subject == f"{entity}:{a}" and c.obj == f"{entity}:{b}"]
        out.append({"from": a, "to": b,
                    "verdict": "SUPPORTED" if support else "UNKNOWN",
                    "claims": support})
    return out


# --- nutrients that can refuse themselves (upgrade 8) --------------------

@dataclass(frozen=True)
class Nutrient:
    nutrient_id: str
    statement: str
    support: tuple = ()              # claim_ids
    counterevidence: tuple = ()      # claim_ids
    unknowns: tuple = ()
    absent_after_search: tuple = ()
    independence_clusters: int = 0
    visual_status: str = "NONE"
    eta_claims: tuple = ()
    replay_receipt: str = ""
    calibration: str = "UNCALIBRATED"
    status: str = "CANDIDATE"
    authority: bool = False          # frozen; there is no admit path
    admission: bool = False

    def __post_init__(self):
        if self.authority or self.admission:
            raise ValueError("E_GARDEN_IS_NOT_KERNEL")

    def self_refusal(self, graph: EvidenceGraph) -> "Nutrient":
        """A generated insight cannot become canonical because HELEN
        generated it — and it composts itself when its own dossier
        argues against it."""
        if not self.support:
            return replace(self, status="COMPOSTED")
        if len(self.counterevidence) >= len(self.support):
            return replace(self, status="COMPOSTED")
        if self.replay_receipt and graph.replay(self.support)["verdict"] != "REPLAYED":
            return replace(self, status="COMPOSTED")
        return replace(self, status="STANDING")
