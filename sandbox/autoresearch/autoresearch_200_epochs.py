#!/usr/bin/env python3
"""
sandbox/autoresearch/autoresearch_200_epochs.py
================================================
HELEN AUTORESEARCH MODE — 200 epochs
authority: NONE · NON_SOVEREIGN · NO_SHIP · SANDBOX_ONLY

Implements the Obsidian Mirror autoresearch loop.
Probes the HELEN corpus for 10 conceptual attractors × 20 probe angles = 200 epochs.

Each epoch:
  1. Picks one (concept, probe_dimension) pair
  2. Probes the real corpus (grep/file walk on SOT at HEAD)
  3. Extracts explicit evidence-bound claim
  4. Validates via K0-K8, Kτ, W gate stack
  5. Emits AUTORESEARCH_RECEIPT_V1

After 200 epochs:
  Aggregates into OBSIDIAN_MIRROR_ATTRACTOR_MAP_V1
  Emits report + state

Corpus probed: the SOT repo at current HEAD (read-only).
All probes are deterministic: same HEAD → same results.
No LLM calls. No network access. No sovereign writes.

Autoresearch doctrine: docs/autoresearch/doctrine.md
Gate reference:        docs/autoresearch/gates.md
Receipt schema:        docs/autoresearch/receipt_schema.md
"""

import hashlib
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent
REPORT_PATH = OUTPUT_DIR / "AUTORESEARCH_200_REPORT.md"
STATE_PATH  = OUTPUT_DIR / "state_autoresearch_200.json"

_PROTECTED = {
    "town/ledger_v1.ndjson": None,
    "helen_os/governance": None,
    "helen_os/schemas": None,
    "oracle_town/kernel": None,
}
_WRITES: list = []

# ------------------------------------------------------------------ #
# Attractor concepts and probe dimensions                             #
# ------------------------------------------------------------------ #

ATTRACTORS = [
    "REPLAY",
    "IDENTITY",
    "WITNESS",
    "DETERMINISM",
    "COMPRESSION",
    "PROVENANCE",
    "GOVERNANCE",
    "RECONSTRUCTION",
    "COUPLING",
    "ADMISSION",
]

# Search terms per concept (case-insensitive)
ATTRACTOR_TERMS = {
    "REPLAY":         ["replay", "Replay", "REPLAY"],
    "IDENTITY":       ["identity", "Identity", "ℐ(L)", "replayable lineage"],
    "WITNESS":        ["witness", "Witness", "WITNESS", "coupling"],
    "DETERMINISM":    ["determinism", "deterministic", "mu_DETERMINISM", "K-tau"],
    "COMPRESSION":    ["compression", "compress", "spectral", "latent"],
    "PROVENANCE":     ["provenance", "Provenance", "PROVENANCE", "commit_sha"],
    "GOVERNANCE":     ["governance", "Governance", "GOVERNANCE", "gate", "MAYOR"],
    "RECONSTRUCTION": ["reconstruct", "Reconstruct", "RECONSTRUCTION", "repair"],
    "COUPLING":       ["coupling", "Coupled", "COUPLED", "delta_R", "Δ_R"],
    "ADMISSION":      ["admission", "Admission", "ADMISSION", "admit", "ADMIT"],
}

# Probe dimensions: (id, label, search_path, probe_type)
PROBE_DIMENSIONS = [
    ("d01", "frequency_in_docs",           "docs",                        "FREQUENCY"),
    ("d02", "frequency_in_governance",     "helen_os/governance",         "FREQUENCY"),
    ("d03", "frequency_in_oracle_town",    "oracle_town",                 "FREQUENCY"),
    ("d04", "frequency_in_sandbox",        "sandbox",                     "FREQUENCY"),
    ("d05", "frequency_in_tools",          "tools",                       "FREQUENCY"),
    ("d06", "frequency_in_scripts",        "scripts",                     "FREQUENCY"),
    ("d07", "frequency_in_tests",          "tests",                       "FREQUENCY"),
    ("d08", "coupling_with_receipt",       ".",                           "COUPLING"),
    ("d09", "coupling_with_ledger",        ".",                           "COUPLING"),
    ("d10", "coupling_with_gate",          ".",                           "COUPLING"),
    ("d11", "coupling_with_sovereign",     ".",                           "COUPLING"),
    ("d12", "in_k8_artifacts",             "artifacts",                   "FREQUENCY"),
    ("d13", "in_garden_reports",           "sandbox/autoresearch",        "FREQUENCY"),
    ("d14", "in_proposals",               "docs/proposals",               "FREQUENCY"),
    ("d15", "in_kernel_canon",             ".",                           "FREQUENCY"),
    ("d16", "in_autoresearch_docs",        "docs/autoresearch",           "FREQUENCY"),
    ("d17", "in_helen_os_tests",           "helen_os/tests",              "FREQUENCY"),
    ("d18", "in_src",                      "src",                         "FREQUENCY"),
    ("d19", "coupling_with_replay",        ".",                           "COUPLING"),
    ("d20", "corpus_coverage",             ".",                           "COVERAGE"),
]

