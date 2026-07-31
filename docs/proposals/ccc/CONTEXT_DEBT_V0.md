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
