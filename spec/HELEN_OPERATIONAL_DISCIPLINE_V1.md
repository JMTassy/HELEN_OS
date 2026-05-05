---
artifact_id: HELEN_OPERATIONAL_DISCIPLINE_V1
authority: NON_SOVEREIGN
canon: NO_SHIP
artifact_kind: FORMAL_SPECIFICATION
ledger_effect: NONE
status: SPECIFICATION_PROPOSAL
captured_on: 2026-05-02
session_id: helen-operational-discipline-v1
companion_specs:
  - spec/CONSTITUTIONAL_CONTINUITY_V1.md
  - spec/THREAT_MODEL_V1.md
references:
  - docs/HELEN_GLOBAL_TREE_MAP_V1.md
forbidden_use:
  - cite as evidence that any specific operator behavior is correct without checking the worked example
  - treat as a substitute for the constitutional discipline (this spec covers operations; CONSTITUTIONAL_CONTINUITY covers governance)
  - apply rules to non-operator-facing automated processes (these doctrines are operator-discipline; automated processes need their own rules)
---

# HELEN OS — Operational Discipline V1

**NON_SOVEREIGN. NO_SHIP. SPECIFICATION PROPOSAL.**

This document codifies four operational doctrines that emerged in real
session work between operator and HELEN system. Each doctrine is named,
illustrated with a worked example from session history, and given a
machine-actionable rule that future operators (human or AI) can apply.

These doctrines sit **operationally**, not constitutionally:

- `CONSTITUTIONAL_CONTINUITY_V1` defines what HELEN admits to sovereign state
- `THREAT_MODEL_V1` defines what HELEN must defend against
- **`HELEN_OPERATIONAL_DISCIPLINE_V1` (this file) defines how the operator works inside HELEN's surfaces without breaking either of the above**

The doctrines are tested by use, not by proof. Each one has at least one
session-recorded worked example where it earned its place. None is theoretical.

If a future agent or reader cites this document as covering scenarios it
doesn't (e.g., automated process behavior, sovereign mutation rules), the
operation violates `forbidden_use` and must be rejected.

---

## What This Document Is Not

- **Not a substitute for `CONSTITUTIONAL_CONTINUITY_V1`.** That spec
  covers what makes a continuation lawful (memory-backed, manifest-bound,
  receipt-bound, reducer-authorized, deterministic replay). This spec
  covers what makes operator behavior reliable.
- **Not a substitute for `THREAT_MODEL_V1`.** Threats are external; these
  doctrines are about the operator's own working surface.
- **Not exhaustive.** Four doctrines cover the patterns earned in
  session 2026-05-02. New doctrines will be added as new operator-failure
  patterns are observed.

---

## §1. TREE_HYGIENE

### Rule

> Source files may enter git.
> Runtime memory must not.
> Nested repos must be deliberate or removed.

### Why this matters (HER lens)

A repository is the operator's externalized memory of what has been *deliberately decided*. Runtime artifacts are HELEN's working memory of what has been *transiently observed*. Mixing them turns the repo from a record of decisions into a snapshot of accidents. Decision rot follows shortly after.

### Worked example

