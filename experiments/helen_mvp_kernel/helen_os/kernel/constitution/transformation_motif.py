"""M — the Transformation Motif: the primitive BENEATH the Governed
Flow Object.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    M = (I, G, T, O, R)      input · guard · transformation ·
                             observable effect · reset rule

and a governed flow is a composition

    F = M_1 ∘ M_2 ∘ ... ∘ M_n  + provenance + permission + receipts.

The Crystal Palace corpus supplies real historical instances of the
motif grammar; HELEN supplies the governance layer those machines did
not have. Hence the central law of this module:

    A MOTIF CARRIES NO AUTHORITY. Executing a mutation- or
    governance-class motif outside a governed flow context (lease +
    admission) is refused: E_MOTIF_HAS_NO_AUTHORITY. The 1851 doffing
    machine acted unattended because nothing governed it; that is an
    observation about 1851, not a license.

The 1851 gate algebra, as observed (descriptive vocabulary — these
name guard KINDS found in the corpus, they import no modern claims):

    G_time           t = t*            early-calling machine
    G_threshold      x >= x*           sliver-lap doffing
    G_safety         hazard condition  railway signals, brakes
    G_human_absence  no response       the CP-527 fallback arm
    G_code           signal -> symbol  telegraph alphabet
    G_measurement    x -> f(x)         graduation machines

Effect classes, by authority over consequence (the relay's table —
"effect class may be a more stable primitive than application
category"):

    observational < advisory < decision_support < escalation < mutation
    governance (restricts transitions) and audit (records them) sit
    beside the ladder, not on it.

SELF-ACTING is a candidate label, not a type: decompose_self_acting
refuses to mint a motif until all five fields (trigger, state sensed,
transition, effect, reset) are witnessed — keyword mining types
nothing.

And the five-layer property ladder, with the GATE result attached:

    possible != conceived != implemented != authorized != patented

No property propagates upward on its own. A promotion crosses one
layer at a time through a gate that declares (information_loss,
assumptions_added, authority_gain, reversibility) — all four, always.

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gates" / "effect_gate"))

from effect_gate import Admission  # noqa: E402

GUARD_TYPES = ("G_time", "G_threshold", "G_safety", "G_human_absence",
               "G_code", "G_measurement")

EFFECT_LADDER = ("observational", "advisory", "decision_support",
                 "escalation", "mutation")
EFFECT_ASIDE = ("governance", "audit")
EFFECT_CLASSES = EFFECT_LADDER + EFFECT_ASIDE

GOVERNED_CLASSES = frozenset({"mutation", "governance"})

PROPERTY_LAYERS = ("possible", "conceived", "implemented", "authorized",
                   "patented")

GATE_DECLARATION_FIELDS = ("information_loss", "assumptions_added",
                           "authority_gain", "reversibility")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class Guard:
    guard_type: str
    condition: str                    # "t = t*", "x >= x*", ...

    def __post_init__(self):
        if self.guard_type not in GUARD_TYPES:
            raise ValueError("E_UNKNOWN_GUARD_TYPE")
        if not self.condition:
            raise ValueError("E_GUARD_WITHOUT_CONDITION")


@dataclass(frozen=True)
class TransformationMotif:
    """M = (I, G, T, O, R). Note what is ABSENT: no authority field,
    no lease field, no admit method. The motif describes a guarded
    transformation; it never licenses one."""
    motif_id: str
    inp: str                          # I — input/state
    guard: Guard                      # G — trigger
    transform: str                    # T
    observable: str                   # O — observable effect
    reset: str                        # R — reset/recovery/next-state
    effect_class: str = "observational"
    witness: str = ""                 # historical or in-frame citation

    def __post_init__(self):
        if self.effect_class not in EFFECT_CLASSES:
            raise ValueError("E_UNKNOWN_EFFECT_CLASS")
        for f in ("inp", "transform", "observable", "reset"):
            if not getattr(self, f):
                raise ValueError("E_MOTIF_FIELD_MISSING:" + f)


def compose(motifs: tuple) -> dict:
    """F = M_1 ∘ ... ∘ M_n. Composition computes what governance the
    flow WILL need — it does not grant it."""
    classes = tuple(m.effect_class for m in motifs)
    return {"flow_skeleton": tuple(m.motif_id for m in motifs),
            "effect_classes": classes,
            "governance_required": any(c in GOVERNED_CLASSES
                                       for c in classes),
            "note": "composition computes required governance; "
                    "it grants none"}


def execute_motif(m: TransformationMotif, guard_satisfied: bool,
                  lease_ref: str = "",
                  admission: Admission | None = None) -> dict:
    """The central refusal. Below-mutation classes run on their guard
    alone (they change no shared state). Mutation/governance classes
    require the governed-flow context: a lease AND an admission — the
    layer 1851 did not have."""
    if not guard_satisfied:
        return {"verdict": "IDLE", "reason": "guard not satisfied"}
    if m.effect_class in GOVERNED_CLASSES:
        if not lease_ref or admission is None:
            return {"verdict": "REFUSED",
                    "reason": "E_MOTIF_HAS_NO_AUTHORITY",
                    "law": "the motif describes; the flow governs; "
                           "1851's unattended action is an observation, "
                           "not a license"}
        return {"verdict": "EXECUTED_UNDER_FLOW", "lease_ref": lease_ref,
                "admitted_by": admission.principal}
    return {"verdict": "EXECUTED", "effect_class": m.effect_class,
            "observable": m.observable}


def authority_over_consequence(m: TransformationMotif) -> dict:
    """Where the motif sits on the effect ladder — the classification
    the relay argues is more stable than application category."""
    if m.effect_class in EFFECT_ASIDE:
        return {"position": m.effect_class, "on_ladder": False,
                "role": ("restricts transitions"
                         if m.effect_class == "governance"
                         else "records transitions")}
    return {"position": m.effect_class, "on_ladder": True,
            "rank": EFFECT_LADDER.index(m.effect_class)}


# ── SELF-ACTING is a label, not a type ──────────────────────────────────

def decompose_self_acting(label: str, trigger: Guard | None = None,
                          state_sensed: str = "", transition: str = "",
                          effect: str = "", reset: str = "",
                          witness: str = "") -> dict:
    """'Self-acting' in the catalogue spans time-drive, thresholds,
    fixed cycles, non-attendance fallback, safety conditions, encoded
    sequencing. The label mints nothing; five witnessed fields mint a
    motif."""
    missing = [name for name, v in (
        ("trigger", trigger), ("state_sensed", state_sensed),
        ("transition", transition), ("effect", effect),
        ("reset", reset)) if not v]
    if missing:
        return {"verdict": "CANDIDATE_LABEL_ONLY",
                "reason": "E_LABEL_IS_NOT_A_TYPE",
                "label": label, "missing_fields": missing}
    return {"verdict": "DECOMPOSED",
            "motif": TransformationMotif(
                motif_id=f"self_acting:{label}",
                inp=state_sensed, guard=trigger, transform=transition,
                observable=effect, reset=reset, witness=witness)}


# ── the five-layer property ladder + the GATE declaration ───────────────

def layer_promotion(frm: str, to: str, gate: dict | None) -> dict:
    """possible != conceived != implemented != authorized != patented.
    One layer per crossing, and the gate must declare all four:
    information_loss, assumptions_added, authority_gain, reversibility.
    No gate, no propagation — a property acquired in one layer never
    climbs on its own."""
    if frm not in PROPERTY_LAYERS or to not in PROPERTY_LAYERS:
        raise ValueError("E_UNKNOWN_LAYER")
    i, j = PROPERTY_LAYERS.index(frm), PROPERTY_LAYERS.index(to)
    if j != i + 1:
        return {"verdict": "REFUSED", "reason": "E_LAYER_SKIP",
                "from": frm, "to": to}
    if not gate:
        return {"verdict": "REFUSED", "reason": "E_NO_GATE",
                "law": "no implicit semantic promotion"}
    missing = [f for f in GATE_DECLARATION_FIELDS if f not in gate]
    if missing:
        return {"verdict": "REFUSED", "reason": "E_GATE_UNDECLARED",
                "missing": missing}
    return {"verdict": "PROMOTED", "from": frm, "to": to,
            "declared": {f: gate[f] for f in GATE_DECLARATION_FIELDS}}


# ── the 1851 instances, cited to the atlas frames ───────────────────────

MOTIF_1851_INSTANCES = (
    TransformationMotif(
        "doffing_fallback", inp="sliver length",
        guard=Guard("G_threshold", "x >= x*"),
        transform="doff the lap", observable="uniform lap length",
        reset="resume winding", effect_class="mutation",
        witness="wellcome:527"),
    TransformationMotif(
        "early_calling", inp="clock state",
        guard=Guard("G_time", "t = t*"),
        transform="sound the call", observable="person awakened",
        reset="rewind", effect_class="mutation",
        witness="catalogue:class10_early_calling"),
    TransformationMotif(
        "railway_interlock", inp="junction state",
        guard=Guard("G_safety", "hazard condition present"),
        transform="restrict transition", observable="signal set against",
        reset="hazard cleared", effect_class="governance",
        witness="catalogue:class5_7_safety"),
    TransformationMotif(
        "atmospheric_recording", inp="atmospheric variables",
        guard=Guard("G_measurement", "continuous, clock-indexed"),
        transform="transduce to paper", observable="aligned trace",
        reset="advance recording surface", effect_class="observational",
        witness="catalogue:dollond_recorder"),
    TransformationMotif(
        "autochronograph_stamp", inp="event occurrence",
        guard=Guard("G_time", "at event"),
        transform="print date-time mark", observable="(e,t,a) record",
        reset="await next event", effect_class="audit",
        witness="catalogue:autochronograph"),
    TransformationMotif(
        "telegraph_decode", inp="needle movements",
        guard=Guard("G_code", "code convention applied"),
        transform="map movements to letters", observable="symbol",
        reset="await next signal", effect_class="observational",
        witness="wellcome:699"),
    TransformationMotif(
        "course_recommendation", inp="origin, destination, geometry",
        guard=Guard("G_measurement", "mechanical construction"),
        transform="compute great-circle course",
        observable="recommended course — NOT a rudder mutation",
        reset="new inputs", effect_class="decision_support",
        witness="wellcome:699"),
)
