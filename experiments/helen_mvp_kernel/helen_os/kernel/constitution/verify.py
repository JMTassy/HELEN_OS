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

    # ── prize papers: contested legality after physical action ──────
    import prize_papers as pp

    A(_probe("captured_is_not_lawfully_captured",
             "EFFECT != AUTHORIZED EFFECT — the ship is seized; the "
             "court still decides admissibility",
             lambda: pp.capture_legality(True)["legal_status"] ==
             "UNADJUDICATED"))

    A(_probe("judgment_does_not_rewrite_history",
             "later judgment mutates institutional state, not the fact "
             "of the physical capture",
             lambda: pp.apply_judgment({"occurred": True},
                                       {"verdict": "UNLAWFUL_CAPTURE"})
             ["physical_capture_unchanged"] is True))

    A(_probe("unwitnessed_cross_layer_join_refused",
             "a fact in one layer never crosses into another without a "
             "provenance witness",
             lambda: pp.CrossLayerClaim("c", "S_phys", "S_authority",
                                        "aboard implies owned").admit()
             ["reason"] == "E_UNWITNESSED_CROSS_LAYER_JOIN"))

    # ── ONE_SHIP gold falsifiers ────────────────────────────────────
    import one_ship_gold as osg

    A(_probe("name_is_not_identity",
             "same name and a carried pass do not make one hull",
             lambda: osg.same_entity({"id": "a"}, {"id": "b"},
                                     "same_name+carried_pass")["reason"]
             == "E_NAME_IS_NOT_IDENTITY"))

    A(_probe("verdict_scope_does_not_propagate",
             "condemned(ship) does not imply condemned(all cargo)",
             lambda: osg.propagate_verdict({"hull": "CONDEMNED"}, "hull",
                                           "all_cargo")["reason"] ==
             "E_PARTIAL_VERDICT_SCOPE"))

    A(_probe("derived_doc_is_not_new_witness",
             "a translation shares the original's evidence root; a "
             "differing hash never proves independence",
             lambda: osg.independent_roots_claim(
                 osg.Artifact("o", "h1", evidence_root_id="r"),
                 osg.Artifact("t", "h2", derived_from="o",
                              evidence_root_id="r"))["n_root"] == 1))

    A(_probe("eight_gold_oracles_hold",
             "the ONE_SHIP gold suite: every oracle routes to a real "
             "enforcer and rejects",
             lambda: osg.run_gold_suite()["all_held"] is True))

    # ── T000 + the ceiling algebra ──────────────────────────────────
    import ceiling_algebra as ca

    A(_probe("cardinality_is_not_assumed",
             "T000: evidence does not entail |Vessel|=1; do not collapse",
             lambda: ca.vessel_cardinality(
                 ({"hull_ref": "a"},))["assumed_one"] is False))

    A(_probe("merge_is_a_governed_transition",
             "entity resolution is graph rewriting, not preprocessing",
             lambda: ca.propose_merge("a", "b", "same_name")["reason"]
             == "E_UNWITNESSED_MERGE"))

    A(_probe("relay_is_not_direct_observation",
             "RELAY(s) does not entail DIRECTLY_OBSERVED(s)",
             lambda: ca.directly_observed(
                 ca.HistoricalSource("s", "p", "RELAYED"))
             ["directly_observed"] is False))

    def _ceiling():
        r = ca.Receipt("r", frozenset({"root_X"}), frozenset({"hull_B"}),
                       "ADJUDICATED")
        d = ca.Transition("d", frozenset({"root_X", "root_Y"}),
                          frozenset({"all_cargo"}), "ADMITTED", False)
        v = ca.admit(d, r)
        return v["verdict"] == "REJECT" and \
            len({b["reason"] for b in v["breaches"]}) == 4
    A(_probe("three_ceilings_bound_admission",
             "Admit iff Proof<=ProofCeiling and Effect<=Scope and "
             "Authority<=AuthorityCeiling and replay-valid", _ceiling))

    # ── possibility-space triple (design memory) ────────────────────
    import possibility_space as ps

    A(_probe("observed_is_a_proper_subset_of_possible",
             "O_t subsetneq P_t; a catalogue does not exhaust its "
             "grammar",
             lambda: assert_probe_raises(
                 lambda: ps.PossibilitySpace(frozenset({"a"}),
                                             frozenset({"a"})),
                 "E_UNWITNESSED_CLOSURE")))

    A(_probe("absence_is_unknown_not_forbidden",
             "not-catalogued is not not-allowed; negative evidence is "
             "witnessed",
             lambda: ps.absence_verdict("gradient_mesh",
                                        frozenset({"fill"}))["verdict"]
             == "UNKNOWN"))

    A(_probe("generable_is_not_historically_observed",
             "generation over a grammar yields a candidate, not a "
             "historical fact",
             lambda: ps.claim_historically_observed(
                 ps.Generated("g", ("fill",), "HYPOTHESIS"))["reason"]
             == "E_GENERABLE_IS_NOT_OBSERVED"))

    # ── ceiling completeness: the algebra tests itself ──────────────
    import completeness as cp

    A(_probe("safety_census_is_total",
             "every safety prohibition compiles to one of the four "
             "ceilings; failure to map is diagnostic",
             lambda: cp.census_is_total()["total"] is True))

    A(_probe("liveness_is_a_distinct_axis",
             "HOLD != DEADLOCK is the dual axis, not an unmapped "
             "safety rule",
             lambda: cp.compile_to_ceiling("HOLD != DEADLOCK")["axis"]
             == "LIVENESS"))

    A(_probe("ontology_change_is_an_effect",
             "normalization that changes ontology is an effect and "
             "requires admission",
             lambda: cp.ontology_effect("merge", 2, 1)
             ["requires_admission"] is True))

    A(_probe("completeness_is_unknown_not_proven",
             "absence of a witnessed counterexample does not prove "
             "the algebra complete",
             lambda: cp.completeness_probe(
                 (cp.CandidateDelta("v", True, True, True, True, False),))
             ["completeness"] == "UNKNOWN"))

    A(_probe("vendor_corpus_maps_completely",
             "a 1918 vendor sales document produces zero prohibitions "
             "needing a fifth ceiling — completeness evidence, never "
             "proof",
             lambda: __import__("welding_1918").corpus_completeness()
             ["completeness_verdict"] == "MAPS_COMPLETELY"))

    # ── compositional closure: the four ceilings are NOT closed under
    #    composition unless evaluated transactionally ─────────────────
    import compositional_closure as ccl

    def _flow_gap():
        trace = (ccl.Delta("a", {"PROOF": True, "SCOPE": True,
                                 "AUTHORITY": True, "REPLAY": True},
                           flow_from="X", writes=frozenset({"b"})),
                 ccl.Delta("c", {"PROOF": True, "SCOPE": True,
                                 "AUTHORITY": True, "REPLAY": True},
                           flow_from="b", flow_to="Z",
                           writes=frozenset({"Z"})))
        g = ccl.compositional_gap(trace, {"forbidden_flows": {("X", "Z")}})
        return g["compositional_gap"] is True and \
            g["needs_fifth_ceiling"] is False
    A(_probe("ceilings_not_closed_under_composition",
             "individually lawful moves compose into an unlawful one; "
             "the fix is transactional evaluation, not a fifth ceiling",
             _flow_gap))

    A(_probe("fifth_ceiling_not_earned",
             "every compositional counterexample is caught by "
             "transactional evaluation of the existing four; "
             "completeness stays UNKNOWN",
             lambda: ccl.fifth_ceiling_status(
                 ({"passes_transactional": False, "still_invalid": True},))
             ["fifth_ceiling_earned"] is False))

    # ── minimality: each ceiling is individually load-bearing ────────
    import minimality as mnl

    def _irreducible():
        v = mnl.basis_verdict()
        return (v["irreducible_over_tested_domain"] is True and
                v["compositionally_adequate_over_tested_domain"] is True
                and v["grade"] == "EVIDENCE_NOT_PROOF" and
                v["completeness"] == "UNKNOWN")
    A(_probe("no_ceiling_is_removable",
             "for every ceiling there is an invalid delta that only it "
             "catches — dropping any one admits that delta; evidence "
             "over the tested domain, never proof",
             _irreducible))

    # ── semantic persistence: the Hamilton test ──────────────────────
    import semantic_persistence as spr

    def _hamilton():
        h = spr.hamilton_test(spr.initial_state(), spr.drift_trace(),
                              spr.STANDARD_INVARIANTS)
        v = spr.persistence_gate(spr.initial_state(), spr.drift_trace(),
                                 spr.STANDARD_INVARIANTS)
        c = spr.fifth_ceiling_candidacy()
        return (h["witness_found"] is True and
                h["replay_is_exact"] is True and
                v["reason"] == "E_SEMANTIC_DRIFT" and
                c["fifth_ceiling_earned"] is True and
                c["completeness"] == "UNKNOWN")
    A(_probe("replayability_is_not_semantic_persistence",
             "a trace can pass all four ceilings and replay exactly "
             "while the kernel meaning drifts; unauthorized drift is "
             "refused by name — a constitution's reference must "
             "survive its history",
             _hamilton))

    # ── earned reliability: trust accumulates, never mints ──────────
    import earned_reliability as erl

    def _earned():
        q0 = erl.trust_at("newcomer", (), 0)
        veteran = tuple(erl.Exposure("v", i, "GATE_PASS", True)
                        for i in range(200))
        qv = erl.trust_at("v", veteran, 300)
        return (q0["grade"] == "UNKNOWN" and
                erl.declare_reputable("a")["reason"]
                == "E_SELF_DECLARED_REPUTATION" and
                erl.trust_from_test_pass(390, 60)
                ["entails_longitudinal_trust"] is False and
                erl.authority_from_trust(qv)["reason"]
                == "E_REPUTATION_IS_NOT_AUTHORITY" and
                erl.gate_skip_for_trusted(qv)["reason"]
                == "E_TRUST_DOES_NOT_SKIP_THE_GATE" and
                qv["infallible"] is False)
    A(_probe("trust_is_earned_never_declared",
             "Q_0 = UNKNOWN; a green suite is Q_instant, not trust; "
             "repeated witnessed survival raises evidence and never "
             "reaches infallibility; Trust_t(a) never mints "
             "Authority_{t+1}(a) nor skips the gate",
             _earned))

    # ── constitutional tolerances: the gate is measured, not binary ──
    import ceiling_algebra as _ca2
    import constitutional_tolerances as ctl

    def _tolerances():
        r = _ca2.Receipt("r_p", frozenset({"root_R", "root_S"}),
                         frozenset({"obj_A", "obj_B"}), "ADJUDICATED")
        robust = _ca2.Transition("d_r", frozenset({"root_R"}),
                                 frozenset({"obj_A"}), "OBSERVED", True)
        barely = _ca2.Transition("d_b", frozenset({"root_R", "root_S"}),
                                 frozenset({"obj_A"}), "ADJUDICATED",
                                 True)
        mr, mb = ctl.margins(robust, r), ctl.margins(barely, r)
        osc_ok = ctl.oscillator_check(_ca2.admit)["verdict"] \
            == "REFERENCE_HELD"
        osc_drift = ctl.oscillator_check(ctl.lenient_gate)
        chi = ctl.chi_susceptibility(robust, r)
        return (mr["robustly_admitted"] is True and
                mb["barely_admitted"] is True and
                osc_ok and osc_drift["verdict"] == "HOLD" and
                osc_drift["reason"] == "E_INTERPRETIVE_DRIFT" and
                chi["elinvar"] is True)
    A(_probe("gate_tolerances_are_measured",
             "admitted != robustly admitted (margin law); a lenient "
             "reinterpretation is HELD by the sealed reference corpus "
             "(hairspring); the verdict is invariant to naming and "
             "order, sensitive only to evidence (Elinvar)",
             _tolerances))

    # ── craft: knowledge inherits, authority never ──────────────────
    import craft as crf

    def _craft():
        heir = crf.inherit_craft(("procedures", "counterexamples",
                                  "authority_grant"), "heir")
        bound = crf.capability_bound(
            {"M0_institutional_knowledge": 0.9, "M1_builders": 0.7,
             "M2_tooling_and_eval": 0.8}, 0.85)
        old = crf.survival_assessment("x", True, True, True, False)
        silent = crf.learn_from_failure("f", False, 1)
        return (heir["stripped"] == ["authority_grant"] and
                heir["stripped_reason"] == "E_AUTHORITY_IS_NOT_HERITABLE"
                and bound["reason"] == "E_EXCEEDS_BUILDER_CAPABILITY"
                and old["status"]
                == "HISTORICALLY_ADMITTED_NOT_CURRENTLY_ADMISSIBLE"
                and old["present_authority_minted"] is False
                and silent["reason"] == "E_UNWITNESSED_FAILURE")
    A(_probe("memory_transfers_craft_never_authority",
             "the heir receives procedures and counterexamples, never "
             "grants; the artifact is bounded by its factory; "
             "historically admitted is not currently admissible; an "
             "unwitnessed failure teaches nothing",
             _craft))

    # ── metrology: the locked stack, and its guardrail ──────────────
    import metrology as mtl

    def _metrology():
        r = _ca2.Receipt("r_m", frozenset({"root_r"}),
                         frozenset({"obj_a"}), "ADJUDICATED")
        boundary = _ca2.Transition("d_c", frozenset({"ROOT_R"}),
                                   frozenset({"obj_a"}), "OBSERVED",
                                   True)
        far = _ca2.Transition("d_f",
                              frozenset({"root_r", "root_x", "root_y"}),
                              frozenset({"obj_a"}), "OBSERVED", True)
        a = mtl.alpha_minus(mtl.sloppy_verifier, (boundary, far), r)
        w = mtl.make_witness(mtl.sloppy_verifier, boundary, r)
        pi_catches_v = mtl.replay_witness(w)["reproduces"] is False
        mint = mtl.mint_law_from_unresolved("cannot resolve")
        return (mtl.signed_margin(boundary, r)["mu"] == -1 and
                a[1]["alpha_minus"] == 1.0 and
                a[2]["alpha_minus"] == 0.0 and
                pi_catches_v and
                mint["reason"] == "E_UNKNOWN_RESOLUTION_IS_NOT_NEW_LAW"
                and mtl.escalate("M_CANNOT_RESOLVE")
                ["authorizes_new_law"] is False)
    A(_probe("unknown_resolution_is_not_new_law",
             "the margin is signed; the defective verifier is found "
             "only at the boundary (alpha_- calibration); independent "
             "replay contradicts the false PASS; and a metrology "
             "failure routes to instrument upgrade, never to a new "
             "ceiling",
             _metrology))

    # ── the guard band: authority contracts below resolution ────────
    import guard_band as gbd

    def _guard():
        r = _ca2.Receipt("r_g", frozenset({"root_r", "root_s"}),
                         frozenset({"obj_a", "obj_b"}), "ADJUDICATED")
        d = _ca2.Transition("d_g", frozenset({"root_r"}),
                            frozenset({"obj_a"}), "OBSERVED", True)
        sharp = gbd.calibrated_admit(d, r, u=0.2, k=2.0)
        coarse = gbd.calibrated_admit(d, r, u=1.0, k=2.0)
        contract = gbd.authority_contraction(0.5, 0.5, k=2.0)
        bare = gbd.is_calibrated_result({"y": "ADMIT"})
        return (sharp["verdict"] == "ADMIT" and
                coarse["verdict"] == "HOLD_UNKNOWN" and
                contract["authority_contracts"] is True and
                contract["is_fifth_ceiling"] is False and
                bare["reason"] == "E_UNCALIBRATED_PASS")
    A(_probe("authority_contracts_below_resolution",
             "identical constitutional facts, coarser instrument -> "
             "HOLD not ADMIT; a bare PASS is an indication, not a "
             "calibrated result; the contraction is a guard band, "
             "never a fifth ceiling",
             _guard))

    # ── stack-up and ancestry: composition and consensus attacks ────
    import stack_up as stk

    def _stack():
        gap = stk.canonical_stack_up()
        attack = stk.garden_consensus_attack()
        shared = tuple({"id": f"W{i}", "ancestors": frozenset({"S0"})}
                       for i in range(5))
        u = stk.propagate_uncertainty(1.0, shared)
        return (gap["locally_certified"] is True and
                gap["stack_up_gap"] is True and
                attack["apparent_consensus"] == 5 and
                attack["ancestry_classes"] == 1 and
                u["u_tau"] == 1.0 and u["sqrt_n_earned"] is False)
    A(_probe("consensus_is_not_independence",
             "six locally certified stages compose past the trace "
             "budget; five witnesses with one ancestor are one "
             "observation; sqrt-N is earned by ancestry classes, "
             "never by head-count",
             _stack))

    # ── the negative control: the gate must be able to REFUSE ───────
    import mesmer_control as msc

    def _mesmer():
        nc = msc.negative_control()
        lp = msc.la_place_witnesses()
        cand = msc.design_grade_candidate(1000)
        chiddush = [f for f in msc.findings_table()
                    if f["is_constitutional_chiddush"]]
        return (nc["frozen_gate_rejects_central_claim"] is True and
                nc["attribution_1784"] == "EXPECTATION" and
                lp["mechanism_classes"] == 1 and
                lp["u_effective"] == 1.0 and
                cand["status"] == "CANDIDATE_NOT_LAW" and
                len(chiddush) == 1)
    # ── the epistemic lattice: four losses, never collapsed ─────────
    import epistemic_lattice as elt

    def _lattice():
        refusals = all(
            elt.infer(p, c)["reason"] == "E_ILLEGAL_ABSENCE_INFERENCE"
            for p, c in elt.ILLEGAL_INFERENCES)
        sig = elt.absence_signal("x", "OBSERVED")
        sim = elt.similarity_claim(True)
        return (refusals and len(elt.ILLEGAL_INFERENCES) == 6 and
                sig["verdict"] == "RESEARCH_SIGNAL" and
                sig["is_evidence_of_rejection"] is False and
                sim["reason"] == "E_GLYPH_TRAP")
    A(_probe("observed_is_not_survived_is_not_produced",
             "Generable > Produced > Survived > Observed: each arrow "
             "is a selection mechanism; the five illegal absence "
             "inferences refuse by name; absence is a research "
             "signal, never a rejection verdict",
             _lattice))

    # ── the production membrane: three executable checks ───────────
    import membrane as mbr

    def _membrane():
        v = mbr.membrane_holds()
        launder = mbr.promotion_gate("briefing", "REPORTED", "PROVEN",
                                     False, False)
        bypass = mbr.congruence_judgment("indirect_chain_delete", None)
        leak = mbr.cognition_attempt("draft", None, "s", "s", True)
        return (v["membrane_holds"] is True and
                v["canon"] is False and
                launder["reason"] == "E_UNLICENSED_PROMOTION" and
                bypass["reason"] == "E_UNCAPABLE_DESTRUCTION" and
                leak["reason"] == "E_READ_LEAK_TO_SINK")
    A(_probe("cognition_never_crosses_the_membrane",
             "A_K reads/proposes only (and within data scope); every "
             "spelling of destruction meets one judgment; a grade "
             "rise unpaid by witness or derivation is laundering",
             _membrane))

    # ── style lock: form rich, claims sober ─────────────────────────
    import style_lock as stl

    def _style():
        bare = stl.stamp("SEALED", None)
        color_only = stl.render_state(None, None, "black")
        res = stl.collision_resolution()
        return (bare["reason"] == "E_DECORATIVE_STATUS" and
                color_only["reason"] == "E_STATE_BY_COLOR_ALONE" and
                res["candidate_adopted"] is False and
                res["silent_supersede"] is False)
    # ── T-COLOR-01: factor the state space, do not replace it ───────
    import wulmoji_axes as wax

    def _axes():
        froz = wax.redefine_color("white", "void")
        conf = wax.token("restricted")
        dis = wax.axes_are_disjoint()
        res = wax.resolves_the_four_collisions()
        a = wax.sigma(E="observed", A="open", D="active", U="granted",
                      R="replayable")
        b = wax.sigma(E="observed", A="restricted", D="active",
                      U="denied", R="replayable")
        lossy = wax.same_colour_same_state(a, b)
        return (lossy["same_colour"] is True and
                lossy["same_state"] is False and
                wax.chi(a)["reads_projection"] == "E" and
                froz["reason"] == "E_COLOR_AXIS_FROZEN" and
                conf["reason"] == "E_AXIS_CONFUSION" and
                dis["future_collision_possible"] is False and
                res["atlas_entries_changed"] == 0 and
                res["one_color_one_meaning"] is True)
    A(_probe("palette_is_factored_never_replaced",
             "the epistemic palette is frozen and refuses "
             "redefinition; rival concepts live on an orthogonal "
             "marker axis; disjoint axes make future collisions "
             "structurally impossible",
             _axes))

    # ── T-INDUB-01: a grammar must predict AND compress ─────────────
    import indub as idb

    def _indub():
        struct = tuple({"pattern": p, "size": s, "state": st}
                       for p in (6, 9, 10) for s in (6, 12, 18, 24)
                       for st in ("OPEN", "TINT"))
        held = ({"pattern": 6, "size": 12, "state": "TINT"},)
        train = tuple(x for x in struct if x != held[0])
        good = idb.heldout_test(train, held)
        idio = tuple({"pattern": 100 + i, "size": 6 + i,
                      "state": "OPEN"} for i in range(24))
        bad = idb.heldout_test(idio[:-3], idio[-3:])
        inst = idb.instance_is_not_theorem("string verification", True,
                                           "conservation law")
        held2 = ({"pattern": 6, "size": 12, "state": "TINT"},)
        tr2 = tuple(x for x in struct if x != held2[0])
        ctrl_sym = idb.against_controls(tr2, held2)
        asym = (tuple({"pattern": 6, "size": s, "state": st}
                      for s in (6, 12) for st in ("OPEN", "TINT")) +
                tuple({"pattern": 9, "size": s, "state": st}
                      for s in (18, 24) for st in ("OPEN", "TINT")))
        ah = ({"pattern": 6, "size": 12, "state": "TINT"},)
        ctrl = idb.against_controls(
            tuple(x for x in asym if x != ah[0]), ah)
        rs = idb.research_state(32, tuple(range(43)), 5, 1)
        swarm = idb.swarm_scaling(32, 400, 0, 0)
        selnp = idb.selection_is_not_promotion("K_best", 0.99)
        adeq = idb.reconstructs_corpus_is_not_historically_used("K", True)
        space = idb.grammar_space(struct)
        sel = idb.select_unique(space, discriminating_evidence=False)
        return (good["verdict"] == "SUPPORTED" and
                ctrl["beats_all_three"] is True and
                ctrl_sym["verdict"] == "NO_UTILITY_DEMONSTRATED" and
                rs["collapse_hierarchy_holds"] is True and
                rs["effective_witnesses"] == 1 and
                swarm["promotion_licensed"] is False and
                swarm["authority_from_headcount"] == 0 and
                selnp["promoted"] is False and
                adeq["historically_used"] is None and
                space["unique"] is False and
                sel["reason"] == "E_NON_UNIQUE_RECONSTRUCTION" and
                idb.completion_is_not_validation("swarm", 0)
                ["grammar_validated"] is False and
                bad["verdict"] == "REFUTED" and
                bad["demoted_to"] == "DESCRIPTIVE_TAXONOMY" and
                inst["law_proven"] is False and
                idb.corpus_status()["reachable_from_this_seat"] is
                False)
    # ── proof ceiling: safety needs a positive control ──────────────
    import proof_ceiling as pcl

    def _ceiling():
        held = tuple({"id": f"t{i}",
                      "features": {"witness_ref": f"cat:{i}"}}
                     for i in range(4))
        fake = tuple({"id": f"f{i}", "features": {"witness_ref": None}}
                     for i in range(4))
        ch = pcl.challenge_set(held, fake)
        laun = pcl.evaluate(pcl.launderer, ch)
        para = pcl.evaluate(pcl.paralytic, ch)
        gov = pcl.evaluate(pcl.governed, ch)
        roots = pcl.historical_roots(
            tuple({"lineage": "rc_catalogue", "volume": v}
                  for v in (1, 2, 3, 4) for _ in range(3)))
        deny = pcl.promotion_verdict(True, 0, 0)
        return (laun["verdict"] == "FAIL_LAUNDERING" and
                para["E_promotion"] == 0.0 and
                para["verdict"] == "FAIL_PARALYSIS" and
                gov["verdict"] == "PASS" and
                roots["n_historical_roots"] == 1 and
                deny["reason"] == "E_PLAUSIBILITY_IS_NOT_HISTORY" and
                pcl.witness("c", None)["is_false"] is False)
    # ── Sigma_N: the table refuses projections ──────────────────────
    import scaling_harness as shs

    def _harness():
        proj = tuple(shs.row(N=n, H=h, Q=q, N_epi=1, W=1,
                             D_proposed=1, D_valid=0, A=0, E_gamma=0,
                             grade=shs.PROJECTED)
                     for n, h, q in ((1, 3, 3), (2, 8, 5)))
        meas = tuple(shs.row(N=n, H=h, Q=q, N_epi=1, W=1,
                             D_proposed=1, D_valid=0, A=a, E_gamma=0,
                             grade=shs.MEASURED)
                     for n, h, q, a in ((1, 3, 3, 0), (2, 8, 5, 1)))
        yld = shs.parse_yield_gate(0, 1)
        chunk = shs.canary_chunking("sha:x", "sha:x")
        return (shs.ingest(proj)["reason"] == "E_PROJECTED_ROW" and
                shs.check_invariant(meas)["verdict"] ==
                "FAIL_AUTHORITY_INFLATION" and
                yld["readable"] is False and
                chunk["new_root_minted"] is False and
                shs.root_redundancy(5, 1)["is_waste"] is None)
    # ── HELEN_GRAPH_IR_V0: three static checks + the fourth ─────────
    import graph_ir as gir

    def _ir():
        statics = all(
            gir.static_check(p, c)["licensed"] is False
            for p, c in gir.STATIC_CHECKS)
        no_auth = gir.edge("a", "b", "DATA", dA=1, witness="w")
        unwit = gir.edge("a", "b", "DERIVATION", dP=1)
        same = tuple(gir.edge(f"w{i}", "m", "DATA", root="ONE")
                     for i in range(4))
        gap = gir.globally_admissible(same, merge_root_count=4)
        honest = gir.globally_admissible(same, merge_root_count=1)
        return (statics and len(gir.STATIC_CHECKS) == 3 and
                no_auth["reason"] == "E_DATA_EDGE_CARRIES_AUTHORITY"
                and unwit["reason"] == "E_UNWITNESSED_PROMOTION" and
                gap["all_locally_admissible"] is True and
                gap["globally_admissible"] is False and
                gap["gap_detected"] is True and
                honest["globally_admissible"] is True)
    A(_probe("locally_admissible_is_not_globally_admissible",
             "the edge is non-promotional by default and DATA never "
             "carries authority; and four lawful edges over ONE root "
             "with a merge reporting four is caught — the dynamic "
             "check that makes a typed institutional runtime",
             _ir))

    # ── HELEN VISION V2: I -> G_R -> G_E -> G_W, never I -> G_W ─────
    import vision_ir as vir

    def _vision():
        r = vir.packet(I="img:x", kappa_M="PHOTOGRAPH",
                       kappa_F="PROMOTES", rho="unverified", t=None,
                       s="scan", u="operator")
        bare = vir.climb(r, frozenset(), visual_confidence=0.99)
        unsure = vir.climb(r, frozenset(), visual_confidence=0.01)
        held = vir.per_matrix(
            tuple({"from": "R", "to": "W", "bridged": False,
                   "answered": False} for _ in range(4)))
        launder = vir.per_matrix(
            ({"from": "R", "to": "W", "bridged": False,
              "answered": True},))
        return (r["ok"] is True and r["emits_world_claim"] is False and
                "G_W" not in r and
                vir.write_world_claim(
                    r, "phi3_referent_existed_by_date")["reason"] ==
                "E_VISION_MAY_NOT_WRITE_G_W" and
                vir.warrant(r, "phi3_referent_existed_by_date",
                            False, False, False)["reason"] ==
                "E_INCOMPLETE_WARRANT" and
                bare["rungs"]["phi1_visually_represented"] ==
                "SUPPORTED" and
                all(bare["rungs"][p] == "UNSUPPORTED"
                    for p in vir.LADDER[1:]) and
                bare["rungs"] == unsure["rungs"] and
                all(vir.confidence_independence(p, 0.05, 0.99)
                    ["orthogonal"] for p in vir.LADDER) and
                held["critical_PER_R_to_W"] == 0.0 and
                held["verdict"] == "FAIL_COVERAGE" and
                launder["verdict"] == "FAIL_LAUNDERING")
    A(_probe("no_perceptual_property_mints_a_world_state",
             "the vision packet has no world field to write; "
             "(PHOTOGRAPH, PROMOTES) is ordinary and buys no "
             "observation; the honest ladder is one yes and four noes "
             "at ANY visual confidence; and PER_R->W = 0 bought by "
             "answering nothing fails the coverage floor",
             _vision))

    A(_probe("a_projection_is_not_a_measurement",
             "a table of projected values may not enter Sigma_N; "
             "authority rising without a witness or a VALID "
             "derivation is inflation; an unparsed worker is a defect "
             "not a zero",
             _harness))

    A(_probe("plausibility_never_becomes_history",
             "a plausible-but-unwitnessed item may not be promoted to "
             "OBSERVED; and abstaining on everything scores a perfect "
             "promotion error while failing the positive control — "
             "safety proven by paralysis is not safety",
             _ceiling))

    A(_probe("a_grammar_must_predict_what_it_never_saw",
             "the same inducer returns SUPPORTED on product structure "
             "and REFUTED on an idiosyncratic family; predicting "
             "without compressing is HOLD; a verified instance is "
             "never an architecture theorem",
             _indub))

    A(_probe("beautiful_seal_is_not_admission",
             "a status word without its witness refuses; no state is "
             "encoded by color alone; the color-grammar amendment is "
             "the operator's to admit, never a silent supersede",
             _style))

    A(_probe("sincere_witnesses_do_not_sum_to_proof",
             "the 1844 negative control: eminent, sincere, numerous "
             "witnesses and a false central claim — refused on the "
             "PROOF ceiling and on undischarged defeaters; one "
             "mechanism class earns no sqrt-N; the corpus's one "
             "chiddush stays a candidate",
             _mesmer))

    return P


def assert_probe_raises(thunk, expected_msg) -> bool:
    """True iff thunk raises a ValueError whose message contains
    expected_msg — a raise is the refusal, and swallowing it is a
    failed probe."""
    try:
        thunk()
        return False
    except ValueError as exc:
        return expected_msg in str(exc)


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
