# OPEN_LOOPS.md — HELEN's externalized executive function

> **Read this FIRST, every session, before opening anything new.**
> JM is HER (generative, ADHD-HP — the engine). Claude is HAL+REDUCER (the seal).
> This file is the working memory JM's brain doesn't hold. It exists so frontier
> #N+1 never erases the open loops from frontier #N.
> Rule: **close a loop, or park it here — never just drop it.**

**Last updated:** 2026-06-08 · **Branch:** `claude/launch-helen-os-0xZXH` @ `59b03f5`

## MINIMUM STATE VECTOR (cross-session sync format — ChatGPT / Claude / Hermes / git)

```
DONE
- MATHS crown: pluginRIEMANN_V8.0_FINAL.tex → CANON/ (d5c0231, helen-corpus-private)
- core.py:188 fix: verified by REDUCER on Python 3.11 (extract _ns, then f-string)
- roles.py + schema.py: compile + 3 gates PASS + 5/5 mutation breaches caught
- Hermes runtime identified: ~/.local/bin/hermes + tools/approval.py
- Execution frontier crossed: /approve → run_command → receipt (grounding caveat noted)
- 6 standalone tools: committed to helen-conquest (runtime-agnostic, not yet wired)

OPEN
- CONSTITUTION crown: STAGED in CANON/CONSTITUTION/cognitive_kernel/ (7 files, fix
  applied, compile+gates PASS). Awaiting operator's one-word declaration. ← step 4, one word away
- IDENTITY crown: not started (step 5)
- helen-corpus-private main: MATHS crown local-only, push pending
- governance corpus: corpus/01 + corpus_txt untracked in helen-corpus-private

BLOCKED
- IDENTITY (step 5) waits on CONSTITUTION declaration. Everything else → SEEDS.

DISSOLVED (2026-06-08): the live core.py:188 hunt across mac/geforce/hermes. HELEN-the-
chatbot CANNOT execute shell commands (confirmed by HELEN itself). The crown needs a
verified canonical SOURCE, not a live running copy. REDUCER holds verified files; staged
them in CANON. Copies sync FROM canon. No live-machine command required to crown.
```

NOTE: Any session showing 100% on KERNEL/MEMORY/LEDGER/RESOLVERS/SKILLS/COCKPIT is
showing DESIRED STATE, not verified state. Verified state is the DONE list above.
Hermes at 71% context / 9h46m — treat anything Hermes-only as at risk of compaction.

---

## THE INSIGHT (JM, 2026-06-08 — supersedes the "discipline" diagnosis)

Not "you generate faster than you close." Deeper: **you generate at 5 abstraction
levels at once** (maths → formal systems → agents → products → narrative). The
failure is **compression, not discipline.** And the corpus DOES exist — it is
**not canonicalized.** Too much, not nothing — the better problem.

**HELEN has THREE corpora, not one:**
```
MATHS_CORE        — Riemann, Finite-Band, Σ-SEED, QPGL, ΦΛΩΣ, Hypocoercivity, Langlands
CONSTITUTION_CORE — HELEN OS, Oracle Town, HAL, ledger, receipts, WUL, kernel, governance
IDENTITY_CORE     — Math→Face, character, director, avatar, doctrine, video, voice
```
Goal: G=(V,E), V = V_M ∪ V_C ∪ V_I, edges within + across corpora.
**31 HELENs become ONE graph; each HELEN a view over it.**

---

## ⭐ THE ONE NEXT ACTION (do only this) — CROWN THE CANONICALS

**The corpus is extracted (994 → 351 txt). The disease is named: 994 finishes,
0 coronations. The cure is crowning one canonical per cluster. Start with MATHS
— it already has its king.**

```bash
cd ~/Desktop/helen-corpus-private
mkdir -p corpus/00_MATHS_RIEMANN_CORE/{CANON,LINEAGE,WILD}
# CROWN the disciplined apex (the only one that refuses to claim RH):
git mv "corpus/00_MATHS_RIEMANN_CORE/pluginRIEMANN_V8.0_FINAL.tex" \
       "corpus/00_MATHS_RIEMANN_CORE/CANON/" 2>/dev/null || \
  mv "corpus/00_MATHS_RIEMANN_CORE/pluginRIEMANN_V8.0_FINAL.tex" \
     "corpus/00_MATHS_RIEMANN_CORE/CANON/"
# (then move QUANTUMFRAMEWORK/QPRF/STQM → WILD/, the other ~22 → LINEAGE/)
```

**Why this one:** crowning is a human-only act (your law: canon = operator mark).
The manifest tool inventories; YOU declare. MATHS is easiest — V8.0_FINAL is the
unambiguous apex. One crowning closes the pattern that's run for a year.

