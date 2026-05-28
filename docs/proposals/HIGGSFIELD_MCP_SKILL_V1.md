# Higgsfield MCP Skill — Skill Registration Proposal (v1)

NO CLAIM — NO SHIP — PROPOSAL ONLY — CANDIDATE_SKILL

```
artifact_type:         PROPOSAL_SKILL_DRAFT
proposal_id:           HIGGSFIELD_MCP_SKILL_V1
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: NOT_IMPLEMENTED
memory_class:          CANDIDATE_SKILL
captured_on:           2026-05-02
captured_by:           operator (Jean-Marie Tassy)
provenance:            operator paste of Higgsfield MCP product page
                       (https://mcp.higgsfield.ai/mcp), 2026-05-02
related_memory:        MASTER_MEMORY_EXPORT_HELEN_OS.md
                       CLAUDE.md (skill layer, non-sovereign tool execution)
hold_reason:           HELEN/MRED baseline stabilization in flight;
                       no implementation work authorized until baseline closed.
```

> **Operator framing**
> Higgsfield is documented enough to treat as real.
> Claude custom connectors are real.
> What is not yet real in HELEN: the wiring between them.
> This proposal defines the wiring contract only. It does not build it.

---

## §1. Executive Summary

Higgsfield exposes a Model Context Protocol (MCP) server at
`https://mcp.higgsfield.ai/mcp` that gives any MCP-compatible client (Claude,
OpenClaw, Hermes, NemoClaw) tool access to image generation, video generation,
character training, generation history, and multi-model comparison. No API key
is required — authentication is delegated to the user's Higgsfield account
through the MCP client.

This proposal specifies how a Higgsfield MCP client integration would be
registered as a **non-sovereign skill** inside HELEN OS, without violating
the existing authority lattice or ledger discipline. It does not authorize
implementation, does not commit to a build path, and does not promote to
canon.

---

## §2. Architectural Fit

### §2.1 Layer placement

Higgsfield MCP integration belongs in **Layer 4 (Skills + Tools)** of the
HELEN OS five-layer architecture, alongside `oracle_town/skills/voice/`,
`oracle_town/skills/video/hyperframes/`, and `oracle_town/skills/feynman/`.

It does **not** belong in:

- **Layer 1 (Constitutional Membrane)** — Higgsfield is not a verdict source.
- **Layer 2 (Append-Only Ledger)** — Higgsfield does not write the ledger.
- **Layer 3 (Execution + Autonomy)** — Higgsfield is not a generic executor;
  it is a specific skill with one upstream vendor.

### §2.2 Distinction from `helen_unified_interface_v1`

`helen_unified_interface_v1.py` is a **text-LLM dispatcher** — it routes
between Ollama, Claude, GPT, Grok, Gemini, and Qwen for conversational
queries. Higgsfield is a **media generation skill** — different shape,
different output type, different cost model.

The dispatcher and the skill registry are sibling subsystems, not parent and
child. Higgsfield should be registered in the skill layer, not added as a
seventh provider in the dispatcher.

### §2.3 Comparison to existing skills

| Existing skill                          | Pattern reused for Higgsfield |
|-----------------------------------------|-------------------------------|
| `voice/gemini_tts/` (Zephyr TTS)        | External vendor, scoped output, receipt-gated invocation |
| `video/hyperframes/` (HyperFrames)      | Media generation skill, declared but not active |
| `feynman/peer_review/`                  | Non-sovereign servitor, output requires witness verification |

---

## §3. Authority Constraints (non-negotiable)

### §3.1 Authority lattice position

```
NONE < NON_SOVEREIGN < WITNESS < REDUCER < SOVEREIGN

Higgsfield_MCP_Skill: NON_SOVEREIGN
```

Higgsfield can **propose** media artifacts. It cannot:
- Issue verdicts (SHIP / NO_SHIP / BLOCK / PASS)
- Mutate the ledger directly
- Modify governance, schemas, or constitutional files
- Self-promote artifacts to RECEIPTED or higher

### §3.2 Lifecycle entry point

Generated media enters HELEN at lifecycle level **RAW** (lowest), not DRAFT
or higher. Promotion to DRAFT requires an explicit operator action with a
receipt binding. Promotion to RECEIPTED requires a witness pass.

```
RAW < DRAFT < CANDIDATE < RECEIPTED < ACTIVE < CANONICAL

Higgsfield output entry point: RAW
Auto-promotion ceiling:        RAW (no auto-promotion)
```

### §3.3 Forbidden arrows

Per HELEN_SERVITOR_LAYER constitutional math:

```
S_higgsfield ↛ L    (skill cannot write to ledger)
S_higgsfield ↛ K    (skill cannot touch kernel)
S_higgsfield ↛ G    (skill cannot modify governance)
S_higgsfield ↛ W    (skill cannot pose as witness)
```

All Higgsfield outputs flow through:

```
S_higgsfield → operator review → MAYOR receipt → ledger writer (helen_say.py)
```

The skill never writes to `town/ledger_v1.ndjson` directly. `tools/kernel_guard.sh`
will reject any such attempt.

---

## §4. Required Receipts (per generation)

Each Higgsfield generation that operator chooses to retain in HELEN state
must produce a receipt with the following fields:

