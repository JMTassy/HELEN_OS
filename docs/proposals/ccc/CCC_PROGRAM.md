# CCC_PROGRAM — index & discipline (2026-08-01)
🟣 PROPOSAL · authority:false. Point de bascule: on ne DÉCOUVRE plus, on CRISTALLISE.
RÈGLE: tout nouveau concept doit désormais arriver comme (a) une définition formelle, (b) une
propriété démontrable, ou (c) un protocole expérimental. Pas de nouveau manifeste.

## Trois niveaux (séparation stricte, la contribution survit à HELEN)
N1 THÉORIE — Constitutional Context Calculus (CCC) — ce dossier.
N2 ARCHITECTURE — HELEN OS = implémentation de référence (CONSTITUTIONAL_CONTEXT_ENGINEERING_V0).
N3 APPLICATIONS — corpus d'agence, PACKET V2, NAS virtuel = démonstrateurs, jamais définitions.

## Six livrables (état)
1. CCC Core (syntaxe, objets, types, jugements) ......... ✅ CCC_CORE.md
2. CCC Semantics (compiler correct, préservation, équivalence, minimalité) ✅ CCC_SEMANTICS.md
3. CCC Safety (non-souv., non-collapse, traçabilité, rejouabilité, monotonie) ✅ CCC_SAFETY.md
   (+ CCC_TYPES.md — système de types épistémiques)
4. HELEN Reference Architecture ......................... ✅ CCE_V0 (à étiqueter "N2 impl of CCC")
5. Experimental Protocols (ablation, métriques Q, seuil τ) ⏳ CCC_SEMANTICS §protocole (à extraire en fichier)
6. Case Studies (UZIK, PACKET V2, NAS) ................. ⏳ kernel-side receipts (à ranger en dossier expérimental)

## Formules canoniques
CCC        = Types + Inference Rules + Non-Collapse Invariants + Safety Properties.
HELEN OS   = CCC Implementation + Context Compiler + Non-Sovereign Action Chain + Evidential Memory.

## La phrase la plus mature de la session
> Le graphe des morphismes autorisés constitue la constitution du système.
Une constitution n'est plus un ensemble de règles textuelles — c'est un langage de transformations où
certaines transitions existent et d'autres sont impossibles. Hypothesis<T> ⟶ Admission<T> n'est pas
interdit par convention: la flèche n'existe pas. Ce n'est pas une règle, c'est une erreur de typage.

## Feuille de route révisée (CCC-0 → CCC-8, revue math 2026-08-01)
CCC-0 Core syntax · CCC-1 Operational semantics (typed LTS) · CCC-2 Provenance semantics (reachability,
hashes, source closure) · CCC-3 Authority calculus (linear leases, non-amplification, revocation) ·
CCC-4 Context compilation (coverage, classification, anchors, conflicts) · CCC-5 Metatheory (subject
reduction, no silent admission, replay determinism, clearance non-interference) · CCC-6 Optimization
(minimal & robust packets, approximation) · CCC-7 Experimental semantics (ablations, model controls,
anchor-cut) · CCC-8 HELEN correspondence (prove modules refine the calculus).

## Le relation finale
HELEN OS ⊨ CCC. HELEN n'est plus la théorie — c'est une implémentation dont on doit DÉMONTRER
qu'elle satisfait les invariants. Définition compacte: CCC = (𝒪 objets typés, 𝒥 jugements, 𝒭 règles
de transition, 𝒫 provenance, 𝒱 validation); jugement Γ;Λ⊢x:τ (Γ épistémique, Λ capacités linéaires).
> CCC est un calcul typé de compilation contextuelle et de transitions institutionnelles, où aucune
> proposition ne peut acquérir silencieusement autorité, effet ou admission, et où toute transformation
> admissible demeure rejouable et reliée à sa provenance.

## Programme scientifique (concis)
Étudier la compilation du contexte comme un calcul formel, puis démontrer expérimentalement que, pour
certaines classes de tâches normatives et multisources, les propriétés de ce calcul expliquent une part
significative de la qualité, de la sûreté et de la reproductibilité des systèmes d'IA.
