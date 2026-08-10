# WULMOJI_STRUCTURE_UPGRADE_V0

```
banner          : 🔵 OBSERVED
zone            : GARDEN / NO_CLAIM
authority       : false
admission       : none
ledger_effect   : none
status          : PROPOSAL — amendment candidate for ops/wulmoji_enhancer
method          : oracle_town/skills/epistemics/structure_over_form (L1)
artifact        : oracle_town/skills/epistemics/structure_over_form/
                  artifacts/wulmoji_fingerprint_v0.json
artifact_sha256 : 0575ee66ddf6d0cd… (full hash embedded in artifact)
measured_commit : befd858c9302 (corpus = *.md tracked at this HEAD)
replay          : verified — two runs, identical payload_sha256
date_recorded   : 2026-08-07
```

Upgrade of the WULmoji doctrine on two axes: **identity** (what makes a
symbol *that* symbol) and **structure** (what makes a seal authentic).
Grounded in the operator principle: what carries meaning is not the signs
but the structure assembling them — measurable as unordered pair
co-occurrence — and the form/value link is justified by structure, never
the reverse.

---

## 1. Identity law — codepoint, never looks (lesson B5)

The adversary round on `ingest_receipt_v1` proved (breach B5) that symbol
filters trusting visual form leak: invisible non-Cf joiners (U+034F, Mn),
homoglyphs, dotless variants. WULmoji is Unicode symbols; the same surface
exists here. Proposed law:

1. The palette is defined as **explicit NFC codepoint sequences**
   (embedded in the fingerprint artifact under `palette_codepoints`).
   A symbol matches by exact sequence or it does not match.
2. Any parser/auditor of WULmoji text matches bytes, not looks.
   `FORM ⊬ IDENTITY` holds at the byte level too.
3. Near-forms are counted and reported, never silently folded.

**Measured now**: the corpus contains **47 bare `⚠` (U+26A0 without
U+FE0F)** against 234 canonical `⚠️`, plus 1 bare `✍`. That is real,
existing identity drift — invisible to the eye, visible to the byte.
V1 decision needed: canonicalize on VS16-present, migrate the 47, and have
the auditor flag bare forms thereafter.

## 2. Structural fingerprint — the seal behind the seal

Computed deterministically over the declared corpus (901 `*.md` **tracked
at HEAD `befd858c`**, 224 palette-bearing; excludes `deprecated/` and
`.claude/`; every corpus file sha256-receipted in the artifact; replay
verified — same bytes → same `payload_sha256`).

**Corpus-rule incident, kept on record.** The first corpus rule was
"working-tree `*.md`". Replay diverged immediately: this report itself —
which contains palette symbols — had entered the corpus it describes. The
observer had become an actor. The rule was corrected to *tracked-at-HEAD*
(`git ls-files`), which closes the hole structurally: the skill's
uncommitted outputs cannot measure themselves, and the measured commit is
recorded in the artifact. The divergence was not noise; it was the
fingerprint catching its own contamination on the first try.

Symbol frequencies (top): ⚠️ 234 · 🟢 162 · 🟣 146 · 🔴 128 · 🔵 123 ·
🟡 101 · ⚪ 68 · 🔁 67. Dominant unordered pairs, stable across all three
windows (line / block / document):

| pair | block-window count |
|---|---|
| 🔵 structure — 🟢 validation | 65 |
| 🟡 cost — 🟢 validation | 61 |
| 🔴 identity — 🟢 validation | 57 |
| 🟣 emergent — 🔵 structure | 54 |

Reading (L1, empirical, no more): the language's backbone is
**system↔gate-pass** — WULmoji is used to talk about structures being
validated, costs being validated, identity being validated. The
distribution is far from uniform (91 possible pairs, mass concentrated in
~8): the corpus has a *shape*. That shape is the fingerprint.

**Use**: any future WULmoji-bearing artifact whose pair distribution
diverges sharply from the fingerprint is a *signal* — innovation to
instruct or imitation to inspect — never a silent pass. Structure is
costly to forge; glyphs are free. `GLYPH = CLAIM · STRUCTURE = RECEIPT`.

## 3. Density-rule audit (free by-product)

Doctrine says max 1 symbol/line. The fingerprint counts **100 multi-symbol
lines**. Sampled: most are **legend/table lines** (palette definitions in
CLAUDE.md and skill docs), not prose violations. Which surfaces a real
limitation of this V0:

**`MENTION ≠ USE`** — L1 counting does not yet distinguish a symbol being
*used* (color-grading a line) from being *mentioned* (defined in a
legend). Legend lines inflate both pair counts and violation counts.
Declared, not hidden. V1 worklist: exclude fenced code blocks and table
rows tagged as legends, then re-run; the fingerprint hash will change and
both versions stay comparable.

## 4. What this upgrade does NOT do

- It does not touch `ops/wulmoji_enhancer/SKILL.md` (DOCTRINE, calibrated
  2026-04-20) — amendment requires its own procedure.
- It does not promote anything: the fingerprint is `OBSERVED`, the
  interpretation in §2 is `AURA_PROPOSED_READING`, the laws in §1 are
  amendment candidates awaiting operator decision.
- It does not claim the corpus choice is the only defensible one — the
  rule is declared in the artifact and swappable; re-running under a
  different declared rule is one command.

## 5. Replay

```
.venv/bin/python oracle_town/skills/epistemics/structure_over_form/fingerprint.py \
  --root . \
  --out /tmp/wulmoji_fingerprint_replay.json
```

Same corpus bytes ⇒ same `payload_sha256`. Divergence ⇒ the corpus moved,
and the manifest says exactly which file.

---

```
seal : FORM ⊬ IDENTITY · GLYPH ⊬ RECEIPT · MENTION ≠ USE
       STRUCTURE FALSIFIES STRONGLY, CONFIRMS WEAKLY
```

HELEN OS — created by JM Tassy.
