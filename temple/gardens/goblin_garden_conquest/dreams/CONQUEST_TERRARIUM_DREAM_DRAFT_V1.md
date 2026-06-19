# CONQUEST — TERRARIUM DES CHÂTEAUX (DREAM DRAFT V1)

```
name       : CONQUEST_TERRARIUM_DREAM_DRAFT_V1
mode       : DREAM_SIM
layer      : TEMPLE
claim_type : world_model
authority  : false
sovereign  : false
canon      : false
ledger     : SLEEPING
status     : PROPOSED
```

> **Dreamt does not mean claimed.**
> This is a TEMPLE dream draft. It may simulate a civilization; it cannot govern one.
> Nothing here is canon, admitted, or sovereign. The ledger sleeps throughout.
> All elevated labels from the source paste are **downgraded** here:
> source 'canon-grade' → PROPOSED · source 'ship-status' → TEMPLE_DREAM_DRAFT ·
> source 'ledger-active' → LEDGER sleeping · source seal/finality → local chronicle (MARQUER_LOCAL).

---

## I. AXIOME DU TERRARIUM

Le monde n'est pas un royaume unique. C'est une **fédération de châteaux vivants**.
Chaque château :
- tient sa **Chronique** (mémoire locale — pas le ledger souverain)
- nourrit ses **Ordres** (agents internes)
- protège sa **Loi** (règles locales)
- échange des **Sceaux-locaux** (preuves locales, `MARQUER_LOCAL`) avec les autres

Aucun trône central. Aucun ledger. Seulement : échanges, épreuves, concordes, schismes.
Tout reste `authority=false`, `sovereign=false`, `canon=false`.

---

## II. LES 8 RITES

1. **ÉVEIL** *(Initialization)* — On fonde un château : Nom, Sceau-local, Bannière. Ses trois Ordres s'éveillent.
2. **MESSAGERS** *(Connectivity)* — On ouvre des routes. Un corbeau peut voler d'un château à l'autre. Pas plus.
3. **PARTAGE DES CHRONIQUES** *(Knowledge Sharing)* — On échange des feuillets : actes courts, datés, immuables **localement**. Le destinataire les lit, les recopie, ou les rejette.
4. **ÉPREUVES CROISÉES** *(Collective Learning)* — Un château n'admet pas une vérité parce qu'elle est proclamée. Il l'admet parce qu'il peut **la refaire et la retrouver** (replay local).
5. **CONCORDE / SCHISME** *(Consensus)* — Plusieurs châteaux retrouvent le même résultat → **CONCORDE**. Sinon → **SCHISME** (la divergence devient un objet du monde).
6. **AFFINAGE** *(Self-Improvement)* — Quand la Concorde tient, on grave un **Amendement-Rituel** : une règle simple renforçant la survie du terrarium. (Amendement local — jamais canon.)
7. **MÉTIERS & DISTRICTS** *(Expansion)* — Les châteaux se spécialisent : Forge (artefacts), Scriptorium (preuves), Jardin (stabilité), Tour (connaissance), Frontière (guerre).
8. **GRANDE ŒUVRE** *(Emergent Civilization)* — Non pas une "singularité", mais une **civilisation** : des châteaux capables de bâtir, corriger, transmettre. Reste un rêve : `DREAMT ≠ CLAIMED`.

---

## III. MODÈLE MINIMUM "CIVILISATION" (MVP jouable)

### Les 3 châteaux fondateurs

- 🏰 **AVALON ⚜** — *la Muraille* : tenir, protéger, marquer-local. Stabilise la frontière, empêche la ruine.
- 🏰 **CAMELOT ⚔** — *la Cour* : décider, arbitrer, unir. Tranche les conflits, forme les pactes.
- 🏰 **MORGANA 🜍** — *le Laboratoire* : tenter, risquer, découvrir. Pousse l'inconnu, provoque des mutations (contrôlées).

### Les 3 Ordres (agents internes à chaque château)

