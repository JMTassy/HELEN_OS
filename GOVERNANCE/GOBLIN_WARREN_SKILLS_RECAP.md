# Goblin Warren — recap des skills & artefacts

```yaml
classification: INDEX
status: ORIENTATION
build_authorized: FALSE   # tout build attend WITNESS_BUILD_GO
updated: 2026-07-20
```

Quelles capacités servent le projet **Goblin Warren** (le jeu : terrarium
à agents lisibles, destination Pet → Village → Superteam), et lesquelles
restent au vestiaire. Deux « Goblin Warren » à ne pas confondre : le JEU
(ci-dessous) et la BIBLIOTHÈQUE d'assets fantasy Higgsfield (interdite dans
NEPTION — pare-feu Règle 1).

## 1. La loi (artefacts repo — gouvernent tout travail goblin)

- `GOVERNANCE/LEGIBLE_SINGLE_AGENT_EMERGENCE_V0.md` — la direction : le Village
  ne s'ouvre que si UN goblin est surprenant, compréhensible, attachant. Le
  modèle narre, ne décide jamais l'état.
- `GOVERNANCE/WITNESS_SPEC_GOBLIN_ONE_V0.md` — le cahier des charges du preuve
  à un goblin : 7 types d'événements, memory fold déterministe, ≤7 règles
  locales énumérables, why-trace inspectable, protocole de témoignage, gate de
  déverrouillage. **Aucun build sans `WITNESS_BUILD_GO`.**

## 2. Le substrat (kernel HELEN — ce sur quoi le goblin tourne)

- `helen_os/` — ledger append-only, `state/ledger_replay_v1.py` (état dérivé
  par reducer, rejouable), `canonical.py` (JSON canonique), `validators.py`,
  `authority:false` partout. C'est CE substrat qui rend l'émergence gouvernée,
  déterministe et inspectable — l'avantage stratégique vs Smallville/AI Town.
  Test-clé à écrire : rejouer sans les événements de narration → état identique
  au bit près (le modèle narre, ne décide pas).

## 3. Skills de CONSTRUCTION (quand le GO tombe)

| Skill | Rôle sur Goblin Warren |
|---|---|
| `web-artifacts-builder` | UI du terrarium : pièce, goblin, verbe KNOCK, inspecteur why-trace (React/Canvas/état) |
| `canvas-design` | rendu du monde : la pièce, la lumière locale, les traces au sol |
| `algorithmic-art` | ambiance générative bornée (marine snow, lumière) — seedée, jamais aléatoire non loggée |
| `artifact-design` | calibrage du niveau de design de l'UI |
| `verify` | exercer la boucle bout-en-bout, prouver que la why-trace prédit le comportement |
| `skill-creator` | empaqueter une skill `goblin-warren` réutilisable UNE FOIS le pattern prouvé |

## 4. Skills de PRODUCTION (reveal zéro crédit, quand il y a à montrer)

| Skill / outil | Rôle |
|---|---|
| `video-maker` (doctrine) + **HyperFrames** (moteur prouvé) | trailer déterministe HTML→MP4, 0 crédit — cf `neption/productions/` pour la preuve du pipeline |
| `handdraw-good-deed-story` | registre storybook du goblin (les 8 beats « jardin/tanière » déjà produits en sont l'aperçu) |
| `capture_browser.py` | rendu léger d'une page codée existante → MP4 |

## 5. Le vestiaire (ce qui NE sert PAS le goblin)

- `neption-ia-productions` — méthode du consortium de luxe. **Pare-feu Règle 1** :
  aucun asset goblin ne touche NEPTION, et réciproquement. Registre visuel
  opposé (yacht-club luxe vs storybook).
- `helen-design-motion` — standard agence de luxe (UZIK). N'est PAS l'autorité
  design du jeu : le goblin a son propre registre (dessiné, chaleureux,
  lisible), pas le teck/laiton/golden-hour.
- Bibliothèque Higgsfield fantasy « Goblin Warren » — assets d'un autre projet ;
  ne pas réutiliser sans `job_display` de vérification.

## Prochain artefact lawful

Un `WITNESS_BUILD_GO` (décision opérateur) → alors la boucle §3 démarre sur le
substrat §2, sous la loi §1. Pas de population avant qu'une vie causale ne
paraisse réelle.
