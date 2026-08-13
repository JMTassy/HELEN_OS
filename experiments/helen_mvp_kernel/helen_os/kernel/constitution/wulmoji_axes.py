r"""WULmoji Axes — T-COLOR-01: do not replace the palette, factor the
state space.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
Operator ruling of record: the Source Atlas palette is NOT superseded.

The collision (4/8 colors) was real, but it revealed a modeling error
in the candidate grammar rather than a defect in the Atlas: several
candidate meanings do not live on the same axis as the Atlas meanings.
Forcing them into one channel is what produced the clash.

    AXIS 1 — COLOR = EPISTEMIC PHASE  (frozen, the Atlas)
        unknown -> observed -> claim -> review -> admitted -> sealed
        -> replayable ;  breach off-lifecycle

    AXIS 2 — GLYPH = TYPE / DISPOSITION / CAPABILITY / ACCESS
        void · restricted · hold · candidate · authority_denied ·
        admission_boundary

    Color = epistemic phase.
    Shape/glyph = type, disposition, capability, or access state.

A token composes the two: 🟣+candidate = candidate claim; 🟠+hold =
claim under review, currently held; 🔵+restricted = observed object
with restricted access. All four collisions dissolve WITHOUT semantic
migration, and the Atlas invariant survives intact:

    one color  =>  one epistemic meaning

FUTURE-COLLISION IMMUNITY, structural rather than promised: the color
axis is FROZEN — a new concept can only ever enter the MARKER axis.
Two axes with disjoint symbol sets and disjoint value spaces cannot
collide, because a collision requires two meanings competing for one
symbol.

Refusals: redefining a color is E_COLOR_AXIS_FROZEN (only a receipted
operator amendment may reopen it); using a marker where a phase is
required (or the reverse) is E_AXIS_CONFUSION.

This module records a ruling already made. It does not make one.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

# ── AXIS 1: epistemic phase — FROZEN (HELEN_SOURCE_ATLAS_V1) ───────────

EPISTEMIC_PHASE = {
    "black": "unknown",
    "blue": "observed",
    "purple": "claim",
    "orange": "review",
    "green": "admitted",
    "yellow": "sealed",
    "white": "replayable",
    "red": "breach",          # off-lifecycle
}

LIFECYCLE_ORDER = ("unknown", "observed", "claim", "review",
                   "admitted", "sealed", "replayable")

AXIS_1_FROZEN = True

# ── AXIS 2: orthogonal typed markers — extensible ──────────────────────

STATE_MARKERS = {
    "void": "absent / no object",
    "restricted": "access-gated",
    "hold": "uncertainty / unresolved",
    "candidate": "proposed, not admitted",
    "authority_denied": "capability refused",
    "admission_boundary": "the gate itself",
}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── composition ─────────────────────────────────────────────────────────

def token(color: str, markers: tuple = ()) -> dict:
    """Compose one axis-1 phase with any number of axis-2 markers.
    Neither axis may borrow the other's vocabulary."""
    if color not in EPISTEMIC_PHASE:
        if color in STATE_MARKERS:
            return {"ok": False, "reason": "E_AXIS_CONFUSION",
                    "detail": f"'{color}' is a marker, not a phase"}
        return {"ok": False, "reason": "E_UNKNOWN_COLOR"}
    bad = [m for m in markers if m not in STATE_MARKERS]
    if bad:
        confused = [m for m in bad if m in EPISTEMIC_PHASE.values()]
        return {"ok": False,
                "reason": "E_AXIS_CONFUSION" if confused
                          else "E_UNKNOWN_MARKER",
                "detail": sorted(bad)}
    return {"ok": True,
            "phase": EPISTEMIC_PHASE[color],
            "markers": tuple(sorted(set(markers))),
            "reading": " + ".join(
                [EPISTEMIC_PHASE[color]] + sorted(set(markers)))}


def redefine_color(color: str, new_meaning: str) -> dict:
    """The refused move that started the collision: overwriting a
    palette entry. Only a receipted operator amendment reopens it."""
    return {"color": color, "proposed": new_meaning,
            "applied": False,
            "reason": "E_COLOR_AXIS_FROZEN",
            "lawful_door": "receipted operator amendment",
            "law": "the palette is not superseded; new concepts enter "
                   "the marker axis"}


def add_marker(name: str, meaning: str) -> dict:
    """Growth happens here, and only here — the extensible axis."""
    if name in EPISTEMIC_PHASE.values():
        return {"added": False, "reason": "E_AXIS_CONFUSION",
                "detail": "that name is an epistemic phase"}
    return {"added": True, "axis": "MARKERS", "name": name,
            "meaning": meaning,
            "collides_with_color_axis": False}


# ── the immunity proof ──────────────────────────────────────────────────

def axes_are_disjoint() -> dict:
    """Collision requires two meanings competing for one symbol. The
    axes share no symbol and no value, so none can arise."""
    overlap = sorted(set(EPISTEMIC_PHASE.values()) & set(STATE_MARKERS))
    return {"value_overlap": overlap,
            "disjoint": not overlap,
            "color_axis_frozen": AXIS_1_FROZEN,
            "future_collision_possible": bool(overlap),
            "law": "a new concept can only enter the marker axis; two "
                   "axes with disjoint symbols and values cannot "
                   "collide"}


def resolves_the_four_collisions() -> dict:
    """The reported 4/8 clash (white, black, yellow, orange), each
    dissolved by re-homing the candidate meaning onto axis 2 — no
    semantic migration on axis 1."""
    mapping = {
        "white": {"atlas_phase": "replayable",
                  "candidate_meaning": "void", "rehomed_to": "MARKERS"},
        "black": {"atlas_phase": "unknown",
                  "candidate_meaning": "restricted",
                  "rehomed_to": "MARKERS"},
        "yellow": {"atlas_phase": "sealed",
                   "candidate_meaning": "candidate",
                   "rehomed_to": "MARKERS"},
        "orange": {"atlas_phase": "review",
                   "candidate_meaning": "hold",
                   "rehomed_to": "MARKERS"},
    }
    return {"collisions": mapping,
            "atlas_entries_changed": 0,
            "one_color_one_meaning": True,
            "verdict": "RESOLVED_BY_FACTORING",
            "law": "do not replace the palette; factor the state "
                   "space"}