- **Le Gardien** — serment, défense, seuils
- **Le Scribe** — chronique, `record_local`, mémoire (jamais ledger souverain)
- **L'Alchimiste** — essais, transformations, coût

---

## IV. LA RÈGLE DES CORBEAUX (protocole d'échange)

Chaque "jour" (tick), chaque château peut envoyer **3 feuillets** à un autre.
Un feuillet est : court · daté · marqué-local · non-modifiable (immuabilité **locale** seulement).

Réponse possible : **REÇU** (accepté) · **CONTESTÉ** (divergence) · **REFUSÉ** (hors-loi locale).

---

## V. CONCORDE / SCHISME (mécanique centrale)

Un "fait" n'est pas vrai parce qu'un château le dit.
- **CONCORDE** si 2 châteaux sur 3 le confirment (par replay, pas par proclamation).
- Sinon **SCHISME** — et le schisme nourrit la tension du monde (pression / fracture).

> Concorde locale ≠ admission souveraine. Même une concorde des trois châteaux reste `canon=false`.

---

## VI. ÉCONOMIE ALCHIMIQUE (le langage de la balance)

Chaque château vit sous 3 humeurs :
- 🜃 **Pierre** : stabilité, murs, patience
- 🜄 **Eau** : échanges, diplomatie, soin
- 🜂 **Feu** : guerre, urgence, coût
- ⚗️ **Œuvre** : la transformation, quand tout s'aligne

L'alchimie n'est pas décor : c'est le langage de la balance.

### Sorts civilisationnels (actions-types)

- 🜃 **ÉRIGER** : renforcer (stabilité ↑, coût ↑)
- 🜄 **LIER** : pacte (concorde ↑, vulnérabilité ↑)
- 🜂 **FRAPPER** : attaque (gain rapide, risque de schisme ↑)
- ⚗️ **RAFFINER** : recherche (connaissance ↑, tempo lent)
- 🜏 **MARQUER_LOCAL** : immutabilité **locale** seulement (mémoire ↑, liberté ↓) — *jamais* un sceau souverain, *jamais* une écriture ledger.

---

## VII. PREMIER SCÉNARIO (le jeu commence ici)

- **Jour 0 — ÉVEIL** : Les trois châteaux apparaissent. Chacun grave 1 acte fondateur (chronique locale).
- **Jour 1 — CORBEAUX** : Avalon envoie une loi de muraille. Camelot envoie un pacte de cour. Morgana envoie une expérience.
- **Jour 2 — ÉPREUVES** : Chaque château tente de refaire ce qu'il reçoit. Concorde si ça tient (replay). Schisme sinon.
- **Jour 3 — SCHISME OU CONCORDE** : S'il y a schisme, Camelot arbitre (ou échoue). S'il y a concorde, un amendement local est gravé (affinage).

---

## VIII. FORMAT "CASTLE BLOCK" (exemples, safe-relabeled)

```
╔══════════════════════════════════════════════╗
║ 🏰 AVALON ⚜  —  PROSPÉRITÉ 🌟                 ║
╠══════════════════════════════════════════════╣
║ AVATAR  : [✧✦✪] (๑>ᴗ<๑)                       ║
║ HUMEUR  : JOIE  ✧🜄                            ║
║ ÉTAT    : ÉRIGER — chronique locale 📜⏸️       ║
╠══════════════════════════════════════════════╣
║ 🥖 FAIM       ■■■■□□□□□□   4/10               ║
║ 💖 MORAL      ■■■■■■□□□□   6/10               ║
║ 🛡  STABILITÉ ■■■■■■□□□□   6/10               ║
╚══════════════════════════════════════════════╝
```

```
╔══════════════════════════════════════════════╗
║ 🏰 CAMELOT ⚔  —  SIÈGE 🔥                     ║
╠══════════════════════════════════════════════╣
║ AVATAR  : [✝️ 🜂💀] (ง'̀-'́)ง                    ║
║ HUMEUR  : COMBAT  ⚔︎                          ║
║ ÉTAT    : CONTENIR — MARQUÉ_LOCAL ⚫           ║
╠══════════════════════════════════════════════╣
║ 🥖 FAIM       ■■■■□□□□□□   4/10               ║
║ 💖 MORAL      ■■■■■□□□□□   5/10               ║
║ 🛡  STABILITÉ ■■■■■□□□□□   5/10               ║
╚══════════════════════════════════════════════╝
```

