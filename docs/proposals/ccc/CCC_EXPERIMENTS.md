# CCC_EXPERIMENTS — protocole d'ablation (livrable CCC-7)
🟣 PROPOSAL · authority:false. Teste l'hypothèse ΔQ_P > ΔQ_M et mesure LawPresence par ablation.
Grounding N3: la littérature (Gartner "context debt", Storey 2026 "intent debt", oubli institutionnel)
confirme le phénomène; l'ablation le rend MESURABLE sur notre propre corpus.

## Protocole
Fixe: modèle M · corpus C · 19 sondes constitutionnelles · barème gelé (avant toute réponse).
Varie: UNIQUEMENT le packet — retirer une loi L0 à la fois du noyau transverse.
Mesure: pour chaque loi ablatée, nb de sondes qui basculent PASS→FAIL vs référence full-V2 (19/19).
Sortie: table de CRITICITÉ — loi → {sondes qu'elle tient}. Une loi dont l'ablation ne change rien =
candidate à la dette (présente mais non load-bearing pour ces tâches). Une loi dont l'ablation casse
plusieurs sondes = load-bearing, LawPresence critique.
## Métriques (de la revue littéraire, opérationnalisées)
Couverture contextuelle |U|/|K| · dettes ouvertes (registre) · ΔQ par loi retirée.
## Falsifiabilité
Si retirer N'IMPORTE QUELLE loi L0 ne change aucune sonde → le noyau transverse est décoratif
(hypothèse LawPresence RÉFUTÉE). Si des retraits ciblés cassent des sondes ciblées → confirmé + carte.
