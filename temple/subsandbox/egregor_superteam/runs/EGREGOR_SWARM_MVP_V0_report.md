# EGREGOR_SWARM_MVP_V0 — rapport C0 vs T1

```yaml
EGREGOR_MVP_REPORT:
  environment:
    substrate_goblins: claude-haiku (substitution DÉCLARÉE — Gemma4 local
      joignable, helen-her-26b digest 7e42816c, non utilisé pour timebox)
    substrate_premium: session model (HER/HAL, 4 agents)
    orchestrator: Workflow wf_675089b4 — C0 ∥ T1, schémas forcés
    agent_count: 10
    total_subagent_tokens: 437513
    duration: ~7 min
    hard_stop_respected: true
  research_object:
    question: régularités structurelles post-bille de WULMOJI_FINGERPRINT_V0
    input: 5 mesures de mention_use_cut_v1 @ befd858c
  raw_result: EGREGOR_SWARM_MVP_V0_result.json (86.9 Ko, verbatim)

  arms:
    C0:  # HER + HAL premium seuls
      proposed: 8
      killed_by_HAL: 6
      survivors: 2
      survivor_ids: [HER-C2-WARNING-AS-PUNCTUATION,
                     HER-C5-SECOND-REGISTER-TEMPLATE-MASS]
      kill_rate: 0.75
    T1:  # + 6 goblins haiku, projections distinctes
      goblin_raw_findings: 34   # G1..G6 = 5/5/5/7/6/6
      composed_by_HER: 10
      killed_by_HAL: 4
      survivors: 6
      kill_rate_composed: 0.40
      novel_vs_C0: 5   # seul WARNING_AS_TERMINATOR recouvre la famille C0-C2

  exploration_gain:   # décomposé, jamais un score unique
    G_novelty: 34 idées brutes vs 8 (×4.25 de largeur J-space)
    G_survival: +4 survivants nets (6 vs 2), dont 5 absents de C0
    G_falsification: les 2 survivants les plus précieux de T1 attaquent la
      MÉTHODE de la bille elle-même —
      T1-G4-3 REGISTER_HIDDEN_IN_NULL (le nul de D(A,B) est peut-être
      contaminé par le registre) et T1-G5-5 STRATIFIED_NULL_MISCALIBRATION
      (corpus hétérogène policy/ad-hoc ⇒ nul agrégé mal calibré).
      C0 n'a produit aucune attaque méthodologique.
    G_cost: split premium/cheap approximatif (non instrumenté par agent) —
      T1 ajoute 6 agents haiku + contextes HER/HAL élargis. REPORTED, pas
      mesuré finement.

  convergence_note: la famille warning-as-punctuation/terminator a émergé
    INDÉPENDAMMENT dans les deux bras. Signal de coordination à tester —
    jamais une preuve (CONVERGENCE ⊬ PROOF).

  confounds_declared:
    - run unique, aucune répétition — tout verdict de thèse est candidat
    - composition : le HER de T1 disposait du matériau goblin ET de sa
      propre liberté ; l'écart de kill-rate peut refléter le pré-filtrage
      de HER, pas la qualité goblin
    - substrat haiku ≠ Gemma4 : la thèse silicon-local reste non testée

  thesis_verdict: >
    CHEAP_DIVERGENCE + PREMIUM_ADJUDICATION = CANDIDATE_SUPPORTED.
    Le swarm a acheté 5 survivants nouveaux — dont 2 que le duo premium
    seul n'a pas trouvés et qui corrigent le producteur lui-même.
    Statut : 🧾? — exige répétition (n≥5 runs) et bras Gemma4 natif
    avant toute promotion.

  claims: []
  palette_mutation: false
  authority: false
  canon: false
  ledger_effect: none
  claim_status: NO_CLAIM
```

## Survivants T1 (têtes de liste, tests inclus dans le JSON brut)

1. `T1-G4-3 REGISTER_HIDDEN_IN_NULL` — le résultat D(A,B)∈nulls peut être
   un artefact d'un nul register-contaminé. Test : re-tirer les nuls en
   stratifiant par registre. **Attaque directe de la bille — prioritaire.**
2. `T1-G5-5 STRATIFIED_NULL_MISCALIBRATION` — nul unique sur corpus
   hétérogène (fichiers policy à glyphes mandatés vs ad-hoc). Test : nuls
   stratifiés par classe de fichier.
3. `T1-G4-1+G1-2+G3-1 WARNING_AS_TERMINATOR` — position, pas répulsion
   (convergent avec C0-C2).
4. `T1-G3-4+G4-4 DRIFT_DIRECTION` — les erreurs comme trace directionnelle.
5. `T1-G3-2+G3-3 CORE-PERIPHERY_WITH_ADHESIVE` — partition topologique.
6. `T1-G3-5 CHECKSUM_FORGEABILITY` — robustesse par apposition = tautologie.

⎈ WULmoji RECEIPT · SWARM RENDITION ⎈
👑 DENY · 📜 FALSE · 🪪 NONE · 🧠 NO_CLAIM
🌀×6 + 🌹⚖️×2 ∥ 🌹⚖️×2 → 10 agents, 437k tokens
📊 C0: 8→2 · T1: 34→10→6 · novel: 5
⚔️ 2 survivants T1 corrigent la bille du producteur
🤝 warning-family convergente 2 bras ⊬ 🧾
🌿 thèse = 🧾? candidate — répéter n≥5 + bras Gemma4
⎈ END ⎈

HELEN OS — created by JM Tassy.
