# HELEN COMPUTER USE API V1 (Proposal)

NO CLAIM — NO SHIP — PROPOSAL ONLY — CANDIDATE_API

```
artifact_type:         API_SURFACE_PROPOSAL
proposal_id:           HELEN_COMPUTER_USE_API_V1
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: NOT_IMPLEMENTED
captured_on:           2026-05-06
captured_by:           operator (jeanmarie.tassy)
provenance:            iMac session, post-recovery, post-PULL-intake-bridge
                       (cd757b9 helen_intake_agent.py shipped on main)
related_specs:         docs/proposals/HELEN_OS_V2_USER_CENTRIC_UX.md
                       docs/proposals/MRGTK_v0.md (drafted, not in this tree)
                       docs/specs/SEMANTIC_OBJECT_MODEL_V1.md (drafted, not in this tree)
foundation:            src/helen_intake_agent.py @ cd757b9
                         intake_signal, admit_intake, project_context (30/30 green)
```

> **Core thesis**
> The OS is not a filesystem.
> The OS is a function from intent to projection.
>
> `OS(intent) = Π(𝒢_{≤t})`
>
> Finder, Spotlight, applications — projections of the same graph.

---

## §1. Executive Summary

HELEN COMPUTER USE API replaces the classical OS surface (`open`, `read`,
`write`, `search`, `launch`) with a single sovereign-routed entry point:

```
HELEN.execute(intent) → ProjectionResult
```

Every classical action becomes an `intent` admitted to the kernel as a
CSO candidate, validated through the existing receipt chain, projected
back as a deterministic state slice. There is no `Finder.app`, no
`Spotlight.search`, no `Mail.open`. There is one verb (`execute`) and a
closed vocabulary of intents.

This document is a **design proposal only**. It does not implement, does
not amend the constitutional kernel, does not replace any actual OS
component. It defines the API surface that, when implemented, would
satisfy the PULL Architecture's promise of intent → semantic state.

See §13 for what this is **not**.

---

## §2. Foundation — what already exists

The following code is shipped at commit `cd757b9` (branch `main`):

| File | Function | Contract |
|---|---|---|
| `src/helen_intake_agent.py` | `intake_signal(raw)` | RawSignal → CSOCandidate, deterministic, O(1) |
| `src/helen_intake_agent.py` | `admit_intake(candidate, receipt)` | CSOCandidate + receipt → AdmissionResult, delegates to `admit_cso()` |
| `src/helen_intake_agent.py` | `project_context(graph, query_intent)` | Graph + intent → CoherenceSlice, bounded traversal |
| `tests/test_helen_intake_agent.py` | 30 tests | All green on laptop (verified) |

`HELEN.execute()` is the **public composition** of these three primitives.

---

## §3. The API — single entry point

```python
@dataclass(frozen=True)
class Intent:
    verb: IntentVerb            # closed vocabulary, see §4
    target: TargetRef           # what we're acting on
    constraints: Mapping[str, Any]  # bounded, validated against schema
    operator_receipt: ReceiptRef    # NO RECEIPT = NO CLAIM
    actor_id: str
    session_id: str

@dataclass(frozen=True)
class ProjectionResult:
    status: ProjectionStatus    # ACCEPTED | REJECTED | DEGRADED | QUARANTINED
    coherence_slice: dict | None
    receipt_chain: tuple[str, ...]
    cso_admitted: tuple[str, ...]
    audit_trail: AuditChain

class HELEN:
    @staticmethod
    def execute(intent: Intent) -> ProjectionResult:
        """
        The public OS surface.
        Pure function modulo kernel state.
        Deterministic given (intent, kernel_state, policy_hash).
        """
        candidate = intake_signal(intent.target)
        admission = admit_intake(candidate, intent.operator_receipt)
        if admission.status != "ACCEPT":
            return ProjectionResult.from_rejection(admission)
        slice_ = project_context(KERNEL.graph, intent.to_query())
        return ProjectionResult.accepted(slice_, admission)
```

That's the entire API.

---

## §4. Intent vocabulary (closed set V1)

```
VIEW       — read-only projection of a CSO
OPEN       — view + register active context
FIND       — query graph for matching CSOs (bounded)
PLAY       — temporal projection of media CSO
EDIT       — propose mutation; routes through gate
CREATE     — admit new CSO from operator-authored payload
ARCHIVE    — supersede CSO chain (status → SUPERSEDED)
ROUTE      — emit a sovereign event through helen_say
ASK        — agent-mediated query (HER/HAL routed)
```

