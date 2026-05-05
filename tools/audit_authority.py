#!/usr/bin/env python3
"""
audit_authority.py — F-002 authority auditor (NON_SOVEREIGN)

Reads registries/plugins_allowlist.json and verifies that every plugin's
declared receipt emitters are valid actors per registries/actors.v1.json.

Doctrine: AUDIT_HONESTY (HELEN_OPERATIONAL_DISCIPLINE_V1 §5).
  - A broken mirror is safer than a false one.
  - Name drift before reconciling it.
  - An auditor that reads the wrong field is not an auditor.

Vocabulary migration discipline (F-002 axis C, 2026-05-02):
  The plugin registry field was renamed `allowed_writers` →
  `allowed_receipt_emitters`. This auditor reads BOTH names during the
  migration window. It reports which version each plugin uses, so drift
  between plugins is visible rather than hidden by silent fallback.

Caveat (F-002 axis B, still open):
  This auditor checks plugins against the registry actors list. The
  registry itself diverges from the formal kernel (formal/LedgerKernel.v
  authority_ok_event_b has 3 actors; registry has 6). That divergence is
  acknowledged in actors.v1.json. This auditor does NOT close axis B; it
  closes axis C only (vocabulary alignment).

Usage:
    python3 tools/audit_authority.py
    python3 tools/audit_authority.py --plugins registries/plugins_allowlist.json
    python3 tools/audit_authority.py --json   # machine-readable output

Exit codes:
    0 — all plugins reference valid actors
    1 — at least one plugin references an unknown actor
    2 — registry file missing or malformed
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLUGINS = REPO_ROOT / "registries" / "plugins_allowlist.json"
DEFAULT_ACTORS = REPO_ROOT / "registries" / "actors.v1.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        print(f"❌ registry file not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ malformed JSON in {path}: {e}", file=sys.stderr)
        sys.exit(2)


def iter_plugins(registry: dict[str, Any]):
    """Yield (tier_label, plugin_key, plugin_dict) for every plugin in the registry."""
    for tier_key in ("tier_0_core_plugins", "tier_1_governance_plugins"):
        tier = registry.get(tier_key, {})
        plugins = tier.get("plugins", {})
        for plugin_key, plugin in plugins.items():
            yield tier_key, plugin_key, plugin


def get_emitters(plugin: dict[str, Any]) -> tuple[list[str], str]:
    """
    Read the receipt-emitter list with graceful fallback.

    Returns (emitter_list, field_version) where field_version is one of:
      - "new"     : only `allowed_receipt_emitters` present (post-F-002-C)
      - "legacy"  : only `allowed_writers` present (pre-F-002-C)
      - "both"    : both present, must match (transitional, should not persist)
      - "missing" : neither present (registry malformed)
    """
    new = plugin.get("allowed_receipt_emitters")
    old = plugin.get("allowed_writers")

    if new is not None and old is not None:
        if new == old:
            return list(new), "both"
        return list(new), "both_mismatch"
    if new is not None:
        return list(new), "new"
    if old is not None:
        return list(old), "legacy"
    return [], "missing"


def audit(plugins_path: Path, actors_path: Path) -> dict[str, Any]:
    plugins_reg = load_json(plugins_path)
    actors_reg = load_json(actors_path)

    valid_actors = set(actors_reg.get("actors", {}).keys())

    results = []
    overall_ok = True
    field_versions_seen = set()

    for tier_label, plugin_key, plugin in iter_plugins(plugins_reg):
        plugin_id = plugin.get("plugin_id", plugin_key)
        emitters, field_version = get_emitters(plugin)
        field_versions_seen.add(field_version)

        unknown = [a for a in emitters if a not in valid_actors]

        if field_version == "missing":
            status = "FAIL"
            overall_ok = False
            note = "no allowed_receipt_emitters or allowed_writers field"
        elif field_version == "both_mismatch":
            status = "FAIL"
            overall_ok = False
            note = "both field names present and disagree"
        elif unknown:
            status = "FAIL"
            overall_ok = False
            note = f"unknown actors: {unknown}"
        else:
            status = "PASS"
            note = ""

        results.append({
            "tier": tier_label,
            "plugin_key": plugin_key,
            "plugin_id": plugin_id,
            "field_version": field_version,
            "emitters": emitters,
            "status": status,
            "note": note,
        })

    return {
        "schema": "AUTHORITY_AUDIT_REPORT_V1",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "plugins_registry": str(plugins_path),
        "actors_registry": str(actors_path),
        "valid_actors": sorted(valid_actors),
        "field_versions_seen": sorted(field_versions_seen),
        "results": results,
        "overall_ok": overall_ok,
        "axis_b_caveat": (
            "This auditor verifies plugins against registries/actors.v1.json. "
            "That registry diverges from formal/LedgerKernel.v "
            "(see actors.v1.json header). F-002 axis B reconciliation is open."
        ),
    }


def render_table(report: dict[str, Any]) -> str:
    lines = []
    lines.append("AUTHORITY AUDIT — F-002 (NON_SOVEREIGN, NO_SHIP)")
    lines.append("=" * 72)
    lines.append(f"  plugins:        {report['plugins_registry']}")
    lines.append(f"  actors:         {report['actors_registry']}")
    lines.append(f"  valid actors:   {', '.join(report['valid_actors'])}")
    lines.append(f"  field versions: {', '.join(report['field_versions_seen'])}")
    lines.append("")
    lines.append(f"{'PLUGIN':<32} {'FIELD':<8} {'STATUS':<6} EMITTERS / NOTE")
    lines.append("-" * 72)
    for r in report["results"]:
        emitters_or_note = r["note"] if r["note"] else ", ".join(r["emitters"])
        lines.append(
            f"{r['plugin_key']:<32} {r['field_version']:<8} {r['status']:<6} {emitters_or_note}"
        )
    lines.append("-" * 72)
    lines.append(f"OVERALL: {'PASS' if report['overall_ok'] else 'FAIL'}")
    lines.append("")
    lines.append(f"AXIS_B_CAVEAT: {report['axis_b_caveat']}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plugins", default=str(DEFAULT_PLUGINS))
    ap.add_argument("--actors", default=str(DEFAULT_ACTORS))
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()

    report = audit(Path(args.plugins), Path(args.actors))

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_table(report))

    return 0 if report["overall_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
