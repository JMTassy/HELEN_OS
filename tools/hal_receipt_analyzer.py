#!/usr/bin/env python3
"""
hal_receipt_analyzer.py

Cross-receipt governance analyzer for GEMMA_PROPOSAL_RAW_V1 receipts.

Reads all *.json receipts in GOVERNANCE/GEMMA_PROPOSALS/ and emits a
read-only report: counts, envelope health, operator/HAL status matrix,
repeated required_receipts, repeated HAL questions, topic clusters,
and drift warnings.

Hard constraints (enforced by code shape):
  - NEVER write to receipt files
  - NEVER write to town/ledger_v1.ndjson
  - NEVER mutate lifecycle_entry
  - NEVER promote, ship, or annotate
  - The only write path is --markdown PATH, which produces a derived
    report file. Receipts, ledger, and lifecycle remain read-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROPOSAL_DIR = REPO_ROOT / "GOVERNANCE" / "GEMMA_PROPOSALS"

OPERATOR_STATUSES = ("APPROVED_FOR_SANDBOX_ONLY", "REJECTED", "PENDING_REVIEW", "(none)")
HAL_STATUSES = ("PASS", "FAIL", "NEEDS_MORE_RECEIPTS", "(none)")

TOPIC_CLUSTER_JACCARD = 0.5
RECURRING_THRESHOLD = 2
WALL_TIME_DRIFT_RATIO = 3.0

STOPWORDS = set(
    "a an the and or of to in on for with by from is are was were be been "
    "being this that these those it its as at not no nor but if then else "
    "than which who whom whose what when where why how all any each every "
    "some many much more most less few several so very too just only also".split()
)


def _read_tolerant(path: Path) -> str:
    """Try utf-8 first, fall back to cp1252 (Windows default for legacy receipts)."""
    raw = path.read_bytes()
    for enc in ("utf-8", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_receipts(proposal_dir: Path) -> list[tuple[Path, dict]]:
    if not proposal_dir.exists():
        return []
    out: list[tuple[Path, dict]] = []
    for f in sorted(proposal_dir.glob("*.json")):
        try:
            out.append((f, json.loads(_read_tolerant(f))))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[analyzer] skip {f.name}: {exc}", file=sys.stderr)
    out.sort(key=lambda fd: fd[1].get("receipt_timestamp_utc", ""))
    return out


def get_status(field) -> str:
    if not field:
        return "(none)"
    if isinstance(field, str):
        return field
    return field.get("status", "(unknown)")


def extract_topic(receipt: dict) -> str:
    for line in receipt.get("prompt_text", "").splitlines():
        if line.lower().startswith("topic:"):
            return line[len("topic:"):].strip()
    return ""


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z]{3,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def split_numbered_items(text) -> list[str]:
    if not text or not isinstance(text, str):
        return []
    parts = re.split(r"^\s*(?:\d+[\.\)]|[-*])\s+", text, flags=re.MULTILINE)
    return [p.strip() for p in parts if p.strip()]


def normalize_item(item: str) -> str:
    s = re.sub(r"\s+", " ", item).strip().lower()
    return " ".join(s.split()[:10])


def _bar(title: str) -> str:
    line = "=" * 72
    return f"\n{line}\n{title}\n{line}"


def render_count(receipts):
    print(_bar("1. RECEIPT COUNT"))
    n = len(receipts)
    print(f"total: {n}")
    if not n:
        return
    by_model = Counter(r.get("model_id", "(unknown)") for _, r in receipts)
    by_route = Counter(r.get("route_id", "(unknown)") for _, r in receipts)
    by_lifecycle = Counter(r.get("lifecycle_entry", "(unknown)") for _, r in receipts)
    print(f"by_model:     {dict(by_model)}")
    print(f"by_route:     {dict(by_route)}")
    print(f"by_lifecycle: {dict(by_lifecycle)}")
    ts = [r.get("receipt_timestamp_utc", "") for _, r in receipts if r.get("receipt_timestamp_utc")]
    if ts:
        print(f"earliest: {min(ts)}")
        print(f"latest:   {max(ts)}")


def render_envelope(receipts):
    print(_bar("2. ENVELOPE PASS / FAIL"))
    n = len(receipts)
    if not n:
        return
    passed = sum(1 for _, r in receipts if r.get("envelope_complete"))
    failed = n - passed
    print(f"complete:   {passed}/{n}  ({passed / n * 100:.1f}%)")
    print(f"incomplete: {failed}")
    if failed:
        print("incomplete receipts:")
        for path, r in receipts:
            if not r.get("envelope_complete"):
                print(f"  - {path.name}")


def render_matrix(receipts):
    print(_bar("3. OPERATOR x HAL STATUS MATRIX"))
    matrix = Counter()
    for _, r in receipts:
        matrix[(get_status(r.get("operator_decision")), get_status(r.get("hal_verdict")))] += 1
    col = 28
    print(" " * col + "".join(h.ljust(col) for h in HAL_STATUSES))
    print(" " * col + "".join(("-" * (col - 2)).ljust(col) for _ in HAL_STATUSES))
    for op in OPERATOR_STATUSES:
        row = op.ljust(col)
        for hal in HAL_STATUSES:
            row += str(matrix.get((op, hal), 0)).ljust(col)
        print(row)


def _render_repeated(label: str, receipts, field: str):
    print(_bar(label))
    counter: Counter[str] = Counter()
    by_sig: dict[str, list[str]] = defaultdict(list)
    for path, r in receipts:
        for item in split_numbered_items(r.get(field)):
            sig = normalize_item(item)
            if not sig:
                continue
            counter[sig] += 1
            by_sig[sig].append(path.name)
    repeated = [(sig, c) for sig, c in counter.most_common() if c >= RECURRING_THRESHOLD]
    if not repeated:
        print(f"(no item appears in >= {RECURRING_THRESHOLD} receipts)")
        return
    for sig, c in repeated:
        print(f"\n  [{c}x] {sig}")
        for f in by_sig[sig][:5]:
            print(f"     - {f}")
        if len(by_sig[sig]) > 5:
            print(f"     - ... ({len(by_sig[sig]) - 5} more)")


def render_repeated_required(receipts):
    _render_repeated("4. REPEATED REQUIRED_RECEIPTS", receipts, "required_receipts")


def render_repeated_hal_q(receipts):
    _render_repeated("5. REPEATED HAL_QUESTIONS", receipts, "hal_questions")


def render_topic_clusters(receipts):
    print(_bar("6. TOPIC CLUSTERS  (jaccard >= %.2f)" % TOPIC_CLUSTER_JACCARD))
    topics = []
    for path, r in receipts:
        t = extract_topic(r)
        if t:
            topics.append((path, t, tokenize(t)))
    if not topics:
        print("(no topics found)")
        return
    clusters: list[tuple[set, list[tuple[Path, str]]]] = []
    for path, topic, toks in topics:
        for keywords, members in clusters:
            if jaccard(keywords, toks) >= TOPIC_CLUSTER_JACCARD:
                members.append((path, topic))
                keywords.update(toks)
                break
        else:
            clusters.append((set(toks), [(path, topic)]))
    clusters.sort(key=lambda c: len(c[1]), reverse=True)
    for idx, (keywords, members) in enumerate(clusters, 1):
        kw = ", ".join(sorted(keywords)[:6]) or "(no keywords)"
        print(f"\n  cluster {idx}  ({len(members)} receipt(s))  keywords: {kw}")
        for path, topic in members:
            print(f"     - {topic}  [{path.name}]")


def render_drift(receipts):
    print(_bar("7. DRIFT WARNINGS"))
    warnings: list[str] = []

    by_topic: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    for path, r in receipts:
        sig = normalize_item(extract_topic(r))
        if sig:
            by_topic[sig].append((path, r))

    for sig, members in by_topic.items():
        if len(members) < 2:
            continue
        ops = {get_status(r.get("operator_decision")) for _, r in members}
        hals = {get_status(r.get("hal_verdict")) for _, r in members}
        non_none_ops = ops - {"(none)"}
        non_none_hals = hals - {"(none)"}
        if len(non_none_ops) > 1:
            warnings.append(f"topic '{sig}' has inconsistent operator decisions across {len(members)} receipts: {sorted(non_none_ops)}")
        if len(non_none_hals) > 1:
            warnings.append(f"topic '{sig}' has inconsistent HAL verdicts across {len(members)} receipts: {sorted(non_none_hals)}")
        stuck = sum(1 for _, r in members if get_status(r.get("hal_verdict")) == "NEEDS_MORE_RECEIPTS")
        if stuck >= 2:
            warnings.append(f"topic '{sig}' has {stuck} NEEDS_MORE_RECEIPTS verdicts -- stuck loop")
        walls = [r.get("wall_time_seconds") for _, r in members if isinstance(r.get("wall_time_seconds"), (int, float)) and r.get("wall_time_seconds") > 0]
        if len(walls) >= 2:
            ratio = max(walls) / min(walls)
            if ratio >= WALL_TIME_DRIFT_RATIO:
                warnings.append(f"topic '{sig}' wall_time variance {ratio:.1f}x (min={min(walls):.1f}s, max={max(walls):.1f}s)")

    incomplete = sum(1 for _, r in receipts if not r.get("envelope_complete"))
    if incomplete:
        warnings.append(f"envelope incomplete receipt detected ({incomplete} receipt(s))")

    disagreements = 0
    for _, r in receipts:
        op = get_status(r.get("operator_decision"))
        hal = get_status(r.get("hal_verdict"))
        if (op == "APPROVED_FOR_SANDBOX_ONLY" and hal == "FAIL") or (op == "REJECTED" and hal == "PASS"):
            disagreements += 1
    if disagreements:
        warnings.append(f"{disagreements} operator/HAL disagreement(s) -- escalation needed")

    if not warnings:
        print("(no drift signals detected)")
        return
    for w in warnings:
        print(f"  [!] {w}")


def _collect_drift(receipts) -> list[str]:
    """Same drift logic as render_drift, but returns warnings instead of printing."""
    warnings: list[str] = []
    by_topic: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    for path, r in receipts:
        sig = normalize_item(extract_topic(r))
        if sig:
            by_topic[sig].append((path, r))
    for sig, members in by_topic.items():
        if len(members) < 2:
            continue
        ops = {get_status(r.get("operator_decision")) for _, r in members} - {"(none)"}
        hals = {get_status(r.get("hal_verdict")) for _, r in members} - {"(none)"}
        if len(ops) > 1:
            warnings.append(f"topic '{sig}' has inconsistent operator decisions across {len(members)} receipts: {sorted(ops)}")
        if len(hals) > 1:
            warnings.append(f"topic '{sig}' has inconsistent HAL verdicts across {len(members)} receipts: {sorted(hals)}")
        stuck = sum(1 for _, r in members if get_status(r.get("hal_verdict")) == "NEEDS_MORE_RECEIPTS")
        if stuck >= 2:
            warnings.append(f"topic '{sig}' has {stuck} NEEDS_MORE_RECEIPTS verdicts -- stuck loop")
        walls = [r.get("wall_time_seconds") for _, r in members if isinstance(r.get("wall_time_seconds"), (int, float)) and r.get("wall_time_seconds") > 0]
        if len(walls) >= 2:
            ratio = max(walls) / min(walls)
            if ratio >= WALL_TIME_DRIFT_RATIO:
                warnings.append(f"topic '{sig}' wall_time variance {ratio:.1f}x (min={min(walls):.1f}s, max={max(walls):.1f}s)")
    incomplete = sum(1 for _, r in receipts if not r.get("envelope_complete"))
    if incomplete:
        warnings.append(f"envelope incomplete receipt detected ({incomplete} receipt(s))")
    disagreements = 0
    for _, r in receipts:
        op = get_status(r.get("operator_decision"))
        hal = get_status(r.get("hal_verdict"))
        if (op == "APPROVED_FOR_SANDBOX_ONLY" and hal == "FAIL") or (op == "REJECTED" and hal == "PASS"):
            disagreements += 1
    if disagreements:
        warnings.append(f"{disagreements} operator/HAL disagreement(s) -- escalation needed")
    return warnings


def _collect_repeated(receipts, field: str) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for _, r in receipts:
        for item in split_numbered_items(r.get(field)):
            sig = normalize_item(item)
            if sig:
                counter[sig] += 1
    return [(sig, c) for sig, c in counter.most_common() if c >= RECURRING_THRESHOLD]


def _md_table_cell(s: str) -> str:
    return str(s).replace("|", "\\|")


def render_markdown(receipts, source_dir: Path) -> str:
    """Build the full markdown report as a string. No file IO here."""
    from datetime import datetime, timezone

    n = len(receipts)
    lines: list[str] = []
    lines.append("# HAL Receipt Analysis Report")
    lines.append("")
    lines.append(f"- Generated: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`")
    lines.append(f"- Source: `{source_dir}`")
    lines.append(f"- Receipts analyzed: **{n}**")
    lines.append("- Mode: **READ-ONLY** (analyzer never mutates receipts, ledger, or lifecycle)")
    lines.append("")

    # 1. Receipt count
    lines.append("## 1. Receipt Count")
    lines.append("")
    lines.append(f"- Total: **{n}**")
    if n:
        by_model = Counter(r.get("model_id", "(unknown)") for _, r in receipts)
        by_route = Counter(r.get("route_id", "(unknown)") for _, r in receipts)
        by_lc = Counter(r.get("lifecycle_entry", "(unknown)") for _, r in receipts)
        lines.append(f"- Models: {dict(by_model)}")
        lines.append(f"- Routes: {dict(by_route)}")
        lines.append(f"- Lifecycle: {dict(by_lc)}")
        ts = [r.get("receipt_timestamp_utc", "") for _, r in receipts if r.get("receipt_timestamp_utc")]
        if ts:
            lines.append(f"- Earliest: `{min(ts)}`")
            lines.append(f"- Latest: `{max(ts)}`")
    lines.append("")

    # 2. Envelope health
    lines.append("## 2. Envelope Pass / Fail")
    lines.append("")
    if n:
        passed = sum(1 for _, r in receipts if r.get("envelope_complete"))
        failed = n - passed
        lines.append(f"- Complete: **{passed}/{n}** ({passed / n * 100:.1f}%)")
        lines.append(f"- Incomplete: {failed}")
        if failed:
            lines.append("")
            for path, r in receipts:
                if not r.get("envelope_complete"):
                    lines.append(f"  - `{path.name}`")
    lines.append("")

    # 3. Status matrix
    lines.append("## 3. Operator x HAL Status Matrix")
    lines.append("")
    matrix = Counter()
    for _, r in receipts:
        matrix[(get_status(r.get("operator_decision")), get_status(r.get("hal_verdict")))] += 1
    header = "| Operator \\ HAL | " + " | ".join(_md_table_cell(h) for h in HAL_STATUSES) + " |"
    sep = "|" + "---|" * (len(HAL_STATUSES) + 1)
    lines.append(header)
    lines.append(sep)
    for op in OPERATOR_STATUSES:
        row = f"| {_md_table_cell(op)} | " + " | ".join(str(matrix.get((op, hal), 0)) for hal in HAL_STATUSES) + " |"
        lines.append(row)
    lines.append("")

    # 4 + 5. Repeated items
    for label, field in (
        ("4. Repeated `required_receipts`", "required_receipts"),
        ("5. Repeated `hal_questions`", "hal_questions"),
    ):
        lines.append(f"## {label}")
        lines.append("")
        repeated = _collect_repeated(receipts, field)
        if not repeated:
            lines.append(f"_None at threshold {RECURRING_THRESHOLD}._")
        else:
            for sig, c in repeated:
                lines.append(f"- **[{c}x]** {sig}")
        lines.append("")

    # 6. Topic clusters
    lines.append(f"## 6. Topic Clusters (Jaccard >= {TOPIC_CLUSTER_JACCARD:.2f})")
    lines.append("")
    topics = []
    for path, r in receipts:
        t = extract_topic(r)
        if t:
            topics.append((path, t, tokenize(t)))
    if not topics:
        lines.append("_No topics found._")
    else:
        clusters: list[tuple[set, list[tuple[Path, str]]]] = []
        for path, topic, toks in topics:
            for keywords, members in clusters:
                if jaccard(keywords, toks) >= TOPIC_CLUSTER_JACCARD:
                    members.append((path, topic))
                    keywords.update(toks)
                    break
            else:
                clusters.append((set(toks), [(path, topic)]))
        clusters.sort(key=lambda c: len(c[1]), reverse=True)
        for idx, (keywords, members) in enumerate(clusters, 1):
            kw = ", ".join(sorted(keywords)[:6]) or "(no keywords)"
            lines.append(f"### Cluster {idx} ({len(members)} receipt(s))")
            lines.append(f"Keywords: _{kw}_")
            lines.append("")
            for path, topic in members:
                lines.append(f"- {topic} `[{path.name}]`")
            lines.append("")

    # 7. Drift warnings
    lines.append("## 7. Drift Warnings")
    lines.append("")
    warnings = _collect_drift(receipts)
    if not warnings:
        lines.append("_No drift signals detected._")
    else:
        for w in warnings:
            lines.append(f"- :warning: {w}")
    lines.append("")

    return "\n".join(lines)


def render_terse(receipts) -> None:
    n = len(receipts)
    print(f"RECEIPTS: {n}")
    passed = sum(1 for _, r in receipts if r.get("envelope_complete"))
    print(f"ENVELOPE COMPLETE: {passed}/{n}")
    if n - passed:
        print(f"ENVELOPE INCOMPLETE: {n - passed}")

    op_counter = Counter(get_status(r.get("operator_decision")) for _, r in receipts)
    hal_counter = Counter(get_status(r.get("hal_verdict")) for _, r in receipts)
    print("OPERATOR: " + " ".join(f"{s}={op_counter.get(s, 0)}" for s in OPERATOR_STATUSES))
    print("HAL:      " + " ".join(f"{s}={hal_counter.get(s, 0)}" for s in HAL_STATUSES))

    rr = _collect_repeated(receipts, "required_receipts")
    print(f"\nREPEATED REQUIRED_RECEIPTS: {len(rr)}")
    for sig, c in rr:
        print(f"  - [{c}x] {sig}")
    if not rr:
        print("  (none)")

    hq = _collect_repeated(receipts, "hal_questions")
    print(f"\nREPEATED HAL_QUESTIONS: {len(hq)}")
    for sig, c in hq:
        print(f"  - [{c}x] {sig}")
    if not hq:
        print("  (none)")

    warnings = _collect_drift(receipts)
    print(f"\nDRIFT WARNINGS: {len(warnings)}")
    for w in warnings:
        print(f"  [!] {w}")
    if not warnings:
        print("  (none)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        default=str(DEFAULT_PROPOSAL_DIR),
        help="proposal directory to analyze",
    )
    parser.add_argument(
        "--terse",
        action="store_true",
        help="One-line-per-fact daily-status format (default is verbose audit mode)",
    )
    parser.add_argument(
        "--markdown",
        metavar="PATH",
        help="Write a markdown report to PATH. Overrides --terse. Creates parent dirs.",
    )
    args = parser.parse_args()
    proposal_dir = Path(args.dir)

    receipts = load_receipts(proposal_dir)
    if not receipts:
        print(f"[analyzer] no receipts found in {proposal_dir}.")
        return 0

    if args.markdown:
        out = Path(args.markdown)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_markdown(receipts, proposal_dir), encoding="utf-8")
        print(f"[analyzer] wrote markdown report ({len(receipts)} receipts) -> {out}")
        return 0

    if args.terse:
        render_terse(receipts)
        return 0

    print(f"[analyzer] {len(receipts)} receipt(s) loaded from {proposal_dir}")
    print("[analyzer] mode: READ-ONLY  (no writes, no promotion, no ledger touch)")
    render_count(receipts)
    render_envelope(receipts)
    render_matrix(receipts)
    render_repeated_required(receipts)
    render_repeated_hal_q(receipts)
    render_topic_clusters(receipts)
    render_drift(receipts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