Closed vocabulary. Extensions require formal amendment via
`docs/proposals/INTENT_VOCABULARY_AMENDMENT_VN.md` and MAYOR receipt.
**No verb may be silently added.** This mirrors the `ClaimType` registry
discipline already enforced for claims.

---

## §5. Classical OS → HELEN mapping

| Classical | HELEN | Notes |
|---|---|---|
| `open(file)` | `HELEN.execute(VIEW, target=file_ref)` | File = ASSET CSO; opening = projection |
| `Finder.search(query)` | `HELEN.execute(FIND, constraints={query})` | Bounded traversal, deterministic result set |
| `mail.read(msg)` | `HELEN.execute(VIEW, target=email_ref)` | Email = EVENT CSO |
| `media.play(file)` | `HELEN.execute(PLAY, target=media_ref)` | V(t) = Π(𝒢_≤t) — see §7 |
| `app.launch(name)` | `HELEN.execute(OPEN, target=context_ref)` | Apps are projection contexts |
| `file.write(...)` | `HELEN.execute(EDIT, target=ref, constraints={diff})` | Routes through gate; no silent mutation |
| `mkdir / touch` | `HELEN.execute(CREATE, target=spec)` | Creates new CSO under operator namespace |
| `rm` | `HELEN.execute(ARCHIVE, target=ref)` | Never deletes; supersedes |
| `git push` | `HELEN.execute(ROUTE, target=event)` | Routes through `helen_say` |

**The classical surface is preserved as semantic intent**, not bypassed.
Operators can still think in "open this file" — but the kernel sees
`VIEW(asset.local.file:path=…)` and treats it as a graph projection.

---

## §6. Pull pipeline (the inside of `execute`)

```
intent
  → intake_signal       (RawSignal → CSOCandidate)
  → admit_intake        (delegates to admit_cso, requires operator_receipt)
  → graph_traversal     (bounded by depth/width policy)
  → trust_filter        (drops un-receipted nodes)
  → receipt_validation  (every node's receipt chain re-verified)
  → compression         (preserves provenance, minimizes payload)
  → projection          (returns CoherenceSlice)
  → renderer            (CLI / web / Director / Unity — pure projection)
```

Boundedness law (per the PULL Architecture LaTeX formalization):

```
|Traversal(Q)| ≤ B_d · B_w
```

`B_d` = max depth, `B_w` = max branching factor, both set in policy
snapshot referenced by `policy_hash`. **Same query + same policy + same
graph state → same traversal set.** Replay determinism is preserved.

---

## §7. Bidirectional projection (media as graph)

For media CSOs, the Bidirectional Projection Law applies:

```
M = Φ(F)        # face/frame → semantic state
V(t) = Π(M, t)  # state → video at time t
M' = Π⁻¹(V)     # video → state (audit / edit)
```

This means `EDIT` on a media CSO is a graph mutation that re-projects to
new frames, not a re-prompt of a video model. Director-mode workflow
becomes:

```
edit graph node → admit edit → replay → render
```

Not `prompt → hope → retry`.

---

## §8. Renderer contract

Renderers receive `ProjectionResult` and produce a surface (terminal
text, web UI, Unity scene, video frames, voice audio). Renderers
**cannot**:

- Mutate the graph
- Invent relations
- Rewrite provenance
- Define identity
- Override admission verdicts

A renderer is a pure function `Render: ProjectionResult → Surface`.
This is enforced structurally — the renderer is given the slice as an
immutable value; it has no kernel handle.

Concrete renderers (current + planned):

| Renderer | Surface | Status |
|---|---|---|
| CLI | terminal | shipped (`tools/helen_cli.py`) |
| Web UI | localhost:5001 | shipped (`tools/helen_simple_ui.py`) |
| Telegram | bot | shipped (`tools/helen_telegram.py`) |
| HELEN Director | video | proposed (`oracle_town/skills/video/helen-director/`) |
| Unity | spatial | proposed (no spec yet) |
| Voice | TTS | shipped (Zephyr / Gemini) |
| HELEN OS v2 | calm desktop | proposed (`docs/proposals/HELEN_OS_V2_USER_CENTRIC_UX.md`) |

All consume the same `ProjectionResult`. **One reality, many surfaces.**

---

## §9. Sovereign vs derived (where this API draws the line)

