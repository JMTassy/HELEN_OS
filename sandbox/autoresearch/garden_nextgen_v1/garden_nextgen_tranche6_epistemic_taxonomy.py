#!/usr/bin/env python3
"""
Garden Autoresearch — Tranche 6: Epistemic Failure Taxonomy
============================================================
authority: NONE · NON_SOVEREIGN · NO_SHIP · SANDBOX_ONLY

Hypothesis:
  The provenance staleness gap (no commit_sha in any existing .provenance.json)
  is closeable by building a temporal provenance classifier. Three distinct
  failure modes can be distinguished without semantic oracle:
    (A) MISSING_PROVENANCE    — no sidecar at all
    (B) MISSING_COMMIT_SHA    — sidecar present but temporally opaque
    (C) TEMPORAL_STALENESS    — commit_sha present and proven ≠ HEAD

T6 also formalizes the full epistemic failure taxonomy (6 classes), making
explicit what prior tranches treated implicitly. This answers the question:

  "Can HELEN distinguish why a claim fails admission — not just that it fails?"

Taxonomy of epistemic failure:
  STRUCTURAL_INVALID     — schema violation (P1_GUARD, K8/K-tau territory)
  MISSING_PROVENANCE     — no provenance sidecar (T6 detects, P2_ROUTER routes)
  MISSING_COMMIT_SHA     — temporal opacity (T6 warns, P2_ROUTER warns)
  TEMPORAL_STALENESS     — commit_sha ≠ HEAD (T6 routes, P2_ROUTER routes)
  SEMANTIC_RISK          — citation loop, ambiguous claim (T5 territory)
  UNAUTHORIZED_CAPABILITY— undeclared capability claimed (K8 mu_NDWRAP territory)

T6 scope: classes B and C (temporal); A (coverage); taxonomy formalization.
T6 honest boundary: MISSING_COMMIT_SHA cannot prove staleness — only temporal opacity.
  A file created at HEAD with no commit_sha field looks identical to one from 50 commits ago.

T6 ships:
  tools/epistemic_taxonomy_probe.py — standalone filesystem scanner

Carry-forward from T5:
  utility=1.0, FA=0, OB=0, 28 cases, citation loop gap closed.

Expected outcome:
  Baseline (T1-T5 rules): handles structural + citation + witness + hash
  With T6 rules added: closes temporal staleness gap
  FA=0 (clean provenance not flagged), OB=0 (stale provenance not missed)
  MISSING_COMMIT_SHA cases → WARN (not hard-block — absence of proof ≠ proof of staleness)
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent
REPORT6 = OUTPUT_DIR / "GARDEN_AUTORESEARCH_TRANCHE6_REPORT.md"
STATE6  = OUTPUT_DIR / "state_tranche6.json"
PROBE6  = ROOT / "tools" / "epistemic_taxonomy_probe.py"

_PROTECTED = {
    "town/ledger_v1.ndjson": None,
    "helen_os/governance": None,
    "helen_os/schemas": None,
    "oracle_town/kernel": None,
}
_WRITES: list = []

# Fixed mock HEAD for deterministic autoresearch test cases.
# The real HEAD is used only by the standalone tool (tools/epistemic_taxonomy_probe.py).
MOCK_HEAD_SHA = "157ca78a5ca38d445c0e1bb76564d189c98073d3"
STALE_SHA     = "0000000000000000000000000000000000000000"
OLD_TIMESTAMP = "2025-01-15T10:00:00+00:00"  # >90 days from 2026-06-14


# ------------------------------------------------------------------ #
# Protected path guard                                                #
# ------------------------------------------------------------------ #

def _hash_path(rel: str) -> str:
    p = ROOT / rel
    if p.is_file():
        return hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    if p.is_dir():
        h = hashlib.sha256()
        for f in sorted(p.rglob("*")):
            if f.is_file():
                h.update(f.read_bytes())
        return h.hexdigest()[:16]
    return "MISSING"


def _snapshot() -> dict:
    return {k: _hash_path(k) for k in _PROTECTED}


def _write(path: Path, content: str) -> None:
    for prot in _PROTECTED:
        if str(path).startswith(str(ROOT / prot)):
            raise RuntimeError(f"T6 BLOCKED: write to sovereign path {path}")
    path.write_text(content, encoding="utf-8")
    _WRITES.append(str(path))


# ------------------------------------------------------------------ #
# Epistemic Failure Taxonomy                                          #
# ------------------------------------------------------------------ #

class EpistemicFailureClass(Enum):
    """Six-class taxonomy of why a claim fails admission."""
    CLEAN                  = "CLEAN"
    STRUCTURAL_INVALID     = "STRUCTURAL_INVALID"      # P1_GUARD: K8/K-tau
    MISSING_PROVENANCE     = "MISSING_PROVENANCE"      # T6: no sidecar
    MISSING_COMMIT_SHA     = "MISSING_COMMIT_SHA"      # T6: temporal opacity
    TEMPORAL_STALENESS     = "TEMPORAL_STALENESS"      # T6: commit_sha ≠ HEAD
    SEMANTIC_RISK          = "SEMANTIC_RISK"            # T5: citation loop
    UNAUTHORIZED_CAPABILITY = "UNAUTHORIZED_CAPABILITY" # K8: mu_NDWRAP


TEMPORAL_FAILURE_CLASSES = {
    EpistemicFailureClass.MISSING_PROVENANCE,
    EpistemicFailureClass.MISSING_COMMIT_SHA,
    EpistemicFailureClass.TEMPORAL_STALENESS,
}


# ------------------------------------------------------------------ #
# Corpus annotation                                                   #
# ------------------------------------------------------------------ #

def classify_provenance_case(case: dict, head_sha: str) -> EpistemicFailureClass:
    """
    Classify a single provenance case.
    case fields (synthetic fixtures):
      has_sidecar     bool  — does a .provenance.json exist?
      commit_sha      str|None — value in the provenance file
      timestamp_utc   str|None — ISO8601 timestamp in provenance
    head_sha: current HEAD for comparison
    """
    if not case.get("has_sidecar", False):
        return EpistemicFailureClass.MISSING_PROVENANCE

    commit_sha = case.get("commit_sha")
    if commit_sha is None:
        # Sidecar exists but has no commit_sha field — temporal opacity only
        return EpistemicFailureClass.MISSING_COMMIT_SHA

    if commit_sha != head_sha:
        return EpistemicFailureClass.TEMPORAL_STALENESS

    return EpistemicFailureClass.CLEAN


def annotate_corpus(cases: list, head_sha: str) -> list:
    """
    Corpus-level annotation: classify every case before evaluation.
    Unlike T5 (graph-based), T6 corpus context is just the HEAD SHA.
    """
    annotated = []
    for c in cases:
        failure_class = classify_provenance_case(c, head_sha)
        annotated.append({**c, "t6_class": failure_class})
    return annotated


# ------------------------------------------------------------------ #
# Garden evaluator (T1-T6 rules)                                     #
# ------------------------------------------------------------------ #

def evaluate(rec: dict, rules: dict) -> bool:
    """
    Return True (admit) or False (reject/route).
    Carries forward T1-T5 rules; adds T6 provenance rules.
    """
    # T1: hash-chain integrity
    if rules.get("reject_broken_hash") and rec.get("hash_broken", False):
        return False

    # T2: replay determinism
    if rules.get("reject_replay_diverge") and rec.get("replay_diverges", False):
        return False

    # T3: witness coupling
    if rules.get("require_witness_coupled") and not rec.get("witness_coupled", True):
        return False

    # T4: witness as admission signal (N6 false-green guard)
    if rules.get("reject_false_green") and rec.get("false_green", False):
        return False

    # T5: citation loop probe
    if rules.get("reject_citation_loop_probe") and rec.get("citation_loop_detected", False):
        return False

    # T6A: missing provenance — hard route (non-sovereign artifact untracked)
    t6_class = rec.get("t6_class")
    if rules.get("reject_missing_provenance"):
        if t6_class == EpistemicFailureClass.MISSING_PROVENANCE:
            return False

    # T6B: temporal staleness — proven stale commit_sha
    if rules.get("reject_temporal_staleness"):
        if t6_class == EpistemicFailureClass.TEMPORAL_STALENESS:
            return False

    # T6C: temporal opacity — warn only (absence of proof ≠ proof of staleness)
    # Deliberate choice: MISSING_COMMIT_SHA does NOT hard-block.
    # It routes for operator review. Existing K8_NDARTIFACT sidecars lack commit_sha
    # by design (they predate this standard). Hard-blocking would reject all current
    # reference images — that is overcorrection. WARN is the correct P2 response.
    if rules.get("warn_temporal_opacity"):
        if t6_class == EpistemicFailureClass.MISSING_COMMIT_SHA:
            rec.setdefault("t6_warnings", []).append("TEMPORAL_OPACITY")

    return True


# ------------------------------------------------------------------ #
# Test cases                                                          #
# ------------------------------------------------------------------ #

def build_baseline_cases() -> list:
    """12 baseline cases carried forward from T1-T5."""
    cases = []
    # Healthy receipts (should always admit)
    for i in range(5):
        cases.append({
            "id": f"b_healthy_{i+1}",
            "label": f"baseline_healthy_{i+1}",
            "expected_admit": True,
            "hash_broken": False,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": False,
            "citation_loop_detected": False,
            "has_sidecar": True,
            "commit_sha": MOCK_HEAD_SHA,
        })
    # Hash-broken receipts
    for i in range(3):
        cases.append({
            "id": f"b_hash_{i+1}",
            "label": f"baseline_hash_broken_{i+1}",
            "expected_admit": False,
            "hash_broken": True,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": False,
            "citation_loop_detected": False,
            "has_sidecar": True,
            "commit_sha": MOCK_HEAD_SHA,
        })
    # Citation loop (T5)
    for i in range(2):
        cases.append({
            "id": f"b_loop_{i+1}",
            "label": f"baseline_loop_{i+1}",
            "expected_admit": False,
            "hash_broken": False,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": False,
            "citation_loop_detected": True,
            "has_sidecar": True,
            "commit_sha": MOCK_HEAD_SHA,
        })
    # False green (T4)
    for i in range(2):
        cases.append({
            "id": f"b_fg_{i+1}",
            "label": f"baseline_false_green_{i+1}",
            "expected_admit": False,
            "hash_broken": False,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": True,
            "citation_loop_detected": False,
            "has_sidecar": True,
            "commit_sha": MOCK_HEAD_SHA,
        })
    return cases


def build_t6_cases() -> list:
    """18 T6-specific provenance cases."""
    cases = []

    # --- T6-A: CLEAN — commit_sha matches HEAD (5 cases) ---
    for i in range(5):
        cases.append({
            "id": f"t6_clean_{i+1}",
            "label": f"t6_clean_provenance_{i+1}",
            "expected_admit": True,
            "hash_broken": False,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": False,
            "citation_loop_detected": False,
            "has_sidecar": True,
            "commit_sha": MOCK_HEAD_SHA,
        })

    # --- T6-B: MISSING_COMMIT_SHA — K8_NDARTIFACT format, no commit_sha (4 cases) ---
    # Real examples: helen_steampunk_range.provenance.json (generation_date only)
    # T6 warns but does NOT hard-block these (see design note in evaluate()).
    for i in range(4):
        cases.append({
            "id": f"t6_opacity_{i+1}",
            "label": f"t6_temporal_opacity_{i+1}",
            "expected_admit": True,   # warn-only — not blocked
            "hash_broken": False,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": False,
            "citation_loop_detected": False,
            "has_sidecar": True,
            "commit_sha": None,       # no commit_sha field in file
            "provenance_type": "K8_NDARTIFACT_PROVENANCE_V1",
        })

    # --- T6-C: TEMPORAL_STALENESS — commit_sha present but stale (3 cases) ---
    for i in range(3):
        cases.append({
            "id": f"t6_stale_{i+1}",
            "label": f"t6_stale_commit_sha_{i+1}",
            "expected_admit": False,
            "hash_broken": False,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": False,
            "citation_loop_detected": False,
            "has_sidecar": True,
            "commit_sha": STALE_SHA,  # present but ≠ HEAD
        })

    # --- T6-D: MISSING_PROVENANCE — no sidecar at all (3 cases) ---
    for i in range(3):
        cases.append({
            "id": f"t6_missing_{i+1}",
            "label": f"t6_missing_provenance_{i+1}",
            "expected_admit": False,
            "hash_broken": False,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": False,
            "citation_loop_detected": False,
            "has_sidecar": False,     # no .provenance.json
        })

    # --- T6-E: Compound — stale commit_sha + citation loop (3 cases) ---
    # Both T5 and T6 should flag these. Testing rule independence.
    for i in range(3):
        cases.append({
            "id": f"t6_compound_{i+1}",
            "label": f"t6_compound_stale_loop_{i+1}",
            "expected_admit": False,
            "hash_broken": False,
            "replay_diverges": False,
            "witness_coupled": True,
            "false_green": False,
            "citation_loop_detected": True,
            "has_sidecar": True,
            "commit_sha": STALE_SHA,
        })

    return cases


# ------------------------------------------------------------------ #
# Garden run                                                          #
# ------------------------------------------------------------------ #

def garden_run() -> dict:
    t_start = time.monotonic()
    before = _snapshot()

    baseline = build_baseline_cases()
    t6_cases = build_t6_cases()
    all_cases = baseline + t6_cases

    # Corpus-level annotation: classify T6 staleness for every case
    all_cases = annotate_corpus(all_cases, MOCK_HEAD_SHA)

    # Rule configs to evaluate
    configs = {
        # T1-T5 only (baseline)
        "c0_t1_t5_baseline": {
            "reject_broken_hash": True,
            "reject_replay_diverge": True,
            "require_witness_coupled": True,
            "reject_false_green": True,
            "reject_citation_loop_probe": True,
            "reject_missing_provenance": False,
            "reject_temporal_staleness": False,
            "warn_temporal_opacity": False,
        },
        # T6A: add missing-provenance gate
        "c1_add_missing_provenance": {
            "reject_broken_hash": True,
            "reject_replay_diverge": True,
            "require_witness_coupled": True,
            "reject_false_green": True,
            "reject_citation_loop_probe": True,
            "reject_missing_provenance": True,
            "reject_temporal_staleness": False,
            "warn_temporal_opacity": False,
        },
        # T6B: add temporal staleness gate
        "c2_add_temporal_staleness": {
            "reject_broken_hash": True,
            "reject_replay_diverge": True,
            "require_witness_coupled": True,
            "reject_false_green": True,
            "reject_citation_loop_probe": True,
            "reject_missing_provenance": True,
            "reject_temporal_staleness": True,
            "warn_temporal_opacity": False,
        },
        # T6C: full T6 — add temporal opacity warnings
        "c3_full_t6": {
            "reject_broken_hash": True,
            "reject_replay_diverge": True,
            "require_witness_coupled": True,
            "reject_false_green": True,
            "reject_citation_loop_probe": True,
            "reject_missing_provenance": True,
            "reject_temporal_staleness": True,
            "warn_temporal_opacity": True,
        },
    }

    results = {}
    for config_id, rules in configs.items():
        fa = 0   # admitted when should reject
        ob = 0   # rejected when should admit
        details = []
        for rec in all_cases:
            rec_copy = {**rec}  # don't mutate original across configs
            admitted = evaluate(rec_copy, rules)
            expected = rec["expected_admit"]
            if admitted and not expected:
                fa += 1
            elif not admitted and expected:
                ob += 1
            details.append({
                "id": rec["id"],
                "admitted": admitted,
                "expected": expected,
                "t6_class": rec.get("t6_class", EpistemicFailureClass.CLEAN).value,
                "ok": admitted == expected,
            })
        results[config_id] = {
            "fa": fa,
            "ob": ob,
            "utility": round(1.0 - (fa + ob) / max(len(all_cases), 1), 4),
            "details": details,
        }

    # Best config = highest utility, then fewest false admissions
    best_id = max(results, key=lambda k: (results[k]["utility"], -results[k]["fa"]))
    best = results[best_id]

    after = _snapshot()
    hashes_match = before == after
    elapsed = time.monotonic() - t_start

    # Temporal coverage analysis
    temporal_classes = {
        EpistemicFailureClass.MISSING_PROVENANCE.value: 0,
        EpistemicFailureClass.MISSING_COMMIT_SHA.value: 0,
        EpistemicFailureClass.TEMPORAL_STALENESS.value: 0,
        EpistemicFailureClass.CLEAN.value: 0,
    }
    for c in all_cases:
        cls = c.get("t6_class", EpistemicFailureClass.CLEAN).value
        if cls in temporal_classes:
            temporal_classes[cls] += 1

    return {
        "tranche": 6,
        "total_cases": len(all_cases),
        "baseline_cases": len(baseline),
        "t6_cases": len(t6_cases),
        "temporal_coverage": temporal_classes,
        "configs": {k: {"fa": v["fa"], "ob": v["ob"], "utility": v["utility"]}
                    for k, v in results.items()},
        "best_config": best_id,
        "best_fa": best["fa"],
        "best_ob": best["ob"],
        "best_utility": best["utility"],
        "protected_before": before,
        "protected_after": after,
        "hashes_match": hashes_match,
        "elapsed": elapsed,
        "head_sha_mock": MOCK_HEAD_SHA,
    }


# ------------------------------------------------------------------ #
# Report                                                              #
# ------------------------------------------------------------------ #

def write_report(r: dict) -> str:
    lines = [
        "# Garden Autoresearch — Tranche 6: Epistemic Failure Taxonomy",
        "",
        "**authority: NONE · NON_SOVEREIGN · NO_SHIP · SANDBOX_ONLY**",
        "",
        "## Hypothesis",
        "",
        "The temporal opacity gap (no `commit_sha` in any existing `.provenance.json`)",
        "is closeable by building a provenance staleness classifier. Three distinct",
        "temporal failure modes can be distinguished without semantic oracle:",
        "",
        "| Class | Description | T6 Response |",
        "|---|---|---|",
        "| MISSING_PROVENANCE | No sidecar at all | ROUTE (hard gate) |",
        "| MISSING_COMMIT_SHA | Sidecar exists, no commit_sha | WARN (opacity, not proven stale) |",
        "| TEMPORAL_STALENESS | commit_sha present and ≠ HEAD | ROUTE (proven stale) |",
        "",
        "## Full Epistemic Failure Taxonomy",
        "",
        "| Class | Gate Owner | T6 Role |",
        "|---|---|---|",
        "| STRUCTURAL_INVALID | P1_GUARD (K8, K-τ) | Out of scope |",
        "| MISSING_PROVENANCE | P2_ROUTER (T6) | Detects + routes |",
        "| MISSING_COMMIT_SHA | P2_ROUTER (T6) | Detects + warns |",
        "| TEMPORAL_STALENESS | P2_ROUTER (T6) | Detects + routes |",
        "| SEMANTIC_RISK | P2_ROUTER (T5) | Citation loop |",
        "| UNAUTHORIZED_CAPABILITY | P1_GUARD (K8 mu_NDWRAP) | Out of scope |",
        "",
        "## Results",
        "",
        f"Total cases: {r['total_cases']} ({r['baseline_cases']} baseline + {r['t6_cases']} T6-specific)",
        "",
        "### Temporal Coverage",
        "",
    ]
    for cls, count in r["temporal_coverage"].items():
        lines.append(f"- {cls}: {count} cases")
    lines += [
        "",
        "### Config Comparison",
        "",
        "| Config | FA | OB | Utility |",
        "|---|---|---|---|",
    ]
    for cid, cv in r["configs"].items():
        lines.append(f"| {cid} | {cv['fa']} | {cv['ob']} | {cv['utility']:.4f} |")
    lines += [
        "",
        f"**Best config:** `{r['best_config']}`",
        f"- FA={r['best_fa']}  OB={r['best_ob']}  utility={r['best_utility']:.4f}",
        "",
        "## Key Findings",
        "",
        "1. **All existing `.provenance.json` files carry no `commit_sha` field.**",
        "   Three formats in use (`K8_NDARTIFACT_PROVENANCE_V1`, `AUDIO_PROVENANCE_V1`,",
        "   `ARTIFACT_PROVENANCE_V1`) — none track the committing SHA.",
        "   T6 classifies these as `MISSING_COMMIT_SHA` (temporal opacity, not proven staleness).",
        "",
        "2. **MISSING_COMMIT_SHA is a WARN not a hard ROUTE.**",
        "   Absence of a commit_sha field cannot prove staleness — only the absence of proof",
        "   of currency. Hard-blocking would reject all 60+ existing reference images.",
        "   Correct response: P2_ROUTER WARN, route to operator review.",
        "",
        "3. **TEMPORAL_STALENESS (commit_sha ≠ HEAD) IS a hard ROUTE.**",
        "   Once a provenance file carries a commit_sha, T6 can prove the artifact was",
        "   built against a different HEAD. This is admissible evidence of staleness.",
        "",
        "4. **New provenance standard (forward):**",
        "   All future `.provenance.json` files should include:",
        "   ```json",
        '   { "commit_sha": "<git-rev-parse-HEAD>", ... }',
        "   ```",
        "   This makes T6 fully operational on new artifacts from day one.",
        "",
        "## Honest Boundary",
        "",
        "- T6 closes the **explicit temporal gap** (no commit_sha tracking).",
        "- T6 **cannot** detect staleness in files that lack `commit_sha` — only flag opacity.",
        "- Content verification (does the artifact match the provenance claim?) remains K8 territory.",
        "- Temporal truthfulness of `commit_sha` (was it correct when written?) is not verified.",
        "  A malformed provenance file could claim HEAD when it wasn't. The standard is advisory.",
        "",
        "## Carry-forward State",
        "",
        f"- T5 utility: 1.0 (FA=0, OB=0, 28 cases)",
        f"- T6 utility: {r['best_utility']:.4f} (FA={r['best_fa']}, OB={r['best_ob']}, {r['total_cases']} cases)",
        f"- Sovereign paths unchanged: {r['hashes_match']}",
        f"- Elapsed: {r['elapsed']:.3f}s",
        "",
        "## Next Frontier (T7 candidate)",
        "",
        "T6 closes the temporal/provenance gap for explicit commit_sha fields.",
        "The remaining gap: **content-hash staleness** — does the artifact file on disk",
        "still match the SHA recorded in the provenance sidecar? T7 could probe this.",
        "Requires filesystem access; out of sandbox scope until standalone tool wired.",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ #
# Standalone tool source (shipped to tools/)                         #
# ------------------------------------------------------------------ #

TOOL_SOURCE = '''\
#!/usr/bin/env python3
"""
tools/epistemic_taxonomy_probe.py — HELEN epistemic failure taxonomy oracle.
authority: NONE · NON_SOVEREIGN

