# HELEN OS — Business Improvement Analysis V1

```yaml
authority: false
canon: false
ledger_effect: none
status: reference doc, built from direct session observation
date: 2026-07-02
owner: operator (JM)
review_date: 2026-07-16
kill_criterion: superseded by next business-improvement pass or explicit reject
```

Answers to the intake questions are **inferred from direct observation of
one long session**, not generic guesses — grounded in git history, files
created, and the operator's actual directives. Flagged where confidence
is lower.

## Intake answers (inferred, confirm/correct as needed)

1. **Main work**: Building and operating HELEN OS — a personal, AI-agent-
   directed governance/companion system, run mostly through Claude Code
   sessions plus a parallel local-GPU training seat.
2. **Repeated tasks** (pattern-inferred): pasting external content for
   HELEN-specific adaptation ("chiddush this"), running bounded
   autoresearch/garden epochs, checking training-pipeline status,
   reviewing generated skill/governance files, git commit+push cycles,
   WULmoji-formatted status requests.
3. **Time-consuming tasks** (directly observed, highest confidence):
   re-deriving context every session (re-reading CLAUDE.md, re-checking
   file locations, re-verifying routing state); reconciling state
   between the local seat (Windows/WSL, Ollama, GPU training) and this
   cloud seat; manually noticing when a diagnosed bug has gone unfixed.
4. **Abandoned automation attempts**: the K-tau needle fix — diagnosed,
   tested, sitting operator-gated 17+ days despite a passing test
   already existing. The GOBLIN-RELAY-1 dispatch — repeatedly blocked by
   a Bash safety classifier on the local seat, worked around with a
   manual escape-hatch script.
5. **Frequent outputs**: skill files (`.claude/commands/*.md`),
   governance/compost receipts (garden-zone `.md` with YAML frontmatter),
   audit scripts (Python), occasional creative artifacts.
6. **Tools/services in use**: git/GitHub, dual local Ollama daemons
   (WSL + win32), a local GPU fine-tune pipeline (ornith-helen), the
   Claude Code skill/agent system, Playwright (verification), HIGGSFIELD
   MCP (available, unused this session), Gmail/Calendar/Drive MCP
   (available, unused this session).
7. **Ideal end state** (inferred from what's been fixed vs. left broken
   this session): one source of truth for routing config instead of
   three disagreeing ones; PROPOSED artifacts that terminate instead of
   accumulate; less time re-deriving state, more time on judgment calls
   only a human can make. **Lower confidence — worth confirming directly.**

## STEP 1 — Work map

| Cadence | Task | Input | Processing | Output | Tool | Sticking point | Human or AI? |
|---|---|---|---|---|---|---|---|
| Daily/per-session | Re-establish context | STATE.md, memory.md, CLAUDE.md | manual read | mental model | eyes | slow, repeated | **AI** (now: `session_digest.py`) |
| Daily/per-session | Direct an agent task | operator directive | agent execution | commit + receipt | Claude Code | none major | AI executes, human directs |
| Weekly-ish | Paste external content, ask for adaptation | pasted text/image | compost extraction | garden `.md` | Claude Code | none | AI |
| Weekly-ish | Check training pipeline | local GPU job | manual status check | pass/fail | local seat | classifier blocks Bash | **human** (judgment on promote) |
| One-off | Resolve model routing drift | 3 disagreeing sources | manual reconciliation | none — still open until this turn | — | never got done | AI (built this turn) |
| One-off | Decide to promote a fine-tune | eval-gate result | `.env` repoint | live model swap | manual | requires operator judgment | **human**, always |
| One-off | Governance audit | repo state | grep/script | receipt | Python | receipt itself becomes another PROPOSED item with no owner | AI, now closes the loop (Build 3) |

## STEP 2 — 15 automation candidates

