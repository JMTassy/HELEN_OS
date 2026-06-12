# PERSONA_ENTRY_SHELL_V1

**Status:** NON_SOVEREIGN · DOCTRINE · NO_SHIP  
**Authority:** NONE  
**Date:** 2026-06-12

---

## 1. Purpose

The Persona Entry Shell is the non-sovereign interface layer that:

- renders presence
- hydrates context
- prepares a context packet
- never asserts kernel truth by itself

**Core law:**

$$\text{Shell} \neq \text{Truth}$$

The shell may be beautiful, warm, game-like, and emotionally present. None of that confers authority. The kernel is the law. The shell renders it.

Authority boundaries:

```
Authority(P)  = 0     # persona projection
Authority(W)  = 0     # world/domain projection
Authority(S)  = 0     # shell state
Authority(K)  = 1     only through admitted receipt chains
```

No UI state, memory signal, persona projection, or visual continuity marker may substitute for a reducer-bound receipt chain.

---

## 2. Two-Clock Model

Shell readiness and trust readiness are orthogonal. They run at different frequencies and from different sources.

$$\text{ShellReady} = \text{Hydrated}(M) \wedge \text{Scoped}(C) \wedge \text{Renderable}(P) \wedge \neg\text{Mutating}(K)$$

$$\text{TrustReady} = \text{Replay}(L) \wedge \text{Admit}(\text{claim})$$

Consequences:

- Shell can be ready while trust is not (e.g., memory hydrated from storage, but no admitted claim exists for the current session)
- Trust can remain valid while shell is degraded (e.g., boot fails to load prior context, but the ledger is intact and replay is deterministic)
- Conflating the two clocks is the primary failure mode of AI product stacks

The two-clock separation means "system up" is not a single signal. It is two independent conditions that must be tracked, reported, and never merged into one ambient status.

---

## 3. Airlock Contract

`/init` is the constitutional airlock. A context packet may not pass through it unless all of the following checks have resolved:

| Check | Condition |
|---|---|
| Memory source | Available (storage-backed) **or** explicitly absent (null-honest) — never fabricated |
| No fabricated continuity | If prior context is absent or corrupted, the packet must report absence, not invent history |
| Scope resolved | The operational domain and permission tier are declared before the packet is assembled |
| Runtime probe completed | `Probe(now)` has been called; result is attached to the packet |
| Packet marked non-sovereign | The assembled context packet carries `authority: NON_SOVEREIGN` |
| No mutation path opened | The airlock does not open a write path to the ledger, kernel, or sovereign schemas |

A packet that passes the airlock is admissible for routing. It is not yet truth. It becomes a candidate for admission only after gates, receipt, and reducer verdict.

Admission is conjunctive — no averaging:

$$\text{Admit}(x) = G_{\text{structural}}(x) \wedge G_{\text{traceability}}(x) \wedge G_{\text{receipt}}(x) \wedge G_{\text{chronos}}(x)$$

$$\text{If any } G_i = 0 \implies \text{Admit}(x) = 0$$

A beautiful shell cannot compensate for a missing gate. A strong metric cannot compensate for a broken receipt.

---

## 4. UI Phrase Mapping

UX language must map precisely to constitutional status. Ambiguity here is not aesthetic — it is an integrity failure.

| UI phrase | Constitutional meaning |
|---|---|
| `"memory restored"` | Storage-backed hydration succeeded; prior session log and epoch state loaded from `storage/` |
| `"local context loaded"` | Context packet assembled from available sources; scope resolved; packet ready for routing |
| `"presence active"` | Shell/runtime available — this is a **shell status only** |
| `"presence active (kernel)"` | Valid only after receipt + admission exist for the current session |

Formally:

$$\text{PresenceActive}_{\text{shell}} = 1$$

does **not** imply

$$\text{PresenceActive}_{\text{kernel}} = 1$$

unless bridged by receipt and admission.

The distinction must be surfaced in the UI, not hidden. An operator seeing "presence active" without qualification should understand this as shell availability, not as a claim about institutional truth.

---

## Closing Law

The Persona Entry Shell may render readiness, continuity, and presence, but only reducer-bound receipt chains may establish institutional truth.
