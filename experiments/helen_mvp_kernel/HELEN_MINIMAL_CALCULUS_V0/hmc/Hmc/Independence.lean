/-
HELEN_MINIMAL_CALCULUS_V0 · Independence — the atomic brick.
`replay_adjacent_swap`: swapping two adjacent, strongly-independent receipts
preserves replay. If this proof had been complicated, the definitions would
have been wrong.
-/
import Hmc.Replay

namespace HMC

universe u v
variable {State : Type u} {Receipt : Type v}

/-- The atomic lemma: an adjacent swap of receipts that are strongly
independent at the swap point preserves replay of the whole list.
Independence is required exactly at the state reached after the prefix —
nowhere else. -/
theorem replay_adjacent_swap (step : Step State Receipt)
    (s₀ : State) (l₁ l₂ : List Receipt) (r q : Receipt)
    (indep : ∀ s', replay step s₀ l₁ = some s' → StrongIndependent step s' r q) :
    replay step s₀ (l₁ ++ r :: q :: l₂) = replay step s₀ (l₁ ++ q :: r :: l₂) := by
  rw [replay_append, replay_append]
  cases hs : replay step s₀ l₁ with
  | none => rfl
  | some s' =>
    obtain ⟨sr, sq, srq, sqr, hr, hq, hrq, hqr, heq⟩ := indep s' hs
    show replay step s' (r :: q :: l₂) = replay step s' (q :: r :: l₂)
    rw [replay_cons, replay_cons, hr, hq]
    show replay step sr (q :: l₂) = replay step sq (r :: l₂)
    rw [replay_cons, replay_cons, hrq, hqr, heq]

end HMC
