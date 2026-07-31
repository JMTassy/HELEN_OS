# CCC_TYPES — système de types épistémiques
🟣 PROPOSAL · authority:false · Niveau 1. Le statut n'est pas une annotation: c'est un TYPE, la contrainte est calculatoire.

## Forme d'une assertion
Assertion<T,S> { content:T · epistemic:S · source_refs · provenance · confidence · context_packet_hash · created_at }
S ∈ { Observation, Derived, Hypothesis, Decision, Receipt, Admission, Verified, Contested, Unresolved, Rejected, Archived }.

## Fonctions bien typées (transitions permises)
derive    : Observation<T> → Derived<U>
infer     : Derived<T> → Hypothesis<U>
evaluate  : Hypothesis<T> × FrozenJudge → {Contested<T> | Verified<T>}   (anchor-cut requis)
authorize : Decision<T> × PermissionRule → Permission<T>
execute   : Permission<T> → Action<T>
receipt   : Action<T> → Receipt<T>
verify    : Receipt<T> × Gate → VerifiedReceipt<T>
admit     : VerifiedReceipt<T> × AdmissionRule × OperatorAuth → Admission<T>
contest   : *<T> × CounterEvidence → Contested<T>
refute    : *<T> × Falsifier → Rejected<T>            (le falsificateur est conservé)

## Signatures INEXISTANTES (erreurs de typage, pas règles documentaires)
admit : Hypothesis<T> → Admission<T>          ✗   (NoDirectHypothesisAdmission)
admit : Receipt<T> → Admission<T>             ✗   (verify() obligatoire d'abord)
authorize : Proposal<T> → Permission<T> sans PermissionRule ✗
verify : self(Action) → VerifiedReceipt       ✗   (NoSelfCertification)
* → * qui accroît le pouvoir de son propre émetteur ✗ (NoSelfAuthorization)
Une admission mal fondée NE COMPILE PAS.

## Invariants de type (dérivés des axiomes)
Hypothesis<T> ≠ Admission<T> · Receipt<T> ≠ Truth<T> · Permission<T> ≠ Action<T> ·
Action<T> ≠ Reality<T> · Evaluation<T> ≠ Correctness<T> · Custody<T> ≠ Verification<T>.

---
# V0.1 (2026-08-01): SÉPARER trois systèmes de types (épistémique/institutionnel/opérationnel) — ne
# pas les enfiler en une chaîne. x : Claim⟨EpistemicStatus, InstitutionalStatus, Classification⟩.
# Contexte de capacité LINÉAIRE/affine (permission bornée = non réutilisable):
#   Γ⊢d:Decision   Λ⊢ℓ:Lease(c,1)  ⊢  authorize(d,ℓ):Permission(c) ,  puis Λ'=Λ\{ℓ}.
# Séparation des types (remplace la non-collapse naïve): Γ⊢x:A ∧ A⋠B ⇒ Γ⊬x:B.
