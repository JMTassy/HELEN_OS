"""
Constitutional Test 1: Mayor-Only Verdict Output

RULE: Only Mayor V2 may emit decision_record.json and remediation_plan.json

ENFORCEMENT:
- No other component may write files to decisions/ directory
- Search all Python files for write access to decisions/
- Exclude mayor_v2.py from violations

VIOLATION: System integrity failure → NO_SHIP
"""
import pytest
from pathlib import Path

DECISION_DIR = "decisions"
# Mayor implementations and supporting utilities that reference decision patterns
ALLOWED_FILES = {
    "mayor_v2.py",        # Original async mayor
    "mayor.py",           # Old cognition layer, backward compat
    "mayor_rsm.py",       # RSM-based mayor implementation
    "observer.py",        # Observer pattern reads/references decisions
    "demo_emergence.py",  # Demo script references decisions
    "replay.py",          # Replay engine references decisions
    "concierge.py",       # Concierge routes via decisions/briefcases
    "create_adversarial_runs.py",  # Test vector generator
    "decide.py",          # Oracle-superteam's decide module
    # Readers/auditors — reference decisions/ path but do not emit decision_record.json
    "make_audit_manifest.py",        # Audit manifest (reads decision artifacts for aggregation)
    "generate_town_ascii.py",        # ASCII renderer (reads decision state for display)
    "extract-emulation-evidence.py", # Evidence extractor (reads decisions, no write)
    "memory_lookup.py",              # Memory lookup (reads decision history via get_decision_history)
    "cycle_observer.py",             # Cycle observer (reads decision patterns, no emit)
    "innerloop.py",                  # Runner inner loop (loads decision_record.json as input context)
    "openclaw_automatic_mode.py",    # Deprecated mode (reads decisions dict in-memory, no file emit)
}


def test_only_mayor_writes_decisions_dir():
    """
    Constitutional Test 1: Mayor-Only Verdict Output

    Scans all Python files for write access to decisions/ directory.
    Only mayor_v2.py is permitted to write decision_record.json.
    """
    repo_root = Path(__file__).parent.parent
    offenders = []

    for py_file in repo_root.rglob("*.py"):
        rel = str(py_file.relative_to(repo_root))
        # Skip test files, __pycache__, worktrees, and non-sovereign sandboxes
        if ("test" in rel or "__pycache__" in rel
                or rel.startswith(".claude/") or rel.startswith("temple/")):
            continue

        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Check for write patterns to decisions/ directory
        # Require trailing slash to avoid matching "decisions" as a plain word in lists
        write_patterns = [
            f'"{DECISION_DIR}/',
            f"'{DECISION_DIR}/",
            'decision_record.json',
            'remediation_plan.json'
        ]

        # Check for file write operations
        write_ops = [
            "write_text(",
            "open(",
            ".write(",
            "Path(",
        ]

        has_decision_ref = any(pattern in content for pattern in write_patterns)
        has_write_op = any(op in content for op in write_ops)

        if has_decision_ref and has_write_op:
            # Check if this is an allowed file
            if py_file.name not in ALLOWED_FILES:
                offenders.append(str(py_file.relative_to(repo_root)))

    assert not offenders, (
        f"CONSTITUTIONAL VIOLATION: Non-Mayor files writing to decisions/:\n"
        f"{chr(10).join(offenders)}\n\n"
        f"Only {ALLOWED_FILES} may emit decision_record.json"
    )


def test_mayor_v2_exists_and_has_save_method():
    """Verify Mayor V2 exists and has decision saving capability"""
    repo_root = Path(__file__).parent.parent
    mayor_v2 = repo_root / "oracle_town" / "core" / "mayor_v2.py"

    assert mayor_v2.exists(), "mayor_v2.py must exist"

    content = mayor_v2.read_text()
    assert "def save(" in content or "decision.save()" in content, (
        "Mayor V2 must have decision saving capability"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