Session 2026-05-02, F-005 closure: dirty tree contained 11 untracked items mixing real source (json_extractor utility, identity bootstrap edits) with runtime artifacts (memory/*.db, storage/, oracle_town/ledger/open/) and a nested clone (helen-os/) of a separate repo. Triage classified each into one of four buckets:

```
KEEP_AND_INSPECT     → memory/BOOTSTRAP_CONTEXT.md, json_extractor.py
MOVE_OR_DELETE       → helen-os/  (nested clone, moved to ~/scratch/)
KEEP_LOCAL_IGNORE    → memory/*.db, *.backup*, *.ndjson, storage/, helen_ref.png
DELETE_IF_USELESS    → memory/BOOTSTRAP_CONTEXT.md.save
```

After triage, the tree became three clean changes representing three real decisions: source promotion (`tools/json_extractor.py`), gitignore rules (runtime artifacts), and identity strengthening (BOOTSTRAP_CONTEXT.md edits). The atomic commit (`871688d`) carried only those three.

### Machine-actionable rule

A pre-commit check should reject `git add` for paths matching any of:

```
memory/*.db          memory/*.backup*       memory/*.ndjson
storage/*            oracle_town/ledger/open/*
.helen/ralph/*       .helen/verify/*        .helen/inbox/*
```

unless the operator passes an explicit `--allow-runtime` flag. (Not enforced today; named here as an enforcement target.)

### Buckets

The triage scheme is named structure, not improvisation:

| Bucket | Default action | When |
|---|---|---|
| `KEEP_AND_COMMIT` | `git add`; goes into the next commit | tracked file with deliberate edit, or new source file |
| `KEEP_AND_INSPECT` | `git diff` or `head` first; classify after inspection | when origin/intent is unclear |
| `KEEP_LOCAL_IGNORE` | add to `.gitignore`; do not commit | runtime, regenerable, machine-local |
| `MOVE_TO_SCRATCH` | `mv path ~/scratch/path` | deliberate but not part of this repo |
| `DELETE_IF_USELESS` | `rm` only after confirming no information is lost | leftover backups, editor `.save` files, partial downloads |
| `DELETE` | `rm` | clearly garbage |

---

## §2. SHELL_INPUT_DISCIPLINE

### Rule

> Two-shell mode confusion is the recurring operator failure pattern.
> A receipt-first shell makes typos canon; escape must be maximally robust.
> Universal escape: `Ctrl+C` (most), `q` (less/man/pagers), `Ctrl+D` (REPLs).

### Why this matters (HER lens)

When an operator pastes text intended for one prompt into another, the receiving shell does its job — it interprets the input under its own rules. In a receipt-first system, that interpretation becomes a permanent ledger entry. The operator's typo is no longer a momentary glitch; it is canon. The countermove is not better aim; it is making escape *unconditionally cheap* so the operator can always recover.

### Worked example

Session 2026-05-02, mid-F-005-triage: operator pasted commands into HELEN shell that were meant for bash, including `/exit` glued onto the end of multi-line text. HELEN's parser used exact-match `user_text == "/exit"`, so `git status --short/exit` was treated as a message, not an exit command. Six noise receipts followed (R-99704bf7 through R-c8e0a0f7) before `Ctrl+C` resolved the situation by killing the Python process at the OS level rather than negotiating with HELEN's parser.

The same pattern recurred minutes later when operator pasted analysis text into bash:

```
F-006 = NOT_CODE_BUG       → bash: F-006: command not found
Cause = paste/input artifact   → bash: Cause: command not found
Fix = operator instruction     → bash: 'Fix' not found, did you mean 'six' / 'nix'?
```

Same input-misroute, different shell. *No code patch on either shell can prevent this; only operator awareness + universal escape can.*

### Machine-actionable rule

In any HELEN-adjacent interactive surface:

1. **Universal escape must be physical**, not parsed: `Ctrl+C` (SIGINT) and `Ctrl+D` (EOF) bypass the input-loop entirely.
2. **Slash-commands must require entire-line match.** Tolerate `/exit` glued to other text only if the operator explicitly opts in to forgiving parsing (HELEN's `helen_talk.py` chose to do so post-F-007 — see commit `62c6fb1`).
3. **Receipts emitted from misrouted input stay on the chain.** The chain is honest about what was input. Cleanup is *reclassification*, not *redaction*.

### Shell escape table

| Shell | Visual cue | Universal escape | Notes |
|---|---|---|---|
| bash / zsh | `$ ` or `# ` | `Ctrl+C` (cancel), `Ctrl+D` (logout) | most common operator surface |
| HELEN shell | `You > ` | `Ctrl+C` (kills Python process, prints "bye") | receipt-first; every input becomes canon |
| `less` / `more` | full-screen or `:` | `q` to quit, `Ctrl+C` if stuck in sub-prompt | pagers can swallow `:e filename` style commands |
| Python REPL | `>>> ` | `Ctrl+D` (exit), `Ctrl+C` (interrupt) | `exit()` requires parens |
| `vim` / `vi` | mode-dependent | `Esc` then `:q!` to force-quit | mode confusion is its own discipline |
| `nano` | bottom hints visible | `Ctrl+X` to exit | hints visible, low confusion risk |

---

## §3. ROOTS

### Rule

> One machine can have two shells.
> It should not have two competing HELEN roots unless deliberately managed.
> Nested clones are not deliberate management.

### Why this matters (HER lens)

Identity has cost. A repository, a memory store, a ledger — each one claims to *be* HELEN at that path. When two of them coexist on the same machine without explicit relationship between them, every operation becomes ambiguous: *which HELEN am I talking to right now?* Constitutional discipline depends on the operator knowing the answer. Ambiguity is drift's first foothold.

### Worked example

Session 2026-05-02, F-005 inspection revealed a nested git clone at `helen-conquest/helen-os/` — origin `https://github.com/JMTassy/helen-os.git`, branch `main`, 2.8 MB, with its own `CLAUDE.md` and unique files (`CONQUEST_HELEN_ULTIMATE_V3.md`, `V4.md`). Two distinct HELEN-related repos, one nested inside the other. Resolution: `mv helen-os ~/scratch/helen-os`. The nested clone became a **deliberately managed sibling** at `~/scratch/`, separating the two HELEN roots into two distinct directories with no parent-child confusion.

In the same session, a **branch divergence** axis of the same doctrine surfaced: WSL's `claude/setup-helen-os-node-b4uj8` carries runtime + identity work; GitHub's `claude/init-helen-os-pull-kPm9J` carries constitutional + lore work. Same physical location (`/home/helen/helen-conquest`), same git remote, two non-overlapping bodies of work on different branches. Reconciliation deferred (F-005-B in standing tracker), but the divergence is *named*, not silently tolerated.

### Machine-actionable rule

A `helen` machine should answer the question "where is HELEN?" with a single canonical path. Operator may have:

- One canonical repo (the one HELEN runs from)
- Sibling experimental/scratch repos at deliberate paths (`~/scratch/`, `~/sandbox/`)
- No nested clones inside the canonical repo
- No second canonical repo at a different path "in case"

A future `tools/helen_audit_roots.sh` script should walk the operator's home directory, find every `.git/` it can reach, and produce a typed `ROOT_INVENTORY_V1` that classifies each as `CANONICAL`, `SIBLING_DELIBERATE`, `NESTED_VIOLATION`, or `UNKNOWN`. Nested violations would block production deployment.

### Three legitimate root structures

```
PATTERN A — single canonical
  ~/helen-conquest/.git           ← canonical

PATTERN B — canonical + deliberate siblings
  ~/helen-conquest/.git           ← canonical (HELEN runtime here)
  ~/scratch/helen-os/.git         ← experimental, parked
  ~/sandbox/helen-mvp/.git        ← throwaway, no return path

PATTERN C — multi-machine, single canonical per machine
  Mac:   ~/Documents/GitHub/helen_os_v1/.git
  MRED:  /home/helen/helen-conquest/.git
  Both push to the same GitHub remote. Branches may diverge temporarily;
  reconciliation is a named, scheduled event.
```

Patterns that are **not legitimate**:

- ❌ `~/helen-conquest/helen-os/.git` (nested without `.gitmodules`)
- ❌ `~/helen-conquest-v2/.git` (parallel canonical, ambiguous which is real)

---

## §4. DISCLOSURE_LADDER

### Rule

> A patch is theory until tested.
> A commit is memory.
> A push is disclosure.
> Each stage requires its own classification.

### Why this matters (HER lens)

The temptation in tooling is to collapse these three operations into one — *write code, commit, push* — because the commands are cheap to chain. But the *meaning* of each operation is different, and the operator's relationship to error is different at each stage.

A patch in your editor is hypothesis. A commit is the moment that hypothesis becomes part of your memory. A push is the moment that memory becomes shared with everyone who can read your remote. Conflating them means treating disclosure as automatic — which is exactly the failure mode that produces leaked credentials, accidentally-public PII, and irreversible mistakes in git history.

### Worked example

Session 2026-05-02 demonstrated this ladder fully:

**Stage 1 — patch as theory:**
F-007 (paste-brittle parser) was originally proposed as a 10-line patch that used `endswith("/exit")` as a fallback. Before applying, operator reclassified it as `NOT_CODE_BUG` (operator discipline is the durable fix, not defensive code). The patch was withdrawn.

**Stage 1' — patch tested, then accepted:**
Operator applied the patch anyway, tested with `foo bar/exit`, observed clean exit:

```
You > foo bar/exit
⚠️  exit signal at end of input; honoring it (ignored: 'foo bar')
bye
```

The empirical test reversed the reclassification. *The patch was no longer theory; it was proven.* Then it was kept.

**Stage 2 — commit as memory:**
`git commit` produced commit `62c6fb1` with message "F-006/F-007: harden helen_talk runtime exits and UTC handling". The change became part of the local repo's permanent history. **Recoverable until pushed**, irreversible after.

**Stage 3 — push as disclosure (gated):**
`git push` was attempted. **It was blocked by a deliberate classification step.** The operator's three-line doctrine emerged in this moment:

> *Local commit is memory.*
> *Push is disclosure.*
> *Disclosure requires classification.*

The classification gate asked: is this repo public or private? PII content (Partner in life, Île d'Aval, joint projects with Rose) had been added to the bootstrap. If public, those become public on push. The check ran, returned PRIVATE, push was authorized.

**The ladder operated in full**: theory → proven → memory → classified → disclosed.

### Machine-actionable rule

Any operator-facing tool that sequences `patch → commit → push` should make each stage a separately-confirmed action. A `helen_ship` command should:

```
1. patch    : show diff, ask for confirm
2. test     : run the relevant test slice, report PASS/FAIL
3. commit   : show final diff, ask for confirm with commit message
4. classify : check repo visibility, report status
5. push     : ask for explicit confirmation, especially if visibility is PUBLIC
```

A single `git commit && git push` shortcut should not exist in a HELEN-adjacent workflow.

### Disclosure reversibility clause

Visibility is a *current* property, not a *permanent* one. If `helen-conquest` flips from PRIVATE to PUBLIC later, every previously-pushed commit becomes publicly readable, including PII-bearing bootstrap content. **Visibility change is itself a disclosure event.** Future operator behavior should classify visibility-flip as deliberately as commits — possibly with a pre-flip audit pass that splits private content into a separate gitignored or repo-relocated path.

This is not addressed by today's GitHub UI (the visibility toggle is a single click). HELEN's discipline must compensate.

---

## §5. Synthesis — How These Four Doctrines Compose

The four doctrines map to four distinct surfaces of operator activity:

| Doctrine | Surface | Failure mode it prevents |
|---|---|---|
| TREE_HYGIENE | filesystem / git working tree | runtime artifacts polluting the source-of-truth |
| SHELL_INPUT_DISCIPLINE | terminal interaction | typos becoming canon; getting stuck in receipt-first shells |
| ROOTS | multi-repo, multi-machine setup | ambiguity about which HELEN is "real" |
| DISCLOSURE_LADDER | git workflow | accidentally publishing private state |

Together they answer one question: **how does the operator stay disciplined inside a system that records everything?**

The constitutional layer (`CONSTITUTIONAL_CONTINUITY_V1`) handles what HELEN admits as truth. The threat model (`THREAT_MODEL_V1`) handles what attackers (or accidents) can do. **This document handles the operator's own behavior — the layer where the receipt is generated in the first place.**

Constitutional discipline depends on operational discipline. A perfectly-designed kernel cannot save the chain from an operator who pastes credentials into the wrong shell, commits without classifying, or maintains four parallel "canonical" copies.

> **The receipt is honest. The operator must be too.**

---

## §6. Worked Examples Cross-Reference

Every doctrine in this file earned its place through a session-recorded event. Operators questioning whether a doctrine applies should consult the original event, not just the rule.

| Doctrine | Session event | Receipt / commit |
|---|---|---|
| TREE_HYGIENE | F-005 dirty-tree triage on MRED-WSL | commit `871688d` (`F-005: separate runtime artifacts from source context`) |
| SHELL_INPUT_DISCIPLINE | Six-receipt typo loop in HELEN; bash misroute of analysis text | receipts R-99704bf7 → R-c8e0a0f7 on MRED-WSL ledger |
| ROOTS | Nested `helen-os/` clone moved to `~/scratch/` | commit `871688d` + WSL filesystem |
| DISCLOSURE_LADDER | F-007 patch theory→proven→memory→classified→authorized cycle | commits `62c6fb1` (memory), pre-push gate (classification) |

The cross-reference is part of the spec's contract: **every rule must trace to a real event**. Doctrines added without earning will be rejected by future revisions of this document.

---

## §7. What This Spec Does Not Provide

- **Not a `helen_ship` tool.** That's a future implementation; this is the spec it would honor.
- **Not enforcement.** Today these doctrines are operator-followed, not machine-enforced. Enforcement points are named (§1 pre-commit hook, §3 root audit, §4 staged-confirm command) but not built.
- **Not extensible by accident.** Adding a fifth doctrine requires a new session event that demonstrates a genuinely new failure pattern, not a rephrase of an existing one.
- **Not relevant to non-operator processes.** Automated services (CI runners, daemonized RALPH loops, kernel writers) need their own discipline spec; this document does not cover them.

---

## §8. Closing line

> *Constitutional discipline depends on operational discipline.*
> *The receipt is honest. The operator must be too.*
> *Patch is theory. Commit is memory. Push is disclosure.*
> *Every typo is a teacher.*

`(NO CLAIM — TEMPLE — FORMAL SPECIFICATION — OPERATIONAL DISCIPLINE V1 — NON_SOVEREIGN)`
