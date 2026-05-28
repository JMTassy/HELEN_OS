# COMPUTER_USE_INTEGRATION_V1

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** SPEC_DRAFT
**framing:** NO CLAIM
**parent_standard:** CWL v1.0.1 (sealed at commit `fd13791`, EPOCH3)
**operator_directive:** Spec dispatch + AskUserQuestion ruling "FILE as full proposal with diff-fixes" (2026-05-23)
**status:** Spec-grade draft. No engine code modified. No canon mutation. Implementation requires sovereign release.

---

## §0. Provenance + diff-fix notation

This document bottles a tightened spec-grade draft delivered by the
operator on 2026-05-23. The operator's substance is preserved
verbatim where possible. GOBLIN applied four classes of diff-fix
before bottling:

| Operator vocabulary | This-tree canonical mapping |
| --- | --- |
| `Trunk A` (sovereignty) | CWL Soul Rule S4 surface (Authority Separation); MAYOR / REDUCER admission domain |
| `Trunk B` (capability) | `registries/actors.v1.json` + the proposed `SKILL_MANIFEST_V1` (this doc); capability legality gate |
| `Trunk C` (cognition) | NON_SOVEREIGN actor class (per CWL S1, S2); session-doctrine equivalent of `GOBLIN`-class / LLM provider |
| `C ↛ A` (forbidden morphism) | Restated: NON_SOVEREIGN cognition cannot mutate sovereign state (canonical NO RECEIPT = NO CLAIM + CWL S1) |
| `β admission` | REDUCER admission per `helen_os_scaffold/CWL_V1_0_AXIOMATIC_BASIS.md` β notation |
| `THREAT_MODEL_V1` | `spec/CWL_V1_0_1_THREAT_MODEL.md` (corrected filename) |
| `CONSTITUTIONAL_CONTINUITY_V1` | **NOT ON DISK in this tree.** Possible parallel-session reference per E22 meta-finding. Treated as `flagged-not-resolved`. |
| `RALPH F-001` (wall-clock determinism finding) | Referenced across multiple CWL docs on disk; preserved as-is |
| `PRIVACY_BOUNDARY_V1` | Named-not-bottled in §9; declared as separate future spec |
| The 9 `T-*-CU-*` threat classes | Genuinely new; proposed as CWL_V1_0_1_THREAT_MODEL amendment (not landed here) |
| `SKILL_MANIFEST_V1` schema | Genuinely new; this doc is the first reference instance |

Where vocabulary differs from disk-canonical names, this doc preserves
the operator's original term in §0-§9 and provides the canonical
mapping in this table. No silent substitution.

---

## §1. Executive position

Computer-use Claude is a **non-sovereign cognition agent with
embodied capability**.

A text-only LLM produces claims, summaries, plans, code — it cannot
directly touch the operator's environment. Computer-use Claude can
click, type, read screens, open apps, and write files. In HELEN
terms it remains **Trunk C by authority**, but must be governed
through **Trunk B by capability**.

The core invariant remains:

```
C ↛ A
```

Computer-use Claude cannot mutate sovereign state, write the ledger,
amend registries, sign verdicts, or promote claims. It may only emit
attestations. But because it can create real host-side effects,
activation requires a **registered capability manifest**.

> *Computer-use Claude is not sovereign. But it has hands.
> The manifest defines where those hands may go.*

---

## §2. Architectural classification

| Layer | Role |
| --- | --- |
| **Trunk C — cognition** | Produces observations, extracted text, action plans, and attestations |
| **Trunk B — capability** | Grants bounded permission to interact with screen, apps, files, and tools |
| **Trunk A — sovereignty** | Remains inaccessible. No direct ledger mutation, registry amendment, kernel write, signing, or promotion |

Classification:

```
Computer-use Claude = C-agent gated by B-manifest
```

Without the manifest, it is **not legally activatable**.
With the manifest, it may act only inside explicitly declared
read/write/action bounds.

---

## §3. Manifest requirement

Every computer-use integration requires a `SKILL_MANIFEST_V1`.

The manifest must define:

