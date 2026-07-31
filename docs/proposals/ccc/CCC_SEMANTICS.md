# CCC_SEMANTICS — sémantique du Context Compiler
🟣 PROPOSAL · authority:false · Niveau 1. Ce qui transforme le compilateur d'un concept d'architecture en objet mathématique.

## Compilateur
P : (C,S,L,E,T) ↦ K   (C corpus · S sélection · L lois · E preuves · T tâche · K packet)

## CORRECTION — K est correct pour T ssi
(1) toutes les lois obligatoires de T présentes; (2) toutes les preuves requises référencées;
(3) aucune source incluse n'a perdu sa provenance; (4) les contradictions pertinentes connues exposées;
(5) les ancres exactes préservées (aucune paraphrase, aucune ellipse); (6) la transformation rejouable.

## COMPLÉTUDE RELATIVE
P est relativement complet pour T si toute information requise par les règles de T et accessible dans C
est: incluse · OU explicitement exclue-avec-justification · OU marquée indisponible. (Jamais omise en silence.)

## PRÉSERVATION (minimum garanti par P)
provenance · law identity · anchor exactness · evidence polarity · contradiction structure · task scope.

## ÉQUIVALENCE DE PACKETS
K₁ ≡_T K₂  ssi ils induisent: mêmes lois actives · mêmes ancres · mêmes obligations de preuve ·
mêmes contradictions pertinentes · mêmes permissions de transition. (Identité textuelle NON requise —
équivalence observationnelle: mêmes verdicts sur toute tâche de la classe.)

## MINIMALITÉ
K*_T = arg min |K| sous contrainte de correction. Packet minimal = correct dont aucun élément ne peut
être retiré sans violer une propriété requise.

## PROBLÈME DE DÉCISION (avant toute classe de complexité)
MCP-DECISION: « Existe-t-il un Context Packet correct pour T de taille ≤ k ? »
Conjecture de dureté: dès qu'on introduit dépendances entre lois + contradictions + redondance
documentaire + sous-ensembles minimaux de preuve + contrainte de taille, MCP-DECISION est apparenté à
SET COVER / HITTING SET (NP-difficile probable). PRUDENCE: définir formellement avant de promettre une
classe. Compilateur pratique = glouton set-cover (ratio ln n), échec DÉCLARÉ sous budget.

## HYPOTHÈSE SCIENTIFIQUE (conditionnelle)
ΔQ_P > ΔQ_M  pour  Task ∈ 𝒯_{normative, multisource, contradictory, exact-anchor}
et  Capacity(Mᵢ), Capacity(Mⱼ) ≥ τ.
« La qualité du compilateur explique une part plus grande de la variation de performance que le choix
du modèle, au-delà d'un seuil minimal de capacité. » Q défini par tâche (exactitude · fidélité ·
reproductibilité · conformité normative). Falsifiable par ablation (retirer une loi L0, mesurer la chute).

## PROTOCOLE EXPÉRIMENTAL (PACKET V2 généralisé)
Fixer M, C, sondes, barème gelé. Varier UNIQUEMENT K. Mesurer Q + taux d'échec-déclaré + ratio
tokens(K_greedy)/tokens(K_naïf). Multi-runs, multi-modèles, ablation loi-par-loi. Le harnais est publié.
Observation de référence (N3, une instance): 47% → 79% → 100% à M constant, poids intouchés.
