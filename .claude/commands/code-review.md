# HELEN Code Review Sweep

Perform a bounded code review pass on a target directory or file set.

## Inputs

$ARGUMENTS — target path(s), or "transport/", "oracle_town/", "tools/", "scripts/", "temple/" etc. Default: git diff of last 2 weeks.

## Recipe

1. **Scope**: Identify all Python files in the target. Cap at 50 files per loop.
2. **Read each file** and check for:
   - Crash bugs (unhashable keys, missing None guards, bare KeyError, ZeroDivisionError)
   - O(n²) hotspots that can be linearized
   - Fail-open security (guards that compare against themselves, missing input validation at system boundaries)
   - Dead code (imports never used, variables assigned but never read, fields written but never consumed)
   - mu_DETERMINISM violations (`datetime.utcnow()`, `datetime.now()` without `timezone.utc`, unsorted set iteration in hashes/IDs)
   - CWD-dependent path resolution (should anchor to module/repo root)
   - WULMOJI rendering rule violations (green/sealed/replayable on non-admitted artifacts)
3. **Classify each finding**: CRASH / PERF / SECURITY / DEAD / DETERMINISM / PATH / GOVERNANCE
4. **For CRASH and SECURITY**: write the fix immediately, run affected tests.
5. **For PERF**: fix if the change is < 20 lines and preserves API.
6. **For the rest**: report only — do not patch without operator GO.
7. **Output**: A findings list with file:line, category, one-sentence description, and disposition (FIXED / REPORT_ONLY / OPERATOR_DECISION).

## Constraints

- Never edit files under `helen_os/governance/`, `helen_os/schemas/`, `oracle_town/kernel/` (sovereign firewall).
- Never mutate `town/ledger_v1.ndjson` or any sealed artifact.
- Run `make test` after any fix. If tests fail, revert and report.
- After CLAUDE.md edits: `python3 scratchpad/generate_claude_index.py` before commit.

## Loop Engineering (Fable)

Each loop iteration covers one directory. Fable orchestrates:
```
for dir in [transport/, tools/, scripts/, temple/, oracle_town/skills/]:
    findings += code_review(dir)
```
Feedback sharpens the finding classifier — false positives from prior runs are excluded.