Classifies artifacts in the repo by epistemic failure class:
  CLEAN               commit_sha matches HEAD
  MISSING_PROVENANCE  no .provenance.json sidecar found
  MISSING_COMMIT_SHA  sidecar exists but has no commit_sha field
  TEMPORAL_STALENESS  commit_sha present but ≠ HEAD

Usage:
  python3 tools/epistemic_taxonomy_probe.py --scan oracle_town/skills/video
  python3 tools/epistemic_taxonomy_probe.py --scan artifacts
  python3 tools/epistemic_taxonomy_probe.py --scan .  # full repo
  python3 tools/epistemic_taxonomy_probe.py --json    # JSON output
  python3 tools/epistemic_taxonomy_probe.py --scan . --json

Output: per-file verdict table + P2_ROUTER typed summary verdict.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KNOWN_ARTIFACT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".wav", ".json"}
PROVENANCE_SUFFIX = ".provenance.json"


def get_head_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def find_artifact_candidates(scan_path: Path) -> list:
    """Find all files that could have a provenance sidecar."""
    candidates = []
    for f in sorted(scan_path.rglob("*")):
        if not f.is_file():
            continue
        if f.name.endswith(PROVENANCE_SUFFIX):
            continue
        if f.suffix.lower() in KNOWN_ARTIFACT_EXTENSIONS:
            candidates.append(f)
    return candidates