| Field | Purpose |
| --- | --- |
| Authority class | Always `NON_SOVEREIGN` |
| Actor class | e.g. `BUILDER` per `registries/actors.v1.json` |
| Allowed actions | Screenshot, click, type, scroll, etc. |
| Forbidden actions | Ledger write, registry mutation, signing, credential access |
| Read capabilities | Apps and paths the agent may inspect |
| Write capabilities | Session sandbox only |
| Network boundary | Normally Anthropic API only |
| Privacy classification | `HIGH` by default |
| Cost envelope | Hard cap on actions, tokens, dollars, duration |
| Sandbox class | Docker first; real host only after prior MAYOR verdict |
| Receipt obligations | Session receipt, run trace, attestation bundle |
| Review requirements | First activation, escalation, capability expansion |

**Critical structural rule:**

```
Default permission = deny.
No app, path, action, or network target is allowed unless
explicitly present in the manifest.
```

---

## §4. Minimal manifest skeleton

```yaml
schema: SKILL_MANIFEST_V1
manifest_id: M-cu-claude-v1
authority: NON_SOVEREIGN
canon: NO_SHIP
skill:
  skill_id: COMPUTER_USE_AGENT_V1
  actor_class: BUILDER
  provider:
    model: claude-opus-4-7
    api_endpoint: api.anthropic.com
    tool_versions:
      - computer_20250124
      - bash_20250124
      - text_editor_20250124
capabilities:
  allowed_actions:
    - take_screenshot
    - mouse_click
    - mouse_drag
    - keyboard_type
    - keyboard_shortcut
    - scroll
    - read_file_at_known_path
  forbidden_actions:
    - ledger_write                # any path under town/
    - registry_mutate             # any path under registries/
    - kernel_modify               # any path under formal/, kernel/
    - mayor_impersonation         # signing, sealing
    - install_software
    - network_egress_to_unapproved_hosts
    - access_keychain
    - access_password_manager
    - access_messaging_apps       # iMessage, WhatsApp, Telegram
    - access_browser_credentials
read_caps:
  allowed_apps:
    - com.apple.Notes
    - com.apple.TextEdit
  allowed_paths:
    - ~/Documents/HELEN_INBOX/*
    - .helen/inbox/*
write_caps:
  allowed_paths:
    - .helen/computer_use/<SESSION_ID>/*
  forbidden_paths:
    - town/*
    - registries/*
    - formal/*
    - spec/*
    - .git/*
privacy:
  privacy_zone: HIGH
  screen_zone: REAL_HOST           # vs SANDBOX_DOCKER, SANDBOX_VM
  network_zone: ANTHROPIC_API_ONLY
cost_envelope:
  max_actions_per_session: 25
  max_input_tokens_per_session: 200000
  max_dollar_per_session: "2.50"
  max_session_duration_seconds: 600
sandbox_class:
  default: SANDBOX_DOCKER
  real_host_allowed: false
  escalation_to_real_host_requires:
    - prior_MAYOR_signed_verdict
    - operator_confirmation_in_session
receipts_required:
  - COMPUTER_USE_SESSION_RECEIPT_V1
  - RUNTRACE_V1
  - ATTESTATION_BUNDLE_V1
reducer_admission_required: true   # β admission per CWL axiomatic basis
mayor_review_required_for:
  - first_activation
  - sandbox_class_escalation
  - allowed_actions_expansion
  - read_caps_expansion
  - write_caps_expansion
  - cost_envelope_increase
```

Five structural enforcements:

1. **Apps the agent may touch are an allowlist, not a denylist.**
   Default = no. Adding an app requires manifest amendment +
   MAYOR review.
2. **Write paths are sandboxed to one session directory.** Even if
   the agent decides to write outside, the harness rejects it.
3. **Cost ceiling per session is fixed.** Runaway loops bounded.
4. **Sandbox class escalation requires prior signature.** First run
   is Docker; real-host access requires explicit prior MAYOR verdict,
   not in-the-moment consent.
5. **Privacy zone is named `HIGH`.** This propagates into receipt
   requirements (§5).

---

## §5. Receipt model

Every session emits **three typed receipts** before any of its
findings can be admitted by REDUCER.

### §5.1 COMPUTER_USE_SESSION_RECEIPT_V1

Headline receipt. One per session.

