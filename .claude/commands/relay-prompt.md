# HELEN Relay Prompt Builder

Prepare bounded prompts for ORNITH (local GPU) dispatch via the relay architecture.

## Inputs

$ARGUMENTS — task type and target. Examples: "goblin proposals", "review transport/drift.py", "epoch M081 drift".

## Recipe

### Prompt Construction

1. **Identify the task type**:
   - `goblin` — GOBLIN-lane mining prompt (read-only, one data pile)
   - `review` — Code review prompt (bounded file set)
   - `epoch` — Math garden epoch prompt (single hypothesis)
   - `eval` — Evaluation/grading prompt (compare against ground truth)

2. **Gather context** — read the target files and extract only what the local model needs:
   - For `goblin`: list files in the target pile, extract key metadata (frontmatter, status fields)
   - For `review`: read the target file(s), extract function signatures and logic
   - For `epoch`: read the theme definition and prior epochs in that theme
   - For `eval`: read the evaluation criteria and test cases

3. **Build the prompt** with these constraints:
   - **Context window**: ~4K tokens max (ORNITH overlay-v3 is a LoRA fine-tune, limited context)
   - **Format**: single self-contained prompt, no external references
   - **Output spec**: exact JSON schema the relay expects back
   - **Guardrails**: include the forbidden-terms list, authority=false reminder

4. **Write the relay packet**:
   ```json
   {
     "relay_id": "RELAY-{task_type}-{hash8}",
     "model": "ornith-helen:v4",
     "prompt": "...",
     "output_schema": {...},
     "max_tokens": 2048,
     "temperature": 0.3,
     "routing": "ORNITH_DEFAULT"
   }
   ```

5. **Escalation check**: If the task requires deep reasoning (proof verification, adversarial gate, multi-step deduction), flag for FABLE escalation instead:
   ```
   routing: "FABLE_ESCALATE"
   reason: "requires adversarial verification / proof-grade reasoning"
   ```

### Output

Write relay packet to scratchpad. Print the prompt for operator to paste into local terminal.

## Routing Law

- **Default**: ORNITH (local GPU, zero API cost)
- **Escalate to FABLE** only when:
  - ORNITH has failed the same task twice
  - Task needs proof-grade reasoning (HAL gate, CHIDDUSH compression)
  - Task requires >4K context window
- **Escalate to Sonnet** for: HAL adversarial verification, code patches, test writing

## Loop Engineering (Fable)

Fable prepares N relay packets in parallel, operator dispatches locally:
```
for task in task_queue:
    packet = relay_prompt(task)
    if packet.routing == "ORNITH_DEFAULT":
        queue_local(packet)  # operator dispatches
    else:
        dispatch_cloud(packet)  # Fable/Sonnet handles directly
```
Feedback: ORNITH outputs that fail HAL gate get re-routed to FABLE on next iteration.
