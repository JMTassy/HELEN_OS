# CCC_CORE — Constitutional Context Calculus · syntaxe & noyau
🟣 PROPOSAL · authority:false · Niveau 1 (théorie). Lire avant CCC_TYPES, puis CCC_SEMANTICS.

## Objets
Source · Law · Evidence · CounterEvidence · Anchor · Task · Packet · Claim · Decision · Permission ·
Action · Receipt · Admission.

## Axiomes (lois de conservation; tout se dérive d'ici)
A1 Contextualité — toute décision dépend d'un contexte explicitement compilé.
A2 Non-souveraineté — aucun composant n'augmente seul son propre pouvoir.
A3 Traçabilité — toute transition produit un reçu vérifiable.
A4 Stratification — observer, interpréter, décider, admettre = 4 opérations distinctes.

## Relation primitive: non-collapsabilité
A ≢_I B  ⇔  dans l'état institutionnel I, aucun chemin de transformation valide n'identifie A et B.
Ce n'est pas une différence sémantique — c'est une INTERDICTION STRUCTURELLE.
Base:  Proposal ≢ Admission · Receipt ≢ Truth · Execution ≢ Reality · Custody ≢ Verification ·
       Transmission ≢ Validation · Inference ≢ Permission · Evaluation ≢ Correctness.

## Le graphe des transitions EST la constitution
Proposal --authorize()--> AuthorizedProposal --execute()--> Action --receipt()--> Receipt
  --verify()--> VerifiedReceipt --admit()--> Admission.
Le chemin direct Proposal ⟶ Admission N'EXISTE PAS dans le langage de transition.
L'interdiction n'est pas une règle écrite qu'on peut oublier — elle est ABSENTE de la grammaire.

## Packet (l'objet compilé)
Packet = (CoreLaws, DomainLaws, Evidence, CounterEvidence, Anchors, Task).
Context Compiler:  P : (C,S,L,E,T) ↦ K.  (correction/équivalence/minimalité: voir CCC_SEMANTICS)
