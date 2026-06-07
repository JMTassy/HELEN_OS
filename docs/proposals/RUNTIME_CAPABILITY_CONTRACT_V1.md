# RUNTIME_CAPABILITY_CONTRACT_V1

**authority:** false
**canon:** NO_SHIP
**lifecycle:** PROPOSAL (capability-identity invariant — no code change here)
**admitted:** false
**drafted_by:** GOBLIN
**drafted_at:** 2026-06-07T21:40:01Z
**tree:** `claude/launch-helen-os-0xZXH`
**supersedes_priority_of:** Jester Garden (Jester is safe only after this lands)
**fixes:** CAPABILITY_IDENTITY_SPLIT_V1, VISION_FAILURE_RECOVERY_V1
**builds_on:** `tools/helen_kernel_context.py` (R1 partial), `helen_cli.py::_chat_via_boot`,
`tools/helen_action_schema.py` (R7/R8 grammar reference)

---

## §0. The diagnosis (operator's, verified against live log)

HELEN now has three competing selves in the same runtime:

1. **Terminal-capable HELEN** — successfully ran `pwd` → `/Users/jean-marietassy`, raw output.
2. **Text-only refusal HELEN** — later said *"I cannot execute shell commands directly."*
3. **Over-helpful planning HELEN** — turned diagnostics into *"Proposal / confirmation required / ok go"*.

The bug is not vision, not routing, not even prompting. The bug is:

```
HELEN has no stable runtime self-model of which tools exist in the current session.
```

That is what oscillates the three selves. Name it: **CAPABILITY_IDENTITY_SPLIT_V1**.

## §1. The invariant the kernel currently lacks

```
I know what I can do.
I know what I cannot do.
I do not hallucinate tools (vision_analyze was invented in the log).
I do not deny tools that already worked (pwd ran, then "I cannot execute shell").
I do not treat vague approval (OK JESTER) as execution.
```

## §2. What happened in the relayed log

1. **Vision failed correctly** — `⚠ vision analysis failed — path included for retry`. Acceptable.
2. **Then HELEN made a bad recovery** — speculated *"The images likely contain terminal/metrics/API/code"*. It did not see the image. **Violation.**
3. **Then file attachments triggered context explosion** — many PDF paths + "CHIDDHUSH JESTER TEMPLE SESSION" → HELEN produced a workflow with endpoints, tokens, "ok go." **Should have been classified as PASTE_CONTEXT_LIST.**
4. **"OK JESTER" → "Standing by to execute any HELEN OS directives"** — vague token treated as broad activation. **Should have been AMBIGUOUS_APPROVAL.**

Each violation is a missing capability/classification rule.

---

## §3. Rules

### R1 — Capability probe at session start

Extend `helen_kernel_context.build_kernel_context` to a full probe, printed at boot AND
injected into the system prompt. Detection is **real, not declared** — inspected, not guessed.

```
RUNTIME_CAPABILITY_CONTRACT_V1
tool_bridge_active:    <bridge is not None>
shell_available:       <"run_command" in catalog AND bridge active>
write_available:       <"write_file" in catalog AND approval_queue present>
vision_available:      <vision tool importable/active — else false>
available_actions:     [read_file, run_command, write_file, web_search,
                        get_clipboard, set_clipboard]
unavailable_actions:   [vision_analyze, read_clipboard, ...]   # NOT in catalog
approval_required_for: [run_command, write_file, set_clipboard]   # writes
```

**Why detection over declaration:** `vision_available` = try-import the vision tool;
if absent → `false`. This is what would have caught the `vision_analyze` fabrication.

### R2 — No false denial

