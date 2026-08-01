# CONTEXT DEBT V0 — le mode d'échec émergent
🟣 PROPOSAL · authority:false · Niveau 1-2. Propriété mesurable révélée par ECAP.

## Définition
> La dette de contexte est l'écart accumulé entre ce qu'une institution a enregistré et ce que ses
> agents peuvent fiablement amener au moment de la décision.
Pas de l'ignorance — un OUBLI INSTITUTIONNEL SOUS MÉMOIRE NOMINALE: la règle existe quelque part,
mais son chemin opérationnel vers les futurs packets est faible, non documenté ou incohérent.
Chaîne d'échec: créé → mal classé → faiblement lié à la loi → rarement récupéré → absent à la décision.

## Vue formelle
K = savoir stocké · R = récupérable · P = présenté dans le packet actif · U = utilisé correctement.
  U ⊆ P ⊆ R ⊆ K.   Dette: D_c = K − U (portion opérationnellement pertinente de K qui n'atteint
répétitivement pas U). Corollaire contre-intuitif: |K|↑ peut faire ↓ la qualité si la couche
d'assemblage devient bruitée/périmée/contradictoire/opaque. Plus de documents ⇒ pires décisions possible.
stored ≢ retrievable ≢ selected ≢ presented ≢ understood ≢ applied.

## Sources de dette
orphaned rules · uncited summaries · duplicate doctrines · stale versions · unresolved contradictions ·
missing provenance · unclear authority · weak metadata · hidden exceptions · implicit institutional memory.

## Primitive: Context Debt Register (par loi/source/ancre)
{ object_id, required_for_tasks[], last_included_at, last_verified_at, version, conflicts[],
  orphan_risk, staleness_risk, context_debt_status:"OPEN|CLOSED" }

## La boucle d'apprentissage (pas de changement silencieux de vision du monde)
DECISION FAILURE → PACKET AUDIT → MISSING LAW/EVIDENCE DETECTED → CONTEXT DEBT RECORDED →
COMPILER POLICY UPDATED → FUTURE PACKETS IMPROVED. Le système apprend en améliorant le CHEMIN
gouverné entre mémoire et jugement, pas en mutant ses poids.
HELEN OS = ECAP + Context Debt Accounting + Non-Sovereign Action + Evidential Memory.

---
# V0.1 — MODÈLE D'OPÉRATEURS + THÉORÈME (revue math, 2026-08-01). Élève la métrique en théorie dynamique.

## Opérateurs (les ensembles deviennent des flèches)
ℛ:K→R (retrieval) · 𝒫:R→P (packet compiler = ECAP) · 𝒰:P→U (application décision).
Φ = 𝒰∘𝒫∘ℛ : K→U, endomorphisme du savoir institutionnel. Ouvre une théorie d'opérateurs.

## Dette comme fonctionnelle mesurable
D_c = μ(K) − μ(U), μ = mesure d'information. Choix ⇒ théories: μ=|·| (cardinalité) · μ=H (entropie) ·
μ=Σwᵢ𝟙ᵢ (importance pondérée) ⇒ D_c = Σwᵢ − Σ_{i∈U}wᵢ ⇒ optimisation.

## Système dynamique
K_{t+1}=K_t+ΔK_t · U_{t+1}=Φ_t(K_{t+1}) · D_t = μ(K_t)−μ(U_t). Questions: converge? explose? oscille?

## Contrôle: HELEN comme contrôleur
Φ_t=Φ(C_t) (C = politique du compilateur). Audit d'échec ⇒ C_{t+1}=G(C_t,D_t). Objectif: min_C D_t.

## THÉORÈME DE CONVERGENCE DE LA DETTE DE CONTEXTE (énoncé, hypothèses explicites)
Hyp: (H1) K_t fini · (H2) ℛ monotone · (H3) politique C améliorée monotonement · (H4) aucun savoir
vérifié retiré. Alors D_t décroît monotonement et D_t→D*. Si D*=0, toute loi vérifiée finit par
apparaître chaque fois qu'elle est requise. À PROUVER (esquisse: monotonie bornée ⇒ convergence;
D*=0 exige que G couvre chaque loi requise détectée par l'audit — lien à MCP-couverture).

## Abstraction plus profonde: DRIFT FUNCTIONAL général
Ce travail n'est pas "la mémoire" — c'est la DISTANCE ENTRE COUCHES SÉMANTIQUES.
Δ(A,B) = d(f_A, f_B), f = sémantique de la couche. Unifie sous un seul objet:
 Context Debt = Δ(K,U) · Implementation drift = Δ(Spec,Code) · Governance drift = Δ(Policy,Admission) ·
 Model drift = Δ(Reality,Prediction) · Doc drift = Δ(Doc,Impl).
Δ est ASYMÉTRIQUE (prémétrique): only_left = loi sans enforcement · only_right = enforcement sans loi.
La directionnalité PORTE l'information de gouvernance (≠ distance d'édition scalaire).

## Ce qui rendrait publiable (checklist honnête)
(1) modèle d'opérateurs K→R→P→U ✅ posé · (2) fonctionnelle de drift à propriétés claires ⏳ ·
(3) théorèmes monotonie/convergence sous hyp explicites ⏳ énoncés, preuves à faire ·
(4) algorithme d'estimation+réduction de D_c ⏳ (ECAP-loop = candidat) ·
(5) validation empirique sur repos réels ⏳ — **l'ablation LawPresence en cours EST le premier échantillon**
(quelles lois L0 sont load-bearing = quelles absences causent l'échec = première mesure de Δ(Policy,Admission)).