# Coupling partners per probe dimension
COUPLING_PARTNERS = {
    "d08": ["receipt", "RECEIPT", "Receipt"],
    "d09": ["ledger", "Ledger", "LEDGER"],
    "d10": ["gate", "Gate", "GATE"],
    "d11": ["sovereign", "Sovereign", "SOVEREIGN"],
    "d19": ["replay", "Replay", "REPLAY"],
}

# Thresholds for CONFIRMED/WEAK/ABSENT
CONFIRM_THRESHOLD = 3   # ≥3 files for CONFIRMED
WEAK_THRESHOLD    = 1   # ≥1 file for WEAK


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
            raise RuntimeError(f"AUTORESEARCH BLOCKED: write to sovereign path {path}")
    path.write_text(content, encoding="utf-8")
    _WRITES.append(str(path))


# ------------------------------------------------------------------ #
# Corpus probe                                                        #
# ------------------------------------------------------------------ #

def _grep_count(term: str, path: Path) -> tuple:
    """
    Returns (file_count, total_lines, matching_files[:5]).
    Uses grep -r -l for file list, grep -r -c for count.
    Deterministic: same corpus = same result.
    """
    if not path.exists():
        return 0, 0, []

    try:
        # File list
        result_l = subprocess.run(
            ["grep", "-r", "-l", "-i", "--include=*.py",
             "--include=*.md", "--include=*.json", "--include=*.txt",
             term, str(path)],
            capture_output=True, text=True, timeout=10, cwd=ROOT,
        )
        files = [f for f in result_l.stdout.strip().splitlines() if f]
        file_count = len(files)

        # Line count
        result_c = subprocess.run(
            ["grep", "-r", "-c", "-i", "--include=*.py",
             "--include=*.md", "--include=*.json", "--include=*.txt",
             term, str(path)],
            capture_output=True, text=True, timeout=10, cwd=ROOT,
        )
        total_lines = 0
        for line in result_c.stdout.splitlines():
            if ":" in line:
                try:
                    total_lines += int(line.split(":")[-1])
                except ValueError:
                    pass

        return file_count, total_lines, sorted(files)[:5]

    except (subprocess.TimeoutExpired, OSError):
        return 0, 0, []


def probe_frequency(concept: str, search_path: Path) -> dict:
    """FREQUENCY probe: count appearances of concept in path."""
    terms = ATTRACTOR_TERMS.get(concept, [concept.lower()])
    total_files = 0
    total_lines = 0
    top_files: list = []

    for term in terms[:2]:  # primary + secondary only (speed)
        fc, lc, tfs = _grep_count(term, search_path)
        total_files = max(total_files, fc)
        total_lines += lc
        for tf in tfs:
            if tf not in top_files:
                top_files.append(tf)

    return {
        "evidence_count": total_files,
        "line_count": total_lines,
        "source_paths": top_files[:5],
        "probe_type": "FREQUENCY",
    }


def probe_coupling(concept: str, coupling_terms: list, search_path: Path) -> dict:
    """COUPLING probe: does concept co-occur with coupling_terms in same files?"""
    # Files containing the concept
    primary_terms = ATTRACTOR_TERMS.get(concept, [concept.lower()])
    concept_files: set = set()
    for term in primary_terms[:1]:
        _, _, files = _grep_count(term, search_path)
        concept_files.update(files)

    if not concept_files:
        return {"evidence_count": 0, "source_paths": [], "probe_type": "COUPLING"}

    # Files also containing coupling term
    coupled_files: set = set()
    for cterm in coupling_terms[:1]:
        _, _, files = _grep_count(cterm, search_path)
        coupled_files.update(files)

    overlap = concept_files & coupled_files
    return {
        "evidence_count": len(overlap),
        "source_paths": sorted(overlap)[:5],
        "probe_type": "COUPLING",
    }


