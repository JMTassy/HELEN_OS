# Render Clarity Audit — Full HELEN OS Operator Surface

```yaml
schema: REVIEW_FINDING_PROPOSAL_V1
authority: false
canon: false
ledger_effect: none
status: PROPOSED
owner: unassigned -- needs operator confirmation
review_date: 2026-07-16
kill_criterion: superseded by an operator decision (fix tranche / accept-as-is / defer) or deleted if not reviewed by review_date
method: three parallel fresh-context reviewers (HTML surfaces / CLI+API render
        paths / repo-wide doctrine sweep), maker-not-grader, synthesized by a
        fourth pass. Findings verified on file content with line numbers, not
        restated from memory.
scope: apps/helen-surface/** (8 surfaces + goblin game reviewed separately),
       helen_status_api.py, helen_api_server_v1.py response shapes,
       tools/session_digest.py, tools/helen_say.py, tools/kernel_guard.sh,
       tools/validators/authority_language_linter.py (render path),
       scripts/ralph/ralph.sh, repo-wide 🟢/status-claim sweep (117 glyphs).
excluded: temple/gardens/, temple/subsandbox/ (NO_CLAIM zones), deprecated/
```

## Verdict

**FAIL at the system level** — not because any single surface is broken, but
because one defect class repeats across every layer: **verification vocabulary
(PASS / CLEAN / VALID / UPHELD / SHIPPED / Receipt=) rendered from constants
instead of from checks.** The kernel's receipts are honest; the panes of glass
in front of them are not.

## The five system patterns (each observed in 3+ independent places)

### P1 · Verdict laundering — verification words with no verifier behind them

