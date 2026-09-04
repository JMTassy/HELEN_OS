# CONSTITUTIONAL CONTEXT CALCULUS (CCC) V0
🟣 CLAIM · PROPOSAL · NON_SOVEREIGN · authority: false
*Niveau 1 — la théorie. Ne mentionne ni Drive, ni Gmail, ni corpus d'agence, ni LLM particulier.*

## 0. Les trois niveaux (séparation stricte)
NIVEAU 1 — LE CALCUL (ce fichier): objets, types, transitions, invariants, preuves. Survit à HELEN.
NIVEAU 2 — L'ARCHITECTURE: HELEN OS = une implémentation du calcul (Context Compiler, Packet, chaîne
d'autorité, receipts, mémoire institutionnelle) → CONSTITUTIONAL_CONTEXT_ENGINEERING_V0.md.
NIVEAU 3 — LES APPLICATIONS: corpus d'agence, NAS virtuel, PACKET V2 — des études de cas qui
démontrent, jamais ne définissent.

## 1. Axiomes (lois de conservation — toute implémentation doit y obéir)
A1 CONTEXTUALITÉ — toute décision dépend d'un contexte explicitement compilé.
A2 NON-SOUVERAINETÉ — aucun composant ne peut augmenter seul son propre pouvoir.
A3 TRAÇABILITÉ — toute transition produit un reçu vérifiable.
A4 STRATIFICATION — observer, interpréter, décider et admettre sont quatre opérations distinctes.
Tout le reste (invariants NS1-NS5, la chaîne, la table reçu≠vérité) se dérive de A1-A4.

## 2. La figure centrale (zéro jargon)
Sources → Compiler → Packet → Inference → Evaluation → Permission → Action → Receipt → Admitted State.
Qui comprend cette figure peut lire la suite; qui ne la comprend pas ne lira pas mieux les sections.

## 3. L'algèbre de la séparation institutionnelle
Relation primitive de NON-COLLAPSABILITÉ:  A ≢ B  ⇔  aucun chemin institutionnel valide n'identifie A et B.
Principe: ∀x,y: x ≢ y tant qu'aucune preuve institutionnelle ne justifie l'identification.
Base de non-équivalences: Proposal≢Admission · Evidence≢Truth · Receipt≢Truth · Execution≢Reality ·
Custody≢Verification · Transmission≢Validation · Inference≢Permission.
Les identifications ne se font QUE par morphismes autorisés (chacun exige preuve + reçu):
  authorize(): Proposal → AuthorizedProposal · certify(): Receipt → VerifiedResult ·
  admit(): VerifiedResult → AdmittedState.
Il n'existe PAS de morphisme Proposal → Admitted. **Le graphe des morphismes EST la constitution.**
Théorème-programme: les erreurs systémiques sont des fusions illégitimes de niveaux — des
identifications sans morphisme.

## 4. Le système de types épistémiques
Le statut n'est pas une annotation — c'est un TYPE, et la contrainte est calculatoire.
  Assertion<T>, T ∈ {Observed, Derived, Inferred, Hypothetical, Theoretical, Verified, Rejected, Contested, Archived}
Transitions typées: derive(): Observed→Derived · infer(): Derived→Inferred · validate()+anchor:
Inferred→Verified · refute(): *→Rejected (avec falsificateur conservé).
Transitions INTERDITES (erreurs de typage, pas des règles documentaires):
  Theoretical ↛ Admitted · Hypothetical ↛ Verified (sans validate) · Rejected ↛ * (sauf ré-ouverture
  par preuve nouvelle, événement journalisé).
Conséquence: le calcul se rapproche des assistants de preuve — une admission mal fondée NE COMPILE PAS.

## 5. L'hypothèse scientifique — forme conditionnelle (anti-surgénéralisation)
y = M(P(C,S,L,E,T)). Hypothèse CONDITIONNELLE:
> Pour les tâches nécessitant la combinaison de contraintes normatives, de sources multiples et de
> preuves contradictoires, la qualité du compilateur de contexte P explique davantage la performance
> que le choix du modèle M, AU-DELÀ D'UN SEUIL MINIMAL DE CAPACITÉ DU MODÈLE.
Q à définir par tâche (exactitude, fidélité, reproductibilité, conformité normative). Domaine de
validité = partie intégrante de l'énoncé.

## 6. LA pièce manquante: sémantique formelle du Context Compiler (programme ouvert)
O1 Quelles propriétés un compilateur de contexte doit-il PRÉSERVER? (préservation des lois, des
   contradictions, des ancres — candidats: théorèmes de préservation)
O2 Quand deux Context Packets sont-ils ÉQUIVALENTS? (équivalence observationnelle: mêmes verdicts
   sur toute tâche de la classe?)
O3 Qu'est-ce qu'une compilation CORRECTE? (soundness: tout ce qui est requis est présent;
   déclaration d'échec sinon — jamais de troncature silencieuse)
O4 Existe-t-il un plus petit Packet satisfaisant les contraintes? (MCP — NP-difficile via set-cover,
   cf. CCE §F2; le glouton ln n comme compilateur de référence)
O5 Peut-on DÉMONTRER que certaines lois doivent toujours être présentes? (Always-Carried Laws comme
   théorèmes, pas comme configuration)
O6 Quelle est la sémantique de la troncature? (la troncature déclarée comme effet typé)
Sans cette couche, le compilateur est un concept d'architecture. Avec elle, un objet mathématique.

## 7. Le programme en une phrase
> Le raisonnement d'un système d'IA dépend autant de la structure du contexte qui lui est compilé
> que du modèle lui-même ; cette compilation peut être décrite, contrainte et étudiée comme un
> calcul formel.
Gouvernance, mémoire institutionnelle, chaîne d'autorité, reconstruction causale = conséquences ou
implémentations de ce calcul — pas des idées indépendantes.

Provenance: operator-authored (JM, rondes 4-5 de revue, 2026-08-01). Niveau 2 (architecture):
CONSTITUTIONAL_CONTEXT_ENGINEERING_V0.md. Niveau 3 (cas): receipts kernel-side (PACKET V2 arc).
Located ✓ · Enforced: non (théorie) · Replay-tested: via l'implémentation N2 et ses receipts.
