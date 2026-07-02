# HELEN Local Dispatch

Dispatch bounded work to local models while preserving HELEN governance.
Adapted from a pasted asset this session — kept the procedure and hard
laws (they were sound), fixed the path/format to match what's actually
verified working in this harness, and wired model resolution through
the registry built earlier this session so this skill can't drift into
a fourth disagreeing source of "which model runs this role."

## Default stance

```
authority=false
canon=false
ledger_effect=none
reducer=NOT_INVOKED
output_status=NO_CLAIM
```

## Use when

- Running ORNITH / Ollama / local GPU model prompts
- Running CHIDDUSH mining (GOBLIN lanes, per `/compost-chiddush`)
- Creating garden-council payloads (per `/council`)
- Testing a local route
- Comparing local model outputs
- Reducing FABLE/cloud spend — local is the default per the barbell strategy

## Do not use when

- The task requires cloud-only tools (repo navigation via Read/Grep/Bash)
- The prompt contains secrets
- The operation posts externally
- The output would be treated as admitted evidence
- The task requires ledger mutation
- The operator has not approved paid/external API use

## Procedure

### 1. Resolve the model — through the registry, never a raw string

```bash
python3 tools/model_registry.py <ROLE>
```

If the role isn't registered, this fails loud (`UnregisteredRoleError`)
instead of silently guessing. Register the role in
`docs/spec/model_routing_registry.json` first — do not hardcode a tag
here as a workaround, that's the exact bug this skill exists downstream
of fixing.

If `tools/model_registry.py --check-drift` shows the resolved role as
`RESOLVED_BUT_*`, say so in the receipt below — dispatching through a
known-drifted role is still allowed, but the receipt must not hide it.

### 2. Choose the route — verify the tag's actual home first, don't assume

Two daemons can both answer `:11434` with **disjoint inventories**
(confirmed on the operator's own machine, 2026-07-02): the win32 daemon
and the WSL daemon do not host the same models. Check both before
assuming a tag resolves where you think it does — `curl -s
localhost:11434/api/tags` on each. Both share one GPU underneath —
queue, don't parallel-dispatch across daemons.

### 3. Write the payload with the Write tool, never a shell heredoc

A heredoc through `$(cmd <<PYEOF)` hits quoting and encoding traps on
mixed shells (cp1252/unicode) that cost real debugging time on the
first attempt at this pattern. Write the JSON payload as a file first,
then dispatch against that file:

```json
{
  "model": "<resolved from step 1>",
  "messages": [
    {"role": "system", "content": "authority=false; NO_CLAIM; answer only the bounded task."},
    {"role": "user", "content": "<bounded prompt>"}
  ],
  "stream": false,
  "think": false
}
```

`"think": false` matters for reasoning-tuned local models (e.g.
DeepSeek-R1 family) — without it, some return an empty `content` field
with the actual answer buried in a `thinking` field the caller wasn't
expecting, which reads as a silent failure if you're not checking for
it specifically. This is failure mode "empty_output" below in
disguise — check `content` is non-empty AND that it isn't the
reasoning trace before classifying the dispatch as successful.

### 4. Dispatch with an allowlisted local curl command, capture output to a sibling file

### 5. Strip hidden/thinking channels if the model emits them despite `think:false` — never surface a raw thinking trace as if it were the answer

### 6. Classify the output — mapped onto the existing WULmoji palette, not a new one

| Verdict | WULmoji | Meaning |
|---|---|---|
| garden_observation | 🔵 observed | merely produced, not yet judged |
| receipt_candidate | 🟠 review | ready for operator/HAL evaluation |
| draft_summary | 🟣 claim | proposed content, not admitted |
| error | ⚫ unknown | dispatch itself failed |
| empty_output | ⚫ unknown | nothing to classify |
| unsafe_output | 🔴 breach | authority-inflation or policy violation detected |

No output from this skill is ever 🟢/🟡/⚪ — those require an operator
admission receipt, a hash/version lock, or replay validation
respectively, none of which a local dispatch call performs.

### 7. Return a receipt (format below)

## Failure modes

| Failure | Required response |
|---|---|
| daemon unavailable | HOLD; report route |
| model missing | HOLD; ask operator for model |
| timeout | HOLD; include timeout |
| malformed JSON | BLOCK; do not infer |
| empty output | HOLD; retry only if bounded |
| thinking channel present | strip, or BLOCK if unsafe |
| output claims authority | BLOCK; classify authority inflation |
| external/cloud route needed | ASK_OPERATOR before spend |
| role not in registry | BLOCK; register it first, don't guess a tag |

## Receipt format

```yaml
LOCAL_DISPATCH_RECEIPT:
  authority: false
  canon: false
  ledger_effect: none
  reducer: NOT_INVOKED
  route:
  role_requested:
  model_resolved:          # from tools/model_registry.py, not hardcoded
  registry_status:          # RESOLVED | RESOLVED_BUT_* (copy from --check-drift)
  payload_file:
  output_file:
  exit_status:
  duration:
  output_class:             # garden_observation | receipt_candidate | draft_summary | error | empty_output | unsafe_output
  wulmoji: "🔵|🟠|🟣|⚫|🔴"
  thinking_channel_stripped: true | false | n/a
  unsafe_claims_detected: []
  next_allowed_action:
```

## Hard laws

```
local_model_output ⊬ evidence
dispatch_receipt ⊬ admission
garden_output ⊬ ledger
checker_green ⊬ commit_ready
no operator approval → no paid/external route
```

## Loop Engineering (Fable)

Single dispatches run inline. Batch dispatches (e.g. GOBLIN-RELAY-style
dual-miner comparisons) use `parallel()` across routes, each resolved
through the registry independently — never assume two "different"
dispatches actually landed on different models without checking.
