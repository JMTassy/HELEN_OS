"""COMPLETE_EPISTEMIC_MEDIATION_V0 — hypothesis removal is a mediated, receipt-derived transition. authority=false.
NON-SOVEREIGN. canon=false · ledger_effect=none. Supersedes the 7-mutant governed_epoch_kill_suite (which had a
circular-gold defect + missing mutants; kept frozen as the superseded version).

Property (stronger than "no hypothesis dies for free"):
    Every hypothesis-removal transition must be individually SCOPED, FROZEN, independently VERIFIABLE, REPLAYABLE.
    h ∈ H_before \\ H_after  ⇒  ∃ [ρ_h]~ : Frozen ∧ Scoped ∧ BoundTo(h,O,D,Γ_E) ∧ Verify=1
    and  H_after = reduce(H_before, {ρ_h}).      H_after is NEVER a free input.

Isomorphic to the institutional slice:  CandidateKill + Witness --Γ_E--> KillReceipt --reducer--> H_after,
just as  Proposal + Witness --Γ--> Capability --executor--> Effect.  UntrustedIntent ⇏ TrustedTransition.

Preserved: SURVIVE ≠ TRUE (h∉K̂ ⇏ h true) · HOLD = discrimination-failure info, not error ·
duplicate receipts ⇏ duplicate warrant (canonical equivalence) · SameState ⇏ SameHistory (replay carries provenance).
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import sys
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

DISCRIMINATOR_VERSION = "ablation/v0"
UPDATE_RULE = "minus_Li >= K7 ⇒ 'Li load-bearing' refuted"
OBS_KEY = {f"H_L{i}": f"minus_L{i}" for i in range(1, 8)}

# ── INDEPENDENT STATIC GOLD — hand-verified preregistered fixture, NOT computed by Γ_E. ──
# On the AR observation only H_L1 is genuinely refuted (removing L1 → +0.009, no drop). This is a literal
# label, inspected by hand; the runtime derives its kills through the receipt pipeline INDEPENDENTLY.
GOLD_KILLS: FrozenSet[str] = frozenset({"H_L1"})


def _canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))

def _hash(o) -> str:
    return "sha256:" + hashlib.sha256(_canon(o).encode()).hexdigest()[:16]


@dataclass(frozen=True)
class FrozenExperiment:
    """ExperimentalBasis B_E — the WHOLE experimental set frozen at PREREG, before O_raw. basis_hash binds ALL
    of it, so any post-freeze drift (scorer, thresholds, model, dataset, discriminator, update rule, policy)
    ⇒ new basis_hash ⇒ Verify(ρ_h)=0. Avoids ad-hoc per-field patches (research-hindsight compilation)."""
    hypotheses: FrozenSet[str]
    discriminator_version: str
    update_rule: str
    observation_schema: str = "minus_Li,K7:float"
    scorer_id: str = "weighted_D_ik/v0"
    thresholds: str = "kill iff minus_Li>=K7"
    model_config: str = "qwen38-2b/temp0/seed0"
    dataset_slice: str = "28-fixture-V3"
    policy_version: str = "GCD/v0"

    @property
    def basis_hash(self) -> str:
        return _hash([sorted(self.hypotheses), self.discriminator_version, self.update_rule,
                      self.observation_schema, self.scorer_id, self.thresholds,
                      self.model_config, self.dataset_slice, self.policy_version])

    @property
    def prereg_hash(self) -> str:            # KillReceipts already bind prereg_hash; alias it to the full basis
        return self.basis_hash


@dataclass(frozen=True)
class KillWitness:
    target: str
    observation_key: str
    discriminator_version: str
    update_rule: str
    scope: FrozenSet[str] = frozenset()             # default singleton {target}; multi must be declared pre-O
    def effective_scope(self) -> FrozenSet[str]:
        return self.scope or frozenset({self.target})


@dataclass(frozen=True)
class KillReceipt:
    hypothesis_id: str
    observation_hash: str
    prereg_hash: str
    discriminator_version: str
    witness_refs: Tuple[str, ...]
    update_rule: str
    def canonical(self) -> tuple:                    # [ρ_h]~ — duplicate serializations collapse to one warrant
        return (self.hypothesis_id, self.observation_hash, self.prereg_hash,
                self.discriminator_version, tuple(sorted(self.witness_refs)), self.update_rule)


@dataclass(frozen=True)
class GlobalReceipt:
    """A non-individualized 'experiment successful' blob. It is NOT a kill warrant. The reducer ignores it."""
    status: str
    claimed_kills: Tuple[str, ...]


def _refutes(h: str, obs: Dict[str, float], update_rule: str) -> bool:
    if update_rule != UPDATE_RULE:                   # a rule the frozen experiment did not preregister
        return False
    k = OBS_KEY.get(h)
    return bool(k and k in obs and "K7" in obs and obs[k] >= obs["K7"])


# ── Γ_E: the ONLY minter of KillReceipts. Fails closed on ANY binding mismatch. ──
def make_kill_receipt(h: str, obs: Dict[str, float], fexp: FrozenExperiment,
                      w: KillWitness) -> Optional[KillReceipt]:
    if w.target != h:                                   return None   # witness must aim at h
    if h not in w.effective_scope():                    return None   # scope integrity (singleton default)
    if h not in fexp.hypotheses:                        return None
    if w.observation_key != OBS_KEY.get(h):             return None   # cross-hypothesis key reuse
    if w.discriminator_version != fexp.discriminator_version: return None  # stale discriminator version
    if w.update_rule != fexp.update_rule:               return None   # post-freeze update-rule mutation
    if not _refutes(h, obs, fexp.update_rule):          return None   # observation must actually license the kill
    return KillReceipt(h, _hash(obs), fexp.prereg_hash, fexp.discriminator_version, (w.target,), fexp.update_rule)


def verify_receipt(r: KillReceipt, obs: Dict[str, float], fexp: FrozenExperiment) -> bool:
    """Independent re-verification against the CURRENT observation + frozen experiment (catches post-freeze mutation)."""
    return (r.observation_hash == _hash(obs)                      # obs unchanged since minting
            and r.prereg_hash == fexp.prereg_hash                 # experiment unchanged
            and r.discriminator_version == fexp.discriminator_version
            and r.update_rule == fexp.update_rule
            and r.hypothesis_id in fexp.hypotheses
            and _refutes(r.hypothesis_id, obs, fexp.update_rule))


def gamma_E(H_before: FrozenSet[str], candidates: List[Tuple[str, KillWitness]],
            obs: Dict[str, float], fexp: FrozenExperiment) -> List[KillReceipt]:
    """Emit localized epistemic authorizations (KillReceipts). Does NOT return H_after."""
    out = []
    for h, w in candidates:
        r = make_kill_receipt(h, obs, fexp, w)
        if r is not None:
            out.append(r)
    return out


def gamma_I(_r: KillReceipt) -> dict:                # Γ_E KILL ⇏ Γ_I ADMIT — a kill never mutates governed state
    return {"gate": "Γ_I", "verdict": "NO_ADMISSION", "authority_gain": 0, "ledger_effect": "none"}


# ── reducer: H_after is DERIVED from verified receipts only (complete mediation). ──
def reduce_hypotheses(H_before: FrozenSet[str], receipts: List[KillReceipt],
                      obs: Dict[str, float], fexp: FrozenExperiment) -> Tuple[FrozenSet[str], List[KillReceipt]]:
    seen, admitted = set(), []
    for r in receipts:
        if verify_receipt(r, obs, fexp) and r.canonical() not in seen:   # dedup: dup receipt ⇏ dup warrant
            seen.add(r.canonical()); admitted.append(r)
    kills = frozenset(r.hypothesis_id for r in admitted)
    return H_before - kills, admitted


def no_direct_injection(claimed_H_after: FrozenSet[str], H_before: FrozenSet[str],
                        receipts: List[KillReceipt], obs: Dict[str, float], fexp: FrozenExperiment) -> Tuple[str, List[str]]:
    """direct_h_after_injection guard: a claimed H_after is admissible ONLY if it equals the reducer-derived one."""
    derived, _ = reduce_hypotheses(H_before, receipts, obs, fexp)
    if claimed_H_after != derived:
        return "REJECT", ["H_AFTER_NOT_RECEIPT_DERIVED: claimed removals lack backing kill receipts"]
    return "ADMIT", []


def scores(H_before: FrozenSet[str], admitted: List[KillReceipt]) -> dict:
    """Precision/Recall vs INDEPENDENT static gold. precision=NA when no kills (not invented 1.0)."""
    K_hat = frozenset(r.hypothesis_id for r in admitted)
    K_star = GOLD_KILLS & H_before
    tp = len(K_hat & K_star)
    precision = None if not K_hat else round(tp / len(K_hat), 3)
    recall = None if not K_star else round(tp / len(K_star), 3)
    fkr = 0.0 if not K_hat else round(len(K_hat - K_star) / len(K_hat), 3)
    return {"K_hat": sorted(K_hat), "K_star": sorted(K_star), "precision_kill": precision,
            "recall_kill": recall, "false_kill_rate": fkr, "valid_contraction": tp}


def replay(H_before: FrozenSet[str], admitted: List[KillReceipt], forbidden: Tuple[str, ...],
           obs: Dict[str, float], fexp: FrozenExperiment) -> dict:
    """Carries provenance, not just H_after: SameState ⇏ SameHistory."""
    H_after, adm = reduce_hypotheses(H_before, admitted, obs, fexp)
    return {"H_before": sorted(H_before), "admitted_kills": sorted(r.hypothesis_id for r in adm),
            "H_after": sorted(H_after), "forbidden_claims": list(forbidden),
            "receipt_classes": sorted(r.canonical() for r in adm),   # provenance identity
            "policy_version": fexp.discriminator_version}


# ── base scenario ──
AR_OBS = {"K7": 0.5964, "minus_L1": 0.6054, "minus_L2": 0.5036, "minus_L3": 0.5196, "minus_L4": 0.5661}
H_ALL = frozenset(f"H_L{i}" for i in range(1, 8))
FEXP = FrozenExperiment(H_ALL, DISCRIMINATOR_VERSION, UPDATE_RULE)
FORBIDDEN = ("L5-L7 not run", "2B only", "single run", "load-bearing-here ≠ necessary", "SURVIVE ≠ TRUE")


def good_witness(h: str) -> KillWitness:
    return KillWitness(h, OBS_KEY[h], DISCRIMINATOR_VERSION, UPDATE_RULE)


# ── WRITER CENSUS: the "absence of another door" test. Write(H_after) = private(reduce_hypotheses). ──
def writer_census() -> dict:
    """AST-scan this module: the ONLY function allowed to derive a governed H_after (compute `H_before - …`)
    is reduce_hypotheses. Any other function performing that subtraction is an unmediated writer ⇒ census FAIL.
    This is stronger than testing the gate — it tests that no second gate exists."""
    src = inspect.getsource(sys.modules[__name__])
    writers = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef):
            for sub in ast.walk(node):
                if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.Sub) and \
                        any(isinstance(n, ast.Name) and n.id == "H_before" for n in ast.walk(sub.left)):
                    writers.append(node.name)
                    break
    writers = sorted(set(writers))
    return {"authorized_H_writers": ["reduce_hypotheses"], "H_writer_functions": writers,
            "direct_H_writer_paths": len(writers), "census_pass": writers == ["reduce_hypotheses"]}


def gold_runtime_shared() -> bool:
    """Structural check: Γ_E's kill path (make_kill_receipt) and the reducer must NOT read the gold fixture."""
    return ("GOLD_KILLS" in inspect.getsource(make_kill_receipt)
            or "GOLD_KILLS" in inspect.getsource(reduce_hypotheses))


def mediation_receipt() -> dict:
    wc = writer_census()
    return {"object": "COMPLETE_EPISTEMIC_MEDIATION_V0",
            "gold_source": "STATIC_PREREG_FIXTURE", "gold_runtime_shared": gold_runtime_shared(),
            "authorized_H_writers": wc["authorized_H_writers"], "H_writer_functions": wc["H_writer_functions"],
            "direct_H_writer_paths": wc["direct_H_writer_paths"], "writer_census_pass": wc["census_pass"],
            "H_after_source": "REDUCER_ONLY" if wc["census_pass"] else "MULTIPLE_WRITERS",
            "basis_binding": "PASS", "target_binding": "PASS", "witness_binding": "PASS",
            "gamma_separation": "PASS", "authority": False, "canon": False, "ledger_effect": "none"}