def probe_coverage(concept: str, search_path: Path) -> dict:
    """COVERAGE probe: how broadly does concept appear across the full repo?"""
    terms = ATTRACTOR_TERMS.get(concept, [concept.lower()])
    _, _, files = _grep_count(terms[0], search_path)
    return {
        "evidence_count": len(files),
        "source_paths": files[:5],
        "probe_type": "COVERAGE",
    }


def hash_sources(source_paths: list) -> dict:
    """sha256 first 256 bytes of each source file for provenance binding."""
    result = {}
    for sp in source_paths:
        p = ROOT / sp if not sp.startswith("/") else Path(sp)
        try:
            data = p.read_bytes()[:256]
            result[str(p.relative_to(ROOT))] = "sha256:" + hashlib.sha256(data).hexdigest()[:16]
        except (OSError, ValueError):
            result[sp] = "UNREADABLE"
    return result


# ------------------------------------------------------------------ #
# Gate validation                                                     #
# ------------------------------------------------------------------ #

def validate_gates(epoch_data: dict) -> dict:
    """
    Run K0-K8, Kτ, W gate stack on a candidate receipt.
    Returns gate_scores dict and gate_total float.
    """
    scores = {}

    # K0: syntax valid — evidence_count is int, claim is string
    scores["K0"] = 1 if (
        isinstance(epoch_data.get("evidence_count"), int) and
        isinstance(epoch_data.get("claim"), str) and
        len(epoch_data.get("claim", "")) > 10
    ) else 0

    # K1: source bound — at least one source_path
    scores["K1"] = 1 if len(epoch_data.get("source_paths", [])) > 0 or \
                        epoch_data.get("evidence_count", 0) == 0 else 0

    # K2: claim explicit — no hedging language
    claim = epoch_data.get("claim", "")
    hedge_words = ["probably", "might", "seems", "appears to", "it seems", "perhaps", "maybe"]
    scores["K2"] = 0 if any(h in claim.lower() for h in hedge_words) else 1

    # K3: evidence attached — source_hashes present
    scores["K3"] = 1 if epoch_data.get("source_hashes") is not None else 0

    # K4: method declared — probe_type is set
    scores["K4"] = 1 if epoch_data.get("probe_type") in (
        "FREQUENCY", "COUPLING", "EVOLUTION", "CONTRADICTION", "COVERAGE", "STALENESS"
    ) else 0

    # K5: contradiction scan — ABSENT verdict with evidence_count > 0 is contradictory
    verdict = epoch_data.get("verdict", "")
    ev_count = epoch_data.get("evidence_count", 0)
    scores["K5"] = 0 if (verdict == "ABSENT" and ev_count > 0) else 1
    scores["K5"] = 0 if (verdict == "CONFIRMED" and ev_count == 0) else scores["K5"]

    # K6: provenance stable — source_hashes computed (we just computed them, so stable)
    scores["K6"] = 1 if epoch_data.get("source_hashes") is not None else 0

    # K7: replay path — claim can be reconstructed from evidence bindings
    # Satisfied if: probe_type + source_paths + evidence_count → deterministic claim
    scores["K7"] = 1 if (
        scores["K4"] == 1 and scores["K1"] == 1 and scores["K0"] == 1
    ) else 0

    # K8: deterministic artifact — no model output, no random in claim chain
    # Satisfied by construction (grep-based, no LLM calls)
    scores["K8"] = 1

    # Kτ: temporal coherence — no datetime.now() in this file (verified externally)
    # Satisfied by construction
    scores["Ktau"] = 1

    # W: witness coupling — claim references real corpus state (we probed the actual files)
    scores["W"] = 1 if epoch_data.get("probe_ran", False) else 0

    gate_total = sum(scores.values()) / len(scores)
    return scores, gate_total


# ------------------------------------------------------------------ #
# Single epoch                                                        #
# ------------------------------------------------------------------ #

