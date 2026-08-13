# ⎈ CORPUS 1711 — MILITARY & SEA DICTIONARY · PROTOCOLE V0

authority=false · canon=false · ledger_effect=none · 🟠 REVIEW
Préenregistré par la porte légale : `corpus_protocol.preregister(
"MILITARY_SEA_DICTIONARY_1711", …)` → `registered: True`, contre le
freeze `710d4f36e20a32b7`. Ouvert en mode *historical adversarial
testing of a frozen governance calculus*.

STATUT SOURCE : METADATA_OPENED · **PDF_BODY_NO_ACCESS** sur ce siège
et sur la lane émettrice. Tous les chiddushim 1–3 relayés sont donc
🟣 HYPOTHESIS. Rien ici ne prétend avoir lu le corps du livre.

## L'HYPOTHÈSE À TESTER (une seule, falsifiable)

    H1  le lexique 1711 encode une part de structure de transition
        typée SIGNIFICATIVEMENT plus élevée qu'un dictionnaire
        général apparié de la même période
    H0  le lexique est principalement lexical (entité → synonyme)

## LES DEUX DISCIPLINES QUI MANQUENT AU PROTOCOLE RELAYÉ

Sans elles, H1 est inréfutable — et le programme vient d'apprendre
les deux à ses dépens.

### D1 — LE CONTRÔLE APPARIÉ (leçon K_matched)

Mesurer M_k sur 1711 seul ne peut rien produire d'autre qu'un nombre
sans échelle. `against_controls` vient de démontrer qu'une victoire
sur des nulls trop faibles n'est pas une victoire. Il faut donc :

    C_gen   un dictionnaire GÉNÉRAL de 1700–1725, même tradition
            lexicographique, même densité d'entrée
    C_tech  (optionnel, plus fort) un lexique technique NON
            coordonné de la même période — droit, botanique,
            commerce — qui isole « technique » de « coordination »

Sans C_gen : NO_UTILITY_DEMONSTRATED, quel que soit M_k. Avec C_gen
seul, un résultat positif signifie « technique » ; il faut C_tech
pour dire « coordination ».

### D2 — LE CODAGE EN AVEUGLE (leçon 1784 / Franklin)

Le codeur des sept classes (E,R,S,D,C,G,A) doit ignorer de quel
corpus vient l'entrée. Sinon `χ` mesure l'attente du codeur, pas la
langue — c'est exactement la dissociation croyance/traitement que
`proof_ceiling.dissociation_test` encode. Procédure :

    1. mélanger les entrées 1711 et C_gen, étiquettes retirées
    2. coder chaque entrée sur {0,1}^7, sans accès au corpus d'origine
    3. ne ré-attacher les étiquettes qu'APRÈS le codage complet
    4. rapporter l'accord inter-codeur (2 goblins indépendants sur
       un échantillon de 100 ; désaccord = incertitude à porter,
       pas à moyenner)

## MÉTRIQUE — PARAMÈTRE-LIBRE D'ABORD

Le score pondéré O(x) = w_R R + w_S S + … a un défaut que le MDL
avait avant ν : **les poids ne sont pas épinglés**, donc on peut
« gagner » en les réglant. Donc :

    PRIMAIRE (sans paramètre)   M_k = (1/N)·|{i : ‖x_i‖₀ ≥ k}|
                                 rapporté pour k = 2, 3, 4
    SECONDAIRE (épinglé)        O(x) avec poids GELÉS avant le run,
                                 version w-v1, publiés dans ce fichier
                                 avant toute mesure

Poids w-v1, gelés ici : E=0, R=2, S=1, D=1, C=2, G=1, A=2.
(E à zéro : une entrée qui ne fait que nommer une entité n'est pas
de la coordination. Toute modification ultérieure = nouvelle version
w-v2, et les comparaisons inter-versions refusent, comme pour ν.)

## VERDICT — PRÉ-ENREGISTRÉ

    M_3(1711) > M_3(C_gen) avec marge et accord inter-codeur > 0.7
        → NEW_PARAMETERIZATION (« la contrainte de coordination
          sélectionne une langue typée ») — PAS un invariant nouveau
    M_3(1711) ≈ M_3(C_gen)
        → H1 REFUTED ; le chiddush retombe en note d'histoire
    accord inter-codeur ≤ 0.7
        → HOLD : le codage n'est pas assez déterminé pour trancher

## CE QUE LE RÉSULTAT NE POURRA JAMAIS DIRE

    structure détectée  ⊬  les acteurs de 1711 ont consciemment
                           utilisé cette grammaire
    (`indub.reconstructs_corpus_is_not_historically_used`)

## L'ÉQUATION À GARDER (relayée, correcte)

    m* = argmin L(m)  s.c.  ΔS_j(m)=ΔS*  ∧  ΔA_j(m) ≤ 0
                            ∧  ΔΓ_j(m) ≤ ΔΓ_licencié(m)

Le meilleur message est le plus petit qui provoque la bonne
transition **sans fabriquer ni preuve ni autorité**. C'est le pont le
plus solide entre ce corpus et le graph calculus : la transmission
sémantique n'est pas la transmission d'autorité.

## NOTE DE CONFORMANCE (pas un amendement)

Le rendu relayé portait « 🟡 receiver interpretation ». Dans l'Atlas
gelé 🟡 = *sealed*. L'interprétation du receveur est 🟣 *claim*.
Correction de conformité à une règle debout — `wulmoji_axes.
conformance_restoration_is_not_amendment` : cela ne passe pas par la
porte d'amendement, et ne change rien à la palette.
