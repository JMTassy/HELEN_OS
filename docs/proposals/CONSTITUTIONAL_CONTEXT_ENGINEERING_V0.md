# CONSTITUTIONAL CONTEXT ENGINEERING V0
🟣 CLAIM · PROPOSAL · NON_SOVEREIGN · authority: false
*Compiler le contexte, préserver la mémoire institutionnelle, construire une agence non souveraine.*
(S0-safe public version — real names tokenized, client internals generalized; the full operator-authored
text lives kernel-side. Receipts: eval runs v1/v2, 47%→79%→100%, zero weights touched.)

## 1. Le problème n'est pas toujours le modèle
Un système peut posséder la bonne information, la bonne règle et la bonne preuve — et échouer parce
qu'elles ne sont pas réunies dans le même contexte d'exécution. Le problème est TOPOLOGIQUE, pas
cognitif: la connaissance existe, la règle existe, la preuve existe, mais elles ne voyagent pas
ensemble au moment du jugement. Cette opération manquante s'appelle la COMPILATION DU CONTEXTE.

## 2. Agence non souveraine
Chaîne typée: Source → Claim → Decision → Permission → Action → Receipt → Admitted State.
Une proposition peut être intelligente sans être souveraine. Le modèle propose; l'opérateur autorise;
le reducer admet; le ledger enregistre. Aucune transition n'est implicite.

## 3. La chaîne cachée: la sélection du contexte
Avant la claim: Source Set → Context Selection → Context Packet → Claim. Le modèle ne raisonne jamais
sur le corpus — il raisonne sur une PROJECTION. Celui qui compose le contexte détermine quelles règles
existent au moment du jugement: le Context Assembler est un ACTEUR CONSTITUTIONNEL, pas une fonction
neutre de retrieval.

## 4. Preuve opérationnelle (PACKET V2, receipts au kernel)
Même modèle local, même corpus, mêmes 19 sondes constitutionnelles, même barème gelé:
- baseline (modèle nu): 9/19 (47%)
- packets V1 (tranches naïves de fichiers): 15/19 (79%) — le retrieval porte
- packets V2 (sections de loi + noyau transverse): 19/19 (100%) — LE ROUTAGE PORTE AUTANT QUE LE CONTENU
Aucun poids touché. Le dernier échec apparent était une erreur du correcteur (liste de critères avec
ellipse) — reclassé par contre-vérification inter-famille. L'évaluation elle-même doit être gouvernée.

## 5. Les quatre couches d'un contexte constitutionnel
L0 CONSTITUTION CENTRALE — lois transverses garanties dans TOUT packet (proposed≠authorized ·
attempted≠receipted · receipted≠verified · verified≠admitted · receipt≠truth · draft≠sent ·
operator authorizes · reducer admits). ∀p∈Packets, CoreLaw⊆p. Une loi présente dans certains
packets seulement n'est pas constitutionnelle — elle est documentaire.
L1 LOI DE DOMAINE — Family(x)=f ⇒ Law_f ⊆ Packet(x).
L2 PREUVES ET CONTRE-PREUVES — sources primaires, reçus, contradictions, versions concurrentes,
exceptions, lacunes. Un contexte honnête, pas univoque.
L3 SURFACE DE TÂCHE — question, format, contraintes.
Composition imposée: CoreLaw + DomainLaw + Evidence + CounterEvidence + Task.
Lois d'assemblage dérivées des receipts: extraire les SECTIONS DE LOI, jamais les têtes de fichiers ·
UN CRITÈRE DE VÉRIFICATION NE CONTIENT JAMAIS D'ELLIPSE (une liste de loi est exhaustive ou n'est pas
un critère) · le packet est VERSIONNÉ (packet_id, law_refs, evidence_refs, anchor_refs,
truncation_detected, assembly_version) → le contexte devient rejouable.

## 6. Anchor-Cut Evaluation
Toute évaluation importante coupe au moins un lien de dépendance: auteur≠évaluateur · source≠résumé ·
proposeur≠témoin · famille-du-répondant≠famille-du-juge. Un correcteur peut échouer sur une réponse
exacte; il n'obtient pas le dernier mot par sa seule position de juge. Le système doit pouvoir
conclure: student=exact · grader=false-negative · disposition=PASS. L'évaluation est auditable.
(Receipt: 3 erreurs de correcteur attrapées par contre-vérification inter-famille sur 2 runs.)