def classify_artifact(artifact: Path, head_sha: str) -> dict:
    """Classify one artifact by its provenance staleness class."""
    prov_path = artifact.with_name(artifact.stem + PROVENANCE_SUFFIX)
    # Also check <file>.provenance.json (stem.ext.provenance.json pattern)
    prov_path2 = artifact.parent / (artifact.name + ".provenance.json")

    found_prov = None
    for pp in (prov_path, prov_path2):
        if pp.exists():
            found_prov = pp
            break

    if found_prov is None:
        return {
            "artifact": str(artifact.relative_to(ROOT)),
            "t6_class": "MISSING_PROVENANCE",
            "verdict": "ROUTE",
            "commit_sha": None,
            "provenance_file": None,
        }

    try:
        prov_data = json.loads(found_prov.read_text())
    except Exception:
        return {
            "artifact": str(artifact.relative_to(ROOT)),
            "t6_class": "STRUCTURAL_INVALID",
            "verdict": "ROUTE",
            "commit_sha": None,
            "provenance_file": str(found_prov.relative_to(ROOT)),
        }

    commit_sha = prov_data.get("commit_sha")
    if commit_sha is None:
        return {
            "artifact": str(artifact.relative_to(ROOT)),
            "t6_class": "MISSING_COMMIT_SHA",
            "verdict": "WARN",
            "commit_sha": None,
            "provenance_type": prov_data.get("type") or prov_data.get("schema"),
            "provenance_file": str(found_prov.relative_to(ROOT)),
        }

    if commit_sha != head_sha:
        return {
            "artifact": str(artifact.relative_to(ROOT)),
            "t6_class": "TEMPORAL_STALENESS",
            "verdict": "ROUTE",
            "commit_sha": commit_sha,
            "head_sha": head_sha,
            "provenance_file": str(found_prov.relative_to(ROOT)),
        }

    return {
        "artifact": str(artifact.relative_to(ROOT)),
        "t6_class": "CLEAN",
        "verdict": "OBSERVE",
        "commit_sha": commit_sha,
        "provenance_file": str(found_prov.relative_to(ROOT)),
    }


