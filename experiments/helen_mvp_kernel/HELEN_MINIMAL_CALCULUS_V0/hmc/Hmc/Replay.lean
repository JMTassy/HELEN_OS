/-
HELEN_MINIMAL_CALCULUS_V0 · Replay — partial fold of receipts over a state.
UNDEFINED is inside the semantics (Option), not bolted on by a harness.
-/
import Hmc.Core

namespace HMC

universe u v
variable {State : Type u} {Receipt : Type v}

/-- Replay a list of receipts from a state. Any inadmissible receipt aborts
the whole replay with `none`. -/
def replay (step : Step State Receipt) : State → List Receipt → Option State
  | s, [] => some s
  | s, r :: rs => (step s r).bind (fun s' => replay step s' rs)

@[simp] theorem replay_nil (step : Step State Receipt) (s : State) :
    replay step s [] = some s := rfl

@[simp] theorem replay_cons (step : Step State Receipt) (s : State) (r : Receipt)
    (rs : List Receipt) :
    replay step s (r :: rs) = (step s r).bind (fun s' => replay step s' rs) := rfl

/-- Replay distributes over append via `Option.bind`. -/
theorem replay_append (step : Step State Receipt) :
    ∀ (l₁ : List Receipt) (s : State) (l₂ : List Receipt),
      replay step s (l₁ ++ l₂)
        = (replay step s l₁).bind (fun s' => replay step s' l₂)
  | [], _, _ => rfl
  | r :: rs, s, l₂ => by
    simp only [List.cons_append, replay_cons]
    cases h : step s r with
    | none => rfl
    | some s' => exact replay_append step rs s' l₂

end HMC