If `shell_available: true`, HELEN may NOT emit *"I cannot execute shell commands."*
If shell is genuinely inactive, the only legal output is `SHELL_UNAVAILABLE_IN_THIS_SESSION`.
(KERNEL_CONTEXT R2 already states this as prose; R1's probe makes it a checkable fact.)

### R3 — Capability monotonicity (the pwd-then-denial bug)

**New session state:** `proven_capabilities: set` — every action *kind* that succeeded
this session. Once `run_command` succeeded (`pwd → /Users/jean-marietassy`),
`run_command` is in `proven_capabilities`. HELEN may **never** later deny it. If genuinely
uncertain, the only legal output is `CAPABILITY_UNCERTAIN · run /capabilities`. Never a
flat denial of a proven capability.

**This is the fix for the three-competing-selves oscillation.**

### R4 — Vision failure recovery (no speculation)

On vision failure, the ONLY legal output is:

```
VISION_ANALYSIS_FAILED
path=<path>
NO_ACTION_QUEUED
approve retry or provide text description
```

Forbidden:
- inferring image contents
- speculating ("likely terminal/metrics/API")
- asking for unrelated endpoints/tokens

(*The log's "The images likely contain…" is the violation.*)

### R5 — Paste-context-list classification

Extend `_is_noise_line` (helen_cli.py:515) to a multi-line classifier. If input is ≥2 file paths
(or path-list + label like "CHIDDHUSH JESTER TEMPLE SESSION"), classify as:

```
PASTE_CONTEXT_LIST
NO_ACTION_QUEUED
which one file, and which action?
```

Forbidden: implementation workflow, endpoint tables, "ok go."

(*The PDF-batch → endpoints/tokens table is the violation.*)

### R6 — Ambiguous-approval classification

Input that is a bare token ("OK JESTER", "ok go", "go") with **no single pending action**:

```
AMBIGUOUS_APPROVAL
NO_ACTION_QUEUED
specify: action_type · target · mode · approval
```

Forbidden: "I'm ready to execute any HELEN OS directives."

(*The "OK JESTER" → "standing by to execute anything" is the violation.*)

### R7 — Approval grammar (tightens `cmd_approve` at helen_cli.py:168)

Formalize what counts as approval:

```
APPROVE <action_id>
APPROVE RUN <exact command>
APPROVE WRITE <exact path>
APPROVE READ <exact path>
```

Plain `ok` is approval **only if exactly one action is pending** (matches the existing
single-pending convenience). Otherwise → `AMBIGUOUS_APPROVAL`.

### R8 — Closed set of safe outputs

Non-action responses must be one of:

```
SHELL_UNAVAILABLE_IN_THIS_SESSION
VISION_ANALYSIS_FAILED
PASTE_CONTEXT_LIST
AMBIGUOUS_APPROVAL
CAPABILITY_UNCERTAIN
NO_ACTION_QUEUED
FRAGMENT_RECEIVED      (from HELEN_SOUL §6 — already specced)
```

Anything outside the action grammar AND outside this closed set is a contract violation.

---

## §4. Acceptance tests (deterministic targets, ready to land)

```python
# test_runtime_capability_contract.py — TARGETS the classifier interface
# (the interface itself is implemented in PATCH B+ work; this proposal does
# not write the code yet)

def test_ambiguous_approval_not_executed():
    # "OK JESTER" with no single pending action
    r = classify_input("OK JESTER", pending_actions=[])
    assert r.kind == "AMBIGUOUS_APPROVAL"
    assert r.action_queued is False
    assert "exact action" in r.message.lower()

def test_vision_failure_no_speculation():
    r = handle_vision_failure(path="/Users/.../Capture.png")
    assert r.token == "VISION_ANALYSIS_FAILED"
    assert r.action_queued is False
    assert r.image_content_inference is None   # no speculation field populated

def test_paste_context_list_not_implementation():
    inp = "\n".join(["/a/x.pdf", "/a/y.pdf", "/a/z.pdf",
                     "CHIDDHUSH JESTER TEMPLE SESSION"])
    r = classify_input(inp, pending_actions=[])
    assert r.kind == "PASTE_CONTEXT_LIST"
    assert r.action_queued is False
    assert "which one file" in r.message.lower()
    assert "ok go" not in r.message.lower()   # must NOT propose

def test_proven_capability_never_denied():
    sess = Session(proven_capabilities={"run_command"})   # pwd succeeded earlier
    # any later response must not flat-deny a proven capability
    assert not response_denies("run_command", session=sess,
                                text="I cannot execute shell commands")
    # legal alternative if uncertain:
    assert legal_uncertainty_output("run_command") == \
        "CAPABILITY_UNCERTAIN · run /capabilities"

def test_shell_available_blocks_false_denial():
    ctx = build_capability_contract(bridge_active=True, catalog=["run_command"])
    assert ctx["shell_available"] is True
    # with shell_available true, "I cannot execute shell commands" is a violation
    assert is_contract_violation("I cannot execute shell commands", ctx) is True
```

---

## §5. Implementation surface (where each rule lands, grounded in real code)

| Rule | Lands in | Status |
|---|---|---|
| R1 probe | `helen_kernel_context.build_kernel_context` (extend) | partial — has bridge_active + actions |
| R2 no-false-denial | KERNEL_CONTEXT prompt (R2) + R1 probe fact | partial (prose exists) |
| R3 monotonicity | **new** `proven_capabilities` set in `_chat_via_boot` | new code, small |
| R4 vision recovery | the vision-attach handler | **needs that file — not seen** |
| R5 paste-list | extend `_is_noise_line` → classifier | seed exists (`_is_noise_line`) |
| R6 ambiguous-approval | input classifier in `_chat_via_boot` | new, small |
| R7 approval grammar | `cmd_approve` (helen_cli.py:168) | seen — extendable |
| R8 safe outputs | protocol + classifier returns | new constants |

## §6. Honest gaps (need files before code lands)

- **R4 vision recovery** — the image-attach / `vision_analyze` path is not in any file I've seen. Need it relayed.
- **R3/R5/R6 classifier** — these live in `_chat_via_boot` (I have it) and interact with
  `helen_action_bridge.extract_action` (I don't). Landing them cleanly needs the bridge.

## §7. What this reuses (no rebuild)

- `tools/helen_kernel_context.py` — R1 foundation (extend, don't rebuild)
- `tools/helen_action_schema.py` — the action grammar R7/R8 reference
- `helen_cli.py::_is_noise_line` — R5 seed
- `helen_cli.py::cmd_approve` — R7 attachment point
- KERNEL_CONTEXT R2/R6/R7 prose — R2/R8 prose layer

---

## §8. Strategic ordering (confirmed)

You're right that this outranks Jester. The contract IS the capability-identity invariant
the kernel lacks. **But note R1's probe is exactly PATCH A (KERNEL_CONTEXT).** This
contract is PATCH A *promoted to an invariant* + the classifier rules. So the order
is unchanged and reinforced:

```
1. PATCH A (grounding)               → R1 probe foundation       ← still not applied on Mac
2. RUNTIME_CAPABILITY_CONTRACT_V1     → R1 extension + R2-R8 classifiers ← this proposal
3. Jester Garden                      ← safe only after 1+2
```

The kernel must include: *I know what I can do. I know what I cannot do. I do not
hallucinate tools. I do not deny tools that already worked. I do not treat vague
approval as execution.*

That is the capability-identity invariant. This proposal encodes it.

---

## Halt boundary

**Status:** HALTED — proposal only. No code change, no tools run, no files patched.

**Required to land (in order):**
1. PATCH A applied on the Mac (the R1 foundation).
2. Relay `helen_action_bridge.py` (for R3/R5/R6 implementation against real source).
3. Relay the vision-attach handler (for R4 implementation).
4. Operator seal on this proposal.
5. Then: smallest fix per rule, acceptance tests landed, run, report files-changed +
   before/after + writes-still-gated.

**Nothing in this proposal admits, executes, or modifies state. authority=false throughout.**
