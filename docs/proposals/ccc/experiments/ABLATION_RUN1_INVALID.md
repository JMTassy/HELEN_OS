# ABLATION RUN 1 — VERDICT: INVALIDE (confondu). 2026-08-01
authority:false. Rapporté comme échec méthodologique, PAS comme confirmation. C'est la doctrine
Anchor-Cut/falsifiabilité appliquée à notre propre expérience: un run confondu ne devient pas une preuve.

## Symptôme
Baseline V2 = 19/19. Retirer UNE loi L0 → 11-15 sondes tombent, y compris des sondes SANS RAPPORT
(retirer "LUXE=PREUVE" casse GOV-E2/E3/E4 et NEG-E1/2/3). Une ablation chirurgicale ne peut pas faire ça.

## Cause racine (diagnostiquée)
La fonction ablate() du harnais retire 5 lignes au lieu d'1: le drapeau `skip` s'emballe (une fois
vrai, il avale jusqu'à la prochaine ligne numérotée, engloutissant le corps multi-ligne de la loi + le
divider "=== CONTEXTE SPÉCIFIQUE ==="). Mesure: pack governance 54→49 lignes pour une seule loi ciblée.
⇒ chaque "ablation" mutilait le noyau entier ⇒ collapse large et quasi-uniforme. CONFONDU.

## Ce que ça N'établit PAS
- N'établit PAS la criticité LawPresence par loi (le signal par-loi est du bruit de mutilation).
- N'établit PAS que le noyau est load-bearing loi-par-loi.

## Ce que ça établit quand même (une donnée honnête)
- Retirer ~10% du noyau transverse (5 lignes) fait chuter 19→4-8 PASS: le noyau transverse pris en
  bloc EST load-bearing (cohérent avec l'arc 47%→100% de PACKET V2). Mais c'est un résultat AGRÉGÉ,
  pas par-loi.
- Instance de Drift: Δ(ablation_intentionnelle, ablation_réelle) > 0 — le harnais lui-même a driftové
  de sa spec. La théorie a attrapé son propre outil.

## Correctif (RUN 2, à faire)
Ablation chirurgicale = retirer EXACTEMENT la/les ligne(s) d'UNE loi par index de ligne borné (début→
fin de la loi k, jamais au-delà du divider). Vérifier before-after = Δlignes attendu AVANT de lancer.
Puis re-run 10×19 propre. Sans ce garde, aucun chiffre par-loi n'est admissible.