**Then:** repeat for GOVERNANCE (pick 1 architecture doc) and IDENTITY (pick 1
character/Math-Face doc). Three coronations → 31 HELENs become one graph with
three canonical roots → RAG from CANON only → Hermes answers with citations.

## 🟢 2026-06-08 — THE THREE CROWNS may now exist (HER drop, REDUCER verified)

JM dropped a clean Cognitive Kernel (core/ledger/memory/model.py — "Phase 1A L1")
+ the HELEN_DAN GOBLIN_RECALL manifesto image. This is NOT sprawl — it's the
compression. Candidate canonicals, one per corpus:

| Corpus | Canonical candidate | REDUCER verdict |
|---|---|---|
| MATHS | pluginRIEMANN_V8.0_FINAL.tex | crowned (disciplined, read) |
| CONSTITUTION | Cognitive Kernel (core/ledger/memory/model) | STRONG — primitives verified, see flags |
| IDENTITY | HELEN_DAN GOBLIN_RECALL manifesto | STRONG — single coherent doctrine |

Cognitive Kernel — VERIFIED (ran ledger.py + memory.py):
- ledger.py: hash-chain valid, deterministic digest stable. D0 contract (timestamps
  = metadata, EXCLUDED from identity hash; canonicalize_for_hash single source of
  truth) = the V0/V1 + Horn B lesson DONE RIGHT in ~140 lines.
- memory.py: namespace isolation (math/world/project), no cross-mutation, invalid
  namespace caught. = three-corpora insight as enforced code.
- core.py: S0 seed contract (seed=H(query+role+namespace)) deterministic.

FLAGS (REDUCER):
- BUG core.py:188 — f-string nested double-quote, SyntaxError on Python <3.12
  (same class as helen_say.py). Fix: extract context.get("namespace") to a var.
- Determinism PROVEN for MockModel, ASPIRATIONAL for Mistral (model.py:67 admits
  "seed may not be used by Ollama"). Docstring "Deterministic Mistral" overclaims.
- roles.py + schema.py imported, NOT uploaded — gate logic (validate_structure,
  validate_namespace_consistency) unverified.
- DECISION: kernel namespaces (math/world/project) differ from corpus triad
  (MATHS/CONSTITUTION/IDENTITY). Align, or 4th taxonomy? Operator's one-sentence call.

## ⭐ THE CROWN ORDER (JM ruling 2026-06-08)

```
1. ✅ MATHS CROWNED — corpus/00_MATHS_RIEMANN_CORE/CANON/pluginRIEMANN_V8.0_FINAL.tex
                      (JM confirmed 2026-06-08; first coronation of the arc)
2. ✅ Kernel compile bug — core.py:188 fix VERIFIED by REDUCER (all 5 kernel files compile)
3. ✅ roles.py + schema.py VERIFIED by REDUCER 2026-06-08 (see verdict below) ← was the blocker
4. CONSTITUTION kernel — VERIFIED, READY TO CROWN (human-only act; JM declares + places in CANON)
5. Crown IDENTITY manifesto (HELEN_DAN GOBLIN_RECALL)
```

## 🟢 2026-06-08 — roles.py + schema.py VERIFIED (REDUCER, independent + mutation-tested)

JM dropped the two gate files; REDUCER wrote them from paste and ran them (not trusting
"smoke test passed" — STATE_AUTHORITY_GAP discipline). Results:
- compile OK (Py 3.11); validate_structure / validate_namespace_consistency /
  validate_kernel_admission_gates = PASS, 0 flags; ROLE_SCHEMAS + get_role_schema resolve.
- MUTATION TEST (the real proof — gates must have teeth): 5/5 breaches DETECTED with
  correct codes — ADMIT_EXECUTE_COLLAPSE, TRUTH_WRITE_AUTHORITY_CREEP, ROLE_MISSING,
  PROPOSE_ADMIT_COLLAPSE, ROLE_NAMESPACE_MISMATCH. The constitution is ENFORCED code.
- Doctrine match: LEDGER = sole truth-writer; admit≠execute; propose≠admit (USER excepted).
OBSERVATIONS (not blockers, JM to confirm):
- Two admitters: USER (= HumanSeal, human authority) + REDUCER (machine gate). Neither
  writes truth (only LEDGER). Reconciles "only REDUCER admits" with "authority human-only".
- Proposer≠Validator present as constraint STRING, enforced at RUNTIME not statically (correct).
- Dependency: schema imports roles; core imports both → kernel loads only once core.py:188
  fix is saved on the Mac (fix verified; just save it).

CROWN ACT (human-only): place the 6 kernel files (core/ledger/memory/model/roles/schema.py)
into a CANON location in the canonical repo + declare. REDUCER has verified; JM crowns.

**FIRST CROWN RECORDED:** MATHS canon = `pluginRIEMANN_V8.0_FINAL.tex`. The disciplined
Riemann apex (no-RH-claim ×3, Tier I/II/III) is now the maths canonical root. The other
~24 Riemann iterations → LINEAGE/WILD. One real victory: 994 finishes, now 1 crown.

