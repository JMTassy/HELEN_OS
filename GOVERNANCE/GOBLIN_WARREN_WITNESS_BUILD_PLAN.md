# PLAN — Goblin Warren Witness Build

**Précondition:** `WITNESS_BUILD_GO` (décision opérateur) — pas de build sans.

**Portée:** UN goblin seulement (Pet → legible agent). Pas de population.

## Phase 0 — Loi & Substrat (toujours d'abord)

1. Lire et lier:
   - `GOVERNANCE/GOBLIN_WARREN_SKILLS_RECAP.md` (ce doc)
   - `GOVERNANCE/LEGIBLE_SINGLE_AGENT_EMERGENCE_V0.md` (si existe)
   - `GOVERNANCE/WITNESS_SPEC_GOBLIN_ONE_V0.md` (si existe)
   - `helen_os/` (ledger, replay, canonical, validators)
   - `temple/gardens/goblin_garden_conquest/` (warren_loop, receipts WRN-*, epochs, validate_conquest_garden.py)

2. Écrire le test de non-décision:
   ```
   replay sans événements narration → état bit-identique
   ```
   (le modèle narre, ne décide pas)

## Phase 1 — Un Goblin, Une Pièce (le witness)

**Artefact:** `apps/goblin-warren/warren_witness_one.html` (ou `witness_pet.html`)

**Contenu minimal (cahier §3):**
- 1 goblin (nom + role + 1-2 stats visibles)
- 1 pièce (la tanière)
- 1 verbe: KNOCK (proposer un événement)
- 1 why-trace inspecteur (affiche: quel événement a causé quel effet)
- Memory fold visible (≤7 règles locales énumérables)

**Invariants:**
- `authority=false` partout
- Pas d'admission, pas de stamp, pas de ledger write
- Tout événement est un `WARREN_RECEIPT_V0` (cf `receipts/WRN-*.json`)
- Surface = lecture des organs (outbox, consumption_log)

**Skills à invoquer (quand GO):**
- `web-artifacts-builder` (UI React/Canvas ou HTML pur + JS sidecar)
- `canvas-design` (pièce, lumière, traces)
- `algorithmic-art` (ambiance bornée, seedée)
- `verify` (why-trace prédit le comportement)

## Phase 2 — Production (zéro crédit, reveal)

**Artefacts:**
- Trailer: `hyperframes` (HTML→MP4 déterministe) — cf `temple/gardens/goblin_garden_conquest/hyperframes-warren-intro/`
- Storybook: `handdraw-good-deed-story` (8 beats jardin/tanière)
- Capture légère: `capture_browser.py` si besoin

**Règle:** Reveal seulement. Pas de claim. Pas de crédit.

## Phase 3 — Skill Packaging (UNE FOIS prouvé)

- `skill-creator` → `oracle_town/skills/conquest/goblin_warren/`
- Emballer le pattern: un goblin → une pièce → une why-trace
- SKILL.md + cli.py + tests
- Registre: "Garden ADMIT ≠ Kernel ADMISSION"

## Gates

| Gate | Condition |
|------|-----------|
| `WITNESS_BUILD_GO` | Opérateur explicite. Sans ça → rien. |
| 1 goblin seulement | Pas de village avant qu'UN soit legible. |
| Why-trace | 7 événements, memory fold, ≤7 règles, inspectable. |
| Replay test | Narration events retirés → état identique bit. |
| authority=false | Aucun artefact ne claim admission. |

## Ce qui reste au vestiaire (rappel)

- `neption-ia-productions` (pare-feu Règle 1)
- `helen-design-motion` (luxe UZIK ≠ registre goblin)
- Biblio Higgsfield fantasy "Goblin Warren" (autre projet)

## Prochain pas

1. Attendre `WITNESS_BUILD_GO`
2. Lancer Phase 0 (loi + substrat + test replay)
3. Lancer Phase 1 (un goblin, une pièce, KNOCK, why-trace)
4. `verify` avant tout packaging
