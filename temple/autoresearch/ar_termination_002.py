#!/usr/bin/env python3
"""AR-TERMINATION-002: finite-lifecycle audit of HELEN's governance objects.

AUTORESEARCH_PULLED_EPOCH. authority=false canon=false ledger_effect=none.
Observable signals only, read-only. No repo mutation, no ledger write,
no doctrine promotion, no runtime behavior change.

Hypothesis: HELEN's PROPOSED / NON_SOVEREIGN / NO_CLAIM objects can be
measured as a finite lifecycle system, and the harness can distinguish
a live safety control from a permanent parking state.
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXCLUDE_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".venv-gates"}
TEXT_EXTS = {".md", ".json", ".py", ".yaml", ".yml", ".txt"}

STATE_PATTERNS = {
    "PROPOSED": re.compile(r"\bPROPOSED\b"),
    "NON_SOVEREIGN": re.compile(r"\bNON_SOVEREIGN\b"),
    "NO_CLAIM": re.compile(r"\bNO_CLAIM\b"),
    "NOT_ADMITTED": re.compile(r"\bNOT_ADMITTED\b"),
    "REJECTED": re.compile(r"\bREJECTED\b"),
    "SUPERSEDED": re.compile(r"\bSUPERSEDED\b"),
    "EXPIRED": re.compile(r"\bEXPIRED\b"),
}
ADMITTED_PATTERNS = [re.compile(r"canon:\s*true"), re.compile(r"canon=true")]
OWNER_PATTERNS = [
    re.compile(r"\bowner\s*[:=]", re.I),
    re.compile(r"\bauthor\s*[:=]", re.I),
    re.compile(r"\bproposer\s*[:=]", re.I),
]
REVIEW_DATE_PATTERNS = [
    re.compile(r"\breview_date\s*[:=]", re.I),
    re.compile(r"\breview_by\s*[:=]", re.I),
    re.compile(r"\bexpires\s*[:=]", re.I),
    re.compile(r"\bexpiry\s*[:=]", re.I),
]
KILL_CRITERION_PATTERNS = [
    re.compile(r"\bkill_criterion\s*[:=]", re.I),
    re.compile(r"\breject_if\s*[:=]", re.I),
    re.compile(r"\bsupersede_when\s*[:=]", re.I),
    re.compile(r"\bkill.criteria\s*[:=]", re.I),
]


def iter_text_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1] in TEXT_EXTS:
                yield os.path.join(dirpath, fn)


def classify_file(text):
    states = {name for name, pat in STATE_PATTERNS.items() if pat.search(text)}
    if any(pat.search(text) for pat in ADMITTED_PATTERNS):
        states.add("ADMITTED")
    return states


def has_any(patterns, text):
    return any(p.search(text) for p in patterns)


def git_last_commit_epoch(path):
    try:
        rel = os.path.relpath(path, REPO_ROOT)
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        )
        s = out.stdout.strip()
        return int(s) if s else None
    except Exception:
        return None


def git_deleted_governance_paths():
    """Bounded lower-bound approximation: paths deleted in *visible* git
    history whose location suggests governance/proposal content. History
    before this shallow clone's root is invisible -- explicitly a floor,
    not a complete count."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=D", "--name-only", "--pretty=format:"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
        )
        paths = {p for p in out.stdout.splitlines() if p.strip()}
        return [
            p for p in paths
            if any(seg in p for seg in (
                "docs/proposals/", "temple/", "GOVERNANCE/",
                "oracle_town/protocols/", "oracle_town/audits/",
                "scratchpad", "schemas/",
            ))
        ]
    except Exception:
        return []


def main():
    now = datetime.now(timezone.utc)
    by_state = {k: [] for k in list(STATE_PATTERNS) + ["ADMITTED"]}
    no_owner, no_review_date, no_kill_criterion = [], [], []
    proposed_ages = []

    scanned = 0
    for path in iter_text_files():
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            continue
        scanned += 1
        states = classify_file(text)
        for s in states:
            by_state[s].append(path)
        if "PROPOSED" in states:
            if not has_any(OWNER_PATTERNS, text):
                no_owner.append(path)
            if not has_any(REVIEW_DATE_PATTERNS, text):
                no_review_date.append(path)
            if not has_any(KILL_CRITERION_PATTERNS, text):
                no_kill_criterion.append(path)
            ts = git_last_commit_epoch(path)
            if ts:
                age_days = (now - datetime.fromtimestamp(ts, tz=timezone.utc)).days
                proposed_ages.append((path, age_days))

    deleted_governance = git_deleted_governance_paths()

    parking_states = ["PROPOSED", "NON_SOVEREIGN", "NO_CLAIM", "NOT_ADMITTED"]
    terminal_states = ["ADMITTED", "REJECTED", "SUPERSEDED", "EXPIRED"]

    parking_union = set()
    for s in parking_states:
        parking_union |= set(by_state[s])
    terminal_union = set()
    for s in terminal_states:
        terminal_union |= set(by_state[s])

    total_governance_objects = len(parking_union | terminal_union) + len(deleted_governance)
    terminated = len(terminal_union) + len(deleted_governance)
    parked = len(parking_union - terminal_union)

    termination_rate = terminated / total_governance_objects if total_governance_objects else 0.0
    parking_rate = parked / total_governance_objects if total_governance_objects else 0.0

    STALE_DAYS = 14  # matches the K-tau needle precedent already on record (17d, operator-gated)
    stale_proposed = [p for p, age in proposed_ages if age >= STALE_DAYS]
    oldest = max(proposed_ages, key=lambda t: t[1]) if proposed_ages else None

    # governance_yield_proxy: the weakest-evidence metric here, explicitly
    # approximated. Numerator is a fixed, hand-verified count of real
    # incidents a governance mechanism is documented (in CLAUDE.md / repo
    # audit docs) to have actually caught -- not inferred from patterns.
    documented_catches = 3  # TOCTOU seq=287 fork (ledger validator);
                             # stale kernel_guard allowlist (manual sweep, 5fd6eb9);
                             # ghost-closure detector (built because closures could be faked)
    governance_yield_proxy = documented_catches / total_governance_objects if total_governance_objects else 0.0

    result = {
        "epoch": "AR-TERMINATION-002",
        "scanned_files": scanned,
        "by_state_counts": {k: len(v) for k, v in by_state.items()},
        "deleted_governance_like_lower_bound": len(deleted_governance),
        "total_governance_objects": total_governance_objects,
        "terminated": terminated,
        "parked": parked,
        "termination_rate": round(termination_rate, 4),
        "parking_rate": round(parking_rate, 4),
        "stale_proposed_count": len(stale_proposed),
        "stale_threshold_days": STALE_DAYS,
        "oldest_pending": {"path": oldest[0], "age_days": oldest[1]} if oldest else None,
        "items_with_no_owner": len(no_owner),
        "items_with_no_review_date": len(no_review_date),
        "items_with_no_kill_criterion": len(no_kill_criterion),
        "proposed_total": len(by_state["PROPOSED"]),
        "governance_yield_proxy": round(governance_yield_proxy, 6),
        "governance_yield_proxy_numerator_documented_catches": documented_catches,
        "governance_yield_proxy_note": (
            "weak proxy -- numerator is a fixed, hand-verified count of "
            "known real catches, not inferred from repo patterns"
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