**NAMESPACE RULING (settled, no conflict):**
```
math/world/project          = RUNTIME namespace (kernel execution layer)
MATHS/CONSTITUTION/IDENTITY  = CORPUS canon namespace (knowledge layer)
Different layers. Orthogonal. Not a 4th taxonomy. No reconciliation needed.
```

**core.py:188 FIX — VERIFIED by REDUCER on Python 3.11 (RE-CONFIRMED 2026-06-08):**
Compile sweep of the 5 uploaded kernel files: ledger/memory/model/main = OK as-is;
core.py = SyntaxError (f-string unmatched paren) until the one-line fix, then OK.
After fix → all 5 compile. Portable (works 3.11+, not just 3.12). Apply on Mac:
```python
_ns = context.get("namespace")
role_header = f"[KERNEL ROLE HEADER]\nROLE_ID={role} ROLE_NS={_ns} ROLE_VER=v1\n"
```

**CONSTITUTION crown — UNBLOCKED:** `roles.py` + `schema.py` VERIFIED 2026-06-08
(compile + 3 gates PASS + 5/5 mutation breaches caught). Ready for JM to crown.

## THE 7-DAY PLAN (JM's — recorded so it survives frontier #N+1)

```
D1-2  build helen_manifest_v1.json          ← THE ONE ACTION (tool ready: 74f801e)
D3    classify every artifact MATHS/CONSTITUTION/IDENTITY   (manifest does this)
D4    mark CANONICAL docs                    (operator sets status RAW→CANONICAL)
D5    build graph edges (depends_on)         (operator-marked; Frontier 3)
D6    RAG index from CANONICAL only          (helen_local_rag over canon subset)
D7    Hermes answers the graph with citations:
        "what theorem depends on Σ-SEED?"  "latest canonical Finite-Band paper?"
        "which doctrine references Math→Face?"
ONLY THEN consider LoRA.
```

---

## 🟢 CLOSED THIS SESSION (proof the dyad works)

- Gates 7+8 (HumanSeal + ¬Override) — shipped `284b347`, Horn D closed
- First clean-gate ADMITTED packet (real cargo) — `6a7a865`
- Replay-on-boot wired in this tree's CLI — `f87a3c8`
- Horn B audit: ledger is V0, guard is blind — `92b1915`
- **Canonical RUNTIME identified = Hermes** (2026-06-08, evidence-closed by JM):
  binary `~/.local/bin/hermes` · source `~/.hermes/hermes-agent/` ·
  approval `~/.hermes/hermes-agent/tools/approval.py` (per-session state, smart
  approval, allowlists). The runtime question is SETTLED.

## 🟢 CLOSED 2026-06-08 — corpus extraction (the biggest loop)

helen-corpus-private EXTRACTED: corpus/ 994 files → corpus_txt/ 351 text files
(poppler). Two corpora live: 00_MATHS_RIEMANN_CORE (~25 Riemann docs incl. the
disciplined V8.0_FINAL + wild QUANTUMFRAMEWORK/QPRF/STQM) + 01_HELEN_GOVERNANCE_CORE
(~200 docs, heavy version-sprawl). First time this session a tool ran on the REAL
corpus and produced output. Math kernel now text-readable + RAG-ready.

DIAGNOSIS REFINED (JM brutal-opinion turn): not "can't finish" — finishes
constantly (994 finishes), never CROWNS a winner (0 coronations). V8.0_FINAL is
proof JM CAN converge (the one disciplined Riemann apex). Cure = crown 1 canonical
per cluster.

## 🟢 2026-06-08 — EXECUTION FRONTIER CROSSED (with caveat)

Hermes executed an action end-to-end: Proposal → /approve appr_fa9b048a015e →
run_command ok=True → receipt sha256:7f6ae639bea3b698. The "ok go doesn't execute"
loop is RESOLVED via Hermes's own /approve. Gate held (queued→approved→ran);
authority=false intact; action receipted (NO RECEIPT = NO CLAIM honored).

CAVEAT (the grounding bug, at the git layer): HELEN ran git in its cwd
(gallant-khayyam worktree), NOT ~/Desktop/helen-corpus-private. Result: commit
b767e2d "corpus: governance + extracted txt" actually committed the 5 grounding
TOOLS (wrong files), on the wrong branch, with a mislabeled message. Ungrounded
action = mislabeled action. This is EXACTLY why KERNEL_CONTEXT/repo_root matters —
proven by the irony that the mislabeled commit's contents ARE the grounding tools.

ACTUAL STATE (both repos):
- helen-corpus-private @ main d5c0231: MATHS crown REAL + safe (V8 in CANON/, 83 files)
- gallant-khayyam b767e2d: mislabeled tool commit, harmless but wrong
- corpus/01_HELEN_GOVERNANCE_CORE + corpus_txt: STILL untracked in helen-corpus-private
  (the intended governance commit never happened)

