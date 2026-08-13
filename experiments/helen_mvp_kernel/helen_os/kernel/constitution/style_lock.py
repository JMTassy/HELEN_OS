r"""Style Lock v1 — form rich, claims sober; the anti-vibe law made
executable.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The operator's STYLE LOCK v1, with its own discipline encoded so the
style can never erase the state:

    FORM = RICHE · CLAIMS = SOBRES · RECEIPTS = EXPLICITES ·
    UNKNOWN = VISIBLE · ACTION = COURTE

    beautiful seal  does not entail  admission

THE FOUR CATEGORIES stay distinct, forever:

    DECORATIVE (✨) · RECEIPT (📜) · ADMITTED (⚖️) · UNRESOLVED (🌿)

ANTI-VIBE LAW, executable: a status word (CANON, PASS, SEALED,
VERIFIED, ADMITTED, LEDGER) written without its corresponding witness
is refused as E_DECORATIVE_STATUS — decoration may never wear the
vocabulary of state.

THE COLOR COLLISION (Source Atlas 'color as state' vs Style Seed
'color for navigation') is resolved here as a RECOMMENDATION carrier,
not a ruling — the ruling is the operator's admission. The proposed
law that dissolves the three severe clashes:

    NO STATE IS EVER ENCODED BY COLOR ALONE.
    State = word + glyph, decoloration-invariant.
    Color = navigation/attention channel only.

This is the Elinvar law applied to rendering: decoloration (grayscale,
color-blind reader, plain terminal) is a constitutionally IRRELEVANT
perturbation — if the state changes when the color is stripped, the
encoding was unconstitutional. chi_state under decoloration must be 0.
Both grammars then survive: the Atlas keeps its state ontology (as
words: unknown/observed/claim/review/admitted/sealed/replayable/
breach), the Style Seed keeps its eight navigation channels, and
'one color, one meaning' holds because color only ever means
attention.

Relay note, witnessed this run: the sibling collision report misquoted
the canon it was defending (canon: yellow=sealed, red=breach; report:
yellow=breach). The collision matrix itself needed the relay law.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

CATEGORIES = ("DECORATIVE", "RECEIPT", "ADMITTED", "UNRESOLVED")

STATUS_WORDS = frozenset({"CANON", "PASS", "SEALED", "VERIFIED",
                          "ADMITTED", "LEDGER"})

# the Style Seed's eight channels — NAVIGATION plane only
NAVIGATION_CHANNELS = {
    "red": "core/risk/fail/contradiction",
    "orange": "action/movement/next",
    "yellow": "evidence/facts/witnesses",
    "green": "pass/valid/grounded",
    "blue": "chiddush/insight",
    "purple": "meta/architecture",
    "white": "law/invariant",
    "herb": "hold/unknown/unresolved",
}

# the Source Atlas state ontology — WORD plane (color-independent)
ATLAS_STATES = ("unknown", "observed", "claim", "review", "admitted",
                "sealed", "replayable", "breach")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the anti-vibe law ───────────────────────────────────────────────────

def stamp(word: str, witness_ref: str | None) -> dict:
    """A status word may appear only with its witness. Without one it
    is not downgraded to decoration — it is REFUSED, because
    decoration wearing state vocabulary is how vibes become records."""
    if word.upper() in STATUS_WORDS and not witness_ref:
        return {"word": word, "rendered": False,
                "reason": "E_DECORATIVE_STATUS",
                "law": "beautiful seal does not entail admission; a "
                       "status word without its witness is refused, "
                       "not decorated"}
    return {"word": word, "rendered": True,
            "category": "RECEIPT" if witness_ref else "DECORATIVE",
            "witness": witness_ref}


def categorize(token: dict) -> dict:
    """Every rendered token belongs to exactly one of the four
    categories; none is convertible by styling."""
    cat = token.get("category")
    if cat not in CATEGORIES:
        return {"ok": False, "reason": "E_UNKNOWN_CATEGORY"}
    return {"ok": True, "category": cat,
            "law": "decorative, receipt, admitted and unresolved are "
                   "different categories; styling converts none"}


# ── the decoloration law (Elinvar for rendering) ────────────────────────

def render_state(word: str | None, glyph: str | None,
                 color: str | None) -> dict:
    """A state token must survive grayscale: strip the color and the
    state must still be fully determined by word+glyph."""
    decolored = {"word": word, "glyph": glyph}
    if word in ATLAS_STATES:
        return {"state": word, "survives_decoloration": True,
                "color_role": "redundant_glow_only",
                "decolored_reading": decolored}
    if color and not word:
        return {"state": None, "survives_decoloration": False,
                "reason": "E_STATE_BY_COLOR_ALONE",
                "law": "no state is ever encoded by color alone; a "
                       "color-blind reader and a grayscale terminal "
                       "must read the same constitution"}
    return {"state": None, "survives_decoloration": word is not None,
            "reason": None if word else "E_EMPTY_STATE_TOKEN"}


def chi_decoloration(tokens: tuple) -> dict:
    """chi_state under decoloration: fraction of state tokens whose
    reading changes when color is stripped. Must be 0."""
    if not tokens:
        raise ValueError("E_NO_TOKENS")
    broken = [t for t in tokens
              if not render_state(t.get("word"), t.get("glyph"),
                                  t.get("color"))
              ["survives_decoloration"]]
    return {"n": len(tokens), "broken": len(broken),
            "chi_decoloration": round(len(broken) / len(tokens), 6),
            "elinvar_for_rendering": not broken}


# ── the collision resolution: a recommendation, never a ruling ─────────

def collision_resolution() -> dict:
    """Record of how the collision was actually settled. This
    module's own candidate — 'color = navigation only, state = word +
    glyph' — was NOT adopted. The operator ruled differently and
    better (T-COLOR-01): do not replace the palette, FACTOR THE STATE
    SPACE. Colour keeps carrying epistemic phase (the Atlas stays
    frozen, one colour => one epistemic meaning); the rival concepts
    move to an orthogonal marker axis. The candidate here would have
    demoted the palette to decoration to buy the same peace; the
    ruling buys it while keeping the palette load-bearing.

    Recorded as a superseded proposal, not quietly deleted: a lane
    that erases its rejected candidates cannot be audited."""
    return {"status": "CANDIDATE_SUPERSEDED_BY_RULING",
            "ruled_by": "OPERATOR",
            "ruling": "T-COLOR-01 — factor the state space; see "
                      "wulmoji_axes.py",
            "this_modules_candidate": ("colour = navigation only; "
                                       "state = word + glyph"),
            "candidate_adopted": False,
            "why_the_ruling_is_stronger": ("it preserves colour as a "
                                           "load-bearing epistemic "
                                           "axis instead of demoting "
                                           "it to decoration"),
            "silent_supersede": False,
            "relay_note": "the sibling collision matrix first "
                          "misquoted the canon it defended "
                          "(yellow=sealed, red=breach per "
                          "docs/proposals/HELEN_SOURCE_ATLAS_V1.md, "
                          "verified in-repo); its third report "
                          "self-corrected to a stable 4/8",
            "law": "unreceipted interpretive drift is forbidden; a "
                   "receipted operator ruling is the lawful door"}