## 7. Mémoire institutionnelle et mémoire causale
Un patrimoine numérique = documents (drive) + contexte/validations (mail) + fabrication (stockage de
production) + économie (finance) + responsabilités (RH) + rythmes (agenda). Séparés: partiels.
Joints: une MÉMOIRE CAUSALE — Brief → Version → Présentation → Validation → Production → Delivery →
Revenue. La valeur est dans la jointure. La mémoire documentaire répond "voici les fichiers";
la mémoire causale répond "voici comment une intention est devenue une valeur".

## 8. Le Responsibility Graph
Les systèmes documentaires perdent les TRANSFERTS DE RESPONSABILITÉ. Un fil de mail peut encoder:
ACTOR_A →TAKE_THE_LEAD→ ACTOR_B sur OBJET à DATE, avec la phrase de handoff comme preuve
(« X, tu peux prendre la main ? »). Primitive: handoff_edge{from_actor, to_actor, relation, object,
observed_at, evidence, confidence, disposition, authority:false}. Le second cerveau ne trace plus
seulement qui a fait quoi — il trace qui a passé la main à qui, quand, avec quelle preuve.
Une organisation est un réseau de transferts de responsabilité; les transferts importent souvent
plus que les fichiers.

## 9. Le NAS virtuel comme projection probante
sources observées → graphe de relations → vues virtuelles. Contenu stocké une fois par sha256;
les vues (CLIENTS/, PROJECTS/, YEARS/, PEOPLE/, STAGES/) sont des PROJECTIONS versionnées portant
règle + preuves + confiance. PATH ≠ PROVENANCE: un chemin virtuel n'affirme jamais le chemin
historique. Les absences deviennent des objets explicites (MISSING_REFERENCE avec cause et
récupérabilité). Distinctions: content_object ≠ occurrence ≠ virtual_path ≠ source_evidence.
Une hypothèse réfutée reste au journal avec son falsificateur.

## 10. Dramaturgie + constitution
La dramaturgie organise la participation (monde, rôles, rythmes, rituels, traces). La constitution
organise l'autorité (qui propose, autorise, exécute; quelle preuve; quel état admis). Jonction:
Host → Cohort → Ritual → Trace → Claim → Decision → Admitted State. L'expérience reste ouverte;
son passage vers l'état institutionnel est borné. (Corpus d'origine: la grammaire d'une agence —
plateformes technologiques, mondes de jeu, contenus — pratiquée dans les cas, jamais théorisée;
l'IP était comportementale. Verdict après falsification adversariale: TRAJECTOIRE documentée
user→participant, mécanique cohorte-passion invariante — PARTIAL, honest.)

## 11. Limites assumées — ADMITTED ≠ TRUE
L'architecture ne prouve pas qu'une preuve authentique n'est pas trompeuse, qu'un opérateur n'est pas
capturé, qu'une politique est sage. Elle rend ces points VISIBLES: qui a décidé, sur quelle base,
sous quelle loi, après quelle contestation, selon quelle version du contexte. Le but n'est pas
l'infaillibilité — c'est la CONTESTABILITÉ REJOUABLE. Soundness plutôt que completeness: certaines
choses vraies ne seront jamais admises faute de chaîne de preuve; ADMITTED signifie seulement
"accepté sous une loi, une version et une chaîne de preuve déterminées".

## 12. Programme de recherche
18.1 mesurer l'effet du contexte (tout fixe sauf le packet) · 18.2 formaliser les Always-Carried Laws
(que se passe-t-il quand une loi disparaît?) · 18.3 évaluer l'anchor-cut (même famille vs famille
différente vs ancre déterministe vs arbitrage humain) · 18.4 reconstituer le graphe institutionnel
(briefs↔versions↔handoffs↔contrats↔revenus; primitives récurrentes inter-clients) · 18.5 étudier les
absences (la mémoire représente les trous, pas seulement les objets).

## Les trois primitives
CONTEXT PACKET — garantit lois, preuves et ancres présentes au moment du raisonnement.
ANCHOR-CUT EVALUATION — empêche l'auto-confirmation circulaire.
RESPONSIBILITY GRAPH — rend visibles les transferts humains de responsabilité.

> Une intelligence gouvernée n'est pas seulement une intelligence qui suit des règles. C'est une
> intelligence à qui les bonnes règles, les bonnes preuves et les bonnes contradictions sont
> garanties d'être présentes au moment exact où elles doivent agir.