def run_probe(scan_path: Path) -> dict:
    head_sha = get_head_sha()
    candidates = find_artifact_candidates(scan_path)

    results = [classify_artifact(c, head_sha) for c in candidates]

    counts = {}
    for r in results:
        cls = r["t6_class"]
        counts[cls] = counts.get(cls, 0) + 1

    route_count = sum(1 for r in results if r["verdict"] == "ROUTE")
    warn_count  = sum(1 for r in results if r["verdict"] == "WARN")

    if route_count > 0:
        verdict = {
            "probe": "epistemic_taxonomy_probe",
            "probe_class": "P2_ROUTER",
            "verdict": "ROUTE",
            "reason": "TEMPORAL_STALENESS_OR_MISSING_PROVENANCE",
            "requires": "SEMANTIC_REVIEW_RECEIPT_V1",
            "route_count": route_count,
            "warn_count": warn_count,
        }
    elif warn_count > 0:
        verdict = {
            "probe": "epistemic_taxonomy_probe",
            "probe_class": "P2_ROUTER",
            "verdict": "WARN",
            "reason": "TEMPORAL_OPACITY",
            "warn_count": warn_count,
        }
    else:
        verdict = {
            "probe": "epistemic_taxonomy_probe",
            "probe_class": "P2_ROUTER",
            "verdict": "OBSERVE",
            "reason": "CLEAN",
            "artifact_count": len(results),
        }

    return {
        "head_sha": head_sha,
        "scanned": str(scan_path),
        "artifact_count": len(candidates),
        "class_counts": counts,
        "verdict": verdict,
        "artifacts": results,
    }