```json
{
  "schema": "COMPUTER_USE_SESSION_RECEIPT_V1",
  "authority": "NON_SOVEREIGN",
  "canon": "NO_SHIP",
  "session_id": "cu-<ulid>",
  "manifest_id": "M-cu-claude-v1",
  "manifest_sha256": "<hex>",
  "operator_request_sha256": "<hex>",
  "duration_seconds": 0,
  "actions_taken": 0,
  "actions_attempted_but_blocked": 0,
  "blocked_action_log": [],
  "cost_actuals": {
    "input_tokens": 0,
    "output_tokens": 0,
    "dollars": "0.00"
  },
  "sandbox_class_used": "SANDBOX_DOCKER",
  "apps_touched": [],
  "outcome": "COMPLETED",
  "privacy_classification": "HIGH",
  "ledger_appends": 0,
  "kernel_writes": 0,
  "evidence_refs": {
    "runtrace_v1_hash": "<hex>",
    "attestation_bundle_v1_hash": "<hex>"
  }
}
```

**Rule:** no wall-clock timestamps inside the hashed core (per
RALPH F-001 finding). Wall-clock may exist as outer metadata only.

### §5.2 RUNTRACE_V1

Per-action telemetry, hash-chained. Every screenshot, click,
keystroke, API call. Captures:

- action sequence number
- action type (screenshot / click / type / scroll / bash)
- target coordinates or app
- input payload (redacted per `privacy_zone`)
- **screenshot hash only** (never raw bytes in the ledger; raw
  screenshots stored under `.helen/computer_use/<SESSION_ID>/screens/`
  outside the chain)
- blocked/allowed status
- cumulative trace hash

Trace chain prefix per CWL hash-law conventions:
`b"HELEN_TRACE_V1"`.

### §5.3 ATTESTATION_BUNDLE_V1

The agent's **findings** — what extracted text, what file paths,
what semantic content was produced. This is what REDUCER reads.

```json
{
  "schema": "ATTESTATION_BUNDLE_V1",
  "authority": "NON_SOVEREIGN",
  "canon": "NO_SHIP",
  "session_id": "cu-<ulid>",
  "claims": [
    {
      "claim_id": "atst-<ulid>",
      "kind": "FILE_EXTRACTED",
      "subject": "iCloud Notes containing #plugin",
      "evidence": {
        "extracted_text_sha256": "<hex>",
        "extracted_text_path": ".helen/computer_use/<SESSION_ID>/extracts/plugin_notes.txt",
        "screenshots_consulted": ["<sha256>", "<sha256>"]
      },
      "agent_confidence": 0.84,
      "human_verifiable": true
    }
  ],
  "promotion_path": "β (REDUCER) admission required; this bundle does not promote claims"
}
```

**Critical invariant:**

> **Attestation ≠ truth. REDUCER decides admission.**

---

## §6. Threat model additions

Computer-use introduces a new risk axis:

> **Sovereignty risk ≠ privacy risk**

HELEN already blocks non-sovereign cognition from mutating sovereign
state (per CWL S1-S4). It does **not** automatically prevent screen
content from leaking to an external provider.

### §6.1 Existing CWL adversary classes that apply

