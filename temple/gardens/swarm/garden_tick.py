#!/usr/bin/env python3
"""
HELEN Garden Tick — Daily autonomous swarm cycle

Orchestrates: GOBLIN-* → HER → HAL → MAYOR-SHADOW → compost sweep → Dawn Report

Authority: NON_SOVEREIGN  Canon: NO_SHIP  Ledger effect: none
Nothing here touches the kernel, ledger, or sovereign schemas.
This is Z2 — the quantum bloom zone.

Usage:
    python garden_tick.py                      # run one full cycle
    python garden_tick.py --dry-run            # print plan, write nothing
    python garden_tick.py --status             # show current garden state
    python garden_tick.py --cycle N            # override cycle number (for testing)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ──────────────────────────────────────────────────────────────────────

SWARM_ROOT = Path(__file__).resolve().parent
GARDEN_ROOT = SWARM_ROOT.parent
SCHEMAS_ROOT = SWARM_ROOT.parent.parent.parent / "schemas" / "helen_superteam"

STATE_FILE = SWARM_ROOT / "garden_state.json"
DAWN_REPORTS_DIR = SWARM_ROOT / "dawn_reports"
COMPOST_ARCHIVE_DIR = SWARM_ROOT / "compost_archive"

NPC_DIRS = {
    "goblin_arxiv":    SWARM_ROOT / "goblin_arxiv",
    "goblin_agora":    SWARM_ROOT / "goblin_agora",
    "goblin_postmaster": SWARM_ROOT / "goblin_postmaster",
    "goblin_compost":  SWARM_ROOT / "goblin_compost",
    "her":             SWARM_ROOT / "her",
    "hal":             SWARM_ROOT / "hal",
    "mayor_shadow":    SWARM_ROOT / "mayor_shadow",
}

# ── constants ──────────────────────────────────────────────────────────────────

DECAY_CYCLES = 7          # artifact dies after this many cycles without collapse
SEED_LIMIT = 20           # max active DreamSeeds
INSIGHT_LIMIT = 5         # max active InsightCandidates
CLAIM_LIMIT = 2           # max active ClaimCandidates

# ── state management ──────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def _hash8(content: str) -> str:
    return _hash_content(content)[:8]

def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "schema": "GARDEN_STATE_V1",
        "current_cycle": 0,
        "started_at": _now(),
        "authority": False,
        "ledger_effect": "none",
        "artifacts": {},
        "compost_hashes": [],
    }

def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def register_artifact(state: dict, artifact: dict, npc: str, artifact_type: str, path: Path) -> None:
    artifact_id = artifact.get("seed_id") or artifact.get("insight_id") or artifact.get("claim_id", "unknown")
    content_hash = _hash_content(json.dumps(artifact, sort_keys=True))
    state["artifacts"][artifact_id] = {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "npc": npc,
        "path": str(path.relative_to(SWARM_ROOT.parent.parent.parent)),
        "content_hash": content_hash,
        "created_cycle": state["current_cycle"],
        "composted": False,
        "collapsed": False,
    }

def get_active_artifacts(state: dict, artifact_type: str) -> list[dict]:
    """Return non-composted, non-collapsed artifacts of a given type."""
    result = []
    for info in state["artifacts"].values():
        if info["artifact_type"] == artifact_type and not info["composted"] and not info["collapsed"]:
            path = SWARM_ROOT.parent.parent.parent / info["path"]
            if path.exists():
                result.append(json.loads(path.read_text()))
    return result

# ── NPC stubs (pluggable) ──────────────────────────────────────────────────────

def _make_seed_id(content: str) -> str:
    return f"SEED-{_hash8(content)}"

def _make_insight_id(content: str) -> str:
    return f"INS-{_hash8(content)}"

def _make_claim_id(content: str) -> str:
    return f"CLM-{_hash8(content)}"

def run_goblin_arxiv(state: dict, dry_run: bool) -> list[dict]:
    """
    GOBLIN-ARXIV: ingest arxiv RSS signals.
    Real implementation: fetch arxiv RSS for allowlisted categories,
    extract abstract fragments, motif-tag, produce DreamSeeds.

    Stub: reads from goblin_arxiv/inbox/ if present, else produces zero seeds.
    Wire real feed: place JSON files in goblin_arxiv/inbox/ before tick.
    """
    inbox = NPC_DIRS["goblin_arxiv"] / "inbox"
    seeds = []
    if not inbox.exists():
        return seeds

    for f in sorted(inbox.glob("*.json"))[:3]:
        raw = json.loads(f.read_text())
        seed_content = json.dumps(raw, sort_keys=True)
        seed = {
            "seed_id": _make_seed_id(f"arxiv:{seed_content}"),
            "source_refs": [raw.get("url", f.name)],
            "raw_fragments": raw.get("fragments", [str(raw)[:300]]),
            "motifs": raw.get("motifs", []),
            "wild_connections": raw.get("wild_connections", []),
            "why_it_feels_interesting": raw.get("why", "arxiv signal — chiddush TBD by HER"),
            "input_type": "article",
            "claim_status": "NO_CLAIM",
            "authority": False,
            "actor": "GOBLIN",
            "created_at": _now(),
        }
        seeds.append(seed)
        if not dry_run:
            f.rename(f.parent.parent / "inbox_processed" / f.name) if False else None
    return seeds

def run_goblin_agora(state: dict, dry_run: bool) -> list[dict]:
    """
    GOBLIN-AGORA: ingest X/Twitter saved posts.
    Stub: reads from goblin_agora/inbox/ JSON files.
    Wire real feed: export saved posts to goblin_agora/inbox/ before tick.
    """
    inbox = NPC_DIRS["goblin_agora"] / "inbox"
    seeds = []
    if not inbox.exists():
        return seeds

    for f in sorted(inbox.glob("*.json"))[:3]:
        raw = json.loads(f.read_text())
        seed = {
            "seed_id": _make_seed_id(f"agora:{f.name}:{raw}"),
            "source_refs": [raw.get("url", f.name)],
            "raw_fragments": [raw.get("text", str(raw)[:280])],
            "motifs": raw.get("motifs", []),
            "wild_connections": [],
            "why_it_feels_interesting": raw.get("why", "X/Twitter signal — resonance TBD"),
            "input_type": "tweet",
            "claim_status": "NO_CLAIM",
            "authority": False,
            "actor": "GOBLIN",
            "created_at": _now(),
        }
        seeds.append(seed)
    return seeds

def run_goblin_postmaster(state: dict, dry_run: bool) -> list[dict]:
    """
    GOBLIN-POSTMASTER: ingest JM email digest patterns (read-only, redacted).
    Stub: reads from goblin_postmaster/inbox/ JSON files.
    Wire real feed: export redacted email digest to goblin_postmaster/inbox/.
    """
    inbox = NPC_DIRS["goblin_postmaster"] / "inbox"
    seeds = []
    if not inbox.exists():
        return seeds

    for f in sorted(inbox.glob("*.json"))[:2]:
        raw = json.loads(f.read_text())
        seed = {
            "seed_id": _make_seed_id(f"postmaster:{f.name}:{raw}"),
            "source_refs": [f"email:{raw.get('subject', f.name)}"],
            "raw_fragments": [raw.get("pattern", str(raw)[:300])],
            "motifs": raw.get("motifs", []),
            "wild_connections": raw.get("wild_connections", []),
            "why_it_feels_interesting": raw.get("why", "email signal pattern — chiddush TBD"),
            "input_type": "other",
            "claim_status": "NO_CLAIM",
            "authority": False,
            "actor": "GOBLIN",
            "created_at": _now(),
        }
        seeds.append(seed)
    return seeds

def run_goblin_compost(state: dict, dry_run: bool) -> list[dict]:
    """
    GOBLIN-COMPOST: generate mutation seeds from decayed artifact hashes.
    This is the recursive feedback loop: what died feeds what lives next.
    """
    hashes = state.get("compost_hashes", [])
    if not hashes:
        return []

    recent_hashes = hashes[-10:]
    seed = {
        "seed_id": _make_seed_id(f"compost:{json.dumps(recent_hashes)}"),
        "source_refs": [f"compost_archive:{h[:8]}" for h in recent_hashes],
        "raw_fragments": [f"composted signal hash: {h[:16]}" for h in recent_hashes],
        "motifs": ["decay as signal", "what was rejected might recombine"],
        "wild_connections": ["Nietzsche: what does not kill me — applied to ideas", "immune selection loop"],
        "why_it_feels_interesting": f"{len(recent_hashes)} artifacts composted recently — their absence is a pattern. What survived tells us what the swarm values.",
        "input_type": "other",
        "claim_status": "NO_CLAIM",
        "authority": False,
        "actor": "GOBLIN",
        "created_at": _now(),
    }
    return [seed]

def run_her_fusion(state: dict, seeds: list[dict], dry_run: bool) -> list[dict]:
    """
    HER fusion pass: fuse 3–5 seeds sharing motifs into InsightCandidates.
    Blindness: HER sees only seed artifacts, never raw input or GOBLIN deliberation.

    Real implementation: call LLM with stripped seeds, ask for chiddush extraction.
    Stub: generates a minimal InsightCandidate if >= 3 seeds exist.
    """
    if len(seeds) < 3:
        return []

    # Collect all motifs across seeds and find common themes
    all_motifs: dict[str, int] = {}
    for seed in seeds:
        for motif in seed.get("motifs", []):
            all_motifs[motif] = all_motifs.get(motif, 0) + 1

    if not all_motifs:
        return []

    # Group seeds by dominant motif (take top 5 seeds)
    top_seeds = seeds[:5]
    top_motifs = sorted(all_motifs, key=lambda m: all_motifs[m], reverse=True)[:3]

    insight_key = f"her:{json.dumps([s['seed_id'] for s in top_seeds])}"
    insight = {
        "insight_id": _make_insight_id(insight_key),
        "derived_from_seed_ids": [s["seed_id"] for s in top_seeds],
        "insight_sentence": f"Across {len(top_seeds)} signals, a pattern emerges around: {', '.join(top_motifs)}. [HER stub — LLM synthesis needed for real chiddush]",
        "source_refs": list({ref for s in top_seeds for ref in s.get("source_refs", [])}),
        "resonance": f"The motifs {top_motifs} appear across unrelated sources — this convergence feels non-accidental.",
        "possible_use": "If the pattern holds, it may inform the next HELEN OS architectural decision or research hypothesis.",
        "uncertainty": "Stub output — real HER requires LLM synthesis. Motif clustering is surface-level.",
        "evidence_needed": "A real LLM pass over the seed fragments to extract genuine chiddush and test whether the pattern survives scrutiny.",
        "claim_status": "CANDIDATE",
        "authority": False,
        "actor": "HER",
        "created_at": _now(),
    }
    return [insight]

def run_hal_binding(state: dict, insights: list[dict], dry_run: bool) -> list[dict]:
    """
    HAL binding pass: bind 2+ insights to evidence → ClaimCandidates.
    Blindness: HAL sees only InsightCandidates, never seeds or HER process.

    Real implementation: LLM call — strict administrator mode, demands falsifiability.
    Stub: generates minimal ClaimCandidate if >= 2 insights exist.
    """
    if len(insights) < 1:
        return []

    insight = insights[0]
    claim_key = f"hal:{insight['insight_id']}"
    claim = {
        "claim_id": _make_claim_id(claim_key),
        "claim_sentence": f"[HAL stub] The pattern in {insight['insight_id']} constitutes a testable structural claim about HELEN OS. [Needs real HAL LLM pass for precision]",
        "claim_type": "architecture",
        "source_refs": insight.get("source_refs", []),
        "evidence_refs": [],
        "evidence_requirement": insight.get("evidence_needed", "Evidence requirement TBD by real HAL pass."),
        "test_or_review_path": "Peer review by MAYOR + operator. Real test path requires LLM synthesis.",
        "risk_if_wrong": "Low — this is a NO_CLAIM zone. Risk materializes only if collapsed into Z3.",
        "hal_reason": f"Derived from InsightCandidate {insight['insight_id']}. Stub — real HAL requires strict falsifiability check.",
        "derived_from_insight_id": insight["insight_id"],
        "claim_status": "CLAIM_CANDIDATE",
        "authority": False,
        "actor": "HAL",
        "created_at": _now(),
    }
    return [claim]

def run_mayor_shadow(state: dict, claims: list[dict], dry_run: bool) -> dict:
    """
    MAYOR-SHADOW: advisory ranking and objection notes.
    NEVER a verdict. NEVER a receipt. Advisory only.
    Blindness: MAYOR-SHADOW sees ClaimCandidates only, stripped of upstream lineage.
    """
    if not claims:
        return {"ranked": [], "objections": [], "advisory": True, "actor": "MAYOR_SHADOW", "authority": False}

    ranked = []
    objections = []
    for i, claim in enumerate(claims):
        score = 10 - i  # stub: first claim ranks highest
        ranked.append({"claim_id": claim["claim_id"], "shadow_rank": score})
        if "stub" in claim.get("claim_sentence", "").lower():
            objections.append({
                "claim_id": claim["claim_id"],
                "objection": "Stub claim — requires real HAL LLM synthesis before MAYOR can evaluate.",
            })

    return {
        "schema": "MAYOR_SHADOW_ADVISORY_V0",
        "cycle": state["current_cycle"],
        "ranked": ranked,
        "objections": objections,
        "advisory": True,
        "note": "MAYOR-SHADOW ranks only. No verdicts. No receipts. Advisory input for JM's Dawn Report.",
        "actor": "MAYOR_SHADOW",
        "authority": False,
        "ledger_effect": "none",
        "created_at": _now(),
    }

# ── compost sweep ──────────────────────────────────────────────────────────────

def run_compost_sweep(state: dict, dry_run: bool) -> dict[str, list]:
    """
    Compost artifacts older than DECAY_CYCLES.
    Content withdrawn from agent view; hash retained forever in compost_hashes.
    The new invariant: EVERY BLOOM DECAYS.
    """
    current_cycle = state["current_cycle"]
    composted_this_sweep = []
    preserved = []

    for artifact_id, info in state["artifacts"].items():
        if info["composted"] or info["collapsed"]:
            continue
        age = current_cycle - info["created_cycle"]
        if age >= DECAY_CYCLES:
            # Compost: withdraw content, retain hash
            path = SWARM_ROOT.parent.parent.parent / info["path"]
            if path.exists():
                # Archive the hash
                archive_entry = {
                    "artifact_id": artifact_id,
                    "artifact_type": info["artifact_type"],
                    "content_hash": info["content_hash"],
                    "created_cycle": info["created_cycle"],
                    "composted_cycle": current_cycle,
                    "composted_at": _now(),
                    "npc": info["npc"],
                }
                archive_path = COMPOST_ARCHIVE_DIR / f"composted_{artifact_id}.json"
                if not dry_run:
                    COMPOST_ARCHIVE_DIR.mkdir(exist_ok=True)
                    archive_path.write_text(json.dumps(archive_entry, indent=2))
                    path.unlink()  # withdraw content from agent view
                    info["composted"] = True
                    state["compost_hashes"].append(info["content_hash"])

                composted_this_sweep.append(artifact_id)
        else:
            preserved.append(artifact_id)

    return {"composted": composted_this_sweep, "preserved": preserved}

# ── artifact writing ──────────────────────────────────────────────────────────

def write_artifact(npc_key: str, artifact: dict, state: dict, artifact_type: str) -> Path:
    artifact_id = (
        artifact.get("seed_id") or
        artifact.get("insight_id") or
        artifact.get("claim_id", "unknown")
    )
    # Skip if already exists (idempotent)
    if artifact_id in state["artifacts"]:
        return SWARM_ROOT / npc_key / f"{artifact_id}.json"

    npc_dir = NPC_DIRS[npc_key]
    npc_dir.mkdir(exist_ok=True)
    path = npc_dir / f"{artifact_id}.json"
    path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False))
    register_artifact(state, artifact, npc_key, artifact_type, path)
    return path

# ── dawn report ──────────────────────────────────────────────────────────────

def generate_dawn_report(
    state: dict,
    new_seeds: list[dict],
    new_insights: list[dict],
    new_claims: list[dict],
    shadow_advisory: dict,
    sweep_result: dict,
    dry_run: bool,
) -> str:
    cycle = state["current_cycle"]
    ts = _now()[:10]

    active_seeds = get_active_artifacts(state, "DreamSeed")
    active_insights = get_active_artifacts(state, "InsightCandidate")
    active_claims = get_active_artifacts(state, "ClaimCandidate")
    compost_total = len(state.get("compost_hashes", []))

    report_lines = [
        f"# GARDEN DAWN REPORT — Cycle {cycle} ({ts})",
        f"`authority: false · ledger_effect: none · NO_CLAIM`",
        "",
        "---",
        "",
        "## Bloom Summary",
        f"- **{len(new_seeds)}** new DreamSeeds bloomed this cycle",
        f"- **{len(new_insights)}** new InsightCandidates fused by HER",
        f"- **{len(new_claims)}** new ClaimCandidates framed by HAL",
        f"- **{len(sweep_result['composted'])}** artifacts composted (7-cycle decay)",
        "",
        "## Active Garden State",
        f"- DreamSeeds alive: **{len(active_seeds)}** / {SEED_LIMIT}",
        f"- InsightCandidates alive: **{len(active_insights)}** / {INSIGHT_LIMIT}",
        f"- ClaimCandidates alive: **{len(active_claims)}** / {CLAIM_LIMIT}",
        f"- Total composted (all time): **{compost_total}** (hashes retained)",
        "",
    ]

    # MAYOR-SHADOW shortlist
    ranked = shadow_advisory.get("ranked", [])
    if ranked:
        report_lines += [
            "## MAYOR-SHADOW Shortlist (advisory — no verdicts)",
        ]
        for r in ranked[:5]:
            report_lines.append(f"- `{r['claim_id']}` — shadow rank: {r['shadow_rank']}")
        report_lines.append("")

    objections = shadow_advisory.get("objections", [])
    if objections:
        report_lines += ["## MAYOR-SHADOW Objections"]
        for o in objections:
            report_lines.append(f"- `{o['claim_id']}`: {o['objection']}")
        report_lines.append("")

    # Compost obituary
    if sweep_result["composted"]:
        report_lines += [
            "## Compost Obituary",
            "The following artifacts did not survive 7 cycles — content withdrawn, hashes retained:",
        ]
        for a_id in sweep_result["composted"]:
            report_lines.append(f"- `{a_id}`")
        report_lines.append("")

    # Collapse candidates
    yes_claims = [c for c in active_claims if not state["artifacts"].get(c.get("claim_id", ""), {}).get("collapsed")]
    if yes_claims:
        report_lines += [
            "## Collapse Candidates",
            "These ClaimCandidates are alive and MAYOR-shadow-ranked. To collapse one:",
            "```bash",
            "python temple/gardens/swarm/garden_collapse.py <block_hash>",
            "```",
        ]
        for c in yes_claims[:2]:
            cid = c.get("claim_id", "?")
            info = state["artifacts"].get(cid, {})
            report_lines.append(f"- `{cid}` hash:`{info.get('content_hash', '?')[:16]}...`")
        report_lines.append("")

    report_lines += [
        "---",
        "",
        "> *Ledger remembers everything. Garden forgets almost everything. That asymmetry is the wall between castle and field.*",
        "",
        f"*Generated by garden_tick.py cycle {cycle} · {ts} · authority=false*",
    ]

    report = "\n".join(report_lines)

    if not dry_run:
        DAWN_REPORTS_DIR.mkdir(exist_ok=True)
        report_path = DAWN_REPORTS_DIR / f"dawn_cycle_{cycle:04d}_{ts}.md"
        report_path.write_text(report)
        # Also write as latest.md for easy access
        (DAWN_REPORTS_DIR / "latest.md").write_text(report)

    return report

# ── main tick ─────────────────────────────────────────────────────────────────

def run_tick(dry_run: bool = False, force_cycle: int | None = None) -> dict:
    state = load_state()

    if force_cycle is not None:
        state["current_cycle"] = force_cycle
    else:
        state["current_cycle"] += 1

    cycle = state["current_cycle"]
    print(f"── GARDEN TICK cycle {cycle} {'[DRY RUN]' if dry_run else ''} ──────────────")

    # 1. GOBLIN passes
    print("  [1/7] GOBLIN ingestion...")
    all_new_seeds = []
    for goblin_fn, npc_key in [
        (run_goblin_arxiv, "goblin_arxiv"),
        (run_goblin_agora, "goblin_agora"),
        (run_goblin_postmaster, "goblin_postmaster"),
        (run_goblin_compost, "goblin_compost"),
    ]:
        seeds = goblin_fn(state, dry_run)
        for seed in seeds:
            if not dry_run:
                write_artifact(npc_key, seed, state, "DreamSeed")
            all_new_seeds.append(seed)
            print(f"    GOBLIN [{npc_key}] → {seed['seed_id']}")

    # 2. HER fusion
    print("  [2/7] HER fusion pass...")
    active_seeds = get_active_artifacts(state, "DreamSeed")
    new_insights = run_her_fusion(state, active_seeds, dry_run)
    for insight in new_insights:
        if not dry_run:
            write_artifact("her", insight, state, "InsightCandidate")
        print(f"    HER → {insight['insight_id']}")

    # 3. HAL binding
    print("  [3/7] HAL binding pass...")
    active_insights = get_active_artifacts(state, "InsightCandidate")
    new_claims = run_hal_binding(state, active_insights, dry_run)
    for claim in new_claims:
        if not dry_run:
            write_artifact("hal", claim, state, "ClaimCandidate")
        print(f"    HAL → {claim['claim_id']}")

    # 4. MAYOR-SHADOW advisory
    print("  [4/7] MAYOR-SHADOW advisory pass...")
    active_claims = get_active_artifacts(state, "ClaimCandidate")
    shadow_advisory = run_mayor_shadow(state, active_claims, dry_run)
    if not dry_run:
        NPC_DIRS["mayor_shadow"].mkdir(exist_ok=True)
        shadow_path = NPC_DIRS["mayor_shadow"] / f"advisory_cycle_{cycle:04d}.json"
        shadow_path.write_text(json.dumps(shadow_advisory, indent=2))
    print(f"    MAYOR-SHADOW → {len(shadow_advisory.get('ranked', []))} ranked, {len(shadow_advisory.get('objections', []))} objections")

    # 5. GOBLIN-COMPOST feedback (mutation seeds from decayed hashes)
    print("  [5/7] GOBLIN-COMPOST feedback...")
    compost_seeds = run_goblin_compost(state, dry_run)
    for seed in compost_seeds:
        if not dry_run:
            write_artifact("goblin_compost", seed, state, "DreamSeed")
        print(f"    GOBLIN-COMPOST → {seed['seed_id']}")
        all_new_seeds.append(seed)

    # 6. Compost sweep — EVERY BLOOM DECAYS
    print("  [6/7] Compost sweep (7-cycle decay)...")
    sweep_result = run_compost_sweep(state, dry_run)
    if sweep_result["composted"]:
        print(f"    Composted: {sweep_result['composted']}")
    else:
        print(f"    No artifacts decayed this cycle")

    # 7. Dawn Report
    print("  [7/7] Generating Dawn Report...")
    report = generate_dawn_report(
        state, all_new_seeds, new_insights, new_claims,
        shadow_advisory, sweep_result, dry_run
    )

    if not dry_run:
        save_state(state)

    print()
    print(report)

    return {
        "cycle": cycle,
        "new_seeds": len(all_new_seeds),
        "new_insights": len(new_insights),
        "new_claims": len(new_claims),
        "composted": len(sweep_result["composted"]),
        "dry_run": dry_run,
    }

def cmd_status() -> None:
    state = load_state()
    active_seeds = get_active_artifacts(state, "DreamSeed")
    active_insights = get_active_artifacts(state, "InsightCandidate")
    active_claims = get_active_artifacts(state, "ClaimCandidate")

    print("── GARDEN STATE ─────────────────────────────────────────")
    print(f"  Current cycle:  {state['current_cycle']}")
    print(f"  DreamSeeds:     {len(active_seeds)} active / {SEED_LIMIT} limit")
    print(f"  Insights:       {len(active_insights)} active / {INSIGHT_LIMIT} limit")
    print(f"  Claims:         {len(active_claims)} active / {CLAIM_LIMIT} limit")
    print(f"  Composted:      {len(state.get('compost_hashes', []))} (hashes retained)")
    print(f"  Total tracked:  {len(state['artifacts'])}")
    print()

    collapsed = [i for i, a in state["artifacts"].items() if a.get("collapsed")]
    if collapsed:
        print(f"  Collapsed (in temple/proposals/): {len(collapsed)}")
        for a_id in collapsed:
            print(f"    {a_id}")

# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="HELEN Garden Tick — NON_SOVEREIGN, authority=false")
    parser.add_argument("--dry-run", action="store_true", help="Plan only, write nothing")
    parser.add_argument("--status", action="store_true", help="Show current garden state")
    parser.add_argument("--cycle", type=int, default=None, help="Override cycle number")
    args = parser.parse_args()

    if args.status:
        cmd_status()
    else:
        run_tick(dry_run=args.dry_run, force_cycle=args.cycle)

if __name__ == "__main__":
    main()
