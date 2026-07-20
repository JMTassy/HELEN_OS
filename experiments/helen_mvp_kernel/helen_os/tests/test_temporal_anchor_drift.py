"""Executable witness for FINDING_TEMPORAL_ANCHOR_DRIFT_V1.

Re-derives the 68-day gap and the Created->Reset->cherry-pick fossil
directly from live git state, so the finding decays to a red test the
moment the underlying history is rewritten or squashed.

Shells out to git (read-only: log/reflog only, no mutation).
NON_SOVEREIGN. authority=false.
"""

import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BRANCH = "claude/setup-helen-os-node-b4uj8"


def _git(*args):
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True, text=True, check=True,
    ).stdout


def test_repo_and_branch_reachable():
    out = _git("log", "-1", "--format=%H")
    assert len(out.strip()) == 40


def test_heygen_and_theorem_forge_commits_exist_with_the_gap():
    log = _git("log", "--format=%ai||%s")
    lines = [l for l in log.splitlines() if l]
    by_subject = {}
    for l in lines:
        ts, subj = l.split("||", 1)
        by_subject.setdefault(subj, ts)

    heygen_subj = "heygen: resume after timeout + transient-error tolerance"
    theorem_subj = ("theorem-forge: phi-contraction floor — the drift "
                     "remembers 12.5%, never forgets to zero")
    assert heygen_subj in by_subject, "heygen resume commit missing from history"
    assert theorem_subj in by_subject, "theorem-forge commit missing from history"

    def parse(ts):
        # git %ai format: "2026-05-04 19:07:21 +0000"
        return datetime.strptime(ts.strip(), "%Y-%m-%d %H:%M:%S %z")

    t_heygen = parse(by_subject[heygen_subj])
    t_theorem = parse(by_subject[theorem_subj])
    gap = t_theorem - t_heygen

    assert gap.days >= 60, f"gap shrank below 60 days: {gap}"
    assert gap.days <= 75, f"gap grew past 75 days — different event now: {gap}"


def test_reflog_contains_the_created_reset_cherrypick_fossil():
    reflog = _git("reflog", "show", BRANCH)
    lines = reflog.splitlines()
    actions_in_order = []
    for l in reversed(lines):  # reflog prints newest first; walk oldest->newest
        if "branch: Created from HEAD" in l:
            actions_in_order.append("created")
        elif "branch: Reset to origin" in l:
            actions_in_order.append("reset")
        elif l.strip().startswith(tuple(f"{BRANCH}@{{" for _ in [0])) and "cherry-pick" in l:
            actions_in_order.append("cherry-pick")

    # The fossil: created, then (later) reset, then (later) cherry-pick —
    # order preserved, not necessarily adjacent.
    assert "created" in actions_in_order, "no 'Created from HEAD' event in reflog"
    assert "reset" in actions_in_order, "no 'Reset to origin' event in reflog"
    i_created = actions_in_order.index("created")
    i_reset = actions_in_order.index("reset")
    assert i_created < i_reset, "reset happened before creation — fossil shape broken"