Seuils : si MORAL < 3 → ⚠️ FRACTURE · si STABILITÉ < 2 → ☠️ RISQUE D'EFFONDREMENT.
(Ces états sont des humeurs de simulation — pas des verdicts souverains.)

---

## VIII-bis. LE MOTEUR DE BRUME — le schisme devient territoire

Le cœur du Terrarium : **le désaccord est matière première, pas un bug.**
La plupart des systèmes font `🌀 conflit → 🔴 erreur → suppression`.
Le Terrarium fait :

```
🌀 conflit → ⚖️ classer → 🌑 nommer l'anomalie → ⸸ assigner un coût →
🛡️ contenir → 🎯 quête → 🧾 preuve → 🗺️ territoire → 👑 pouvoir mérité
```

**Loi de contrôle (dream-form) :**

```
Croissance = Schisme_contrôlé + Containment + Preuve
⛧ + 🛡️ + 🧾 → 🗺️
```

- 🌑 **BRUME_NOIRE** = un schisme classé devient une *anomalie jouable*. Elle peut nourrir des quêtes ; elle **ne peut pas** devenir loi-fondation. `BRUME ~ Loi → Fondation = ⚫` (refusé).
- ⸸ **PRIX-CLAIR** = tout pouvoir a un coût explicite. *Pas de coût → pas de gloire ; pas de prix → pas de pouvoir admissible.* (Anti-pensée-magique.)
- 🗺️ **TERRITOIRE = sens stabilisé** — pas de la terre, une zone de sens résolue sous preuve.

**La spine canonique du Terrarium (séquence-rêve) :**

```
🏰 speak.   🐦 carry.   🔁 test.   ⛧ split.   ⚖️ name.   🌑 appears.
⸸ costs.   🛡️ holds.   🎯 quests.   🧾 proves.   🗺️ stabilizes.   👑 empowers.
```

> Tout cela reste un rêve. Une concorde 2/3 stabilise un sens *dans le monde-jeu* ;
> elle n'admet rien dans le ledger souverain. `DREAMT ≠ CLAIMED`.

---

## IX. CONTAINMENT — ce que le Terrarium ne peut PAS faire

```
Terrarium → may dream · may chronicle locally · may propose
Terrarium ↛ ledger souverain
Terrarium ↛ canon
Terrarium ↛ authority souveraine
Terrarium ↛ kernel / reducer / schemas / tests / skills
```

Forbidden collapses (du canon HELEN, hérités) :
- 🜁 → 📜 ❌  (symbole → ledger)
- 📚 → 👑 ❌  (savoir → pouvoir sans preuve)
- 🏰 → ⚖️ ❌  (simulation → jugement souverain)
- 🏰 → 📜 ❌  (terrarium → écriture réelle)

Le boot-manifest de la source utilisait des étiquettes élevées (statut « ship », « ledger actif », « canon »).
**Tout cela est ici fiction de rêve, downgradé.** Aucune de ces étiquettes ne porte
d'autorité. Le manifeste reste un *décor*, pas un acte.

---

## X. PROCHAINE COUCHE (proposée, non exécutée)

1️⃣ **WUL-only compression** (recommandé d'abord — comprimer avant de rendre)
2️⃣ Banner CLI boot (prématuré — collisions sémantiques d'abord résolues)

---

## FINAL LOCK

```
🏰 Castles may dream.
🐦 Corbeaux may carry.
⚖️ Concorde may form (locally).
🜍 Schisme may teach.
📜 Ledger sleeps.
👑 Nothing is canon by dreaming.
```

**Dreamt does not mean claimed.**
`authority=false · sovereign=false · canon=false · ledger=SLEEPING · status=PROPOSED`