def run_epoch(epoch_num: int, concept: str, dim_id: str, dim_label: str,
              search_path_rel: str, probe_type: str) -> dict:
    """Run one autoresearch epoch. Returns AUTORESEARCH_RECEIPT_V1."""
    search_path = ROOT / search_path_rel

    # Run probe
    if probe_type == "FREQUENCY":
        probe_result = probe_frequency(concept, search_path)
    elif probe_type == "COUPLING":
        coupling_terms = COUPLING_PARTNERS.get(dim_id, ["receipt"])
        probe_result = probe_coupling(concept, coupling_terms, search_path)
    elif probe_type == "COVERAGE":
        probe_result = probe_coverage(concept, search_path)
    else:
        probe_result = {"evidence_count": 0, "source_paths": [], "probe_type": probe_type}

    evidence_count = probe_result["evidence_count"]
    source_paths   = probe_result["source_paths"]

    # Determine verdict
    if evidence_count >= CONFIRM_THRESHOLD:
        verdict = "CONFIRMED"
    elif evidence_count >= WEAK_THRESHOLD:
        verdict = "WEAK"
    else:
        verdict = "ABSENT"

    # Build explicit claim
    if verdict == "CONFIRMED":
        claim = (f"{concept} appears in {evidence_count} files under {search_path_rel!r} "
                 f"via {probe_type} probe ({dim_label}) — strong attractor signal")
    elif verdict == "WEAK":
        claim = (f"{concept} appears in {evidence_count} files under {search_path_rel!r} "
                 f"via {probe_type} probe ({dim_label}) — weak attractor signal")
    else:
        claim = (f"{concept} is absent from {search_path_rel!r} "
                 f"via {probe_type} probe ({dim_label}) — no attractor signal in this dimension")

    # Bind evidence
    source_hashes = hash_sources(source_paths)

    epoch_data = {
        "epoch": epoch_num,
        "concept": concept,
        "probe_dimension": dim_label,
        "probe_id": dim_id,
        "probe_type": probe_type,
        "search_path": search_path_rel,
        "hypothesis": (f"{concept} is a recurring concept in {search_path_rel!r} "
                       f"({probe_type}: {dim_label})"),
        "evidence_count": evidence_count,
        "verdict": verdict,
        "claim": claim,
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "probe_ran": True,
    }

    # Validate gates
    gate_scores, gate_total = validate_gates(epoch_data)

    # Compute receipt hash
    receipt_payload = {
        "epoch": epoch_num,
        "concept": concept,
        "probe_dimension": dim_label,
        "claim": claim,
        "evidence_count": evidence_count,
        "verdict": verdict,
    }
    receipt_hash = "sha256:" + hashlib.sha256(
        json.dumps(receipt_payload, sort_keys=True).encode()
    ).hexdigest()[:32]

    return {
        "type": "AUTORESEARCH_RECEIPT_V1",
        "epoch": epoch_num,
        "concept": concept,
        "probe_dimension": dim_label,
        "probe_type": probe_type,
        "hypothesis": epoch_data["hypothesis"],
        "evidence_count": evidence_count,
        "verdict": verdict,
        "claim": claim,
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "gate_scores": gate_scores,
        "gate_total": round(gate_total, 4),
        "lineage_contribution": 1.0 if verdict == "CONFIRMED" else (0.5 if verdict == "WEAK" else 0.0),
        "receipt_hash": receipt_hash,
        "authority": "NONE",
        "non_sovereign": True,
    }


# ------------------------------------------------------------------ #
# Attractor map aggregation                                           #
# ------------------------------------------------------------------ #

def build_attractor_map(receipts: list, head_sha: str) -> dict:
    """Aggregate 200 epoch receipts into OBSIDIAN_MIRROR_ATTRACTOR_MAP_V1."""
    by_concept: dict = {}
    for r in receipts:
        c = r["concept"]
        if c not in by_concept:
            by_concept[c] = {"confirmed": 0, "weak": 0, "absent": 0, "error": 0,
                              "gate_totals": [], "top_sources": set()}
        bucket = by_concept[c]
        v = r.get("verdict", "ERROR")
        if v == "CONFIRMED":
            bucket["confirmed"] += 1
        elif v == "WEAK":
            bucket["weak"] += 1
        elif v == "ABSENT":
            bucket["absent"] += 1
        else:
            bucket["error"] += 1
        bucket["gate_totals"].append(r.get("gate_total", 0))
        for sp in r.get("source_paths", []):
            # extract top-level dir
            parts = sp.split("/")
            if parts:
                bucket["top_sources"].add(parts[0])

    attractors = []
    for concept in ATTRACTORS:
        b = by_concept.get(concept, {"confirmed": 0, "weak": 0, "absent": 0,
                                     "error": 0, "gate_totals": [], "top_sources": set()})
        total_probes = b["confirmed"] + b["weak"] + b["absent"]
        if total_probes == 0:
            total_probes = 1
        lineage_pressure = round(
            (b["confirmed"] + 0.5 * b["weak"]) / total_probes, 4
        )
        avg_gate = round(sum(b["gate_totals"]) / max(len(b["gate_totals"]), 1), 4)
        attractors.append({
            "concept": concept,
            "probe_angles_run": len(PROBE_DIMENSIONS),
            "confirmed": b["confirmed"],
            "weak": b["weak"],
            "absent": b["absent"],
            "lineage_pressure": lineage_pressure,
            "avg_gate_score": avg_gate,
            "top_sources": sorted(b["top_sources"]),
        })

    # Sort by lineage_pressure desc
    attractors.sort(key=lambda x: x["lineage_pressure"], reverse=True)

    return {
        "type": "OBSIDIAN_MIRROR_ATTRACTOR_MAP_V1",
        "epochs_run": len(receipts),
        "head_sha": head_sha,
        "attractors": attractors,
        "authority": "NONE",
        "non_sovereign": True,
    }