| Field                   | Source                              |
|-------------------------|-------------------------------------|
| `skill_id`              | `higgsfield_mcp_v1`                 |
| `skill_authority`       | `NON_SOVEREIGN`                     |
| `prompt_text`           | operator-issued generation prompt   |
| `model_id`              | Higgsfield model selected (Soul, Veo, etc.) |
| `output_kind`           | `image` \| `video` \| `character` \| `asset_history_ref` |
| `output_uri`            | Higgsfield asset URI or local path  |
| `output_sha256`         | SHA256 of retrieved asset bytes     |
| `credits_consumed`      | Higgsfield credit count             |
| `lifecycle_entry`       | `RAW` (always)                      |
| `operator_decision`     | `KEEP` \| `DISCARD` \| `ITERATE`    |
| `receipt_timestamp_utc` | ISO-8601 Zulu                       |

Discarded generations leave **no ledger trace**. Only KEEP and ITERATE
decisions append.

---

## §5. Open Questions (unresolved)

### §5.1 Where does Higgsfield MCP actually run?

Two deployment patterns are possible:

- **(A) claude.ai web client** — operator connects Higgsfield via Settings →
  Connectors. Higgsfield is invoked from Anthropic's hosted Claude. HELEN
  receives outputs via paste / upload only. **Most likely path today.**
- **(B) Local MCP client inside HELEN** — HELEN ships an MCP client library,
  authenticates with Higgsfield directly, invokes generation server-side.
  Higher engineering cost, full receipt automation possible.

Pattern (A) is paste-driven and requires no HELEN code changes beyond a
receipt template. Pattern (B) requires a new dependency (MCP client SDK)
and an authentication store. **Pattern (A) is the recommended starting
point.**

### §5.2 Asset retention

Higgsfield stores generation history server-side. HELEN's ledger discipline
requires asset content to be hash-pinned, not URL-pinned (URLs rot,
content-addressed hashes do not). Operator must download retained assets
locally before receipt creation.

### §5.3 Credit-cost surfacing

Higgsfield bills credits per generation. HELEN's existing cost tracking in
`helen_unified_interface_v1.py` (USD-denominated, per-token) does not map
cleanly to Higgsfield credits. A separate cost ledger field
(`credits_consumed`, vendor-namespaced) is required.

### §5.4 Prompt firewall posture

Higgsfield outputs are media, not text — the prompt-firewall (data ↛ command)
risk is lower than for text LLMs. However, if operator pastes Higgsfield
output URLs back into HELEN prompts, the URL contents are **data**, not
authority. This must remain enforced.

---

## §6. Required Tests (before ACTIVE promotion)

This proposal does not authorize implementation. If a future task packet
authorizes implementation, the following test discipline must be met:

- **T1**: Skill registration renders correctly in `oracle_town/skills/`
  registry without breaking existing skills.
- **T2**: Receipt schema (`§4`) validates against `helen_os/schemas/`.
- **T3**: Forbidden-arrow tests confirm skill cannot write to ledger,
  kernel, governance, or witness layers.
- **T4**: One end-to-end live test: prompt → Higgsfield → asset → SHA256
  → receipt → ledger entry. Recorded as smoke-test receipt.
- **T5**: Cost-tracking test: credits surface separately from USD,
  no double-counting.

---

## §7. NOT YET (what this proposal does NOT authorize)

- ❌ Implementation of MCP client code in HELEN.
- ❌ Skill registration in `oracle_town/skills/`.
- ❌ Modification of `helen_unified_interface_v1.py`.
- ❌ Any commit touching `town/`, `helen_os/governance/`, or
  `helen_os/schemas/`.
- ❌ Telegram bot integration with Higgsfield (separate proposal required;
  current `tools/helen_telegram.py` `/video` command uses local Pillow +
  ffmpeg renderer, not Higgsfield).
- ❌ Promotion of any Higgsfield-generated artifact above RAW lifecycle.
- ❌ Use of Higgsfield in any AUTORESEARCH or autonomy loop.

---

## §8. Adjacent Proposals (referenced, not bundled)

- `META_ADS_MCP_SKILL_V1` — **NOT YET DRAFTED.** Meta Ads MCP connector
  (`https://mcp.facebook.com/ads`) is unverified as of 2026-05-02.
  Pending live setup test or official Meta documentation.
- `FRAMEWORK_ADMISSIBILITY_GATE_V1` — referenced parent gate for
  third-party MCP connector admission, currently missing from repo.
  HERMES_CAPABILITY_ANNEX_V1 is also blocked on this.
- `DIRECTIVE_AS_DATA_GATE_V1` — pending; relevant if Higgsfield outputs
  ever become input to subsequent prompts.

---

## §9. Operator Verbs (next moves)

When HOLD lifts and baseline stabilization closes, operator may:

- **[1] PROCEED-PATTERN-A** — Author a task packet for paste-driven
  Higgsfield use through claude.ai web. Receipt template only, no MCP
  client code. Smallest surface area.
- **[2] PROCEED-PATTERN-B** — Author a task packet for in-HELEN MCP
  client. Larger surface, full automation possible.
- **[3] HOLD** — Keep this proposal at PROPOSAL lifecycle. No code work.
- **[4] REJECT** — Discard proposal. Higgsfield remains operator-side
  only, no HELEN integration ever.

Default verb until operator chooses: **[3] HOLD**.

---

## §10. Provenance

- 2026-05-02 — Higgsfield MCP product page pasted by operator (twice).
  URL: `https://mcp.higgsfield.ai/mcp`. Confidence: high (vendor-documented).
- 2026-05-02 — Operator memo drafted (sober operator framing, three
  confidence tiers). Confidence on Higgsfield: high. Confidence on Meta:
  low until tested.
- 2026-05-02 — This proposal drafted in response to operator request to
  "keep Higgsfield work at spec level under HOLD."

---

NO CLAIM — NO SHIP — PROPOSAL ONLY — CANDIDATE_SKILL