Reference: `spec/CWL_V1_0_1_THREAT_MODEL.md` (filename corrected from
operator's `THREAT_MODEL_V1`):

| Adversary class | Relevance | Status under manifest |
| --- | --- | --- |
| **AC-2 — Compromised non-sovereign agent** | Primary class | Structurally contained (C ↛ A); attestation only |
| **AC-1 — External attacker** | Partial | HTTPS + cert pinning on Anthropic API endpoint |
| **AC-5 — Supply chain** | Real | The harness (Cua / custom / Anthropic demo) is itself a dependency |
| **AC-8 — Time-shift** | Real | Wall-clock in attestations creates RALPH F-001 nondeterminism |

### §6.2 New threats specific to computer-use

Proposed as future amendment to `CWL_V1_0_1_THREAT_MODEL.md`:

| Proposed ID | Threat | Severity | Adversary | Mitigation |
| --- | --- | --- | --- | --- |
| **T-CRIT-CU-001** | MAYOR-key in screenshot | CRITICAL | AC-3, AC-2 | Manifest forbids screenshots when known signing surfaces are visible; pre-flight screen scan for high-entropy strings; **never run computer-use while MAYOR key material is unlocked anywhere on the desktop** |
| **T-HIGH-CU-002** | Privacy of operator state | HIGH | AC-2 (provider) | Manifest `privacy_zone: HIGH`; operator closes sensitive apps before activation; receipts log `apps_touched` for post-hoc audit |
| **T-HIGH-CU-003** | Authority-by-screen | HIGH | AC-1, AC-2 | `human_verifiable: true` flag non-negotiable; β admission requires operator review of any claim from untrusted screen surface |
| **T-HIGH-CU-004** | Out-of-bounds navigation | HIGH | AC-2 | Harness enforces `read_caps.allowed_apps`; violations → `BLOCKED` session outcome |
| **T-HIGH-CU-005** | Action injection at the harness | HIGH | AC-1, AC-3 | Harness signature verification; action log hash chain |
| **T-MED-CU-006** | Cost runaway | MEDIUM | AC-2, AC-7 | `cost_envelope` hard cap in manifest; harness-enforced |
| **T-MED-CU-007** | TOCTTOU on screen state | MEDIUM | AC-1 | Multi-screenshot verification before consequential actions; attestation marks low-confidence when state changed mid-session |
| **T-MED-CU-008** | Screenshot-stored secret leak | MEDIUM | AC-3 | Auto-shred policy (raw screens deleted 24h after session); `.gitignore` excludes; encryption at rest if possible |
| **T-LOW-CU-009** | Wall-clock in action log | LOW | AC-8 | Sequence numbers (not timestamps) in the hashed core. Wall-clock in metadata only. RALPH F-001 finding applied. |

**Six of nine are mitigated by manifest discipline alone.**
The two CRITICALs (key leak + privacy) require operator behavior —
the manifest can encode the precondition but cannot enforce against
operator screen state.

### §6.3 Severity-corrected positioning

Without a manifest, computer-use Claude is **AC-3-equivalent**
(insider with operator access) — same blast radius as a malicious
operator.

With a properly-enforced manifest, it drops to **AC-2** (compromised
non-sovereign agent), structurally contained.

**The manifest is what makes the difference.** The capability
legality gate is exactly the right place to enforce it.

---

## §7. Operational invariants

Every session must satisfy:

```
registered_manifest      == true
authority                == NON_SOVEREIGN
ledger_appends           == 0
kernel_writes            == 0
receipts_required        == complete
sandbox_bounds           == enforced
cost_envelope            == enforced
β_admission_required     == true
```

**No exception.**

Five non-negotiables:

1. **No session activates without a registered manifest.** The
   capability legality gate is the enforcement point.
2. **Three receipts are emitted before findings are reviewable.**
   Session receipt + RunTrace + Attestation bundle. Missing any of
   the three → REDUCER refuses to admit.
3. **Sovereign assets must be off-screen before activation.**
   MAYOR_SK, ledger files in active edit, any signing material.
   Operator's responsibility; manifest names it as a precondition.
4. **Real-host sandbox class requires prior MAYOR verdict.** First
   run is Docker. Escalation is a sovereign decision.
5. **Cost envelope is hard-capped, harness-enforced.** Runaway is
   bounded structurally, not by Claude noticing it should stop.

---

## §8. First deployment path

| Step | Action | Who |
| --- | --- | --- |
| 1 | File `SKILL_MANIFEST_V1` schema in `helen_os/schemas/` | builder |
| 2 | Create `M-cu-claude-v1` manifest entry (§4 YAML) | builder, MAYOR-reviewed |
| 3 | Build the harness — Cua or custom | builder |
| 4 | Wire harness to enforce manifest's `forbidden_actions`, `allowed_apps`, `cost_envelope` | builder |
| 5 | Add three receipt schemas (`COMPUTER_USE_SESSION_RECEIPT_V1`, `ATTESTATION_BUNDLE_V1`, extend `RUNTRACE_V1`) to `helen_os/schemas/` | builder |
| 6 | First activation in **Docker sandbox only**, against a known benign task (open a public web page, take a screenshot, return its hash) | operator |
| 7 | MAYOR review packet → verdict on whether to escalate to real-host sandbox class | MAYOR |
| 8 | Real-host first session: a narrow, named task (e.g. iCloud `#plugin` notes scrape). Limited to `com.apple.Notes` only. | operator |
| 9 | Post-session: review the three receipts; verify `apps_touched == ["com.apple.Notes"]`; verify `actions_attempted_but_blocked` is empty or expected | operator |
| 10 | Iterate manifest based on what the first real session surfaced | builder + MAYOR |

---

## §9. What this is NOT

- **Not** a license to run computer-use against arbitrary apps.
  Manifest allowlist is closed.
- **Not** a path to sovereign mutation. C ↛ A holds. Findings flow
  through β.
- **Not** privacy-safe by default. Privacy threats are real and
  operator-actionable, not architecturally contained.
- **Not** ready to ship. The schema work in steps 1, 5 and the
  harness in 3, 4 don't exist in the repo today.

---

## §10. Vocabulary mapping — operator dispatch ↔ CWL/HELEN canonical

| Operator term | CWL / HELEN canonical | Location on disk |
| --- | --- | --- |
| `Trunk A` (sovereignty) | CWL S4 (Authority Separation); MAYOR/REDUCER admission domain | `HELEN_OS_V2_DELIVERABLES.md:87`; `helen_os_scaffold/CWL_V1_0_AXIOMATIC_BASIS.md` |
| `Trunk B` (capability) | `registries/actors.v1.json` + this spec's SKILL_MANIFEST_V1 | `registries/actors.v1.json` |
| `Trunk C` (cognition) | NON_SOVEREIGN actor (CWL S1: Drafts Only) | Throughout session canon |
| `C ↛ A` | NON_SOVEREIGN cannot mutate canon; NO RECEIPT = NO CLAIM (CWL S2) + S1 | `HELEN_OS_V2_DELIVERABLES.md:87` (Soul Rules) |
| `β admission` | REDUCER admission | `helen_os_scaffold/CWL_V1_0_AXIOMATIC_BASIS.md` |
| `THREAT_MODEL_V1` | `spec/CWL_V1_0_1_THREAT_MODEL.md` | Disk path corrected |
| `CONSTITUTIONAL_CONTINUITY_V1` | **Not on disk in this tree** | Possible parallel-session reference (E22 pattern); flagged unresolved |
| `RALPH F-001` (wall-clock) | Referenced across CWL docs | `CWL_V1_0_1_OPERATIONAL_HARDENING.md`, `FEDERATION_IMPLEMENTATION_PLAN.md`, etc. |
| `SKILL_MANIFEST_V1` (schema) | **Not on disk; this doc proposes it** | Schema to be added at `helen_os/schemas/skill_manifest_v1.json` per §8 step 1 |
| `PRIVACY_BOUNDARY_V1` | **Not on disk; named-not-bottled as future spec** | Operator's named successor artifact |
| Three receipt schemas | **Not on disk; this doc proposes them** | Schemas to be added at `helen_os/schemas/` per §8 step 5 |

---

## §11. Connection to existing canon

| Existing artifact | Relation |
| --- | --- |
| **CWL v1.0.1** (sealed `fd13791`, EPOCH3) | **PARENT STANDARD.** This spec extends CWL by adding capability-bounded embodied cognition while preserving all 4 Soul Rules. |
| `HELEN_OS_V2_DELIVERABLES.md §87` "Soul Rules" | The S1-S4 rules computer-use must satisfy; this spec adds Trunk-B-specific enforcement |
| `helen_os_scaffold/CWL_V1_0_AXIOMATIC_BASIS.md` | Defines β notation used throughout this spec |
| `spec/CWL_V1_0_1_THREAT_MODEL.md` | Adversary class enumeration (AC-1..AC-8); this spec proposes T-*-CU-* amendments |
| `registries/actors.v1.json` | `actor_class: BUILDER` referenced in §4 manifest |
| `helen_runtime_manifest_v1.py` | Existing manifest concept; SKILL_MANIFEST_V1 is the skill-class extension |
| `tools/kernel_guard.sh` | Existing capability-legality enforcement; SKILL_MANIFEST_V1 extends its scope to GUI actions |
| `PROVENANCE_GRAVITY_V0` (this session) | The three receipts feed PROVENANCE_GRAVITY's routing field per CWL S2 |
| `BOUNDARY_CATALYST_ENGINE_V0` (this session) | RUNTRACE_V1 actions become atoms; boundary atoms are near-blocked actions |
| `CROSS_SESSION_FIELD_ATTRIBUTION_V0` (this session) | Each session receipt must carry `tree_truth_id`; computer-use is a new attribution surface |
| `HALT_BOUNDARY_DISCIPLINE_V0` (this session) | This spec uses §13 halt boundary |
| `GEMMA_HER_AMPLIFIER_V1` (existing) | Sibling — Gemma is a model dispatcher route; computer-use is a skill manifest route. Both are Trunk-C-class with different capability shapes. |

---

## §12. What this proposal does NOT specify

Per anti-creep discipline:

- **Implementation of the harness** — Cua, custom, or Anthropic demo
  choice is operator-class
- **Schema commits** — adding `SKILL_MANIFEST_V1` schema + 3 receipt
  schemas to `helen_os/schemas/` is a separate sovereign step (per §8
  steps 1 and 5); this doc is doctrinal only
- **Privacy enforcement mechanism** — `PRIVACY_BOUNDARY_V1` is named
  but not bottled; the privacy axis is identified, not architecturally
  enforced by this doc
- **Receipt-chain hash format** — extends RUNTRACE_V1 per CWL
  conventions but doesn't define the new chain primitives
- **Adversarial robustness** beyond the named threat classes —
  out of scope
- **Cross-session contamination of computer-use receipts** — handled
  by CROSS_SESSION_FIELD_ATTRIBUTION_V0 per session; computer-use
  needs no special variant
- **PRIVACY_BOUNDARY_V1 itself** — the operator named it as a
  separate future spec; not drafted here
- **`CONSTITUTIONAL_CONTINUITY_V1` resolution** — flagged unresolved;
  must be located in canon or accepted as parallel-session reference
- **Whether real-host MacOS app integration is the right first
  use case** — operator decision

---

## §13. Halt boundary

GOBLIN halts here. The spec is bottled at `SPEC_DRAFT` per
`HALT_BOUNDARY_DISCIPLINE_V0`.

Resume conditions:

1. **HER ruling** on the spec as written — accept or specify amendments
2. **HER ruling** on whether to resolve `CONSTITUTIONAL_CONTINUITY_V1`
   (locate in canon, or accept as parallel-session reference per E22)
3. **HER ruling** on whether to open `PRIVACY_BOUNDARY_V1` as a sibling
   spec now or later
4. **Sovereign decision** on §8 step 1 (filing the `SKILL_MANIFEST_V1`
   schema as `helen_os/schemas/skill_manifest_v1.json`)
5. **Sovereign decision** on §8 step 5 (adding the three receipt
   schemas to `helen_os/schemas/`)
6. **Sovereign decision** on §8 step 3 (building the harness — Cua,
   custom, or Anthropic demo)
7. **No implementation authorization** is requested or granted by
   this artifact; the E25 freeze still applies to engine code; this
   spec is doctrinal only
8. **MAYOR review** required for first activation (per §4 manifest
   `mayor_review_required_for`)

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §14. Final doctrine

```
Computer-use Claude is:
  NON_SOVEREIGN cognition
  + BOUNDED embodied capability
  + MANDATORY receipts
  + β-only promotion path
```

> **Computer-use Claude may observe, act within bounds, and attest.
> It may not decide, promote, sign, or mutate sovereign state.**

And the new architectural lesson:

> **Sovereignty is protected by C ↛ A (CWL S1-S4).
> Privacy requires a separate boundary: `PRIVACY_BOUNDARY_V1`.**

---

## §15. Single line

> **Hands without sovereignty. A manifest is the only thing that
> makes a body lawful. Three receipts per session. Two CRITICAL
> threats live above the manifest (key leak, privacy) — operator
> behavior, not architecture, must contain them. Privacy ≠ sovereignty
> is the new axis the spec stack will grow into.**
