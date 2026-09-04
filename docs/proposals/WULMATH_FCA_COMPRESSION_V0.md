# WULMATH_FCA_COMPRESSION_V0

```
banner        : 🔵 OBSERVED
zone          : GARDEN / NO_CLAIM
authority     : false
admission     : none
ledger_effect : none
status        : PROPOSAL — notation layer, not doctrine
register      : WULmath-v0 (SEPARATE from WULmoji-v1 — see §0)
date_recorded : 2026-08-07
```

Compression WULmoji des équations minimales Galois/FCA pour la skill
`epistemics/structure_over_form`, avec la frontière de registres qui
empêche cette notation d'éroder le vocabulaire verrouillé.

---

## 0. Frontière de registres (loi préalable)

```
WULmoji-v1 = vocabulaire opérationnel / gouvernance (14 glyphes, verrouillé)
WULmath-v0 = couche de notation mathématique (ce document)

parse_math : WULmath → M          (total : tout token WULmath a un sens formel)
render_gov : M ⇢ WULmoji          (PARTIEL : tout objet formel n'a pas,
                                   et ne doit pas avoir, de glyphe de
                                   gouvernance)
```

**Loi structurelle : `SHARED_GLYPH ⊬ SHARED_TYPE`.** Un glyphe (⚖️) peut
apparaître dans les deux registres ; sa sémantique est résolue par la
grammaire déclarée du registre, jamais par le rendu. Fusionner les deux
vocabulaires dans un seul G parce que leurs tokens rendus se recouvrent
est exactement l'erreur forme→identité que structure-over-form interdit.
Aucun amendement de palette n'est demandé par ce document.

## 1. Contexte formel

```
𝒦 = (G, M, I)          🧩K := (🔣G, 🧬M, 🔗I)
g I m                    g 🔗 m  := g possède l'attribut structurel m
```

## 2. Dérivations

```
A ⊆ G :  A′ = {m ∈ M : ∀g ∈ A, g I m}     🔣A ⚖️′→ 🧬COMMON(A)
B ⊆ M :  B′ = {g ∈ G : ∀m ∈ B, g I m}     🧬B ⚖️′→ 🔣MATCH(B)
```

## 3. Antitonie (loi centrale de la connexion)

```
A₁ ⊆ A₂ ⇒ A₂′ ⊆ A₁′        🔣↑ → 🧬COMMON↓
B₁ ⊆ B₂ ⇒ B₂′ ⊆ B₁′        🧬constraints↑ → 🔣matches↓
```

## 4. Fermeture, extensivité, idempotence, monotonie

```
A ⊆ A″    B ⊆ B″           X ⊆ ⚖️closure(X)
A″″ = A″  B″″ = B″          ⚖️closure(⚖️closure(X)) = ⚖️closure(X)
A ⊆ C ⇒ A″ ⊆ C″
```

**Théorème anti-rumination (qualifié).** Sous un contexte **fixé**
(G, M, I) et une évidence inchangée :

```
⚖️C(⚖️C(x)) = ⚖️C(x)  ↛  🧾NEW_EVIDENCE
```

Formulation referee-safe (gravée, amendement 2026-08-07) : *sous contexte
formel fixé et évidence inchangée, réappliquer le même opérateur de
fermeture ne modifie pas la fermeture obtenue et ne fournit aucune
nouvelle évidence empirique indépendante.* Un second calcul peut produire
des métadonnées d'exécution nouvelles (logs, reçus de run) — jamais un
nouvel élément de X″ :

```
NEW_EXECUTION_RECEIPT ⊬ NEW_EVIDENCE
EXECUTION_RECEIPT ⊬ EMPIRICAL_CORROBORATION
```

Le qualificatif est obligatoire : un run ultérieur peut porter une
évidence nouvelle ou un contexte modifié — l'idempotence n'interdit que
la re-application du même opérateur aux mêmes données. (Version non
qualifiée « ⚖️⚖️⚖️ ↛ preuve » : trop forte, rejetée.)

## 5. Concept formel et ordre du treillis

```
🧩C = (🔣A, 🧬B)  ⇔  A′ = B ∧ B′ = A       A = extent · B = intent

🧩C₁ ≤ 🧩C₂  ⇔  🔣A₁ ⊆ 🔣A₂  ⇔  🧬B₂ ⊆ 🧬B₁     extent↑ ↔ intent↓
```

## 6. Implication d'attributs

```
🧬X ⇒ 🧬Y   ssi   🧬Y ⊆ ⚖️closure(🧬X)

FCA_IMPLICATION ⊬ HISTORICAL_CAUSATION
```

## 7. Frontière constitutionnelle

```
PAIR_FREQUENCIES ⊬ GALOIS_CONNECTION   (L1 ≠ L2 : la connexion n'existe
                                        qu'après déclaration de (G,M,I))
🧩FORMAL_CONCEPT ⊬ 🧾HISTORICAL_IDENTITY
⚖️CLOSURE ⊬ 🧾ORIGIN
📊STRUCTURAL_SIMILARITY ⊬ SAME_SOUND
LOOKS_LIKE ↛ SAME_ROLE ↛ SAME_SOUND ↛ SAME_ORIGIN

┌──────────────────────────────────────────────┐
│ ⚖️ FORMAL CLOSURE  ⊬  🧾 WORLD TRUTH          │
└──────────────────────────────────────────────┘
```

Le treillis dit ce qui suit du contexte déclaré. Il ne dit pas que le
contexte représente correctement l'histoire, la phonétique ou le monde.

---

```
seal : SHARED_GLYPH ⊬ SHARED_TYPE · ⚖️FORMALITY ⊬ 🧾TRUTH
       idempotence ⇒ anti-rumination, sous (G,M,I) fixé seulement
```

HELEN OS — created by JM Tassy.