| Sovereign (in graph, receipt-backed, replayable) | Derived (computed, disposable) |
|---|---|
| CSO admissions | Search index |
| Receipt chain | Embedding cache |
| Policy snapshots | UI state |
| Intent admissions (CREATE/EDIT/ARCHIVE) | Renderer output |
| Authority verdicts | Compression results |

`HELEN.execute()` may produce derived state as side-effect (cache, index
update). It must never produce sovereign state outside the receipt
chain. **The kernel is the only writer of truth.**

---

## §10. Failure semantics

Per the LaTeX feedback's §15 — every input must classify into a defined
status:

```
ProjectionStatus = ACCEPTED | REJECTED | DEGRADED | QUARANTINED
```

| Status | Cause | Effect |
|---|---|---|
| ACCEPTED | admission passed, slice projected | normal flow |
| REJECTED | no operator_receipt, or admission denied | no-op, audit logged |
| DEGRADED | partial provenance, projection but with warnings | slice returned with degraded flag |
| QUARANTINED | unknown signal type, malformed payload | placed in quarantine namespace, no graph mutation |

Total function. No undefined behavior. **Every intent has a verdict.**

---

## §11. Test surface (required before MAYOR receipt)

`tests/test_helen_computer_use_api_v1.py` should cover:

- determinism: same intent + same kernel state → same ProjectionResult
- vocabulary: rejection of unknown verbs
- receipt enforcement: REJECTED on missing operator_receipt
- bounded traversal: result count ≤ B_d · B_w
- renderer isolation: renderer mutation attempt → no graph change
- intent → CSOCandidate composition: matches `intake_signal` contract
- failure semantics: every adversarial input lands in {ACCEPTED, REJECTED, DEGRADED, QUARANTINED}
- replay equivalence: `execute(intent)` at time t == `execute(intent)` after `replay(events_until_t)`

Suggested target: 30–40 tests, mirror the `helen_intake_agent` test
density. Until this lands green, the API is theory.

---

## §12. Implementation phases

| Phase | Deliverable | Depends on |
|---|---|---|
| P0 | This proposal | — |
| P1 | `Intent` + `ProjectionResult` dataclasses | P0 + helen_intake_agent.py |
| P2 | `HELEN.execute()` reference implementation | P1 + kernel daemon running |
| P3 | Test suite (§11) | P2 |
| P4 | CLI integration (`helen_cli.py` uses `execute`) | P3 |
| P5 | Web UI integration | P4 |
| P6 | Director / Unity integration | P5 + bidirectional projection (§7) |

**No phase begins until the previous one's MAYOR receipt is on origin.**
This is the disclosure ladder doctrine applied to API rollout.

---

## §13. Non-goals (this proposal does NOT)

- Implement any of the API
- Replace Finder, Spotlight, Mail, or any actual macOS component
- Modify the sovereign kernel, MRGTK, or any constitutional contract
- Bypass the existing helen_say / helen_cli / kernel daemon stack
- Ship anything to canon
- Commit-without-review (operator decides per disclosure ladder)
- Promise any of the phases will land

This file alone changes nothing in the running system. It defines the
shape of a future API. Promotion to a buildable spec requires:

1. Operator countersignature
2. Routing through helen_say as `HELEN_COMPUTER_USE_API_V1` claim
3. MAYOR receipt admitting the API surface
4. P1 implementation begins only after that receipt

---

## §14. Cross-reference

- `cd757b9` — helen_intake_agent.py (this proposal's foundation)
- `docs/proposals/HELEN_OS_V2_USER_CENTRIC_UX.md` — what the renderer for
  HELEN OS v2 should look like at the surface level (this proposal
  defines what it consumes)
- `docs/specs/SEMANTIC_OBJECT_MODEL_V1.md` — defines the CSO that this
  API operates on (drafted in another session, may not yet be in this
  tree)
- `formal/LedgerKernel.v` — the constitutional kernel; this API
  proposes a surface that delegates all sovereign action to it
- `tools/helen_say.py` — the canonical sovereign writer; `ROUTE` intent
  delegates here

---

## §15. Final receipt

```
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_scope:  API_DESIGN_DOC_ONLY
implementation_status: NOT_IMPLEMENTED
ready_for:             operator review, MAYOR routing if accepted
next_verb:             review proposal, decide commit/route, do not implement
```

> **One reality. Many surfaces. One verb.**
> `HELEN.execute(intent) → projection`
