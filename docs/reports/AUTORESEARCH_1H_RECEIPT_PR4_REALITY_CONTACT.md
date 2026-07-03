# AUTORESEARCH_1H_RECEIPT — PR #4 Reality Contact

One bounded loop, 2026-07-03. Placed in `docs/reports/` (the existing
receipts location; the directive's `reports/` allowlist entry
interpreted as this directory — noted per honest-receipt discipline).

```json
{
  "object": "AUTORESEARCH_MODE_LOOP_1H",
  "hypothesis": "If PR #4's claim (shell 'run:' routes through the read-only executor, mutations rejected, 9+32 tests pass) is still true on today's metal, then (a) its named tests pass at the PR head, (b) run_readonly() live-rejects mutation commands, and (c) the patch still merges against current main.",
  "objection_tried": "F1 claimed test files absent; F2 tests fail today; F3 'rm -rf .' not rejected live; F4 merge conflicts with current main or executor dropped on main; F5 pass-counts differ from claimed 9/32. All written before testing.",
  "test_run": "isolated worktree at PR head e22f57e: pytest tests/test_helen_readonly_executor.py tests/test_helen_computer_use_api.py -q; live run_readonly() probes (1 safe, 5 adversarial); git merge-tree --write-tree origin/main e22f57e; blob-level diff of all four touched files between origin/main and PR head",
  "evidence_checked": [
    "41 passed in 0.16s at PR head == claimed 9+32 exactly (F2, F5 survive)",
    "run_readonly('rm -rf .') raises ReadOnlyExecutionRejected: Forbidden command: rm (F3a survives)",
    "git status -sb EXECUTED rc=0; git push/shell-token >/;-chain/curl/python all REJECTED — including probes beyond the PR's advertised examples (F3 survives)",
    "git merge-tree exit 128: 'refusing to merge unrelated histories' — PR head shares no common ancestor with current main; main was re-rooted since 2026-05-06 (F4 FIRES)",
    "src/helen_readonly_executor.py IDENTICAL main vs PR head; both test files IDENTICAL — machinery already on main via the rewrite",
    "tools/helen_cli.py DIFFERS: run_readonly references on main = 0, at PR head = 4 — the PR's entire actual delta (+70 lines wiring) is ABSENT from main",
    "net state on main today: read-only executor + its 41 tests exist UNWIRED; no CLI path routes through them"
  ],
  "files_touched": [
    "docs/reports/AUTORESEARCH_1H_RECEIPT_PR4_REALITY_CONTACT.md (this receipt only; PR checkout was an isolated scratchpad worktree, read-only)"
  ],
  "forbidden_paths_touched": false,
  "result": "FAIL",
  "classification": "EVIDENCE",
  "authority": false,
  "canon": false,
  "ledger_effect": "none",
  "reducer": "not_invoked",
  "push": "blocked",
  "next_action": "Operator decision, two clean options: (1) close PR #4 as unmergeable-but-vindicated and re-apply the verified 70-line wiring as a fresh commit on a main-rooted branch (content proven good this loop: 41/41 + adversarial rejection), or (2) close PR #4 and accept the executor remaining unwired on main. Separate follow-up action either way -- no patching was performed inside this loop, per rule.",
  "final": "HOLD_FOR_OPERATOR"
}
```

Non-implications preserved: TestPASS ⊬ Ship · Receipt ⊬ Ledger ·
Candidate ⊬ Admitted · Evidence ⊬ Admission.

Evidence precedes optimization. One hypothesis. One possible no.
One receipt. Stop.
