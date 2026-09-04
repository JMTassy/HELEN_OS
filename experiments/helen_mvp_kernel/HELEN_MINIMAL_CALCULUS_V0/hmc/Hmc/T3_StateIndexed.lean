/-
HELEN_MINIMAL_CALCULUS_V0 · T3 State-Indexed (L4′).

Strengthens L4: independence is required ONLY
  (a) at states reachable from s₀ by replaying an ORDER-COMPATIBLE prefix
      whose elements come from the actual receipt set, and
  (b) for receipt pairs drawn from that same set.

This is where the permutation theorem meets the real kernel: `r #ₛ q` is
state-indexed, and the hypothesis now quantifies over exactly the states a
compatible execution can inhabit — not over an abstract universe of states.

Key facts making this sound (proved in Poset.lean):
  · PSwap preserves Perm      — intermediate lists stay enumerations of the set
  · PSwap preserves Compat    — intermediate lists stay order-compatible
  hence every prefix at which the swap lemma invokes independence is a
  compatible prefix over the ground set, i.e. covered by (a)+(b).
-/
import Hmc.T3_Global

namespace HMC

universe u v
variable {State : Type u} {Receipt : Type v}

/-- Independence demanded only at compatibly-reachable states, only for
receipts of the ground set. -/
def ReachablyIndependent (step : Step State Receipt) (s₀ : State)
    (prec : Receipt → Receipt → Prop) (ground : List Receipt) : Prop :=
  ∀ (p : List Receipt) (s' : State) (r q : Receipt),
    (∀ x ∈ p, x ∈ ground) → Compat prec p →
    replay step s₀ p = some s' →
    r ∈ ground → q ∈ ground → Incomp prec r q →
    StrongIndependent step s' r q

/-- Bridge (state-indexed): a pure swap chain on a compatible enumeration of
`ground` yields a state-anchored swap chain, using independence only where
the replay actually stands. -/
theorem swapConnected_of_pconnected_reachable
    (step : Step State Receipt) (s₀ : State)
    (prec : Receipt → Receipt → Prop) (ground : List Receipt)
    (hreach : ReachablyIndependent step s₀ prec ground) :
    ∀ {l₁ l₂ : List Receipt}, PConnected prec l₁ l₂ →
      Compat prec l₁ → l₁.Perm ground →
      SwapConnected step s₀ l₁ l₂ := by
  intro l₁ l₂ h
  induction h with
  | refl l => intro _ _; exact SwapConnected.refl l
  | @cons m₁ m₂ m₃ hswap _ ih =>
    intro hc hperm
    cases hswap with
    | mk A B r q hrq =>
      have hswap' : PSwap prec (A ++ r :: q :: B) (A ++ q :: r :: B) :=
        PSwap.mk A B r q hrq
      have hc₂ : Compat prec (A ++ q :: r :: B) := Compat.of_pswap hswap' hc
      have hperm₂ : (A ++ q :: r :: B).Perm ground :=
        hswap'.perm.symm.trans hperm
      have hadj : AdjSwap step s₀ (A ++ r :: q :: B) (A ++ q :: r :: B) := by
        refine AdjSwap.mk A B r q ?_
        intro s' hs
        have hAc : Compat prec A := (List.pairwise_append.mp hc).1
        have hmemA : ∀ x ∈ A, x ∈ ground := fun x hx =>
          hperm.mem_iff.mp (List.mem_append_left _ hx)
        have hrg : r ∈ ground :=
          hperm.mem_iff.mp (List.mem_append_right _ (List.mem_cons_self ..))
        have hqg : q ∈ ground :=
          hperm.mem_iff.mp (List.mem_append_right _
            (List.mem_cons_of_mem r (List.mem_cons_self ..)))
        exact hreach A s' r q hmemA hAc hs hrg hqg hrq
      exact SwapConnected.cons hadj (ih hc₂ hperm₂)

/-- L4′ — Global T3, state-indexed form: replay is serialization-independent
when incomparable pairs of the ACTUAL receipt set are strongly independent at
every COMPATIBLY-REACHABLE state. Strictly weaker hypothesis than L4's
uniform independence; the uniform theorem is a special case. -/
theorem replay_confluence_global_stateIndexed
    (step : Step State Receipt) (s₀ : State)
    (prec : Receipt → Receipt → Prop)
    (hirr : ∀ x, ¬ prec x x)
    {l₁ l₂ : List Receipt}
    (hreach : ReachablyIndependent step s₀ prec l₁)
    (hperm : l₁.Perm l₂)
    (h₁ : Compat prec l₁) (h₂ : Compat prec l₂) :
    replay step s₀ l₁ = replay step s₀ l₂ :=
  replay_confluence_of_swapConnected step s₀
    (swapConnected_of_pconnected_reachable step s₀ prec l₁ hreach
      (pconnected_of_perm_compat hirr hperm h₁ h₂) h₁ (List.Perm.refl l₁))

/-- Sanity: the uniform hypothesis implies the reachable one — L4 is a
corollary of L4′. -/
theorem reachablyIndependent_of_uniform
    (step : Step State Receipt) (s₀ : State)
    (prec : Receipt → Receipt → Prop) (ground : List Receipt)
    (huniform : ∀ (s : State) (r q : Receipt),
      Incomp prec r q → StrongIndependent step s r q) :
    ReachablyIndependent step s₀ prec ground :=
  fun _ s' r q _ _ _ _ _ hrq => huniform s' r q hrq

end HMC