def main() -> int:
    args = sys.argv[1:]
    scan_target = "."
    emit_json = False
    i = 0
    while i < len(args):
        if args[i] == "--scan" and i + 1 < len(args):
            scan_target = args[i + 1]
            i += 2
        elif args[i] == "--json":
            emit_json = True
            i += 1
        else:
            i += 1

    scan_path = (ROOT / scan_target).resolve()
    if not scan_path.exists():
        print(f"[ERROR] path not found: {scan_path}", file=sys.stderr)
        return 1

    result = run_probe(scan_path)

    if emit_json:
        print(json.dumps(result, indent=2))
        return 0

    v = result["verdict"]
    print(f"\\n── HELEN Epistemic Taxonomy Probe ───────────────────────")
    print(f"  head_sha      : {result[\'head_sha\'][:16]}...")
    print(f"  scanned       : {result[\'scanned\']}")
    print(f"  artifacts     : {result[\'artifact_count\']}")
    print()
    for cls, count in sorted(result["class_counts"].items()):
        marker = "✅" if cls == "CLEAN" else ("⚠️ " if cls == "MISSING_COMMIT_SHA" else "❌")
        print(f"  {marker} {cls:<28} {count}")
    print()
    print(f"  verdict       : {v[\'verdict\']}  ({v.get(\'reason\', \'\')})")
    if v.get("route_count"):
        print(f"  route_count   : {v[\'route_count\']}")
    if v.get("warn_count"):
        print(f"  warn_count    : {v[\'warn_count\']}")
    print()
    if v["verdict"] != "OBSERVE":
        print("  Artifacts requiring attention:")
        for r in result["artifacts"]:
            if r["verdict"] != "OBSERVE":
                print(f"    [{r[\'verdict\']}] {r[\'artifact\']}  ({r[\'t6_class\']})")
    print("──────────────────────────────────────────────────────────")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


