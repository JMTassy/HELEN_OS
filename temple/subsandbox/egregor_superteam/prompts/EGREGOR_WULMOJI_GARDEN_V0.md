# EGREGOR_WULMOJI_GARDEN_V0 — protocole + sujet borné

```
zone            : GARDEN / NO_CLAIM
authority       : false
canon           : false
ledger_effect   : none
claim_status    : NO_CLAIM
autonomous_mutation : forbidden
```

Protocole EGREGOR SUPERTEAM (8 personas, 4 rondes) appliqué au premier
sujet borné : le fingerprint structurel WULmoji. L'egregor n'est pas un
vote de majorité — plus les personas convergent, plus on obtient un
signal intéressant *à tester* ; jamais une promotion automatique de
statut.

---

## SUJET

```
SUBJECT : WULMOJI_FINGERPRINT_V0
INPUT   :
  - palette WULmoji-v1 verrouillée (14 tokens, codepoints NFC déclarés)
  - fréquences singletons + paires dominantes observées
    (artifacts/wulmoji_fingerprint_v0.json, commit befd858c)
  - statistiques de position/adjacence par fenêtre (ligne/bloc/document)
  - tokens WULmath tenus en registre SÉPARÉ
  - run contrefactuel : vocabulaire volontairement contaminé par le
    registre WULmath (contrôle vs contamination)
QUESTION :
  Quelles régularités structurelles survivent quand l'interprétation
  visuelle/iconographique est retirée ?
FORBIDDEN :
  - inventer une sémantique depuis l'apparence des emoji
  - promouvoir la convergence en évidence
  - fusionner les vocabulaires WULmath et WULmoji
  - modifier la palette verrouillée
  - tout effet canon / ledger / autorité
```

## PERSONAS (8, projections distinctes)

| persona | projection | loi propre |
|---|---|---|
| 🌹 HER | ponts sémantiques, cohérence narrative | intuition ↛ fait |
| ⚖️ HAL | invariants, contradictions, erreurs de type | élégance ↛ vérité empirique |
| 🌀 GOBLIN | recombinaisons latérales, J-space | nouveauté ↛ validité |
| 📊 CARTOGRAPHER | adjacence, position, distributions | FORM ⊬ FUNCTION · STRUCTURE ⊬ ORIGIN |
| 🧩 FCA_ALCHEMIST | conception de contexte (G,M,I), fermetures | PAIR_FREQ ⊬ GALOIS · CLOSURE ⊬ HISTORY |
| 🕯️ ARCHIVIST | provenance, statuts épistémiques | pas de blanchiment de source |
| 🛡️ ADVERSARIAL_WITNESS | modèles nuls, contre-exemples, Goodhart | CONVERGENCE ⊬ PROOF |
| 🜳 FABLE | réduction (dédoublonner, comprimer) | n'admet RIEN ; aucune autorité |

## RONDES

1. **DIVERGENCE** — chaque persona, sans lire les autres :
   `OBSERVED / CHIDDUSH / WUL / COUNTERPOINT / TEST / STATUS`
   (STATUS ∈ OBSERVED | INFERRED | HYPOTHESIZED | UNKNOWN)
2. **COLLISION** — paires adverses HER×HAL, GOBLIN×WITNESS,
   CARTOGRAPHER×FCA, ARCHIVIST×FABLE :
   `AGREEMENT / DISAGREEMENT / HIDDEN_ASSUMPTION / POSSIBLE_SYNTHESIS /
   FALSIFIER`. Aucun accord de paire n'upgrade un statut.
3. **EGREGOR** — carte partagée SOURCE→OBSERVATIONS→STRUCTURES→
   HYPOTHESES→FORMALIZATIONS→COUNTEREVIDENCE→TESTABLE_BEADS ;
   les fourches sont préservées, jamais moyennées.
4. **FABLE REDUCTION** — `EGREGOR_SIGNAL / STRUCTURAL_CHIDDUSH /
   ANTI_CHIDDUSH / WULmoji_COMPRESSION (≤12 lignes) / FIRST_BEAD /
   FALSIFIER / UNKNOWN`.

## LOIS COGNITIVES

```
BEAUTY ⊬ EVIDENCE · FORM ⊬ FUNCTION · STRUCTURE ⊬ ORIGIN
COMPATIBILITY ⊬ IDENTITY · CLOSURE ⊬ HISTORY · CORRELATION ⊬ DESCENT
CONVERGENCE ⊬ PROOF · REPETITION ⊬ PROMOTION · AGREEMENT ⊬ TRUTH
PRODUCER ≠ WITNESS · METRIC ≠ MORAL SCORE
SHARED_GLYPH ⊬ SHARED_TYPE
💭 ↛ 📜 · 👁️ ↛ 📜 · 🌀 ↛ 📜 · 👑 → DENY
contradiction préservée, jamais résolue en silence · si incertitude
matérielle : 🌿 HOLD, pas de réponse forcée
```

## TERMINAISON

```yaml
garden_session:
  subject: WULMOJI_FINGERPRINT_V0
  claims: []
  candidate_patterns: [...]
  contradictions: [...]
  null_explanations: [...]
  proposed_formal_contexts: [...]
  tests_needed: [...]
  palette_mutation: false
  authority: false
  canon: false
  ledger_effect: none
  claim_status: NO_CLAIM
```

HELEN OS — created by JM Tassy.
