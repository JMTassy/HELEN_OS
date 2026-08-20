<!-- authority=false · a spec/architecture map, not a ruling. Palette rule (CLAUDE.md): 🟢 = ADMITTED only,
     never "successfully written". This card marks nodes' STATE-COLOR separately from whether they are
     EXECUTABLE (test-green in the non-sovereign sandbox). Executable ≠ admitted ≠ true. -->

# HELEN OS V1 — FULL COLOR WULMOJI TREE (frozen)
status = 🟡 sealed (hash-locked; contextual alias: spec/frozen) · authority=false · canon=false

## Load-bearing color law
```
COLOR = licensed state projection ≠ truth        Color(x) ⇏ Truth(x)
COLOR = canonical state          LABEL = contextual rendering
label variation ⇏ state mutation     Alias(x) ≠ Reassignment(x)     ΔVisualConstitution = 0
```
Canonical SOT palette UNCHANGED (repo CLAUDE.md, one-meaning-per-color). Relay terms are **contextual
aliases**, NOT reassignments — the color keeps its single committed sense; only the vocabulary varies by view:
`⚫ unknown · 🔵 observed · 🟣 claim (alias: candidate) · 🟢 admitted · 🔴 breach (alias: rejected) · ⚪ replayable ·`
`🟡 sealed (alias: spec/frozen) · 🟠 review (alias: hold)`
No color means "true" by itself. Green is admitted, not "done". No CLAUDE.md palette mutation.

## The tree
```
                              🌈 HELEN OS V1
                 ╔═════════════════╪═════════════════╗
                 ║          UNTRUSTED WORLD          ║
                 ║   🧠 Qwen   🧠 Gemma   👁 Vision   ║
                 ║   📈 TimesFM  ∀ Prover  🔎 Search  ║
                 ║   🐝 Goblins   🧠 Human cognition  ║
                 ╚═════════════════╪═════════════════╝
                                   ▼
                           🟣 CandidateEnvelope
                    (hypotheses · observations · plans · derivations · attacks)
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
               🟣 Proof Frontier            🧬 Provenance (candidate roots)
                    └──────────────┬──────────────┘
═══════════════════════════════════╪══════════════════════════════════
                              TRUST SEAM
═══════════════════════════════════╪══════════════════════════════════
                                   ▼
                              🟡 WUL SPEC ──Compile──▶ 🟡 TYPED IR
                                   │           TYPE / REQUIRE / FORBID / TRANSITION
                                   ▼
                                  ⚖️ Γ  (admission semantics)          ✔ executable
                         ┌─────────┼─────────┐
                         ▼         ▼         ▼
                      🔴 DENY    🟠 HOLD    🟢 ADMIT
                                             ▼
                                    👑 Scoped Capability             ✔ executable (HMAC-modeled)
                                     action/resource/scope · policy/version/nonce · proposal_hash
                                             ▼
                                         ⚡ ATTEMPT                    ✔ executable
                                             ▼
                                         🔵 OBSERVE
                                             ▼
                                       🔍 VERIFY EFFECT               ← relabeled (no ✅)
                                      ┌──────┼──────┐
                                      ▼      ▼      ▼
                          🔵 VERIFIED_OBSERVED  🟠 UNRESOLVED  🔴 FAILED
                                      ▼   (only if the rule is satisfied)
                                    📜 EVENT ─▶ 🔗 LEDGER ─▶ 🔁 REPLAY ─▶ ⚪ GOVERNED STATE   ✔ executable (fold)
```
Even a successful verification stays `🔵 VERIFIED_OBSERVED` — a licensed observation, not absolute truth.

## Two most important separations
```
NIM ≠ Γ           NIM ATTACKS the seam · Γ ENFORCES it            ✔ executable (nim_v0_1/v0_2)
ΔF* > 0 ⇏ ΔAuthority > 0     epistemic gain ≠ institutional gain
```
NIM sits sideways, not inside the kernel:
```
        🧪 NIM ──▶ WRITE · FLOW · RELEASE ──▶ attack TRUST SEAM
```
Proof Frontier orthogonal: `🧠 → 🟣 derivation → 🧪 validate → 🟣 Proof Frontier↑`  but  `Proof Frontier↑ ↛ 👑`.

## Every cognition substrate is ONE institutional type
```
G_i : Context → CandidateEnvelope         (Qwen · Gemma · Goblins · Human · Prover · Vision)
Qwen "AUTHORIZED" → 🟣 candidate text      100 goblins agree → 🟣 candidate consensus
🟣 ↛ 👑    🟣 ↛ ⚡    🟣 ↛ 📜    🟣 ↛ 🕯
```

## Compact kernel + master law
```
🧠 → 🟣 → 🟡 → ⚖️ ─┬─ 🔴
                    ├─ 🟠
                    └─ 🟢 → 👑 → ⚡ → 🔵 → 📜 → 🔗 → 🔁 → ⚪

Search∞ ⟂ Promotion        ∂|𝒞|/∂Q_cognition > 0        ∂|𝒫|/∂Q_cognition = 0
```
🧠 cognition may grow arbitrarily powerful; ⚖️ the seam stays small, typed, testable, replayable.

## Executable vs doctrine (honesty legend — this session's on-disk state)
- **✔ executable, test-green (non-sovereign sandbox):** Γ, Scoped Capability, ATTEMPT/OBSERVE/VERIFY,
  EVENT/LEDGER/REPLAY fold, 7 bypass mutants dead → `HELEN_VERTICAL_SLICE_V0` (6/6 props, pytest 31).
  NIM WRITE/FLOW/RELEASE → `nim_v0_1` (1×9) + `nim_v0_2` (relational NI, strict-improvement).
- **🟣 candidate / doctrine (not yet executable here):** WUL SPEC→IR compiler, Proof Frontier, full policy
  reconstruction across many event types, external-effect verification against real services.
- `✔ executable ≠ 🟢 admitted ≠ true`. Installation toward the sovereign kernel is MAYOR-routed.

*HELEN OS — created by JM Tassy.*
