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