| Where | What it renders | What actually happened |
|---|---|---|
| `scripts/ralph/ralph.sh:111` | `hal=PASS`, "commit is authorised" | HAL_VERDICT is copied from the operator's own `--close GREEN` argument; the test run is never consulted |
| `scripts/ralph/ralph.sh:106-109` | GREEN success banner | pytest that never ran (0 collected, missing venv) yields passed=0 failed=0 → renders identically to all-green |
| `apps/helen-surface/temple.html:108` | `REPLAY STATUS: CLEAN` (green) | hardcoded; `updatePulse()` never touches `pp-replay` — a broken replay chain stays CLEAN forever |
| `apps/helen-surface/cockpit_v4.html:519-523` | `Continuity: 1.000000 · Chain integrity: PASS` | fully fabricated block, rebuilt identically on every render |
| `apps/helen-surface/temple_akashic_v1.html:639-644` | `ALL AXIOMS UPHELD 🔒`, five green-dot ON claims | static HTML, no verification path, contradicts the page's own NO_CLAIM footer |
| `apps/helen-surface/home_v1.html:215-216` | `'no gates failed'` | pushed unconditionally on every render; a real gate failure still renders "no gates failed" |
| `apps/helen-surface/starship.html:383-415, 556-594` | fake kernel log (`K8 PASS · k8=+1.000`), fake sovereign ledger with invented payload_hashes, `trust: HIGH — sovereign`, `cum_hash chain: VALID` | all hardcoded fiction — the strongest misleading-authority instance in the suite |
| commit `8aafc55` (this session's own receipt) | "Verified via Playwright: no JS errors" | the pageerror listener was attached *after* all interactions — vacuously true, not observed |

The last row is included deliberately: the pattern reaches agent receipts, not
just HTML. `reported_metal ⊬ observed_metal` is a system-wide disease.

### P2 · Client-side receipt minting — UI invents receipt-shaped objects

- `home_v1.html:221-231` — CONFIRM mints `RCPT-xxxx` IDs **and decrements the
  governance-debt counter** client-side. Clicking a button appears to
  discharge unreceipted events with zero ledger write.
- `temple.html:440-449` — dwell-confirm mints `R-XXXX` into a panel titled
  "· RECEIPT SPINE ·" with `[OK]` tags; SYSTEM PULSE counts them as
  `OPEN RECEIPTS`.
- `starship.html:834-843` — `makeReceipt()` flashes `RECEIPT MINTED` with a
  hash-shaped local ID.

This is NO RECEIPT = NO CLAIM inverted: **NO LEDGER = FAKE RECEIPT.** The word
"receipt" must be reserved for ledger-anchored objects; everything minted in
the browser is an *intent*.

### P3 · Unobserved verdicts at the API boundary

- `helen_api_server_v1.py:309-322` — `/actions/execute` returns
  `"success": true` with no ledger-bridge field; the bridge bool is discarded
  (cross-ref: FIRE_AND_FORGET_LEDGER_BRIDGE_V1.md).
- `tools/helen_say.py:152-153` — prints ANSI-green `ACK. Receipt=None` when
  the kernel returns no receipt_id: a green success line that literally
  contains the absence of its own proof.
- `tools/helen_say.py:282-288` — execution failure of an ACCEPTed dialog goes
  to stderr as `[WARN]` while stdout renders green PASS.
- `apps/helen-surface/helen_status_api.py:155-165, 180` — `/api/connectors`
  **fabricates calendar meetings from the wall clock** ("standup 14:00")
  rendered with real-looking status, and stamps the whole payload
  `"source": "live"` while half the badges are demo.
- `helen_status_api.py:64-95` — every `except: pass` collapses a broken or
  absent ledger to `0`, so unreadable renders identically to empty; SOT path
  is hardcoded to one machine, serving all-zeros-as-live anywhere else.

### P4 · Green semantics drift (and one competing palette law)

Repo-wide sweep: **117 🟢 occurrences in scope, 24 violations.** The honest
pattern: **every violation predates the palette machine-law commit
(`7b6ee6a`); nothing written after it violates it.** The law worked; the
backlog remains. Worst instances:

- `PHASE_2_HASH_SCHEME_MIGRATION.md:3` — `🟢 BLOCKED` (green on a *blocked*
  status — the exact inverse of the rule).
- `EMOJOS_RENDERING_RULES_V1.md:73,84` — a **competing palette law** binding
  🟢 to SEALED (palette says 🟡) and stacking five meanings on one glyph. The
  CI drift detector parses only CLAUDE.md's palette line, so this file
  escapes it entirely.
- `HELEN_WULMOJI_WEATHER_FORMAT.md`, `WULMOJI_DEPLOYMENT_STATUS.md` — an
  unregistered third meaning ("safe") outside `CROSS_NAMESPACE_REUSE`.
- CSS layer: `cockpit_v4.html:64` maps `shipped` AND `live` to the same green
  (`#00ff88`); `helen2027.html:224` + `focus.html:132` hardcode a green
  pulsing "Online" that checks nothing; the goblin game (prior review) put a
  third unregistered meaning on 🟢/🔴.
- `authority_language_linter.py:240,256` — the *authority-language linter
  itself* renders ✅ for PASS and 🟡 for warnings (green-as-success and
  sealed-as-warning) — the police wearing the contraband.
- No surface renders the literal string `🟢 ADMITTED` on authority:false
  content — the letter of the rule holds; the colour semantics behind it are
  broken ~30 times.

### P5 · The demo/live boundary is unmarked (or self-destructs)

- `helen2027.html:1023-1026` — going live **deletes the Demo badge** (the
  element is reused as a git-dirty indicator) while most of the page stays
  hardcoded.
- `focus.html`, `starship.html` — 100% hardcoded, no fetch, and focus.html
  has **no authority/NO_CLAIM banner at all** (the only surface without one).
- `temple_akashic_v1.html:734-744` — seeded demo events interleave with live
  ones through the same code path, indistinguishably.
- `cockpit_v4.html:493-506` — live commit hash spliced into slot one of a
  list of fabricated receipt rows, lending them its credibility.
- `home_v1.html:400-402` — API failure swallowed silently; fabricated values
  render with no OFFLINE marker.
- Reference pattern that already exists in-tree: `temple.html:102/347` —
  explicit `● LIVE` / `● FALLBACK/DEMO` badge that flips on API
  reachability, + `AUTHORITY: FALSE` in three places. Findings above are
  largely the absence of this pattern elsewhere.

### P6 (cross-cutting) · Doctrine text is the least legible text on every page

- Authority banners at ~1.2–1.5:1 contrast (`home_v1.html:151`
  `rgba(0,212,255,.12)`; `cockpit_v4.html:216` `.25` alpha) — the one line
  saying `authority: false` is effectively invisible.
- Load-bearing status text at 5.5–8.5px across all surfaces.
- **Zero ARIA in all 8 files** (verified by grep): no `aria-live`, no
  keyboard path to canvas nodes; `temple.html:113` advertises "TAB cycle
  rings" but the variable is write-only and Tab is preventDefault()ed —
  a dead accessibility promise.
- `cockpit_v4.html:596-598` — bonus: `#sb-clock` doesn't exist in the DOM;
  `updateClock()` throws a TypeError every second.

## Ranked fix tranches (root fixes, not 60 one-liners)

**T1 — ralph.sh verdict integrity (HIGH, ~8 lines).** Derive HAL_VERDICT from
`FAILED_CT`/`TOTAL`, refuse GREEN when verdict≠PASS or TOTAL=0:
```bash
HAL_VERDICT="FAIL"
[[ "${FAILED_CT:-0}" -eq 0 && "${TOTAL}" -gt 0 ]] && HAL_VERDICT="PASS"
if [[ "${CLOSE_OUTCOME}" == "GREEN" && "${HAL_VERDICT}" != "PASS" ]]; then
  echo "REFUSED: GREEN close with hal=${HAL_VERDICT} (passed=${PASSED} failed=${FAILED_CT} total=${TOTAL})" >&2
  exit 1
fi
```
Also: stop recording pre-work HEAD as the story `commit_hash` (line 120 —
record it as `pre_close_head`, set `commit_hash: null`).

**T2 — rename minted objects (HIGH, 3 surfaces).** `RCPT-`→`INTENT-`,
"RECEIPT SPINE"→"INTENT LOG (LOCAL · UNLEDGERED)", "RECEIPT MINTED"→"LOCAL
DRAFT (UNLEDGERED)"; never decrement governance debt client-side.

**T3 — kill fabricated verification claims (HIGH).** Every hardcoded
PASS/CLEAN/VALID/UPHELD either reads a real API field or renders
`UNVERIFIED`/`NOT WIRED` in amber with the real command to run
(e.g. `VERIFY → not wired. Run: .venv/bin/python scripts/helen_k8_lint.py`).
starship.html gets a fixed `MOCK DATA · NOT THE LEDGER · authority=false`
banner. API side: `/actions/execute` returns
`"ledger_bridge": {"dispatched": bool, "confirmed": false, "mode": "fire_and_forget"}`;
`helen_say.py` refuses the green line when `receipt_id` is None.

**T4 — one provenance pattern for all surfaces (MEDIUM).** Generalize
`temple.html`'s `● LIVE / ● FALLBACK/DEMO` badge into a tiny shared snippet;
per-field `"src": "live"|"static"|"demo"` in both status API payloads;
`"source": "mixed"` instead of the blanket `"live"`; demo seeds tagged
`[SEED]` or cleared on first live fetch; helen2027's Demo badge gets its own
element so going live can't delete it.

**T5 — palette enforcement closes its own gap (MEDIUM).**
1. Subordinate or quarantine `EMOJOS_RENDERING_RULES_V1.md` (drop the
   🟢=SEALED binding; add authority:false frontmatter).
2. Register or remove the weather namespace in `CROSS_NAMESPACE_REUSE`.
3. Fix the linter's own glyphs (✅→🔵, 🟡→🟠 at
   `authority_language_linter.py:240,256`).
