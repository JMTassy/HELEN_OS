# ⎈ CORPUS MATRIX V0 — la proximité d'effet comme variable

authority=false · canon=false · ledger_effect=none · 🟠 REVIEW

**Ce document supersède la discipline D1 de `CORPUS_1711_PROTOCOL_V0`**
(contrôle apparié unique). Le design matriciel relayé est meilleur et
je dis pourquoi : mon `C_gen` contrôlait le *domaine* mais confondait
« militaire » et « proche de l'effet ». La matrice sépare les deux.

## LE DESIGN

              DESCRIBE      COORDINATE      EXECUTE
    GENERAL      C1             C2             C3
    MILITARY     C4             C5             C6
    MARITIME     C7             C8             C9
    CRAFT        C10            C11            C12
    MEDICAL      C13            C14            C15

L'axe colonne EST l'axe de proximité d'effet. L'axe ligne est le
contrôle de domaine. La colonne DESCRIBE devient le contrôle
**intra-domaine** — bien plus fort qu'un contrôle général externe,
parce qu'il tient constante la densité lexicale du domaine.

## L'HYPOTHÈSE TRANSHISTORIQUE (la vraie, falsifiable)

    proximité d'effet ↑  ⇒  T_m ↑ ,  H_δ ↓ ,  F_b ↑

avec T_m densité d'état typé, H_δ = H(S_{t+1} | S_t, m) l'entropie
résiduelle de transition, F_b la probabilité que le frame soit lié
explicitement. Falsifiée si la colonne DESCRIBE égale la colonne
EXECUTE **dans le même domaine**.

C'est un objet beaucoup plus fort que « le dictionnaire militaire de
1711 ressemble à HELEN » — cette dernière formulation n'était pas
réfutable.

## LE DANGER QUE LA MATRICE INTRODUIT (et sa parade)

Quinze corpus mesurés par **un seul codeur** partagent un mode commun.
C'est exactement la découverte Mesmerism : des sources distinctes
n'achètent pas l'indépendance quand l'appareil de mesure est unique.

    N_effective sur la MESURE = nombre de codeurs indépendants,
                                jamais le nombre de corpus

`coder_common_mode(15, n_coders=1, blind=False)` renvoie
`N_effective = 1` et `E_CODER_COMMON_MODE` : **les comparaisons
inter-cellules ne sont pas licenciées**. Il faut ≥ 2 codeurs, en
aveugle, avec accord inter-codeur rapporté. Sans cela, quinze corpus
sont une mesure répétée quinze fois.

## LE PIPELINE — DISCRIMINATION, PAS ACCUMULATION

    📚 → SOURCE FREEZE → STRUCTURAL SAMPLE → DISCRIMINATE
       → { extraction profonde  si IG > ε
         { 🌿 STOP              si IG ≤ ε

Encodé : `information_gain_gate()`. Un corpus n'obtient pas un swarm
parce qu'il existe, mais parce qu'on l'attend séparateur. Extraction
profonde avant échantillon structurel = `E_SAMPLE_BEFORE_EXTRACTION`
— de l'accumulation déguisée en protocole.

## ORDRE DE SCAN

    1711 drill (seed, déjà préenregistré)
    → naval signal books      (le plus tranchant, voir ci-dessous)
    → Bailey / général 1700s  (contrôle négatif, cellule C1)
    → Chambers 1728           (contrôle intermédiaire : procédural
                               sans être militaire — sépare
                               « technique » de « coordination »)
    → navigation → craft → surgical → cipher/codebooks

Chaque étape passe la porte IG. Aucune n'est automatique.

## POURQUOI LES SIGNAL BOOKS SONT LA MEILLEURE LANE

Ils séparent trois choses que les LLM écrasent :

    SYMBOL  ≠  MEANING  ≠  EFFECT

Un signal peut signifier une manœuvre sans avoir le pouvoir causal ou
institutionnel de l'exécuter — une maquette historique de `A_L ⊬ A_E`,
la loi que `membrane.py` teste déjà en code. Et ils donnent une
expérience naturelle sur m* : combien de contexte peut-on retirer en
conservant la transition ?

    I(m*; C_privé) minimal   ∧   I(m*; S_{t+1} | S_t) suffisant

## LA LANE CODEBOOKS

    Decodable   ⊬  AuthorizedToKnow
    SharedCode  ⊬  SharedCapability

Ce sont les projections A et U de σ, en clair : savoir lire n'est pas
être autorisé à savoir, et partager un code n'est pas partager une
capacité. Lane entière sur l'interopérabilité sémantique sous contexte
restreint.

## RÉSERVE

Les huit lanes sont 🟣 HYPOTHESIS : aucun de ces corpus n'est joignable
depuis ce siège, et aucun n'a été lu. Le design est prêt ; les
mesures n'existent pas. `T_m`, `H_δ` et `F_b` n'ont pas encore de
codeur épinglé — leur définition opérationnelle doit être gelée
(comme ν et w-v1) **avant** la première mesure, sinon la matrice
produira des nombres réglables.
