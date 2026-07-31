# CCC_SAFETY — propriétés de sûreté & théorèmes
🟣 PROPOSAL · authority:false · Niveau 1. Dérivés de CCC_CORE (A1-A4), CCC_TYPES, CCC_SEMANTICS.
Chaque théorème: énoncé + esquisse. Les preuves rigoureuses suivront la stabilisation des définitions.

## Propriétés de sûreté (à démontrer, chacune = test candidat)
NoSelfAuthorization · NoSelfCertification · NoDirectHypothesisAdmission · NoHistoryErasure ·
Replayability · ProvenancePreservation · LawPresence.

## T1 — Non-collapsabilité
Énoncé: s'il n'existe aucun morphisme A→B dans le graphe des transitions, alors A ≢_I B.
Esquisse: par A4 (stratification) les types sont distincts par construction; l'identification n'est
possible que via un morphisme (CCC_CORE §graphe). Absence de morphisme ⇒ aucun chemin d'identification
⇒ ≢. Corollaire: Proposal ≢ Admission (pas de flèche directe), Receipt ≢ Truth (verify() ne produit
qu'un VerifiedReceipt, jamais Truth).

## T2 — Préservation de provenance
Énoncé: si x→y est une transition valide, alors Prov(y) ⊇ Prov(x).
Esquisse: par A3 (traçabilité) toute transition émet un reçu incluant la référence de son antécédent;
la provenance est monotone croissante le long de tout chemin. Conséquence: NoHistoryErasure — aucune
transition ne peut réduire Prov (sinon elle violerait A3, donc n'est pas dans le langage).

## T3 — Non-souveraineté
Énoncé: aucun objet ne peut produire une autorisation portant sur lui-même; pas de boucle
Authority→Authority sans médiation externe.
Esquisse: authorize() exige (Decision, PermissionRule) où PermissionRule est externe à l'émetteur
(A2); une auto-application fournirait la règle depuis l'émetteur ⇒ signature interdite (CCC_TYPES:
NoSelfAuthorization). Idem verify() interdit self(Action)→VerifiedReceipt (NoSelfCertification).
Formalise les invariants NS1-NS5.

## T4 — Rejouabilité
Énoncé: Reducer(R₁) = Reducer(R₂) dès que R₁ = R₂ (suites de reçus identiques → même état admis).
Esquisse: le reducer est une fonction pure des reçus ordonnés (A1: pas d'entrée cachée hors packet/
reçus; A3: chaque étape est un reçu). Déterminisme ⇒ même entrée, même sortie. Base de la
contestabilité rejouable.

## T5 — Monotonie
Énoncé: l'ajout de preuves COMPATIBLES n'invalide pas une admission déjà obtenue.
Esquisse: une admission est indexée par (loi, version, chaîne de preuve) — ADMITTED≠TRUE. Une preuve
compatible étend E sans retirer d'élément de la chaîne existante; la chaîne reste valide sous sa
version. (Une preuve CONTRADICTOIRE, elle, déclenche contest()→Contested, pas une invalidation
silencieuse — c'est un nouvel événement typé, jamais une réécriture.)

## Le problème mathématique central (rappel, CCC_SEMANTICS)
K*_T = arg min |K| s.t. Correct(K,T). MCP-DECISION: ∃ packet correct de taille ≤ k ? — définir avant
de promettre une classe (parenté set-cover/hitting-set; glouton ln n comme compilateur pratique).

---
# V0.1 — CORRECTIONS (revue mathématique, 2026-08-01). Les T1-T5 ci-dessus sont SUPERSEDED, conservés
# pour la lignée (T5-monotonie du ledger appliquée à nous-mêmes). Les vrais théorèmes visés:

## Préalable: trois systèmes de types, pas une chaîne linéaire
ÉPISTÉMIQUE {Observed, Inferred, Hypothetical, Contested, Verified} · INSTITUTIONNEL {Proposal,
Decision, Permission, Admission} · OPÉRATIONNEL {ActionAttempt, ProviderReceipt, WitnessVerdict, Outcome}.
Objet = produit: x : Claim⟨EpistemicStatus, InstitutionalStatus, Classification⟩.
Une Decision n'est PAS épistémiquement supérieure à une Hypothesis; une Permission n'est PAS une
assertion plus vraie. L'ancienne chaîne unique confondait les niveaux.

## Structure: système de transitions étiquetées TYPÉ (la catégorie se dérive après)
𝔥 = (Q, Λ, →), Q états institutionnels, Λ événements typés λ=(actor, role, capability, evidence,
timestamp, hash), q —λ→ q' transition admissible. Contexte de capacité LINÉAIRE/affine (une permission
bornée à une opération n'est pas réutilisable). Catégorie = objets:états · morphismes:traces valides ·
composition:concaténation · identité:trace vide — construite SECONDAIREMENT.

## Théorèmes visés (conditionnels, à prouver)
T1 SUBJECT REDUCTION — Γ⊢q:ValidState ∧ q→q' ⇒ Γ⊢q':ValidState. (remplace l'ancienne non-collapse
   par une SÉPARATION DES TYPES: Γ⊢x:A ∧ A⋠B ⇒ Γ⊬x:B, où ≤ est la coercion autorisée; Proposal⋠Admission.)
T2 NO SILENT ADMISSION — Proposal(x)∧Admitted(x) ⇒ ∃ d,p,a,r,w: la trace contient Decision(d),
   Permission(p), Action(a), Receipt(r), Witness(w) typés reliés. (Le vrai contenu de "pas de flèche directe".)
T3 PROVENANCE REACHABILITY — Admitted(x) ⇒ ∃s∈𝒮: x⤳s. (remplace Prov(y)⊇Prov(x), faux sous
   abstraction/résumé, par: la provenance est INDIRECTE mais RÉCUPÉRABLE — clôture transitive Prov*.)
T4 REPLAY DETERMINISM — canon(R₁)=canon(R₂) ⇒ Reducer_v(q₀,R₁)=Reducer_v(q₀,R₂), sous: reducer
   déterministe · schémas versionnés · ordre canonique · pas d'horloge système · pas d'I/O cachée ·
   mêmes règles v · même q₀. (La version v fait partie de l'identité de la réduction.)
T5 AUTHORITY NON-AMPLIFICATION — Authority(q') ⊆ Authority(q) ∪ ExplicitGrants; et ∀c∈Sacred:
   CanGrant(a,a,c)=False (issuer≠beneficiary pour les capacités sensibles). (remplace "pas de cycle".)
T6 CLEARANCE NON-INTERFERENCE — q₁≡_c q₂ ⇒ Project_c(q₁)=Project_c(q₂). Non-interférence
   informationnelle: rien au-dessus de la clearance ne fuit dans chemins/snippets/compteurs. Théorème
   central du Sacred Kernel.

## Monotonie corrigée (l'ancienne T5 était dangereuse)
Ledger_t ⊆ Ledger_{t+1} (l'histoire ne disparaît pas) · Beliefs_t ⊄ Beliefs_{t+1} (croyances
NON-MONOTONES: révision possible) · Admitted_t(x) ⇒ HistoricalRecord_{t+1}(x) (même réfuté après,
l'admission passée n'est pas effacée). HELEN = révision de croyances non-monotone + journal monotone.
