#!/usr/bin/env python3
"""
HELEN M8 — Operator packet builder.

Compiles a run directory into HOLD_FOR_OPERATOR.md.

Refuses any artifact that fails verify_packet. Raw attachments are listed
but explicitly marked NO AUTHORITY. The packet always terminates in
HOLD_FOR_OPERATOR — this script cannot admit anything (Law 7).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_packet import verify  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: operator_packet.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])

    admitted_evidence = []
    refused = []

    for p in sorted(run_dir.glob("*.packet.json")):
        v = verify(p)
        if v["admissible_as_evidence"]:
            admitted_evidence.append((p, json.loads(p.read_text())))
        else:
            refused.append((p, v["reasons"]))

    raw_files = sorted(
        f for f in run_dir.iterdir()
        if f.suffix == ".json" and not f.name.endswith(".packet.json") and f.name != "preflight.json"
    )

    lines = [
        "# HOLD_FOR_OPERATOR",
        "",
        f"Run directory: `{run_dir}`",
        f"Compiled: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Disposition required",
        "",
        "Only the operator may choose: **ADMIT · HOLD · REJECT · REVISION_REQUESTED**",
        "",
        "No human seal ⇒ no canon.",
        "",
        "## Evidence packets (seal-verified)",
        "",
    ]

    if not admitted_evidence:
        lines.append("_None. Nothing in this run qualifies as evidence._")
    for p, pk in admitted_evidence:
        lines += [
            f"### `{p.name}`",
            f"- provider: {pk['provider']} · model: {pk['model']} · role: {pk['role']}",
            f"- authority: {pk['authority']} · seal: `{pk['normalizer_seal'][:23]}…`",
            f"- observations: {len(pk['observations'])} · inferences: {len(pk['inferences'])} · proposals: {len(pk['proposals'])}",
            f"- errors: {len(pk['errors'])}",
            "",
        ]
        for ob in pk["observations"][:10]:
            lines.append(f"  - OBSERVED [{ob['source_ref']}]: {ob['text'][:200]}")
        for inf in pk["inferences"][:5]:
            lines.append(f"  - INFERRED (no evidence weight): {inf[:200]}")
        for pr in pk["proposals"][:5]:
            lines.append(f"  - PROPOSED (no evidence weight): {pr[:200]}")
        lines.append("")

    if refused:
        lines += ["## REFUSED artifacts (failed seal / schema verification)", ""]
        for p, reasons in refused:
            lines.append(f"- `{p.name}` — {'; '.join(reasons)}")
        lines.append("")

    if raw_files:
        lines += ["## Raw attachments — NO AUTHORITY, provenance only", ""]
        for f in raw_files:
            lines.append(f"- `{f.name}`")
        lines.append("")

    lines += [
        "## State",
        "",
        "```",
        "epistemic_status: proposed",
        "action_status:    not_attempted (read-only run)",
        "evidence_status:  see packets above",
        "review_status:    unreviewed",
        "admission_status: candidate → HOLD_FOR_OPERATOR",
        "```",
        "",
        "NO_RECEIPT until operator seal.",
    ]

    out = run_dir / "HOLD_FOR_OPERATOR.md"
    out.write_text("\n".join(lines))
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
