"""Frame-indexed constitution audit — the status matrix as an instrument.

NON_SOVEREIGN · authority=false · ledger_effect=none.

A status matrix is a claim about a filesystem. This module recomputes it:
for every constitution row C1..C12 it runs a probe against THIS frame and
reports the delta between the claimed status (the registry R, from the
Constitution Status Matrix V1.2) and the witnessed status (F, this disk).

Frame-indexed statuses:
  WITNESSED_HERE     🟢  functional probe executed and passed in this frame
  PRESENT_UNVERIFIED 🟡  matching artifacts exist here, no functional probe
  REGISTRY_GHOST     🔴  claimed witnessed elsewhere; nothing found here
  CONFIRMED_UNBUILT  ⚫  claimed unbuilt; nothing found here (frame agrees)
  PROBE_FAILED       🔴  a functional probe raised or asserted false

Laws obeyed by the auditor itself:
  - Functional probes EXECUTE the invariant (extensional); artifact scans
    only ever earn 🟡, never 🟢 — grep is not a witness.
  - Deterministic: sorted walks, no wall-time, no randomness; the frame
    identifier is an input, never sampled from the environment.
  - The auditor holds no authority: it renders a delta, admits nothing.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = REPO_ROOT / "experiments"

SKIP_DIRS = {".git", "node_modules", "deprecated", "__pycache__"}

WITNESSED_HERE = "WITNESSED_HERE"
PRESENT_UNVERIFIED = "PRESENT_UNVERIFIED"
REGISTRY_GHOST = "REGISTRY_GHOST"
CONFIRMED_UNBUILT = "CONFIRMED_UNBUILT"
PROBE_FAILED = "PROBE_FAILED"

GLYPH = {WITNESSED_HERE: "🟢", PRESENT_UNVERIFIED: "🟡",
         REGISTRY_GHOST: "🔴", CONFIRMED_UNBUILT: "⚫", PROBE_FAILED: "🔴"}


def _py_corpus() -> list[tuple[str, str]]:
    """All .py files in the repo, sorted, quarantine and vendor dirs skipped."""
    out = []
    for path in sorted(REPO_ROOT.rglob("*.py")):
        parts = set(path.parts)
        if parts & SKIP_DIRS or any(p.startswith("_quarantine") for p in path.parts):
            continue
        try:
            out.append((str(path.relative_to(REPO_ROOT)), path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return out


def _scan(corpus, pattern: str, exclude_prefix: str = "experiments/constitution_audit") -> list[str]:
    rx = re.compile(pattern)
    return [p for p, text in corpus if not p.startswith(exclude_prefix) and rx.search(text)]


# --- functional probes: they RUN the invariant ---------------------------

def _probe_chromodynamics():
    sys.path.insert(0, str(EXPERIMENTS / "wul_core"))
    try:
        from core_schema import (AUTHORITY_BEARING_TYPES, AuthorityGrade,
                                 GlyphType, PhaseColor, WorldFrame, WULState,
                                 encode_wul, parse_wul)
        assert AUTHORITY_BEARING_TYPES == frozenset({GlyphType.CAP, GlyphType.EFFECT})
        proj = parse_wul("🟢|⚖️|⬡")
        assert not hasattr(proj, "authority") and not hasattr(proj, "provenance")
        a0 = WULState(GlyphType.EFFECT, PhaseColor.EXECUTED, WorldFrame.SOVEREIGN,
                      AuthorityGrade.NONE)
        a1 = WULState(GlyphType.EFFECT, PhaseColor.EXECUTED, WorldFrame.SOVEREIGN,
                      AuthorityGrade.GOVERNED, ("receipt:r1",))
        assert encode_wul(a0) == encode_wul(a1)
        try:
            parse_wul("🟢|🐉|⬡")
            return False, "mythic vocabulary accepted"
        except ValueError:
            pass
        return True, "codec invariants executed: projection-only, {CAP,EFFECT}, D(x)⊬A(x), 🐉 rejected"
    finally:
        sys.path.pop(0)


def _probe_witness_calculus():
    sys.path.insert(0, str(EXPERIMENTS / "witness_protocol"))
    try:
        import witness_core as wc
        x = {"package_id": "p", "items": [{"id": "a"}]}
        lying = wc.CoverageReceipt(witness_id="w", input_hash="stale",
                                   claims_live=True)
        r = wc.verify_witness(lying, x, lambda *_: True)
        assert r["verdict"] == wc.UNKNOWN  # live=true never trusted
        foreign = wc.CoverageReceipt(
            witness_id="w", input_hash=wc.package_hash(x), checked_ids=("a",),
            evidence=({"item_id": "a", "package_hash": "elsewhere"},))
        assert wc.verify_witness(foreign, x, lambda *_: True)["verdict"] == wc.FAIL
        assert not any("admit" in n.lower() for n in dir(wc) if not n.startswith("_"))
        assert wc.aggregate([{"verdict": wc.PASS}, {"verdict": wc.FAIL}]) == wc.FAIL
        return True, "Live recomputed, live=true untrusted, foreign evidence FAILs, no admit surface"
    finally:
        sys.path.pop(0)


# --- the registry: matrix V1.2 claims + how to probe them here -----------

ROWS = [
    {"id": "C1", "title": "Color vs Type (chromodynamics)",
     "claimed": "CONVENTION", "functional": _probe_chromodynamics},
    {"id": "C2", "title": "Projection vs Authority (A ∉ Codomain(P))",
     "claimed": "CONVENTION", "functional": _probe_chromodynamics},
    {"id": "C3", "title": "Universal Non-Transport (instance: witness Live calculus)",
     "claimed": "PARTIAL", "functional": _probe_witness_calculus},
    {"id": "C4", "title": "Exact Transition Binding κ_T=(G0,c,e,G1)",
     "claimed": "WITNESSED", "patterns": r"kappa_T|TransitionCapability|transition_binding"},
    {"id": "C5", "title": "Choke-Point Derivation (authoritative state/candidate provider)",
     "claimed": "WITNESSED", "patterns": r"CandidateProvider|choke_point|AuthoritativeState"},
    {"id": "C6", "title": "Affine Capability Consumption (ConsumeOnce)",
     "claimed": "WITNESSED", "patterns": r"ConsumeOnce|consume_once|invoke_once"},
    {"id": "C7", "title": "Warren Functional Factorization (E012-A metamorphic suite)",
     "claimed": "WITNESSED", "patterns": r"metamorphic"},
    {"id": "C8", "title": "Lineage Multiplicity Collapse (declared ≠ derived root)",
     "claimed": "WITNESSED", "patterns": r"derived_root|lineage_resolver|multiplicity"},
    {"id": "C9", "title": "Multidimensional Anti-Overfit Vector",
     "claimed": "UNBUILT", "patterns": r"anti_overfit|overfit_vector"},
    {"id": "C10", "title": "HAL Tri-Valued Completeness (E013 controls)",
     "claimed": "WITNESSED", "patterns": r"tri_valued|tri-valued|TRI_VALUED"},
    {"id": "C11", "title": "Single-Head Mutation Surface (UnifiedStore)",
     "claimed": "UNBUILT", "patterns": r"UnifiedStore|unified_store"},
    {"id": "C12", "title": "E012-B Warren Mediation Path Completeness",
     "claimed": "UNBUILT", "patterns": r"mediation_path|path_completeness"},
]


def audit(frame_id: str = "UNIDENTIFIED_FRAME") -> dict:
    corpus = _py_corpus()
    rows = []
    for row in ROWS:
        entry = {"id": row["id"], "title": row["title"], "claimed": row["claimed"]}
        if "functional" in row:
            try:
                ok, evidence = row["functional"]()
                entry["status"] = WITNESSED_HERE if ok else PROBE_FAILED
                entry["evidence"] = evidence
            except Exception as exc:  # probe absence or breakage is a result
                entry["status"] = PROBE_FAILED
                entry["evidence"] = f"probe raised: {type(exc).__name__}"
        else:
            hits = _scan(corpus, row["patterns"])
            if hits:
                entry["status"] = PRESENT_UNVERIFIED
                entry["evidence"] = f"artifacts matched (grep ≠ witness): {hits[:3]}"
            elif row["claimed"] == "WITNESSED":
                entry["status"] = REGISTRY_GHOST
                entry["evidence"] = "claimed witnessed elsewhere; no artifact in this frame"
            else:
                entry["status"] = CONFIRMED_UNBUILT
                entry["evidence"] = "claimed unbuilt; frame agrees"
        rows.append(entry)
    ghosts = sorted(r["id"] for r in rows if r["status"] == REGISTRY_GHOST)
    return {
        "schema_name": "CONSTITUTION_FRAME_AUDIT_V1",
        "schema_version": "1.0.0",
        "frame_id": frame_id,
        "registry_source": "Constitution Status Matrix V1.2",
        "rows": rows,
        "registry_ghosts": ghosts,
        "verdict": "MATRIX_NOT_FULLY_WITNESSED_IN_FRAME" if ghosts else "MATRIX_WITNESSED_IN_FRAME",
    }


def render(report: dict) -> str:
    lines = [f"⎈ CONSTITUTION FRAME AUDIT · frame={report['frame_id']} ⎈"]
    for r in report["rows"]:
        lines.append(f"{GLYPH[r['status']]} {r['id']:>3} [{r['status']:<18}] "
                     f"claimed={r['claimed']:<9} {r['title']}")
    lines.append(f"registry_ghosts: {', '.join(report['registry_ghosts']) or 'none'}")
    lines.append(f"VERDICT: {report['verdict']} · AUTHORITY: DENY · LEDGER_EFFECT: NONE")
    return "\n".join(lines)


def canon(report: dict) -> str:
    return json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


if __name__ == "__main__":
    frame = sys.argv[1] if len(sys.argv) > 1 else "UNIDENTIFIED_FRAME"
    report = audit(frame)
    if "--json" in sys.argv:
        print(canon(report))
    else:
        print(render(report))