4. Add a render-rule lint: walk `*.md`/`*.html` outside NO_CLAIM zones, flag
   🟢 within N lines of BLOCKED/READY/COMPLETE/OPERATIONAL or in files with
   authority:false frontmatter; wire into the doc-index CI job. Today the
   rule is enforced only by human review.
5. Mechanical backlog: the 24 pre-doctrine glyph swaps (one commit, zero
   logic).

**T6 — legibility floor (LOW, one CSS pass).** Authority banners to ≥4.5:1
and ≥10px on every surface; `aria-live="polite"` on queue/toast/pulse/receipt
lists; fix or remove the dead TAB hint; add `#sb-clock` or guard the
interval; `focus.html` gets its missing banner.

## What is already clean (verified, worth protecting)

- `.claude/` skills and state files — fully compliant; several actively
  restate the rendering rule.
- `docs/proposals/` — every 🟢 is either quoted palette grammar or carries an
  explicit "🔵 OBSERVED — Not 🟢 ADMITTED" disclaimer. Exemplary.
- `GOVERNANCE/CLOSURES/` + `TRANCHE_RECEIPTS/` spot-check — receipts speak in
  typed JSON fields, no colour glyphs at all. Correct instinct: **receipts
  speak in types; colours are for humans.**
- `oracle_town/protocols/`, `oracle_town/audits/` — zero 🟢.
- `tools/session_digest.py` — doctrine-clean render (one LOW: git failures
  return stdout regardless of exit code).
- `temple.html`'s LIVE/FALLBACK badge — the in-tree reference pattern.

## One-line diagnosis

The constitution says NO RECEIPT = NO CLAIM; the glass says CLAIM ANYWAY.
Fixing T1–T3 makes the glass stop counterfeiting; T4–T5 make the counterfeit
class structurally impossible to reintroduce.

---
authority=false · canon=false · ledger_effect=none · PROPOSED
owner: unassigned -- needs operator confirmation
review_date: 2026-07-16
kill_criterion: superseded by an operator decision or deleted if not reviewed by review_date
