"""SENTINEL_LOOP_V0 — iterative-deepening corpus loop with remembered coverage. authority=false · canon=false ·
ledger_effect=none. NON-SOVEREIGN. Corpus-agnostic STATE MACHINE + PROMOTION GATE — it does NOT read the Drive
(no connector here); the Drive-connected side feeds it claim-atoms per file, and this governs accumulation,
novelty, and promotion so the loop is CUMULATIVE and GOODHART-GUARDED.

Loop:  MAP → READ → EXTRACT → LINK → FALSIFY → EXPAND → COMPRESS → STATE   (state persists between rounds)

Load-bearing invariants (the whole reason this exists):
  - EXTRACT: a claim is admissible knowledge ONLY with provenance. c=(claim,source,date,entity,evidence_class,root_id).
             evidence_class ∈ {OBSERVED, REPORTED, INFERRED, PROPOSAL, UNKNOWN}. No source / UNKNOWN ⇒ NOT_KNOWLEDGE.
  - PROMOTION LADDER:
        1 source                      → OBSERVATION
        ≥N INDEPENDENT ROOTS (N_epi)  → PATTERN        (fan-out law: many docs from one root = one root)
        PATTERN + survived FALSIFY    → CHIDDUSH
  - NOVELTY has the FALSIFY gate INSIDE it: only WITNESSED novelty counts. Source-less/UNKNOWN claims contribute 0.
    A "pattern" that failed falsification is demoted, not counted. Hallucinated structure cannot inflate novelty.
  - STOP when novelty < ε for K consecutive rounds, or coverage ≥ target, or budget exhausted. (HOLD = knowledge.)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

EVIDENCE_CLASSES = {"OBSERVED", "REPORTED", "INFERRED", "PROPOSAL", "UNKNOWN"}
N_INDEPENDENT = 2          # roots required for a PATTERN (N_epi threshold, not N_repr)
EPS = 0.15                 # novelty stopping threshold
K_DRY = 3                  # consecutive low-novelty rounds ⇒ stop


@dataclass(frozen=True)
class ClaimAtom:
    claim: str
    source: str                 # provenance (file/url/person) — REQUIRED for knowledge
    date: str
    entity: str
    evidence_class: str         # EPISTEMIC_SYNTAX
    root_id: str                # the INDEPENDENT epistemic root this derives from (fan-out control)

    def is_knowledge(self) -> bool:
        return bool(self.source.strip()) and self.evidence_class in EVIDENCE_CLASSES and self.evidence_class != "UNKNOWN"


@dataclass(frozen=True)
class Falsification:
    hypothesis: str
    attempted: bool             # was a contra-search actually run?
    refuting_witness: str       # non-empty ⇒ the hypothesis was refuted
    @property
    def refuted(self) -> bool:
        return bool(self.refuting_witness.strip())
    @property
    def survived(self) -> bool:
        return self.attempted and not self.refuted


def classify(c: ClaimAtom) -> str:
    return "OBSERVATION" if c.is_knowledge() else "NOT_KNOWLEDGE"


def independent_roots(claims: List[ClaimAtom]) -> Set[str]:
    return {c.root_id for c in claims if c.is_knowledge()}


def is_pattern(claims_for_hypothesis: List[ClaimAtom]) -> bool:
    """PATTERN iff ≥ N_INDEPENDENT distinct roots among knowledge-grade claims (fan-out defeated)."""
    return len(independent_roots(claims_for_hypothesis)) >= N_INDEPENDENT


def is_chiddush(claims_for_hypothesis: List[ClaimAtom], fals: Optional[Falsification]) -> bool:
    """CHIDDUSH iff PATTERN holds AND a falsification was attempted AND it survived."""
    return is_pattern(claims_for_hypothesis) and fals is not None and fals.survived


@dataclass
class SentinelState:
    # coverage (MAP)
    seen_files: Set[str] = field(default_factory=set)
    fully_read_files: Set[str] = field(default_factory=set)
    partially_read_files: Set[str] = field(default_factory=set)
    unread_subtrees: Set[str] = field(default_factory=set)
    # graph (EXTRACT/LINK)
    entities_seen: Set[str] = field(default_factory=set)
    queries_executed: Set[str] = field(default_factory=set)
    claims: List[ClaimAtom] = field(default_factory=list)
    contradictions: List[Tuple[str, str, str]] = field(default_factory=list)
    open_witnesses: Set[str] = field(default_factory=set)       # edge-directed frontier (missing witnesses)
    # promotions
    patterns: Dict[str, bool] = field(default_factory=dict)     # hypothesis -> is_pattern
    chiddushim: Dict[str, bool] = field(default_factory=dict)   # hypothesis -> is_chiddush
    falsifications: Dict[str, Falsification] = field(default_factory=dict)
    # loop
    round: int = 0
    novelty_history: List[float] = field(default_factory=list)

    def ingest_round(self, *, read_files: List[str], partial_files: List[str],
                     new_claims: List[ClaimAtom], new_contradictions: List[Tuple[str, str, str]],
                     new_open_witnesses: List[str], new_relations: List[str],
                     queries: List[str], docs_read: int) -> dict:
        """One EXTRACT/LINK/FALSIFY/EXPAND round. Returns the round's novelty + what advanced (WITNESSED only)."""
        self.round += 1
        self.seen_files.update(read_files + partial_files)
        self.fully_read_files.update(read_files)
        self.partially_read_files.update(f for f in partial_files if f not in self.fully_read_files)
        self.queries_executed.update(queries)
        self.claims.extend(new_claims)
        self.contradictions.extend(new_contradictions)
        for c in new_claims:
            if c.entity: self.entities_seen.add(c.entity)
        self.open_witnesses.update(new_open_witnesses)
        # NOVELTY with the falsify/provenance gate INSIDE: only knowledge-grade novelty counts
        witnessed_claims = [c for c in new_claims if c.is_knowledge()]
        num = len(witnessed_claims) + len(new_relations) + len(new_contradictions) + len(new_open_witnesses)
        nov = num / max(1, docs_read)
        self.novelty_history.append(nov)
        return {"round": self.round, "novelty": round(nov, 4),
                "witnessed_new_claims": len(witnessed_claims), "dropped_no_provenance": len(new_claims) - len(witnessed_claims),
                "new_relations": len(new_relations), "new_contradictions": len(new_contradictions),
                "frontier_growth": len(new_open_witnesses)}

    def falsify(self, hypothesis: str, fals: Falsification) -> None:
        self.falsifications[hypothesis] = fals

    def derive(self, hypotheses: Dict[str, List[ClaimAtom]]) -> dict:
        """COMPRESS: recompute patterns/chiddushim from current claims + falsifications. Pure over inputs."""
        for h, cs in hypotheses.items():
            self.patterns[h] = is_pattern(cs)
            self.chiddushim[h] = is_chiddush(cs, self.falsifications.get(h))
        return {"patterns": [h for h, v in self.patterns.items() if v],
                "chiddushim": [h for h, v in self.chiddushim.items() if v],
                "demoted": [h for h, v in self.chiddushim.items() if not v and self.patterns.get(h)]}

    def should_continue(self, coverage: float, target: float, budget_remaining: bool) -> Tuple[bool, str]:
        if not budget_remaining:
            return False, "STOP:budget_exhausted"
        if coverage >= target:
            return False, "STOP:coverage_target_reached"
        recent = self.novelty_history[-K_DRY:]
        if len(recent) >= K_DRY and all(n < EPS for n in recent):
            return False, "STOP:novelty_dry (HOLD — no discriminating reads under budget)"
        return True, "CONTINUE"

    def report(self) -> dict:
        return {"round": self.round,
                "coverage": {"fully_read": len(self.fully_read_files), "partial": len(self.partially_read_files),
                             "seen": len(self.seen_files), "unread_subtrees": len(self.unread_subtrees)},
                "entities": len(self.entities_seen), "claims_total": len(self.claims),
                "claims_knowledge": sum(c.is_knowledge() for c in self.claims),
                "contradictions": len(self.contradictions), "open_witnesses": sorted(self.open_witnesses),
                "patterns": sorted(h for h, v in self.patterns.items() if v),
                "chiddushim": sorted(h for h, v in self.chiddushim.items() if v),
                "last_novelty": self.novelty_history[-1] if self.novelty_history else None,
                "authority": False, "canon": False, "ledger_effect": "none"}


# EXPAND: the corpus generates the next search (default keyword frontier; Drive side may override).
def expand_queries(c: ClaimAtom) -> Set[str]:
    toks = {t.strip(".,;:()[]").lower() for t in (c.claim + " " + c.entity).split() if len(t) > 3}
    frontier = {c.entity, c.date} | toks
    return {q for q in frontier if q}