| # | Improvement idea | Challenge it solves | Expected effect | What to create | Difficulty | Time | Risk | Priority |
|---|---|---|---|---|---|---|---|---|
| 1 | Model routing resolver | 3-way HAL drift, silent fallback | 1 source of truth, loud failure on unregistered role | JSON registry + resolver module | Low | 1-2h | Low (additive, read-only for existing code) | **Built today** |
| 2 | Session bootstrap digest | re-deriving context every session | minutes saved every session, compounding | Python script | Low | 1-2h | Low | **Built today** |
| 3 | Lifecycle stub inserter | 0/931 PROPOSED items have owner/review_date/kill_criterion | governance objects start terminating instead of accumulating | dry-run-safe Python script | Low | 1-2h | **Medium if `--apply` run broadly — gated on confirmation** | **Built today** |
| 4 | `/session-start` skill wrapper for #2 | script isn't a slash command yet | invokable inline, not just CLI | `.claude/commands/session-start.md` | Low | 15m | Low | Quick win |
| 5 | Fix `/council`'s HAL reference now that #1 exists | council.md still says "flagged, unresolved" | one fewer open loop | small edit | Low | 10m | Low | Quick win |
| 6 | Governance Termination Dashboard | AR-TERMINATION-002's JSON is not visually scannable | operator can eyeball drift without reading JSON | single HTML file (Chart.js or plain SVG, no build step) | Medium | 2-3h | Low | Business OS |
| 7 | Skill-file lint (hardcoded model tags) | this exact mistake was caught twice by hand this session | automates a QA step already done manually | Python script, grep-based | Low | 1h | Low | Quick win |
| 8 | Compost search index | past chiddush extractions aren't searchable, get re-derived | faster reuse of prior mining work | small index script over `temple/gardens/compost_*.md` | Low | 1h | Low | Business OS |
| 9 | PR-watch loop actually run | speced in `helen-loop.md`, never invoked | catches CI failures/review comments without manual polling | `subscribe_pr_activity` wired to an actual PR | Low (already speced) | 15m to invoke | Low | Quick win, once there's a live PR |
| 10 | HIGGSFIELD asset-gen skill | MCP available, unused this session | reusable pipeline for HELEN's render/video work | `.claude/commands/asset-gen.md` | Medium | 2h | Low (confirm before any paid generation calls) | Business OS |
| 11 | Keep/Revert eval logging wired into more skills | only `instructions.md` states the rule, not enforced anywhere yet | skills actually measurably improve instead of just accumulating | small addition per skill file | Medium | 2-3h across files | Low | Business OS |
| 12 | Naming/frontmatter consistency checker | some garden files may drift from the YAML-frontmatter convention | catches format drift before it compounds | Python script | Low | 1h | Low | Quick win |
| 13 | Owner/review-date reminder loop | stub inserter (#3) creates the fields; nothing yet reads them proactively | `/loop`-driven weekly nudge instead of manual digest-reading | `/loop` config using `session_digest.py`'s overdue-check | Low (composition of #2+#3) | 30m | Low | Business OS |
| 14 | CSV export of AR-TERMINATION classification | JSON isn't spreadsheet-friendly for manual triage | operator can sort/filter 931 items outside the terminal | small export flag on `ar_termination_002.py` | Low | 30m | Low | Quick win |
| 15 | Fable-orchestrated weekly self-audit loop | governance-audit + termination-audit + routing-drift-check are all separate manual invocations | one weekly digest instead of three manual runs | compose existing pieces into `/fable-orchestrate weekly` extension | Medium-High | 2-3h | Low | **High-difficulty, Fable-5-enabled** |
| 16 | Posting/distribution automation | **no evidence found this session of a posting/publishing cadence for this operator** | — | — | — | — | — | **insufficient signal — ask directly rather than fabricate** |

## STEP 3 — Prioritization

**Quick Wins (today)**: #1, #2, #3 (built), #4, #5, #7, #9, #12, #14 —
all low-difficulty, low-risk, buildable in under 2 hours each.

**Business OS (long-term payoff)**: #6, #8, #10, #11, #13 — compound
value, none destructive, worth sequencing after the quick wins land.

**High-difficulty, Fable-5-enabled now**: #15 — composing existing
audit tools into one autonomous weekly loop is only practical because
this session already proved out `/fable-orchestrate`, `/loop`, and the
individual audit scripts independently. Doing this without Fable-5-class
long-run orchestration would mean manually running and reading three
separate scripts every week.

**Selected for today: #1, #2, #3.** Reasoning: these three, together,
directly close the two most expensive things actually observed this
session — re-deriving context (fixed by #2), and routing decisions
resting on silently-disagreeing sources (fixed by #1) — while #3 is the
mechanical fix for the single sharpest finding from AR-TERMINATION-002
(0% of PROPOSED items have any of the fields a live control needs),
built safely (dry-run default, confirmation-gated bulk apply).
