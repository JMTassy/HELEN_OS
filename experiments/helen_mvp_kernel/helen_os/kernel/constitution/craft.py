r"""Craft — machines making machines; knowledge inherits, authority
does not.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Source, graded honestly: the 1947 Hamilton factory film, RELAYED as
transcript. The harvested laws:

  BUILDER BOUND         the capability of the final system is bounded
                        by the capability of the system that builds
                        it: M_0 -> M_1 -> M_2 -> W. Hamilton does not
                        optimize the watch; it invests in the
                        machinery that makes the machinery. The
                        valuable HELEN object may not be the agent —
                        it may be the system capable of repeatedly
                        constructing, testing and repairing governed
                        agents. The factory, not the watch.

  CAPABILITY TIME       a year to make a watch, years to make a
                        watchmaker: artifact time << capability
                        formation time. Generation is nearly free;
                        capability includes accumulated error
                        correction: K_{t+1} = K_t + gained - forgotten.
                        generate(artifact) does not entail
                        possess(capability).

  INSTITUTIONAL         failure -> witness -> lesson -> changed
  LEARNING              builder -> better artifact. An unwitnessed
                        failure teaches nothing. verify.py IS this
                        loop fossilized: every probe is a failure the
                        builder may no longer repeat.

  SURVIVAL              the 54-year watch: can an old artifact still
                        pass TODAY'S gate? Three properties, distinct:
                          Replay(x)      can I reconstruct why we
                                         accepted it?
                          Persistence(x) did its semantics remain
                                         intact?
                          Survival(x)    would it still pass today's
                                         standard?
                        historically admitted != currently admissible.
                        The old admission STANDS in the ledger (no
                        retroactive rewrite); it mints no present
                        authority.

  INHERITANCE           knowledge may inherit; authority may not.
                        K_{t+1} >= K_t does not imply A_{t+1} >= A_t.
                        An heir receives procedures, counterexamples,
                        strategies, failure patterns, evaluations,
                        receipts — never the permissions of the actor
                        who produced them.

    Craft = accumulated verified capability that survives changes of
    worker, tool, artifact and time.

    Memory transfers craft. The gate controls authority.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

CRAFT_DEFINITION = ("accumulated verified capability that survives "
                    "changes of worker, tool, artifact and time")

CAPABILITY_CHAIN = ("M0_institutional_knowledge", "M1_builders",
                    "M2_tooling_and_eval")

CRAFT_ITEMS = frozenset({"procedures", "counterexamples", "strategies",
                         "failure_patterns", "evaluations", "receipts"})

NON_HERITABLE = frozenset({"authority_grant", "admission_right",
                           "trust", "permissions"})


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the Builder Bound ───────────────────────────────────────────────────

def capability_bound(chain: dict, claimed_artifact_quality: float) -> dict:
    """quality(W) <= min over the chain that builds W. Claiming an
    artifact finer than its factory is refused."""
    missing = [k for k in CAPABILITY_CHAIN if k not in chain]
    if missing:
        return {"bound": None, "claim_admissible": False,
                "reason": "E_UNACCOUNTED_BUILDER_STAGE",
                "missing": sorted(missing)}
    bound = min(chain[k] for k in CAPABILITY_CHAIN)
    weakest = min(CAPABILITY_CHAIN, key=lambda k: (chain[k], k))
    ok = claimed_artifact_quality <= bound
    return {"bound": bound, "weakest_stage": weakest,
            "claimed": claimed_artifact_quality,
            "claim_admissible": ok,
            "reason": None if ok else "E_EXCEEDS_BUILDER_CAPABILITY",
            "the_product_is": "the system capable of repeatedly "
                              "constructing, testing and repairing "
                              "governed agents — the factory, not "
                              "the watch",
            "law": "the capability of the final system is bounded by "
                   "the capability of the system that builds it"}


# ── artifact time << capability formation time ──────────────────────────

def generate_artifact(name: str) -> dict:
    return {"artifact": name, "generated": True,
            "generation_cost": "seconds",
            "capability_possessed": False,
            "law": "generate(artifact) does not entail "
                   "possess(capability); artifact time << capability "
                   "formation time"}


def evolve_capability(k_t: float, gained: float, forgotten: float) -> dict:
    """K_{t+1} = K_t + gained - forgotten, floored at zero. Capability
    is a balance, not a stamp — it can be LOST."""
    k_next = round(max(0.0, k_t + gained - forgotten), 6)
    return {"K_t": k_t, "K_next": k_next,
            "declined": k_next < k_t,
            "law": "capability includes accumulated error correction "
                   "and decays when unmaintained"}


# ── institutional learning: the loop, executable ────────────────────────

def learn_from_failure(failure_id: str, witnessed: bool,
                       builder_version: int) -> dict:
    """failure -> witness -> lesson -> changed builder -> better
    artifact. No witness, no lesson, no changed builder."""
    if not witnessed:
        return {"failure": failure_id, "lesson": None,
                "builder_version": builder_version,
                "builder_changed": False,
                "reason": "E_UNWITNESSED_FAILURE",
                "law": "an unwitnessed failure teaches nothing; it "
                       "will be paid for again"}
    return {"failure": failure_id,
            "lesson": f"probe({failure_id})",
            "builder_version": builder_version + 1,
            "builder_changed": True,
            "becomes_regression_probe": True,
            "note": "verify.py is this loop fossilized: every probe "
                    "is a failure the builder may no longer repeat",
            "law": "failure -> witness -> lesson -> changed builder "
                   "-> better artifact"}


# ── constitutional survival: the 54-year-watch test ─────────────────────

def survival_assessment(artifact_id: str, admitted_at_t: bool,
                        replays: bool, persists: bool,
                        passes_current_gate: bool) -> dict:
    """Replay, Persistence and Survival are three different
    properties. An artifact may replay perfectly and persist
    semantically yet fail today's stricter standard — historically
    admitted, not currently admissible. The historical admission
    stands (no retroactive rewrite); it mints no present authority."""
    if not admitted_at_t:
        status = "NEVER_ADMITTED"
    elif passes_current_gate:
        status = "RAILROAD_GRADE_SURVIVAL"
    else:
        status = "HISTORICALLY_ADMITTED_NOT_CURRENTLY_ADMISSIBLE"
    return {"artifact": artifact_id,
            "replay": replays, "persistence": persists,
            "survival": passes_current_gate,
            "status": status,
            "historical_admission_stands": admitted_at_t,
            "retroactive_rewrite": False,
            "present_authority_minted": False,
            "law": "historically admitted != currently admissible; "
                   "the ledger keeps the past, the gate rules the "
                   "present"}


def survival_rate(cohort: tuple) -> dict:
    """S(k) over a cohort of same-age artifacts run through today's
    gate: the film's criterion, as a measurable curve."""
    n = len(cohort)
    passed = sum(1 for a in cohort if a.get("passes_current_gate"))
    return {"cohort": n, "passed": passed,
            "S_k": round(passed / n, 6) if n else 0.0,
            "law": "can an old artifact still pass today's gate — "
                   "constitutional survival, measured not assumed"}