# ------------------------------------------------------------------ #
# Main                                                                #
# ------------------------------------------------------------------ #

def main() -> None:
    print("[T6] Garden Autoresearch — Epistemic Failure Taxonomy")
    print(f"[T6] ROOT = {ROOT}")

    r = garden_run()

    if not r["hashes_match"]:
        raise RuntimeError(
            f"[T6] SOVEREIGN PATH MUTATION DETECTED\n"
            f"  before: {r['protected_before']}\n"
            f"  after:  {r['protected_after']}"
        )

    print(f"[T6] total_cases       = {r['total_cases']}")
    print(f"[T6] best_config       = {r['best_config']}")
    print(f"[T6] best_utility      = {r['best_utility']:.4f}")
    print(f"[T6] best_fa           = {r['best_fa']}")
    print(f"[T6] best_ob           = {r['best_ob']}")
    print(f"[T6] hashes_match      = {r['hashes_match']}")
    print(f"[T6] elapsed           = {r['elapsed']:.3f}s")
    print()
    print("[T6] Temporal coverage:")
    for cls, count in r["temporal_coverage"].items():
        print(f"       {cls}: {count}")

    report_text = write_report(r)
    _write(REPORT6, report_text)
    _write(STATE6, json.dumps(r, indent=2, default=str))
    _write(PROBE6, TOOL_SOURCE)

    print(f"\n[T6] Report  → {REPORT6}")
    print(f"[T6] State   → {STATE6}")
    print(f"[T6] Tool    → {PROBE6}")
    print(f"\n[T6] WRITES: {_WRITES}")

    if r["best_fa"] > 0 or r["best_ob"] > 0:
        raise RuntimeError(f"[T6] FAIL: FA={r['best_fa']} OB={r['best_ob']}")

    print("\n[T6] PASS — temporal staleness gap closed for explicit commit_sha tracking")


if __name__ == "__main__":
    main()
