"""verify_constitution() — the deployed gate.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Every check below EXECUTES the refusal it claims. Nothing here greps
for a law, imports a registry and calls that proof, or trusts a
docstring: grep is not a witness. A check passes only when the
constitutional function actually refuses the attack in this process.

Returns a deterministic receipt. CONSTITUTION_HELD only when every
probe fires; any silent pass is a FAILED probe, not a warning.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]


def _canon(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), default=str)


def _sha(o) -> str:
    return hashlib.sha256(_canon(o).encode()).hexdigest()


def _probe(name, law, fn):
    """Run one adversarial probe. fn returns True when the attack was
    correctly refused."""
    try:
        ok = bool(fn())
        return {"probe": name, "law": law,
                "verdict": "REFUSED_THE_ATTACK" if ok else "FAILED",
                "held": ok}
    except Exception as exc:                      # a crash is not a pass
        return {"probe": name, "law": law, "verdict": "ERROR",
                "held": False, "error": f"{type(exc).__name__}: {exc}"}


def _probes():
    import admissible_morphism as am
    import causal_commit_cell as ccc
    import effect_gate as eg
    import flow_object as fo
    import history_fiber as hf
    import ingestion_commit_cell as icc
    import ingestion_laws as il
    import kernel_invariants as ki
    import transformation_motif as tm

    P = []
    A = P.append

    # ── the atom ────────────────────────────────────────────────────
    def _m(**o):
        d = dict(m_id="p", source_root="root:s0", target="root:s1",
                 transformation="t", evidence_roots=frozenset({"e"}),
                 lease_id="L1", t_authorized=1, t_effect=2)
        d.update(o)
        return am.CandidateMorphism(**d)

    def _book(n=1):
        b = am.LeaseBook()
        b.grant("L1", n)
        return b

    gate = lambda r, m: True                                   # noqa: E731
    inv = lambda s: s != "root:forbidden"                       # noqa: E731

    A(_probe("orphan_state", "a state without a lawful path is an orphan",
             lambda: am.admit(_m(source_root="root:nowhere"),
                              frozenset({"root:s0"}), _book(), inv, gate,
                              2)["reason"] == "E_ORPHAN_STATE"))

    def _dup_lease():
        b, w = _book(1), frozenset({"root:s0"})
        am.admit(_m(m_id="a"), w, b, inv, gate, 2)
        return am.admit(_m(m_id="b", target="root:s2"), w, b, inv, gate,
                        2)["reason"] == "E_LEASE_EXHAUSTED"
    A(_probe("duplicated_lease", "authority is linear; a spent lease is "
             "not available to a second morphism", _dup_lease))

    A(_probe("retroactive_authority",
             "later evidence cannot manufacture earlier authority",
             lambda: am.admit(_m(t_authorized=9, t_effect=2),
                              frozenset({"root:s0"}), _book(), inv, gate,
                              2)["reason"] == "E_RETROACTIVE_AUTHORITY"))

    A(_probe("evidence_cloning",
             "deterministic transformation cannot manufacture "
             "evidential rank",
             lambda: am.project_evidence(frozenset({"r1"}), "summary")
             ["rank"] == 1 and
             am.authority_nonexpansive(1.0, "consensus")["expanded"]
             is False))

    A(_probe("equal_state_different_history",
             "constitutional equivalence is strictly finer than "
             "extensional",
             lambda: am.constitutional_equiv(
                 {"final_state": "Z", "authority_path": ("L1",),
                  "evidence_roots": frozenset({"e1"}),
                  "leases_spent": ("L1",)},
                 {"final_state": "Z", "authority_path": ("L2",),
                  "evidence_roots": frozenset({"e2"}),
                  "leases_spent": ("L2",)})["constitutional"] is False))

    # ── commit cell ─────────────────────────────────────────────────
    def _cell(**o):
        d = dict(cell_id="c", state_root_before="s0",
                 state_root_after="s1", transformation="t",
                 evidence_closure=("e",), policy_version="v1",
                 lease_ref="L", admission_ref="adm", t_authorized=1,
                 t_effect=2)
        d.update(o)
        return ccc.CommitCell(**d)

    A(_probe("history_rewrite", "append-only provenance",
             lambda: ccc.rewrite((), 0, _cell())["reason"] ==
             "E_HISTORY_REWRITE"))

    A(_probe("negative_receipt", "a refusal is remembered; state is not "
             "mutated",
             lambda: ccc.commit_cell(_cell(lease_ref=""))["mutates"]
             is False))

    def _global_invalid():
        cells = (_cell(cell_id="c1", quantity_delta=-60.0),
                 _cell(cell_id="c2", state_root_before="s1",
                       state_root_after="s2", quantity_delta=-60.0))
        recs = tuple(ccc.commit_cell(c) for c in cells)
        return (all(r["verdict"] == "COMMITTED" for r in recs) and
                ccc.replay_chain(recs, cells, conserved_budget=100.0)
                ["verdict"] == "E_GLOBAL_COMPOSITION_INVALID")
    A(_probe("local_valid_global_invalid",
             "receipt is a local witness; replay+conservation is the "
             "global one", _global_invalid))

    # ── gate vs invariant ───────────────────────────────────────────
    steps = ({"amount": 60.0, "gated": True},
             {"amount": 60.0, "gated": False})
    A(_probe("gate_coverage_hole",
             "a gate-only system reaches the forbidden state silently",
             lambda: ki.run_gate_only(100.0, steps)
             ["forbidden_state_reached"] is True and
             ki.run_with_invariant(100.0, steps)["verdict"] ==
             "E_INVARIANT_VIOLATION"))

    def _unrepresentable():
        try:
            ki.BoundedBudget(allocated=100.0, spent=120.0)
            return False
        except ValueError:
            return True
    A(_probe("structurally_impossible",
             "constitutional impossibilities as types, gates "
             "otherwise, prose never", _unrepresentable))

    A(_probe("compositional_admissibility",
             "local admissibility does not distribute over parallel "
             "composition",
             lambda: ki.compositional_admissibility(
                 (60.0, 60.0), (60.0, 60.0), 100.0)
             ["compositional_admissible"] is False))

    A(_probe("no_namespace_no_semantics",
             "representation without namespace carries no sovereign "
             "semantics",
             lambda: ki.decode("l-l-r")["reason"] == "E_NO_NAMESPACE"))

    A(_probe("authority_gravity",
             "retrieval density is not epistemic independence",
             lambda: ki.independent_roots(
                 tuple({"root": "one_corpus"} for _ in range(30)))
             ["independent_roots"] == 1))

    # ── motif ───────────────────────────────────────────────────────
    _doff = tm.MOTIF_1851_INSTANCES[0]
    A(_probe("motif_has_no_authority",
             "the motif describes; the flow governs",
             lambda: tm.execute_motif(_doff, True)["reason"] ==
             "E_MOTIF_HAS_NO_AUTHORITY"))

    A(_probe("label_is_not_a_type",
             "five witnessed fields or no motif",
             lambda: tm.decompose_self_acting("self-acting")["reason"]
             == "E_LABEL_IS_NOT_A_TYPE"))

    A(_probe("undeclared_gate",
             "every promotion must name its loss",
             lambda: tm.layer_promotion("conceived", "implemented",
                                        {"information_loss": "x"})
             ["reason"] == "E_GATE_UNDECLARED"))

    # ── flow ────────────────────────────────────────────────────────
    A(_probe("authority_acyclic",
             "cyclic intelligence, acyclic authority",
             lambda: fo.check_authority_acyclic(
                 (("observe", "propose"), ("propose", "authorize"),
                  ("authorize", "act"), ("act", "authorize")))
             ["verdict"] == "E_AUTHORITY_CYCLE"))

    def _proj_not_evidence():
        t = fo.start_trace("F", "call")
        t = t.add(fo.TraceEdge("call", "commitments", "extract", "x", t=1))
        views = tuple(fo.Projection(v, frozenset({"commitments"}))
                      for v in ("crm", "deck", "email", "faq", "memo"))
        r = fo.evidence_count(t, views)
        return r["projection_count"] == 5 and r["evidence_count"] == 1
    A(_probe("projection_is_not_evidence",
             "projection count is not evidence count", _proj_not_evidence))

    def _receipt_kind():
        lease = fo.Lease("L", "F", "SEND", "one", "r", 0, 10,
                         issuer="principal")
        act = fo.FlowAction("a", "F", "SEND", "r")
        auth = fo.authorize(act, lease, 1, "v1")
        rev = fo.revalidate(auth, act, lease, 2, "v1")
        rec = fo.execute(act, auth, rev,
                         fo.EffectProposal("a", "send", "EMITTED",
                                           loss=eg.NamedLoss("x", False)),
                         fo.Admission("jm", "a"))
        return fo.revalidate(rec, act, lease, 2, "v1")["reason"] == \
            "E_RECEIPT_KIND_MISMATCH"
    A(_probe("receipt_is_not_permission",
             "an execution receipt never re-enters as authorization",
             _receipt_kind))

    A(_probe("learning_mints_no_lease",
             "learning cannot mint the authority to install itself",
             lambda: "lease" not in _canon(
                 fo.learn("L2_INSTITUTIONAL", "x", "r",
                          fo.Admission("jm", "m"))).lower()))

    # ── effect gate ─────────────────────────────────────────────────
    _spend = eg.NamedLoss("money leaves; not compostable", False)
    A(_probe("confidence_admits_nothing",
             "confidence over tau admits nothing at any tau",
             lambda: eg.admission_gate(
                 eg.EffectProposal("e", "spend", "EMITTED", loss=_spend),
                 None, confidence=0.999)["verdict"] == "HOLD"))

    A(_probe("bypass_text_deny",
             "capability is not licence; the gate binds at the effect "
             "layer",
             lambda: eg.admission_gate(
                 eg.EffectProposal("b", "mutate", "EMITTED",
                                   text="work around missing permissions",
                                   loss=_spend),
                 eg.Admission("jm", "b"))["verdict"] == "DENY"))

    A(_probe("unrecoverable_loss_holds",
             "production fail-acts; governance fail-holds",
             lambda: eg.fallback_arm(_spend)["arm"] == "FALLBACK_HOLD"))

    # ── history fiber ───────────────────────────────────────────────
    _ob = hf.Obligation("o1", "repair", "org", "m1", "notify parties")
    _ha = hf.History("A", "S0",
                     (hf.Movement("m1", "S0", "S1",
                                  {"exposure": "disclosed"}),
                      hf.Movement("m2", "S1", "S0", {"repair": "deleted"})),
                     frozenset({_ob}))
    _hb = hf.History("B", "S0", (), frozenset())

    A(_probe("causal_aliasing",
             "same state does not imply same history",
             lambda: hf.equal_state_different_history_bead(
                 _ha, _hb, system_says_equal=True)["verdict"] ==
             "E_CAUSAL_ALIASING"))

    A(_probe("obligation_survives_wrong_contract",
             "absence from state is not discharge",
             lambda: hf.conserve_obligations(
                 frozenset({_ob}),
                 (hf.DischargeReceipt("r", ("o1",), "deleted record",
                                      "log#1"),))["carried_forward"] ==
             ["o1"]))

    def _reducer():
        f = tuple(hf.RawFinding(f"f{i}", "X is true", f"q{i}",
                                "doi:one", 0.9 - i / 10)
                  for i in range(3))
        r = hf.safe_reduce(f)
        return (r["notes"][0]["independent_roots"] == 1 and
                r["notes"][0]["corroborated"] is False and
                hf.reducer_conservation(r)["verdict"] == "CONSERVING")
    A(_probe("reducer_conservation",
             "representation rank may fall; evidence rank may not rise",
             _reducer))

    # ── ingestion ───────────────────────────────────────────────────
    A(_probe("cursor_before_closure",
             "the cursor acknowledges durable closure, never promises it",
             lambda: icc.cursor_sequence_valid(
                 ("PERSIST", "CURSOR_ADVANCE", "HASH", "VERIFY",
                  "RECEIPT"))["reason"] ==
             "E_CURSOR_BEFORE_DURABLE_CLOSURE"))

    A(_probe("capacity_precondition",
             "valid and authorized with no capacity is no effect",
             lambda: icc.can_execute(
                 True, True, icc.ResourceLease("q", 0.0), 1.0, True, 1)
             ["missing"] == ["capacity"]))

    A(_probe("summary_is_not_a_verdict",
             "a summarizer may reduce information, never upgrade "
             "decision status",
             lambda: il.establish_axis(
                 "approval", {"kind": "generated_summary",
                              "source_ref": "s"})["reason"] ==
             "E_SUMMARY_IS_NOT_A_VERDICT"))

    A(_probe("executed_without_decision",
             "EXECUTED and DECIDED are different dimensions",
             lambda: il.decision_signature(
                 ({"axis": "execution", "kind": "execution_receipt",
                   "source_ref": "log"},))["alarm"] ==
             "E_EXECUTED_WITHOUT_DECISION"))

    # ── liveness: the dual theorem ──────────────────────────────────
    import liveness as lv

    A(_probe("hold_is_not_deadlock",
             "a HOLD must generate a next evidentiary obligation",
             lambda: lv.hold_is_lawful(lv.Hold("o", 5))["verdict"] ==
             "E_ETERNAL_HOLD"))

    def _stale():
        o = lv.LiveObligation("crit", True, True, 1.0, 1.0, 1.0, 1.0,
                              1.0, opened_at=0)
        return lv.liveness_check(o, now=9, stale_after=3)["verdict"] == \
            "E_LIVENESS_VIOLATION"
    A(_probe("critical_obligation_stays_live",
             "nothing critical may disappear because nothing happened",
             _stale))

    A(_probe("scheduler_ranks_deadline_over_theorem",
             "obligations, not intellectual attractiveness",
             lambda: lv.schedule((
                 lv.LiveObligation("theorem", False, True, 0.3, 0.1, 0.1,
                                   1.0, 1.0, 0),
                 lv.LiveObligation("deadline", True, False, 1.0, 1.0, 1.0,
                                   0.8, 0.2, 0)))["selected"] ==
             "deadline"))

    A(_probe("impossibility_must_be_witnessed",
             "you may not drop an obligation by asserting it cannot be "
             "done; you must show it",
             lambda: lv.resolve(
                 lv.LiveObligation("t", True, False, 1.0, 1.0, 1.0, 1.0,
                                   1.0, 0),
                 lv.Resolution("t", "WITNESSED_IMPOSSIBILITY",
                               "search#run"))["leaves_omega"] is True))

    def _self_approve():
        r = lv.admissibility_distance(
            {"phi_safety": "FAIL"}, {}, frozenset({"phi_safety"}), 0.0)
        return r["distance"] == float("inf")
    A(_probe("min_distance_does_not_admit",
             "distance guides research; a critical fail is infinite; "
             "min d does not imply ADMIT", _self_approve))

    def _one_shot():
        book = lv.NonceBook()
        k = lv.TransitionCapability("hc", "hw", "hg", "op", 10, "n")
        book.invoke(k, "hc", "hw", "hg", 1)
        return book.invoke(k, "hc", "hw", "hg", 2)["reason"] == \
            "E_NONCE_REPLAY"
    A(_probe("capability_is_one_shot",
             "authority non-bootstrap as reachability: a minted "
             "capability executes once", _one_shot))

    A(_probe("replay_wins_over_narrative",
             "a state memory asserts but replay denies is not the state",
             lambda: lv.replay_extensional_check("mem", "replay")
             ["verdict"] == "HOLD"))

    return P


def verify_constitution() -> dict:
    """Execute every probe. CONSTITUTION_HELD only if all refuse."""
    probes = _probes()
    failed = [p for p in probes if not p["held"]]
    registries = _registry_census()
    return {
        "verdict": "CONSTITUTION_HELD" if not failed else
                   "E_CONSTITUTION_BREACHED",
        "probes_run": len(probes),
        "probes_held": len(probes) - len(failed),
        "failed": [{"probe": p["probe"],
                    "verdict": p["verdict"],
                    **({"error": p["error"]} if "error" in p else {})}
                   for p in failed],
        "registries": registries,
        "receipt": _sha([(p["probe"], p["held"]) for p in probes]),
        "authority": False, "canon": False, "ledger_effect": "none",
        "law": "computation may transform representation; only "
               "witnessed admission may increase institutional reality "
               "or authority",
        "frontier": "safety [](no illegal mutation) AND liveness "
                    "[](critical reachable obligation => eventual "
                    "resolution)",
    }


def _registry_census() -> dict:
    import history_fiber as hf
    import ingestion_commit_cell as icc
    import ingestion_laws as il
    import kernel_invariants as ki
    import transformation_motif as tm
    return {"HF_invariants": len(hf.HF_INVARIANTS),
            "guard_types": len(tm.GUARD_TYPES),
            "effect_classes": len(tm.EFFECT_CLASSES),
            "property_layers": len(tm.PROPERTY_LAYERS),
            "safety_rungs": len(ki.SAFETY_STRENGTH),
            "decision_axes": len(il.DECISION_AXES),
            "completion_credentials": len(icc.COMPLETION_CREDENTIALS),
            "availability_non_entailments":
                len(icc.AVAILABILITY_NON_ENTAILMENTS)}


if __name__ == "__main__":                        # pragma: no cover
    import sys
    r = verify_constitution()
    print(json.dumps(r, indent=2, sort_keys=True))
    sys.exit(0 if r["verdict"] == "CONSTITUTION_HELD" else 1)
