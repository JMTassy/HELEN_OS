# Linter Document-Global Receipt Pardon — Proposal

```yaml
schema: REVIEW_FINDING_PROPOSAL_V1
authority: false
canon: false
ledger_effect: none
status: PROPOSED
owner: unassigned -- needs operator confirmation
review_date: 2026-07-16
kill_criterion: superseded by an operator decision (fix / accept-as-is / defer) or deleted if not reviewed by review_date
source: docs/proposals -- previously a one-line report-only note in CLAUDE.md
        (2026-07-01 snapshot), verified against live code this pass, not
        re-stated from memory
verified_against: tools/validators/authority_language_linter.py, tests/test_authority_language_linter.py, read directly this session
```

## What was previously known

CLAUDE.md's 2026-07-01 snapshot noted, in one clause: *"linter's
document-global receipt pardon (test-pinned)"* — flagged report-only,
operator decision pending, no further detail.

## What this pass verified on the actual code

One design-level issue in
`tools/validators/authority_language_linter.py:lint_text()` (line 124).

### Document-global receipt search pardons all violations (confirmed, line 124)

```python
def lint_text(text: str) -> LintResult:
    receipt_found = bool(_RECEIPT_PATTERN.search(text))      # line 124 — searches ENTIRE text
    ...
    for pattern, description, severity in _FORBIDDEN_PATTERNS:
        matches = list(pattern.finditer(text))               # line 130 — per-match
        ...
    if hard_violations and not receipt_found:                 # line 151 — global pardon
        verdict = "BLOCK"
```

`_RECEIPT_PATTERN.search(text)` runs a single regex search over the
**entire input text** and sets a single boolean `receipt_found`. This
boolean then pardons **all** HARD violations found anywhere in the
document (line 151). The receipt check is not per-violation, not
per-section, not proximity-based — it's document-global.

**Failure scenario**: a long document (e.g. a multi-section protocol,
a proposal with appendices, or a concatenated agent transcript) contains
a legitimate `REDUCER_RECEIPT_V1` in section A — a real receipt from a
real reducer invocation. In section B, 500 lines later, an agent writes
"REDUCER admits: this finding is validated" without any receipt. The
linter sees the receipt marker from section A, sets `receipt_found =
True`, and every HARD violation — including the fabricated one in
section B — is pardoned. Verdict: PASS.

This is exactly authority laundering: the receipt in section A didn't
authorize the claim in section B, but the linter treats them as if it
did. A single receipt anywhere in the text provides universal pardon.

### Test suite is consistent with the bug (confirmed, test lines 120-143)

The tests are not wrong — they correctly test the implemented behavior:

```python
def test_receipt_pardons_reducer_admits() -> None:
    text = 'REDUCER admits: done. receipt_id: R-2026-001. REDUCER_RECEIPT_V1 attached.'
    result = lint_text(text)
    assert result.receipt_found is True
    assert result.verdict == "PASS"           # receipt in same text → pardon
```

But every test uses short, single-context strings where the receipt and
the violation are in the same sentence. No test exercises the case where
a receipt in one section pardons a violation in a different, unrelated
section. The "test-pinned" note in CLAUDE.md correctly identifies this:
the behavior is locked by tests, which means changing it requires
changing the tests too.

### Severity assessment

How dangerous this is depends on the linter's actual usage pattern:

- **If called on short, single-purpose texts** (a single agent message,
  a single WUL packet, a single receipt), the document-global search is
  effectively section-scoped because the document IS a section. In this
  case the finding is latent, not live.

- **If called on files or concatenated transcripts** (via `--file` or
  `--stdin` on a multi-section document), the finding is live — a real
  receipt anywhere in the file pardons fake claims everywhere else.

The CLI supports `--file` and `--stdin`, both of which accept
arbitrarily large inputs.

## What's still open (not verified this pass)

- **Actual call sites**: where is `lint_text()` / `lint_file()` actually
  invoked in the codebase today? If it's only ever called on
  short, single-purpose strings, the finding is latent. If it's called
  on files or multi-section inputs, it's live.
- **Intent**: was document-global pardoning a deliberate simplification
  ("receipts protect the whole document") or an oversight ("we need
  per-violation receipt binding but didn't build it yet")? The note
  "test-pinned" suggests it was known and accepted, not overlooked.

## Candidate fixes (not applied — proposal only)

1. **Minimum viable: proximity-based pardon.** Instead of a single
   document-global `receipt_found`, check whether a receipt marker
   appears within N lines (e.g. ±10 lines) of each HARD violation.
   Only pardon violations that have a nearby receipt. This is a
   middle ground between global (current) and per-violation binding.

2. **Correct: per-section scoping.** Split the input on section
   boundaries (e.g. `---`, `## `, blank-line blocks), lint each section
   independently, merge results. A receipt in section A only pardons
   violations in section A. This requires defining "section" — for YAML
   frontmatter documents the boundary is clear, for free-text it's
   ambiguous.

3. **Strict: per-violation receipt binding.** Each HARD violation
   requires its own receipt reference within the same logical block.
   The linter would need to associate specific receipt IDs with specific
   claims. This is the most correct but the most complex to implement
   and the hardest to write inputs for.

4. **Accept as-is with guard.** Keep the current behavior but add an
   explicit `max_text_length` parameter — if the input exceeds a
   threshold (e.g. 2000 chars), force BLOCK regardless of receipts, on
   the principle that document-global pardoning is only safe for short
   inputs. This is a size-based circuit breaker that prevents the
   worst case (long documents with distant receipt+violation pairs).

All fixes are additive — none touches the sovereign firewall. The test
suite would need corresponding updates (new tests for the boundary
cases, possibly adjusted expectations for existing tests). None has been
applied; this document is the proposal, not the fix.

---
authority=false · canon=false · ledger_effect=none · PROPOSED
owner: unassigned -- needs operator confirmation
review_date: 2026-07-16
kill_criterion: superseded by an operator decision or deleted if not reviewed by review_date
