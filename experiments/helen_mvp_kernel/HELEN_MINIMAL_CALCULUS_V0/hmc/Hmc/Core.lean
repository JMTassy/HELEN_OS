/-
HELEN_MINIMAL_CALCULUS_V0 · Core — partial transition semantics.
No HELEN in this file: no Agent, no LLM, no Authority, no Garden.
Only states, receipts, partial steps, admissibility, strong local independence.
NON_SOVEREIGN · authority=false · this file is mathematics, not doctrine.
-/

namespace HMC

universe u v

/-- A partial transition function: applying a receipt to a state may fail. -/
abbrev Step (State : Type u) (Receipt : Type v) := State → Receipt → Option State

variable {State : Type u} {Receipt : Type v}

/-- `Admissible step s r`: the receipt `r` is applicable at state `s`. -/
def Admissible (step : Step State Receipt) (s : State) (r : Receipt) : Prop :=
  ∃ s', step s r = some s'

/-- Strong local independence `r #ₛ q` at state `s`.

Admissibility of BOTH orders is part of the definition (C1 is folded in),
together with commutation of the results (C2). Independence is indexed by the
state: `r #ₛ q` at `s₀` does not imply `r #ₛ q` at some later `s₇`. -/
def StrongIndependent (step : Step State Receipt) (s : State) (r q : Receipt) : Prop :=
  ∃ sr sq srq sqr,
    step s r = some sr ∧
    step s q = some sq ∧
    step sr q = some srq ∧
    step sq r = some sqr ∧
    srq = sqr

end HMC
