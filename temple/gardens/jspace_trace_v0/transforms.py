#!/usr/bin/env python3
"""
JESTER frame transforms — content producers (the 'model output' analog).

V0 status:
  MIRROR = 🟢 REAL computation (provenance_rank: N_repr⊬N_epi).
  NULL, ROLE = deterministic V0 stand-ins for model-emitted content (NOT model-driven yet).
Each returns candidate content carrying an optional `invariant` class + an executable x*.
The graph/detector decide survival & bloom — transforms never self-promote. ΔA=0.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "provenance_rank_v0"))
import provenance_rank as PR

SEED = {
    "assertion": "Repeated confirmation increases confidence",
    "assumptions": ["INDEPENDENCE: confirmation_count ≈ independent_support",
                    "each source is a distinct witness"],
    "roles": {"witness": "source", "target": "confidence"},
    "provenance_items": PR.CHI_STAR,
    "class": "SEED",
}


def mirror(G):
    """REAL: apply the evaluator's own rule to itself via the provenance semiring."""
    c = PR.census(G["provenance_items"])
    if c["N_epi"] < c["N_repr"]:
        return {"theta": "MIRROR", "invariant": "INDEPENDENCE_COLLAPSE",
                "content": f"{c['N_repr']} representations → {c['N_epi']} roots ({c['inflation_factor']}×)",
                "x_star": "collapse-representations-by-provenance-root", "executable": True}
    return {"theta": "MIRROR", "invariant": None, "content": "roots independent", "executable": False}


def null(G):
    """V0 stand-in: remove the INDEPENDENCE assumption; observe what the claim needs."""
    removed = next((a for a in G["assumptions"] if a.startswith("INDEPENDENCE")), None)
    if removed:
        return {"theta": "NULL", "invariant": "INDEPENDENCE_COLLAPSE",
                "content": "consensus survives but evidentiary multiplicity disappears",
                "x_star": "verify whether all confirmers share one provenance root", "executable": True}
    return {"theta": "NULL", "invariant": None, "content": "no removable dependency", "executable": False}


def role(G):
    """V0 stand-in: swap witness ↔ copier — tests a different failure mode than NULL."""
    return {"theta": "ROLE", "invariant": "WITNESS_COPIER_SWAP",
            "content": "what if every confirmer is downstream of one witness",
            "x_star": None, "executable": False}   # produces a frame but no executable x* → HAL will test it


TRANSFORMS = {"MIRROR": mirror, "NULL": null, "ROLE": role}