RULE ADDED: do NOT let HELEN run git until grounded. Run repo commands in operator
shell, in the correct directory. Execution works; grounding-of-execution does not yet.

## 🟡 STANDALONE TOOLS — VALID (runtime-agnostic libraries)

These are importable into ANY runtime, including Hermes. They survive the runtime
finding. **Not yet wired into Hermes** (wiring needs `~/.hermes/hermes-agent/` source):

| Tool | Commit | Library for |
|---|---|---|
| `helen_kernel_context.py` | `7d97db6` | runtime grounding probe |
| `helen_action_schema.py` | `1ccc290` | action validate/repair |
| `helen_session_restore.py` | `5490566`/`05d1f81` | memory restore (incl. chat-log shape) |
| `helen_local_rag.py` | `fe37286` | cited code/corpus lookup |
| `helen_image_corpus.py` | `8e9211c` | screenshots/PDFs → corpus |
| `helen_manifest.py` | `74f801e` | tri-corpus classify + manifest |

## 🔴 INVALID TARGET — RETIRED (wrong runtime)

JM's runtime evidence (Hermes) retires every patch that wired `boot.py`/`helen_cli.py`:

| Retired | Commit | Why invalid |
|---|---|---|
| `apply_helen_grounding.sh` | `b9d6a15` | wires helen_cli.py/boot.py, not Hermes |
| PATCH A/B/C (grounding/schema/restore wiring) | `3f8d81b` | same — wrong runtime |
| PATCH D (approval loop) | `e1d538f` | helen_cli.py cmd_approve ≠ Hermes approval.py |

→ **Re-do as:** wire the VALID standalone tools into Hermes — requires reading
`~/.hermes/hermes-agent/` source first. PARKED to SEEDS (JM chose corpus track).

## 🔵 DECISIONS PENDING (JM's call, parked — not dropped)

1. **Canonical runtime** — `hermes` vs the `helen_cli.py` trees. (THE ONE ACTION resolves the input to this.)
2. **Canonical governance tree** — `helen-conquest` is the only chain-verified ledger; likely the governance root even if `hermes` is the runtime.
3. **31 trees / 7 repos / 28 worktrees** — tag each ACTIVE / ARCHIVED / EXPERIMENTAL. Stop booting non-canonical.
4. **Seal A** — `LEDGER_WRITER_UNIFICATION_V1` (`00d1535`), the V0-not-V1 fix.

## 🟣 SEEDS (TRACE_ONLY — do not let these become frontiers yet)

- **Wire the 6 valid tools into Hermes** → needs `~/.hermes/hermes-agent/` source read.
- **"ok go" approval bug** → re-diagnose against Hermes `tools/approval.py` (NOT
  PATCH D — that targeted the wrong runtime).
- Gemma4-12B LoRA on math corpus → **step 6 of 6.** Blocked on: canonical corpus.
- Gemma-4 MTP speculative decoding → verified real (`eb03a54`), deferred.
- Vision fix (PIL / VLM check) → diagnosed, not fixed.
- Jester Garden → gated behind capability contract (your own rule).
- Obsidian bridge, HELEN_SOUL persona, RUNTIME_CAPABILITY_CONTRACT → specced, await Hermes wiring.

---

## THE BRUTAL OPINION (preserved, amended by JM's reframe)

The work is real (`pluginRIEMANN_V8` is disciplined math, "no RH claim" ×3; your
classifier already sorts rigorous math from quantum-foam wild_text). The kernel is
real. **The bottleneck is convergence, not capability** — ~20 tools built this
session, zero installed; 31 HELENs = 31 unclosed loops.

**JM's amendment (accepted):** the fix is not "stop generating" — that's the engine.
The fix is **the dyad**: JM generates (HER), Claude seals (HAL+REDUCER). ADHD-HP +
Claude-as-executive-function is a valid architecture — it's HELEN's own role tensor,
externalized to the human+AI pair. This file is the seal made durable.

**The discipline JM preaches in code and must let the dyad apply to the work:**
`Termination is sacred. SHIP or ABORT. Close the loop or park it — never drop it.`
"Fix the tubulin before summoning the town."

---

## HOW TO USE THIS FILE (the protocol)

1. **Start of session:** Claude reads this first, states THE ONE NEXT ACTION.
2. **JM generates freely** — new ideas go to SEEDS, not into immediate action.
3. **One loop closes** → move it to CLOSED, pick the next ONE ACTION, update timestamp.
4. **Never** open a new frontier while THE ONE NEXT ACTION is undone — park it in SEEDS.
5. This file is the canonical "where are we." If it and JM's memory disagree, **this file wins** (it's the ledger; memory is narrative).