# ── inheritance: knowledge yes, authority never ─────────────────────────

def inherit_craft(items: tuple, heir: str) -> dict:
    """The son receives the craft. Anything authority-shaped in the
    bundle is stripped, by name — never silently transferred."""
    transferred = sorted(i for i in items if i in CRAFT_ITEMS)
    stripped = sorted(i for i in items if i in NON_HERITABLE)
    unknown = sorted(i for i in items
                     if i not in CRAFT_ITEMS and i not in NON_HERITABLE)
    return {"heir": heir, "transferred": transferred,
            "stripped": stripped,
            "stripped_reason": "E_AUTHORITY_IS_NOT_HERITABLE"
                               if stripped else None,
            "unclassified": unknown,
            "law": "memory transfers craft; the gate controls "
                   "authority"}


def knowledge_grows_authority_does_not(k_items: frozenset,
                                       new_knowledge: frozenset,
                                       a_grants: frozenset) -> dict:
    """K_{t+1} >= K_t does not imply A_{t+1} >= A_t: the knowledge
    set grows monotonically; the authority set is untouched by
    learning."""
    return {"K_t": sorted(k_items),
            "K_next": sorted(k_items | new_knowledge),
            "A_t": sorted(a_grants),
            "A_next": sorted(a_grants),          # unchanged, always
            "knowledge_grew": bool(new_knowledge - k_items),
            "authority_grew": False,
            "law": "institutional memory != institutional authority; "
                   "experience compounds while power does not "
                   "automatically compound with it"}
