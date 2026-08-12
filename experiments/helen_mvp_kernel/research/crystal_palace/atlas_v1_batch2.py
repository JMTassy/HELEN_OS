"""Crystal Palace motif atlas · batch 2 (V1) — six new frames.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Same provenance law as batch 1: relayed seat-reads, grade REPORTED here
(ObservedThere ⊬ ObservedHere). Batch 2 freezes SEPARATELY and cites
batch 1's freeze hash as its predecessor — batch 1's hash never moves.

State transitions this batch performs, explicitly:

  DOLLOND EXCLUSION LIFTED — sensor_to_record was excluded from batch 1
    because its page was witnessed only through a Smithsonian citation.
    The relay now carries the official catalogue's own description
    (self-registering multivariate observation on a clock-driven
    surface). Direct-witness condition met -> the motif enters, with
    the part/volume attribution conflict recorded as a contradiction,
    not resolved by fiat.

  THE BUILDING STAYS OUTSIDE THE VOL-1 ATLAS — the Palace-as-modular-
    production-system motif is real and strong, but its witness is a
    V&A institutional report about the SITE, not a catalogue canvas.
    It lives in PALACE_MOTIFS under scope 'palace_structure', and
    atlas_scope_check refuses it at the vol1 door. The boundary law
    applies to our own enthusiasm first.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import atlas_v0 as av
from crystal_palace import (  # noqa: E402
    UNREACHABLE,
    Corpus1851,
    Motif,
    PageRecord,
    freeze_candidates,
)

C_VOL1_B2 = Corpus1851(
    corpus_id="great_exhibition_1851_vol1_wellcome772",
    availability=UNREACHABLE,
    pages_total=772,
    pages_in_frame=av.C_VOL1.pages_in_frame | frozenset({
        "catalogue:dollond_recorder", "catalogue:autochronograph",
        "catalogue:class5_7_safety", "catalogue:class10_early_calling",
        "catalogue:class10_graduation"}))

FRAMES_B2 = {
    "CP-DOLLOND": PageRecord(
        "catalogue:dollond_recorder",
        observed=(
            "self-registers pressure, temperature, evaporation, "
            "electrical state, rain, wind force and direction on paper",
            "a clock drives the recording surface; separate time "
            "markers provide temporal indexing",
            "simultaneous registration stressed because variables "
            "change while no human watches"),
        technical_objects=("atmospheric recorder", "clock drive",
                           "time markers"),
        inferred_claims=(
            "observation + common time base + persistent record = "
            "trace, not merely memory",),
        contradictions=(
            "earlier citation located this at catalogue pt2 pp.414-415 "
            "(via Smithsonian); part/volume attribution across "
            "digitizations remains unresolved",),
        future_candidate="sensor -> transduce -> clock -> record",
        confidence=0.8),
    "CP-AUTOCHRON": PageRecord(
        "catalogue:autochronograph",
        observed=(
            "instantly marks or prints month, day, hour, minutes and "
            "fractions",
            "jury discussion: could register train arrivals/departures "
            "and record presence or identity of guards"),
        technical_objects=("autochronograph",),
        inferred_claims=(
            "a clock yields t; an event recorder yields (e,t); with "
            "actor association it approaches (e,t,a) — proto-provenance "
            "structurally, no ancestry claimed",),
        future_candidate="event + time + actor -> audit record",
        confidence=0.75),
    "CP-SAFETY": PageRecord(
        "catalogue:class5_7_safety",
        observed=(
            "self-acting railway signals; simultaneously acting "
            "crossing gates; self-acting collision/braking "
            "arrangements; self-acting fire extinguishers; junction "
            "semaphores; mechanisms for stopping trains quickly"),
        technical_objects=("railway signals", "crossing gates",
                           "brake arrangements", "fire extinguishers"),
        inferred_claims=(
            "the safety subsystem exists because the productive "
            "subsystem cannot be trusted to self-govern — capability "
            "and permission are separate mechanisms",),
        future_candidate="productive mechanism (+) independent safety "
                         "mechanism",
        confidence=0.8),
    "CP-TIME": PageRecord(
        "catalogue:class10_early_calling",
        observed=(
            "early-calling machine to awaken a person at a required "
            "hour using a clock; self-acting chronometers and repeaters"),
        technical_objects=("early-calling machine", "chronometers"),
        inferred_claims=(
            "t = t* -> A is a distinct trigger class from x = x* -> A: "
            "the corpus contains different KINDS of transition guards",),
        future_candidate="time-triggered transition G_time",
        confidence=0.75),
    "CP-MEASURE": PageRecord(
        "catalogue:class10_graduation",
        observed=(
            "machines graduating hydrometer/thermometer scales at "
            "mathematically determined positions; dial weighing "
            "machines; wind-duration registers"),
        technical_objects=("graduation machines", "dial scales"),
        inferred_claims=(
            "a calibrated transformation mediates physical quantity "
            "and measurement value — world != observation != "
            "normalized representation",),
        future_candidate="mechanized measurement convention x -> f -> y",
        confidence=0.75),
    "CP-BUILDING": PageRecord(
        "site:vanda_report",
        observed=(
            "standardized prefabricated iron/timber/glass components; "
            "~2,000 workers; 293,655 panes; 200+ miles of glazing "
            "bars; certified seven months after ground-break; "
            "dismantlable and reusable"),
        technical_objects=("prefabricated components", "interfaces"),
        inferred_claims=(
            "complexity shifted from bespoke objects into standardized "
            "interfaces — organization lives in interfaces and "
            "composition rules, not in the parts",),
        missing_witnesses=(
            "this witness is a modern institutional report about the "
            "SITE, not a catalogue canvas",),
        future_candidate="standard parts + interface discipline + "
                         "parallel assembly -> large system",
        confidence=0.7),
}

MOTIFS_B2 = (
    Motif("sensor_to_record",
          ("world_variable", "sensor", "transduction", "common_time_base",
           "persistent_record"),
          witness_frames=("catalogue:dollond_recorder",),
          forbidden_promotions=("telemetry infrastructure lineage",
                                "database ancestry")),
    Motif("event_timestamping",
          ("event", "time", "actor", "audit_record"),
          witness_frames=("catalogue:autochronograph",),
          forbidden_promotions=("audit-log lineage", "provenance-system "
                                "ancestry")),
    Motif("independent_safety_mechanism",
          ("productive_process", "hazard_condition",
           "restricted_transition"),
          witness_frames=("catalogue:class5_7_safety",),
          forbidden_promotions=("AI-safety lineage",
                                "modern interlock ancestry")),
    Motif("time_triggered_action",
          ("clock", "t_equals_t_star", "action"),
          witness_frames=("catalogue:class10_early_calling",),
          forbidden_promotions=("cron lineage", "scheduler ancestry")),
    Motif("mechanized_measurement",
          ("physical_quantity", "calibrated_transformation",
           "measurement_value"),
          witness_frames=("catalogue:class10_graduation",),
          forbidden_promotions=("metrology-standard lineage",)),
    Motif("automatic_return_self_relief",
          ("cut", "return", "next_cut", "undesired_state",
           "automatic_unloading"),
          witness_frames=("wellcome:546",),
          forbidden_promotions=("exception-handling lineage",)),
)

# the building motif: real, strong, and OUTSIDE the vol1 corpus scope
PALACE_MOTIFS = (
    Motif("standard_parts_interface_assembly",
          ("standard_parts", "interface_discipline", "parallel_assembly",
           "large_system"),
          witness_frames=("site:vanda_report",),
          forbidden_promotions=("software modularity lineage",),
          corpus_scope="palace_structure"),
)

# ── the HAL board, as relayed ───────────────────────────────────────────

HAL_SHIP = {
    "conditional state-triggered actuation": "conditional_automation",
    "time-triggered action": "time_triggered_action",
    "independent safety mechanisms": "independent_safety_mechanism",
    "self-registering multivariate observation": "sensor_to_record",
    "event timestamping": "event_timestamping",
    "source-channel-code representation": "source_channel_code",
    "parallel independently controlled operations": "parallel_execution",
    "structural disturbance cancellation":
        "structural_error_cancellation",
    "decision support separated from execution":
        "mechanized_decision_support",
    "mechanically standardized measurement": "mechanized_measurement",
}

HAL_HOLD = (
    "technological novelty is primarily recombination",
    "most future invention motifs were already present by 1851",
    "1851 contains closed-loop feedback as a general design class",
    "motif saturation predicts future patents",
)

HAL_NO_SHIP = (
    "Crystal Palace invented computing",
    "Crystal Palace contained AI",
    "catalogue patent language establishes valid patent claims",
    "many matching exhibits constitute independent corroboration",
    "we have already predicted post-1851 patents",
)


def all_motifs() -> tuple:
    """batch 1 ∪ batch 2 — the vol1 atlas as currently frozen."""
    return av.MOTIFS + MOTIFS_B2


def freeze_batch2() -> dict:
    """Freeze batch 2 with explicit lineage to batch 1's hash."""
    r = freeze_candidates(MOTIFS_B2, access_log=av.DESCRIPTIVE_ACCESS_LOG)
    r["predecessor_freeze_hash"] = av.freeze_batch1()["freeze_hash"]
    r["exclusion_lifted"] = ("sensor_to_record",)
    return r