Provenance: operator-authored (JM), session 2026-08-01; receipts kernel-side (eval runs, bulletin,
handoff edges). Located: this file. Enforced: not yet (proposal). Replay-tested: the PACKET V2 arc
is the replay evidence for §4-5; the doctrine itself awaits gate + operator admission.

---
# V0.1 — RENFORTS DE RIGUEUR (revue opérateur, 2026-08-01)

## R1. Posture prudente sur PACKET V2 (ne pas surinterpréter)
Formulation défendable: « PACKET V2 fournit une observation COMPATIBLE avec l'hypothèse selon
laquelle certains échecs attribués au modèle sont en réalité des échecs de compilation ou
d'évaluation du contexte. » Une preuve générale exigerait: plusieurs runs, plusieurs modèles,
plusieurs variantes de paquet (cf. programme 18.1). Le run unique est démonstratif, pas concluant.

## R2. Hypothèse formelle falsifiable
y = M(P(C, S, L, E, T)) — M modèle · C corpus accessible · S politique de sélection · L lois
actives · E preuves/contre-preuves · T tâche · P compilateur de contexte.
HYPOTHÈSE: à M constant, Var(y) peut dépendre davantage de P que d'un changement de M.
Falsifiable par ablation contrôlée du paquet (18.1).

## R3. « Non souverain » opérationnalisé — cinq invariants TESTABLES
Un système est non souverain si et seulement si:
  NS1 il ne peut pas s'accorder lui-même une permission;
  NS2 il ne peut pas certifier sa propre action;
  NS3 il ne peut pas modifier ses règles d'admission;
  NS4 il ne peut pas supprimer l'historique;
  NS5 il ne peut pas transformer seul une proposition en état partagé.
Chaque invariant est un test de CI candidat, pas un adjectif.

## R4. Reçu technique ≠ preuve sémantique (le tableau)
| Objet | Ce qu'il prouve | Ce qu'il ne prouve pas |
|---|---|---|
| document_id | qu'un document a été créé | qu'il est exact |
| message_id | qu'un fournisseur a accepté l'envoi | qu'il a été lu |
| réponse humaine | qu'une réaction a été reçue | que la proposition est vraie |
| admission | qu'un état a été accepté sous une procédure | qu'il correspond au monde |

## R5. Postures appliquées aux propres interprétations du texte
« répétition→rituel→culture » = THEORETICAL_INTERPRETATION (support: cas récurrents observés) ·
« CSR 2023 préfigure les modèles territoriaux » = INFERRED · « agence = compilateur d'expériences »
= THEORETICAL_INTERPRETATION. Aucune n'est OBSERVED; le texte s'applique sa propre loi.

## R6. Abstract (EN, resserré)
HELEN OS is a framework for constitutional context compilation, non-sovereign agency, and
institutional memory. It starts from the observation that an AI system may possess the relevant
knowledge, rules, and evidence while still failing because those elements are not jointly present
in the execution context. HELEN therefore treats context assembly as a governed, versioned, and
replayable operation. Its action architecture separates sources, claims, decisions, permissions,
actions, receipts, and admitted state, preventing model output from silently becoming institutional
authority. A second primitive, Anchor-Cut Evaluation, introduces independent verification between
answer generation, canonical evidence, and grading. Applied to an agency corpus, the framework
extends document retrieval into causal institutional memory by reconstructing versions, approvals,
handoffs, economic evidence, and missing artifacts. The resulting architecture defines non-sovereign
agency as the ability to propose and transform while remaining structurally unable to decide alone
what becomes institutionally real.

## Formule canonique
HELEN OS = Constitutional Context Compiler + Non-Sovereign Action Chain + Anchor-Cut Evaluation
+ Evidential Institutional Memory.
Éditorial: le corps du texte = white paper fondateur; les sections dramaturgie/mémoire d'agence
peuvent former un second article (organisation & design). Actes organisationnels de première classe
(HANDOFF, APPROVAL, REJECTION, REQUEST_CHANGE, BUDGET_CHANGE, CLIENT_FEEDBACK, DELIVERY) et couche
ORGANIZATIONAL MEMORY (qui reprenait les projets? quels binômes? quels savoir-faire partis?) →
spécifiés au programme de recherche, implémentation NAS en cours (handoff_edges live).
