/-
HELEN_MINIMAL_CALCULUS_V0 · T3 Global (L4) — composition of the earned layers.

  L1/L2 (Independence, T3_ReplayConfluence): SwapConnected ⇒ replay equal.
  L3    (Poset): Perm + Compat + irrefl ⇒ PConnected (pure combinatorics).
  L4    (here): PConnected ⇒ SwapConnected, under an independence hypothesis.

SCOPE — stated exactly, nothing smuggled: the bridge uses STATE-UNIFORM
independence (incomparable pairs are strongly independent at EVERY state).
This is stronger than the state-indexed `r #ₛ q`. The state-indexed global
theorem (independence required only at the states actually reached along the
swap chain) remains OPEN — it needs reachability tracking through L3's
induction. L4 below is therefore: GLOBAL T3 UNDER UNIFORM INDEPENDENCE.
-/
import Hmc.T3_ReplayConfluence
import Hmc.Poset

namespace HMC

universe u v
variable {State : Type u} {Receipt : Type v}

/-- Pure order-swaps become state-anchored swaps when incomparable pairs are
strongly independent at every state. -/
theorem swapConnected_of_pconnected
    (step : Step State Receipt) (s₀ : State) (prec : Receipt → Receipt → Prop)
    (huniform : ∀ (s : State) (r q : Receipt),
      Incomp prec r q → StrongIndependent step s r q)
    {l₁ l₂ : List Receipt} (h : PConnected prec l₁ l₂) :
    SwapConnected step s₀ l₁ l₂ := by
  induction h with
  | refl l => exact SwapConnected.refl l
  | cons hs _ ih =>
    cases hs with
    | mk L₁ L₂ r q hrq =>
      exact SwapConnected.cons
        (AdjSwap.mk L₁ L₂ r q (fun s' _ => huniform s' r q hrq)) ih

/-- L4 — Global T3 (uniform-independence form): any two order-compatible
enumerations of the same receipts replay to the same result. -/
theorem replay_confluence_global
    (step : Step State Receipt) (s₀ : State) (prec : Receipt → Receipt → Prop)
    (hirr : ∀ x, ¬ prec x x)
    (huniform : ∀ (s : State) (r q : Receipt),
      Incomp prec r q → StrongIndependent step s r q)
    {l₁ l₂ : List Receipt} (hperm : l₁.Perm l₂)
    (h₁ : Compat prec l₁) (h₂ : Compat prec l₂) :
    replay step s₀ l₁ = replay step s₀ l₂ :=
  replay_confluence_of_swapConnected step s₀
    (swapConnected_of_pconnected step s₀ prec huniform
      (pconnected_of_perm_compat hirr hperm h₁ h₂))

end HMC
