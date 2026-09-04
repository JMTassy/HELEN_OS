/-
HELEN_MINIMAL_CALCULUS_V0 · T3 — Replay Confluence.

PROVED HERE (machine-checked, no axioms, no sorry):
  SwapConnected step s₀ ℓ₁ ℓ₂ → replay step s₀ ℓ₁ = replay step s₀ ℓ₂
i.e. confluence under any finite chain of adjacent strongly-independent swaps.

DELIBERATELY OPEN (stated as a hypothesis, never an axiom, nothing smuggled):
  the combinatorial fact that any two linear extensions of a finite causal
  poset — with strong independence holding at every swap point encountered —
  are SwapConnected. This is the trace-theory / adjacent-transposition
  argument; it must be formalized, not assumed. Until then, T3 is delivered
  in conditional form: LinExt-connectivity ⇒ full confluence.
-/
import Hmc.Independence

namespace HMC

universe u v
variable {State : Type u} {Receipt : Type v}

/-- One adjacent swap of two receipts, with strong independence witnessed at
the exact replay point where the swap happens. -/
inductive AdjSwap (step : Step State Receipt) (s₀ : State) :
    List Receipt → List Receipt → Prop
  | mk (l₁ l₂ : List Receipt) (r q : Receipt)
      (indep : ∀ s', replay step s₀ l₁ = some s' → StrongIndependent step s' r q) :
      AdjSwap step s₀ (l₁ ++ r :: q :: l₂) (l₁ ++ q :: r :: l₂)

/-- Finite chains of adjacent swaps. -/
inductive SwapConnected (step : Step State Receipt) (s₀ : State) :
    List Receipt → List Receipt → Prop
  | refl (l : List Receipt) : SwapConnected step s₀ l l
  | cons {l₁ l₂ l₃ : List Receipt} :
      AdjSwap step s₀ l₁ l₂ → SwapConnected step s₀ l₂ l₃ →
      SwapConnected step s₀ l₁ l₃

/-- T3 (proved core): replay is invariant along any chain of adjacent
strongly-independent swaps. -/
theorem replay_confluence_of_swapConnected
    (step : Step State Receipt) (s₀ : State) {l₁ l₂ : List Receipt}
    (h : SwapConnected step s₀ l₁ l₂) :
    replay step s₀ l₁ = replay step s₀ l₂ := by
  induction h with
  | refl l => rfl
  | cons hswap _ ih =>
    cases hswap with
    | mk L₁ L₂ r q indep =>
      exact (replay_adjacent_swap step s₀ L₁ L₂ r q indep).trans ih

/-- T3 (conditional global form): if every pair of linear extensions of the
causal order is swap-connected — the OPEN combinatorial lemma — then replay
is independent of the chosen serialization. The hypothesis is explicit;
nothing is assumed silently. -/
theorem replay_confluence_of_linExt_connectivity
    (step : Step State Receipt) (s₀ : State)
    (LinExt : List Receipt → Prop)
    (connectivity : ∀ {l₁ l₂ : List Receipt},
      LinExt l₁ → LinExt l₂ → SwapConnected step s₀ l₁ l₂)
    {l₁ l₂ : List Receipt} (h₁ : LinExt l₁) (h₂ : LinExt l₂) :
    replay step s₀ l₁ = replay step s₀ l₂ :=
  replay_confluence_of_swapConnected step s₀ (connectivity h₁ h₂)

end HMC
