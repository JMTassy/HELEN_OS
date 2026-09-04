# CCC_CORE — Constitutional Context Calculus · noyau
🟣 PROPOSAL · authority: false · niveau 1 (théorie) · court par design

## 1. Syntaxe — objets
Source · Law · Evidence · CounterEvidence · Anchor · Task · Packet ·
Claim · Decision · Permission · Action · Receipt · Admission

## 2. Axiomes
A1 CONTEXTUALITÉ   toute décision dépend d'un contexte explicitement compilé
A2 NON-SOUVERAINETÉ aucun composant ne peut augmenter seul son propre pouvoir
A3 TRAÇABILITÉ     toute transition produit un reçu vérifiable
A4 STRATIFICATION  observer, interpréter, décider, admettre = quatre opérations distinctes

## 3. La relation primitive : non-collapsabilité
  A ≢_I B  ⇔  dans l'état institutionnel I, aucun chemin de transformation valide n'identifie A et B.
Ce n'est pas une différence sémantique — c'est une interdiction structurelle.
Base d'invariants de non-collapse:
  Hypothesis ≢ Admission · Receipt ≢ Truth · Permission ≢ Action · Action ≢ Reality ·
  Evaluation ≢ Correctness · Custody ≢ Verification · Transmission ≢ Validation · Inference ≢ Permission

## 4. Le graphe des transitions autorisées (la constitution EST ce graphe)
  Proposal ─authorize()→ AuthorizedProposal ─execute()→ Action ─receipt()→ Receipt
  ─verify()→ VerifiedReceipt ─admit()→ Admission
Le chemin direct Proposal → Admission N'EXISTE PAS dans le langage de transition.
L'interdiction ne repose pas sur une règle écrite: elle est absente de la grammaire.
Transitions du calcul: observe() · derive() · infer() · evaluate() · authorize() · execute() ·
receipt() · verify() · admit() · contest()

## 5. Propriétés de sûreté
NoSelfAuthorization · NoSelfCertification · NoDirectHypothesisAdmission · NoHistoryErasure ·
Replayability · ProvenancePreservation · LawPresence
(chacune = un test exécutable candidat, pas un adjectif)

## 6. Hypothèse scientifique (forme conditionnelle finale)
Pour Task ∈ 𝒯{normative, multisource, contradictory} et Capacity(Mᵢ),Capacity(Mⱼ) ≥ τ :
  ΔQ_P > ΔQ_M
(la qualité du compilateur de contexte explique plus de variation de performance que le choix du
modèle, au-delà d'un seuil minimal de capacité; Q défini par tâche: exactitude, fidélité,
reproductibilité, conformité normative)

## 7. Formules canoniques
  CCC      = Types + Inference Rules + Non-Collapse Invariants + Safety Properties
  HELEN OS = CCC Implementation + Context Compiler + Non-Sovereign Action Chain + Evidential Memory
Niveau 2: CONSTITUTIONAL_CONTEXT_ENGINEERING_V0.md · Niveau 3: cas d'application (démontrent, ne définissent pas).