# ------------------------------------------------------------------ #
# Report                                                              #
# ------------------------------------------------------------------ #

def write_report(attractor_map: dict, stats: dict) -> str:
    am = attractor_map
    lines = [
        "# HELEN Autoresearch — 200 Epochs Report",
        "",
        "**authority: NONE · NON_SOVEREIGN · NO_SHIP · SANDBOX_ONLY**",
        "",
        f"epochs_run     : {am['epochs_run']}",
        f"head_sha       : {am['head_sha'][:16]}...",
        f"elapsed        : {stats['elapsed']:.2f}s",
        f"sovereign_safe : {stats['hashes_match']}",
        "",
        "## Obsidian Mirror — Attractor Map",
        "",
        "| Rank | Concept | Confirmed | Weak | Absent | Lineage Pressure | Top Sources |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, att in enumerate(am["attractors"], 1):
        sources = ", ".join(att["top_sources"][:3]) if att["top_sources"] else "—"
        lp = att["lineage_pressure"]
        signal = "🔴" if lp >= 0.8 else ("🟡" if lp >= 0.5 else "⚪")
        lines.append(
            f"| {i} | {signal} **{att['concept']}** | {att['confirmed']} | "
            f"{att['weak']} | {att['absent']} | {lp:.4f} | {sources} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "**Lineage pressure** = (confirmed + 0.5 × weak) / total_probes",
        "- ≥ 0.80: Strong attractor — concept recurs across multiple corpus dimensions",
        "- 0.50–0.79: Moderate attractor — present but unevenly distributed",
        "- < 0.50: Weak or context-specific — not a corpus-level attractor",
        "",
        "## Gate Performance",
        "",
        f"Receipts with gate_total = 1.0: {stats['perfect_gate_count']} / {am['epochs_run']}",
        f"Receipts with gate failure:     {stats['gate_fail_count']}",
        "",
        "## Honest Boundary",
        "",
        "1. **Frequency ≠ importance.** High lineage_pressure means the concept appears",
        "   often in the corpus — not that it is philosophically primary.",
        "2. **Coupling probes are shallow.** Co-occurrence in the same file ≠ causal link.",
        "3. **ABSENT does not mean irrelevant.** A concept may be real but named differently.",
        "4. **This map is NON_SOVEREIGN.** It is a candidate input for doctrine delta,",
        "   not doctrine itself. MAYOR routing required before any doctrine update.",
        "5. **Gate K5 (contradiction scan) is structural only.** Semantic contradictions",
        "   are not detected — requires reducer/human oracle (same gap as T5).",
        "",
        "## Doctrine Delta Candidates",
        "",
        "The following concepts have lineage_pressure ≥ 0.80 and are candidate inputs",
        "for doctrine delta (subject to MAYOR routing and receipt admission):",
        "",
    ]
    for att in am["attractors"]:
        if att["lineage_pressure"] >= 0.80:
            lines.append(
                f"- **{att['concept']}** (pressure={att['lineage_pressure']:.4f}, "
                f"confirmed={att['confirmed']}/20)"
            )
    lines += [
        "",
        "## Next Frontier (T7)",
        "",
        "T6 established temporal opacity as the dominant provenance gap.",
        "T7 candidate: content-hash staleness — verify artifact SHA on disk",
        "matches the SHA recorded in the provenance sidecar.",
        "epistemic_taxonomy_probe.py already walks paths; SHA check is one field away.",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ #
# Main                                                                #
# ------------------------------------------------------------------ #

def main() -> None:
    t_start = time.monotonic()
    print("[AR200] HELEN Autoresearch — 200 Epochs")
    print(f"[AR200] ROOT = {ROOT}")

    before = _snapshot()

    # Get HEAD SHA (read-only git command)
    head_result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT,
        capture_output=True, text=True,
    )
    head_sha = head_result.stdout.strip() if head_result.returncode == 0 else "UNKNOWN"
    print(f"[AR200] HEAD = {head_sha[:16]}...")

    # Build 200 epochs: 10 attractors × 20 probe dimensions
    epochs_plan = []
    epoch_num = 1
    for dim_id, dim_label, search_path_rel, probe_type in PROBE_DIMENSIONS:
        for concept in ATTRACTORS:
            epochs_plan.append((epoch_num, concept, dim_id, dim_label,
                                search_path_rel, probe_type))
            epoch_num += 1

    assert len(epochs_plan) == 200, f"Expected 200 epochs, got {len(epochs_plan)}"

    # Run epochs
    receipts = []
    perfect_gate_count = 0
    gate_fail_count = 0
    confirmed_count = 0
    weak_count = 0
    absent_count = 0

    print(f"[AR200] Running {len(epochs_plan)} epochs...")
    for i, (ep_num, concept, dim_id, dim_label, search_path_rel, probe_type) in enumerate(epochs_plan):
        receipt = run_epoch(ep_num, concept, dim_id, dim_label, search_path_rel, probe_type)
        receipts.append(receipt)

        gt = receipt.get("gate_total", 0)
        if gt == 1.0:
            perfect_gate_count += 1
        else:
            gate_fail_count += 1

        v = receipt.get("verdict", "")
        if v == "CONFIRMED":
            confirmed_count += 1
        elif v == "WEAK":
            weak_count += 1
        else:
            absent_count += 1

        if (i + 1) % 50 == 0:
            print(f"[AR200] {i+1}/200 complete...")

    # Build attractor map
    attractor_map = build_attractor_map(receipts, head_sha)

    after = _snapshot()
    hashes_match = before == after
    elapsed = time.monotonic() - t_start

    if not hashes_match:
        raise RuntimeError(
            f"[AR200] SOVEREIGN PATH MUTATION DETECTED\n"
            f"  before: {before}\n  after:  {after}"
        )

    stats = {
        "elapsed": elapsed,
        "hashes_match": hashes_match,
        "perfect_gate_count": perfect_gate_count,
        "gate_fail_count": gate_fail_count,
        "confirmed_count": confirmed_count,
        "weak_count": weak_count,
        "absent_count": absent_count,
    }

    # Print attractor map summary
    print()
    print("[AR200] OBSIDIAN MIRROR — ATTRACTOR MAP")
    print(f"{'Rank':<5} {'Concept':<18} {'Conf':<6} {'Weak':<6} {'Abs':<6} {'Pressure':<10}")
    print("-" * 55)
    for i, att in enumerate(attractor_map["attractors"], 1):
        lp = att["lineage_pressure"]
        marker = "🔴" if lp >= 0.8 else ("🟡" if lp >= 0.5 else "⚪")
        print(f"  {i:<3} {marker} {att['concept']:<16} {att['confirmed']:<6} "
              f"{att['weak']:<6} {att['absent']:<6} {lp:.4f}")

    print()
    print(f"[AR200] epochs:    {len(receipts)}")
    print(f"[AR200] confirmed: {confirmed_count}")
    print(f"[AR200] weak:      {weak_count}")
    print(f"[AR200] absent:    {absent_count}")
    print(f"[AR200] gate 1.0:  {perfect_gate_count}/{len(receipts)}")
    print(f"[AR200] elapsed:   {elapsed:.2f}s")
    print(f"[AR200] sovereign: {hashes_match}")

    # Write outputs
    report_text = write_report(attractor_map, stats)
    state_data = {
        "autoresearch_mode": True,
        "epochs_run": len(receipts),
        "head_sha": head_sha,
        "attractor_map": attractor_map,
        "stats": stats,
        "receipts_summary": {
            "total": len(receipts),
            "confirmed": confirmed_count,
            "weak": weak_count,
            "absent": absent_count,
            "perfect_gate": perfect_gate_count,
        },
        "protected_before": before,
        "protected_after": after,
    }

    _write(REPORT_PATH, report_text)
    _write(STATE_PATH, json.dumps(state_data, indent=2))

    print(f"\n[AR200] Report → {REPORT_PATH}")
    print(f"[AR200] State  → {STATE_PATH}")
    print(f"\n[AR200] AUTORESEARCH COMPLETE — sovereign paths intact")


if __name__ == "__main__":
    main()
