# CONSTITUTIONAL_DYNAMICS_V0 — la gouvernance comme système dynamique projeté

```
banner        : 🔵 OBSERVED
zone          : GARDEN / NO_CLAIM · authority=false · admission=none ·
                ledger_effect=none
status        : PROPOSAL — programme de recherche, réserves de revue en §7
date_recorded : 2026-08-07
these         : remplacer « intelligence » par « transitions d'état
                contrôlées » — un seul objet mathématique à toutes les
                échelles du stack.
```

## 1. Échelle des niveaux

```
L1  agent seul        x_{t+1} = F(x_t, u_t)          aucune contrainte
L2  HELEN             x_{t+1} = G(F(x_t))            G = opérateur de
                                                     gouvernance
L3  multi-agent       x = (x_1..x_n), F = (F_1..F_n) feedback, coalitions,
                                                     instabilité
L4  variété           G : X → M                      M = variété des états
    constitutionnelle                                admissibles ;
                                                     illégal →proj→ légal
```

## 2. Idempotence

```
G² = G
```

Gouverner deux fois ne change rien — même loi que la fermeture FCA
`A″″ = A″` (cf. WULMATH_FCA_COMPRESSION_V0 §4, théorème anti-rumination,
avec le même qualificatif : sous politique fixée et évidence inchangée).

## 3. Stabilité (Lyapunov)

```
V(x) = αC + βD + γE + δR
       C conflit · D drift · E dette d'évidence · R violations
objectif HELEN : V(x_{t+1}) ≤ V(x_t), ou au moins borné
```

`E` existe déjà dans le stack sous un autre nom : la **pression
d'événements non-receiptés** (governance debt) de la doctrine
receipted-agency. V est sa généralisation pondérée.

## 4. Évolution des règles — deux échelles de temps

```
x_{t+1} = G_{θ_t}(F(x_t))          rapide : les agents
θ_{t+1} = U(θ_t, K_t)              lent : la constitution
                                   (K_t = mémoire institutionnelle)

condition de stabilité : ‖θ_{t+1} − θ_t‖ ≪ ‖x_{t+1} − x_t‖
```

Les règles évoluent plus lentement que la société, sinon la gouvernance
chasse le bruit. Déjà vécu dans le stack : « MAYOR approuve des règles,
pas des cas ».

## 5. Programme spectral

```
𝒞 = G ∘ F            opérateur constitutionnel
ρ(𝒞) < 1  ⇒  les perturbations décroissent
ρ(𝒞) > 1  ⇒  les petites erreurs s'amplifient
```

La gouvernance devient de l'ingénierie spectrale.

## 6. Le chiddush — théorème de relèvement

> Les reçus sont à la gouvernance ce que les certificats de positivité
> locale sont à la théorie des opérateurs.

Dans les deux cadres, la question centrale non résolue est un théorème
de relèvement :

```
┌──────────────────────────────────────────────────┐
│ contraintes locales certifiées                   │
│        ⟹ ?                                       │
│ comportement global stable                       │
└──────────────────────────────────────────────────┘
```

Finite-band : relever des matrices finies vers l'opérateur limite.
HELEN : relever des actions receiptées individuelles vers la stabilité
d'une institution qui évolue. Même forme, objets différents — **aucun
transfert de résultat n'est affirmé** ; c'est une lentille commune, à
explorer indépendamment dans chaque domaine.

## 7. Réserves de revue (locales, avant tout usage)

1. **G² = G ne vaut que sur la coordonnée d'état.** Dans HELEN, G émet
   des reçus : le ledger (monoïde append-only) croît à chaque
   application. L'idempotence exige des écrivains idempotents —
   re-gouverner un état déjà admis doit être un no-op ledger. À spécifier,
   pas à supposer.
2. **V est une politique, pas une découverte.** Les poids α,β,γ,δ et la
   mesure de C/D/E/R doivent être receiptés et gelés avant toute lecture
   de V — sinon V est du vibes-scoring (leçon du scorer HAL : métrique
   divergée de la fitness).
3. **Le programme spectral suppose un plongement.** L'état HELEN est
   largement discret/symbolique ; ρ(𝒞) n'a de sens que sur un linéarisé
   près d'un équilibre dans une représentation choisie. Premier problème
   ouvert : le choix du plongement — et notre propre loi s'applique :
   `rigueur formelle sur une représentation ≠ vérité de la
   représentation`.
4. Le programme en 9 points (modèle projeté → variété M → Lyapunov →
   bornes → spectre → relèvement multi-échelle) est referee-safe tel
   quel : aucune revendication de conscience, aucune analogie RH.

---

```
seal : G² = G (état, pas ledger) · V gelé avant lecture ·
       ρ(𝒞) relatif au plongement · RELÈVEMENT = question, pas théorème
```

HELEN OS — created by JM Tassy.
