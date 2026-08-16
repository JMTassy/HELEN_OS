/-
HELEN_MINIMAL_CALCULUS_V0 · Poset — T-004 (L3): pure finite-order combinatorics.
NO replay semantics, NO HELEN vocabulary. Only: a relation, incomparability,
adjacent swaps, and connectivity of compatible enumerations.

Target: two order-compatible enumerations of the same multiset are connected
by adjacent swaps of incomparable elements.
-/

namespace HMC

universe u
variable {α : Type u}

/-- Incomparability under a strict precedence relation. -/
def Incomp (prec : α → α → Prop) (r q : α) : Prop :=
  ¬ prec r q ∧ ¬ prec q r

theorem Incomp.symm {prec : α → α → Prop} {r q : α}
    (h : Incomp prec r q) : Incomp prec q r :=
  ⟨h.2, h.1⟩

/-- One adjacent swap of two incomparable elements (pure lists, no state). -/
inductive PSwap (prec : α → α → Prop) : List α → List α → Prop
  | mk (l₁ l₂ : List α) (r q : α) (h : Incomp prec r q) :
      PSwap prec (l₁ ++ r :: q :: l₂) (l₁ ++ q :: r :: l₂)

theorem PSwap.symm {prec : α → α → Prop} {l l' : List α}
    (h : PSwap prec l l') : PSwap prec l' l := by
  cases h with
  | mk l₁ l₂ r q hrq => exact PSwap.mk l₁ l₂ q r hrq.symm

/-- Finite chains of incomparable adjacent swaps. -/
inductive PConnected (prec : α → α → Prop) : List α → List α → Prop
  | refl (l : List α) : PConnected prec l l
  | cons {l₁ l₂ l₃ : List α} :
      PSwap prec l₁ l₂ → PConnected prec l₂ l₃ → PConnected prec l₁ l₃

theorem PConnected.trans {prec : α → α → Prop} {l₁ l₂ l₃ : List α}
    (h₁ : PConnected prec l₁ l₂) (h₂ : PConnected prec l₂ l₃) :
    PConnected prec l₁ l₃ := by
  induction h₁ with
  | refl _ => exact h₂
  | cons hs _ ih => exact PConnected.cons hs (ih h₂)

theorem PConnected.single {prec : α → α → Prop} {l₁ l₂ : List α}
    (h : PSwap prec l₁ l₂) : PConnected prec l₁ l₂ :=
  PConnected.cons h (PConnected.refl _)

theorem PConnected.symm {prec : α → α → Prop} {l₁ l₂ : List α}
    (h : PConnected prec l₁ l₂) : PConnected prec l₂ l₁ := by
  induction h with
  | refl _ => exact PConnected.refl _
  | cons hs _ ih => exact ih.trans (PConnected.single hs.symm)

/-- Swaps in the tail lift through a common head. -/
theorem PSwap.cons_lift {prec : α → α → Prop} {t t' : List α} (a : α)
    (h : PSwap prec t t') : PSwap prec (a :: t) (a :: t') := by
  cases h with
  | mk l₁ l₂ r q hrq => exact PSwap.mk (a :: l₁) l₂ r q hrq

theorem PConnected.cons_lift {prec : α → α → Prop} {t t' : List α} (a : α)
    (h : PConnected prec t t') : PConnected prec (a :: t) (a :: t') := by
  induction h with
  | refl _ => exact PConnected.refl _
  | cons hs _ ih => exact PConnected.cons (hs.cons_lift a) ih

/-- Bubble: an element incomparable with everything before it can be moved to
the front by adjacent swaps. -/
theorem bubble {prec : α → α → Prop} (a : α) :
    ∀ (u v : List α), (∀ x ∈ u, Incomp prec x a) →
      PConnected prec (u ++ a :: v) (a :: (u ++ v))
  | [], v, _ => PConnected.refl _
  | x :: u, v, hu => by
    have hxa : Incomp prec x a := hu x (List.mem_cons_self ..)
    have hrec : PConnected prec (u ++ a :: v) (a :: (u ++ v)) :=
      bubble a u v (fun y hy => hu y (List.mem_cons_of_mem x hy))
    have step1 : PConnected prec (x :: (u ++ a :: v)) (x :: a :: (u ++ v)) :=
      hrec.cons_lift x
    have step2 : PSwap prec (x :: a :: (u ++ v)) (a :: x :: (u ++ v)) :=
      PSwap.mk [] (u ++ v) x a hxa
    exact step1.trans (PConnected.single step2)

/-- Order-compatibility of an enumeration: no later element precedes an
earlier one. This is the list form of "linear extension". -/
def Compat (prec : α → α → Prop) (l : List α) : Prop :=
  l.Pairwise (fun x y => ¬ prec y x)

/-- T-004 (L3): two order-compatible enumerations of the same elements are
connected by adjacent swaps of incomparable elements.
Hypotheses: `prec` irreflexive; permutation; both compatible. -/
theorem pconnected_of_perm_compat {prec : α → α → Prop}
    (hirr : ∀ x, ¬ prec x x) :
    ∀ {l₁ l₂ : List α}, l₁.Perm l₂ →
      Compat prec l₁ → Compat prec l₂ → PConnected prec l₁ l₂
  | [], l₂, hperm, _, _ => by
    have : l₂ = [] := hperm.symm.eq_nil
    subst this; exact PConnected.refl _
  | a :: t₁, l₂, hperm, h₁, h₂ => by
    -- a occurs in l₂; split at (an occurrence of) a
    have ha : a ∈ l₂ := hperm.mem_iff.mp (List.mem_cons_self ..)
    obtain ⟨u, v, huv⟩ := List.append_of_mem ha
    subst huv
    -- every element before a in l₂ is incomparable with a
    have hincomp : ∀ x ∈ u, Incomp prec x a := by
      intro x hxu
      by_cases hxa : x = a
      · subst hxa; exact ⟨hirr x, hirr x⟩
      · constructor
        · -- x before a in l₂ and l₂ compatible ⇒ ¬ prec a x is about (a,x);
          -- here we need ¬ prec x a: x sits in l₁'s tail (perm), a before it.
          have hx1 : x ∈ a :: t₁ := hperm.symm.mem_iff.mp
            (List.mem_append_left _ hxu)
          have hxt : x ∈ t₁ := by
            cases hx1 with
            | head => exact absurd rfl hxa
            | tail _ h => exact h
          exact (List.pairwise_cons.mp h₁).1 x hxt
        · -- compat of l₂ = u ++ a :: v gives ¬ prec a x for x ∈ u
          have := List.pairwise_append.mp h₂
          exact this.2.2 x hxu a (List.mem_cons_self ..)
    -- bubble a to the front of l₂
    have hbub : PConnected prec (u ++ a :: v) (a :: (u ++ v)) :=
      bubble a u v hincomp
    -- tails are permutations
    have hperm' : t₁.Perm (u ++ v) := by
      have h1 : (a :: t₁).Perm (a :: (u ++ v)) :=
        hperm.trans List.perm_middle
      exact h1.cons_inv
    -- compatibility descends to the tails
    have h₁' : Compat prec t₁ := (List.pairwise_cons.mp h₁).2
    have h₂' : Compat prec (u ++ v) := by
      have hsub : (u ++ v).Sublist (u ++ a :: v) :=
        List.Sublist.append_left (List.sublist_cons_self a v) u
      exact h₂.sublist hsub
    have hrec : PConnected prec t₁ (u ++ v) :=
      pconnected_of_perm_compat hirr hperm' h₁' h₂'
    -- assemble: a :: t₁ ⇝ a :: (u ++ v) ⇝ u ++ a :: v
    exact (hrec.cons_lift a).trans hbub.symm

end HMC
