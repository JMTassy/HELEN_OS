# FIVE_MACHINES_V0 — composition de transducteurs à autorité asymétrique

```
banner        : 🔵 OBSERVED
zone          : GARDEN / NO_CLAIM · authority=false · admission=none ·
                ledger_effect=none
status        : PROPOSAL — synthèse doctrine, corrigée en revue locale
date_recorded : 2026-08-07
```

## 1. Les cinq machines (niveau opérateur)

| machine | rôle | interdit structurel |
|---|---|---|
| 🛠 BUILDERS (Goblins/Superteams) | brainstorm, drafts, candidats | jamais la clé du bâtiment |
| 🧪 WITNESS (labo / POC Factory) | « show me the test » → evidence | ne décide pas |
| ⚖️ MAYOR (videur/réducteur) | gates OUI/NON, délibérément stupide | ne raisonne pas |
| 📜 LEDGER (boîte noire) | append-only, hash-chaîné, rejouable | ne s'efface pas |
| 🌿 GARDEN (HER/imagination) | what-if, désaccords, mutation | 💭 ↛ 📜 |

> Le génie n'est dans aucune boîte. Il est dans **qui a interdiction de
> faire le travail de la boîte suivante**.

## 2. Formalisation (niveau guru)

Espaces : D (cognition libre), P (propositions), E (évidence),
R (reçus), L (état ledger).

```
α : D → 𝒫(P)          expressif — stochastique, multi-agent, riche
V : P × X → E          vérification dans l'environnement observable X
r = H(canon(p, e, π, v))   constructeur de reçus (politique π, version v)
β : L × R × Π → L′     transition souveraine — DÉTERMINISTE
```

Invariant constitutionnel de non-interférence :

```
∄ morphisme admissible  D → L
```

Le ledger est un monoïde libre (Σ*, ⊕, ε), sans inverse — append-only.
Replay : (L,R,Π) identiques ⇒ β identique, octet pour octet.

Lois de l'essaim : `n·agreement ⊬ truth` — l'essaim élargit la recherche,
jamais l'autorité. Le falsificateur rétrécit l'ensemble viable, il ne
produit pas de vérité. Décision minimale :

```
SHIP(p) = 1[ gap(p) = 0 ∧ K(p) = 1 ]
gap(p)  = |{ oᵢ ∈ O(p) : ∄ a ∈ A, a ⊨ oᵢ }|
```

## 3. LA SIXIÈME MACHINE (correctif de revue — obligatoire)

`SHIP(p)` est aussi fort que `O(p)` est complet. **Si le proposeur écrit
ses propres obligations, il shippe trivialement** : gap = 0 sur un contrat
creux. C'est proposer ≠ validator appliqué aux obligations — et c'est la
brèche B1 constatée en lane (`ingest_receipt_v1` : le contrat jurait une
inforgeabilité, le code n'avait qu'un refus de mot-clé ; witness vert
dans le périmètre, adversaire rouge hors périmètre ; 11 réfutations sur
12 tours ont cette forme).

```
⚔️ CONTRACT ADVERSARY — auteur/auditeur adverse de O(p)
   entrée  : p + O(p) proposé
   sortie  : O′(p) durci + limites non déclarées
   interdit: être le proposeur ; être le witness du même p
```

Sans cette boîte, la faiblesse systémique dominante reste invisible dans
la théorie alors qu'elle est la cause principale des réfutations vécues.

## 4. RLM — accès à la cognition, borné par la provenance de lecture

Les Recursive Language Models traitent le corpus comme environnement
externe et s'invoquent récursivement dessus. Admissible dans HELEN
seulement avec :

```
chaque descente qui produit une evidence candidate ENREGISTRE
les spans lus + leurs hashes (ReplayBasis de l'évidence).
```

Borner l'autorité ne suffit pas : sans trace de lecture, RLM est un
générateur d'évidence non journalisé sous le seuil du réducteur.

## 5. Structure profonde

```
HER/Goblins · RLM   →   PROPOSALS → ⚔️CONTRACT → FALSIFIER → TESTS
                        → EVIDENCE → RECEIPTS → [réducteur petit,
                        stupide, déterministe] → LEDGER → REPLAY
```

```
┌──────────────────────────────────────────────────────┐
│ cognition riche + interfaces étroites +              │
│ autorité déterministe rare                           │
│                                                      │
│ puissance cognitive ↑  ⊬  autorité ↑                 │
└──────────────────────────────────────────────────────┘
```

Le protocole delta 2-goblins est le même objet à petite échelle :
`S_{t+1} = S_t ⊕ Δ_t` — event sourcing, même monoïde que le ledger.

---

```
seal : AGREEMENT ⊬ PROOF · gap=0 ⊬ contrat complet ·
       RLM sans trace ⊬ évidence · ∄ D→L
```

HELEN OS — created by JM Tassy.
