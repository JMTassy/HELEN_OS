"""GOVERNED_EPOCH_V0_KILL_SUITE — the falsifier for witnessed contraction. authority=false. NON-SOVEREIGN.
canon=false · ledger_effect=none. Attacks ONE property of GOVERNED_EPOCH_V0 (frozen, unchanged):

    NO HYPOTHESIS DIES FOR FREE.
    H_after ⊊ H_before ⇒ for every h in (H_before minus H_after), there is a witness w : w licenses Kill(h)
    — each elimination has its OWN witness targeting THAT hypothesis, derived from the un-modified prereg
      observation. A global "experiment conclusive" receipt is insufficient.

Contraction alone is NOT progress (else HELEN could be rewarded for deleting uncertainty). We score BOTH errors:
    Precision_kill = licensed kills / all kills            (false kills = deleting live uncertainty)
    Recall_kill    = licensed kills done / licensed avail  (missed kills = a lazy always-HOLD looks fake-perfect)
    ValidContraction = |licensed kills done|
Objective:  max ValidContraction / Cost   s.t.  FalseKillRate ≤ ε.   AuthorityGain = 0 always.

Concrete refutation model (so witness-target mismatch is checkable): hypothesis H_Li = "law Li is load-bearing",
refuted by the ablation observation iff removing Li did NOT drop Q  (obs["minus_Li"] ≥ obs["K7"]).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

# ── refutation model: each hypothesis reads exactly ONE observation key ──
OBS_KEY = {f"H_L{i}": f"minus_L{i}" for i in range(1, 8)}


def _canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def obs_hash(obs: Dict[str, float]) -> str:
    return "sha256:" + hashlib.sha256(_canon(obs).encode()).hexdigest()[:16]


def refuted(h: str, obs: Dict[str, float]) -> Optional[bool]:
    """True = observation refutes 'Li is load-bearing' (removing Li did NOT drop Q). None = not run (unresolved)."""
    k = OBS_KEY.get(h)
    if k is None or k not in obs or "K7" not in obs:
        return None
    return obs[k] >= obs["K7"]


@dataclass(frozen=True)
class KillWitness:
    target: str            # the hypothesis this witness licenses killing
    observation_key: str   # which observation field it reads — must be the target's canonical key
    rule: str = "ΔQ ≥ 0 ⇒ 'load-bearing' refuted"


@dataclass(frozen=True)
class WitnessedEpoch:
    hypotheses: FrozenSet[str]          # H_before
    observation: Dict[str, float]       # raw (current)
    prereg_observation_hash: str        # hash captured at PREREG time (detects post-prereg tampering)
    kill_witnesses: Tuple[KillWitness, ...]
    claimed_H_after: FrozenSet[str]     # what the epoch ASSERTS survives — checked against witnessed kills
    forbidden_claims: Tuple[str, ...] = ()


def _witness_valid(w: KillWitness, ep: WitnessedEpoch) -> Tuple[bool, str]:
    if w.target not in ep.hypotheses:
        return False, "TARGET_UNKNOWN"
    if w.observation_key != OBS_KEY.get(w.target):
        return False, "WITNESS_TARGET_MISMATCH"          # e.g. a witness reading minus_L1 aimed at H_L2
    r = refuted(w.target, ep.observation)
    if r is None:
        return False, "TARGET_UNRESOLVED"                 # no observation to license the kill
    if r is not True:
        return False, "TARGET_NOT_REFUTED"                # observation does not license killing this h
    return True, "OK"


def gamma_E_strict(ep: WitnessedEpoch) -> dict:
    """Epistemic gate: honor a kill ONLY if it carries a valid witness targeting THAT hypothesis, derived
    from the un-tampered prereg observation. Claimed survivors must equal witnessed survivors."""
    reasons: List[str] = []
    if obs_hash(ep.observation) != ep.prereg_observation_hash:
        reasons.append("OBSERVATION_MODIFIED_AFTER_PREREG")
    valid_kills, bad = set(), []
    for w in ep.kill_witnesses:
        ok, why = _witness_valid(w, ep)
        (valid_kills.add(w.target) if ok else bad.append(f"{w.target}:{why}"))
    if bad:
        reasons.append("INVALID_WITNESS:" + ",".join(bad))
    computed_after = frozenset(ep.hypotheses) - valid_kills
    claimed_removals = frozenset(ep.hypotheses) - ep.claimed_H_after
    unwitnessed = sorted(claimed_removals - valid_kills)   # a hypothesis claimed dead with no valid witness
    if unwitnessed:
        reasons.append("ELIMINATION_WITHOUT_WITNESS:" + ",".join(unwitnessed))
    if ep.claimed_H_after != computed_after and not unwitnessed:
        reasons.append("CLAIMED_AFTER_MISMATCH")
    if reasons:
        return {"gate": "Γ_E", "verdict": "REJECT", "reasons": reasons}
    verdict = "CONTRACT" if valid_kills else "HOLD"
    return {"gate": "Γ_E", "verdict": verdict, "licensed_kills": sorted(valid_kills),
            "H_before": sorted(ep.hypotheses), "H_after": sorted(computed_after)}


def gamma_I(_ep: WitnessedEpoch) -> dict:
    """A research kill NEVER admits governed state, whatever Γ_E decided. Γ_E=KILL ⇏ Γ_I=ADMIT."""
    return {"gate": "Γ_I", "verdict": "NO_ADMISSION", "authority_gain": 0, "ledger_effect": "none"}


def scores(ep: WitnessedEpoch) -> dict:
    """Precision/Recall of kills + FalseKillRate. Available licensed kills = hypotheses the obs truly refutes."""
    performed = {w.target for w in ep.kill_witnesses if _witness_valid(w, ep)[0]}
    all_claimed_kills = {w.target for w in ep.kill_witnesses}
    available = {h for h in ep.hypotheses if refuted(h, ep.observation) is True}
    licensed_done = performed & available
    prec = len(licensed_done) / len(all_claimed_kills) if all_claimed_kills else 1.0
    rec = len(licensed_done) / len(available) if available else 1.0
    fkr = len(all_claimed_kills - available) / len(all_claimed_kills) if all_claimed_kills else 0.0
    return {"precision_kill": round(prec, 3), "recall_kill": round(rec, 3),
            "false_kill_rate": round(fkr, 3), "valid_contraction": len(licensed_done),
            "licensed_available": sorted(available)}


def replay(ep: WitnessedEpoch) -> dict:
    g = gamma_E_strict(ep)
    return {"H_after": g.get("H_after"), "forbidden_claims": list(ep.forbidden_claims),
            "verdict": g["verdict"]}


# ── the base scenario: the witnessed AR ablation (only H_L1 is genuinely refuted) ──
AR_OBS = {"K7": 0.5964, "minus_L1": 0.6054, "minus_L2": 0.5036, "minus_L3": 0.5196, "minus_L4": 0.5661}
H_ALL = frozenset(f"H_L{i}" for i in range(1, 8))                # L5-L7 unresolved (not in AR_OBS)
FORBIDDEN = ("L5-L7 not run", "2B only", "single run", "load-bearing-here ≠ necessary")


def base_epoch() -> WitnessedEpoch:
    return WitnessedEpoch(hypotheses=H_ALL, observation=AR_OBS, prereg_observation_hash=obs_hash(AR_OBS),
                          kill_witnesses=(KillWitness("H_L1", "minus_L1"),),
                          claimed_H_after=H_ALL - {"H_L1"}, forbidden_claims=FORBIDDEN)
