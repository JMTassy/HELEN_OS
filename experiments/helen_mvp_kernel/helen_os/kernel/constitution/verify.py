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
        # the rerun constraints
        halluc = shs.extraction("c", "Battalion", source_legible=False)
        blind = shs.ignorance_baseline(0, 0, 200)
        swarm = shs.swarm_common_mode(5, 1, 0.0, False)
        return (shs.ingest(proj)["reason"] == "E_PROJECTED_ROW" and
                shs.check_invariant(meas)["verdict"] ==
                "FAIL_AUTHORITY_INFLATION" and
                yld["readable"] is False and
                chunk["new_root_minted"] is False and
                shs.root_redundancy(5, 1)["is_waste"] is None and
                halluc["reason"] == "E_HALLUCINATED_LEGIBILITY" and
                blind["interpretable"] is False and
                swarm["N_effective_on_hypotheses"] == 1 and
                swarm["reason"] == "E_SWARM_COMMON_MODE" and
                shs.claim_status("A_N_flat")["status"] ==
                "TRUE_BY_CONSTRUCTION" and
                shs.claim_status("Q_N_rises")["status"] ==
                "FALSIFIABLE_THIS_RUN")
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

    # ── Phase A item 1: tenant isolation, enforced in the data path ─
    import tenant_runtime as trt

    def _tenant():
        s = trt.boot()
        s, _ = trt.provision_tenant(s, "A")
        s, _ = trt.provision_tenant(s, "B")
        s, ra = trt.open_handle(s, "A", ("store.read", "store.write"))
        s, _ = trt.write(s, ra["handle"], "A", "doc1", {"v": 1})
        s, _ = trt.publish_release(s, "rel", "sha:x")
        _, cross = trt.write(s, ra["handle"], "B", "doc1", {"v": 2})
        _, crossr = trt.read(s, ra["handle"], "B", "doc1")
        _, absent = trt.read(s, ra["handle"], "A", "nope")
        _, forged = trt.read(s, "0" * 16, "A", "doc1")
        _, ambient = trt.open_handle(s, "A", ("ALL",))
        _, cpw = trt.write_release_via_tenant(s, ra["handle"], "rel",
                                              "sha:evil")
        _, cpr = trt.read_release(s, ra["handle"], "rel")
        frozen = trt.canon(s)
        trt.write(s, ra["handle"], "A", "k", 9)
        inv = trt.isolation_invariant(s)
        return (cross["reason"] == "E_TENANT_BOUNDARY" and
                crossr["reason"] == absent["reason"] ==
                "E_NOT_READABLE" and
                forged["reason"] == "E_UNKNOWN_HANDLE" and
                ambient["reason"] == "E_AMBIENT_AUTHORITY" and
                cpw["reason"] == "E_CONTROL_PLANE_READ_ONLY" and
                cpr["ok"] is True and
                trt.canon(s) == frozen and
                inv["holds"] is True)
    A(_probe("isolation_is_a_property_of_the_state_not_a_promise",
             "a handle for A dies against B's data in the data path "
             "itself; a forged handle is unknown however well-formed; "
             "cross-boundary and absent-key are one indistinguishable "
             "answer so existence never leaks; releases are readable "
             "by all tenants and writable by none; no operation "
             "mutates its input; and the isolation invariant is "
             "re-derivable on the real state — the first vNext "
             "primitive that is code",
             _tenant))

    # ── I_5: the swarm's survivor, witnessed then closed ────────────
    def _rebind():
        import global_admissibility as gad5
        gap = gad5.global_validate(gad5.fixture_warrant_rebind())
        honest = gad5.global_validate(gad5.fixture_honest_warrant())
        return (gap["all_edges_locally_valid"] is True and
                gap["GLOBAL_RESULT"] == gad5.FAIL and
                gap["REASON"] == "E_WARRANT_VALUE_REBIND" and
                honest["GLOBAL_RESULT"] == gad5.PASS)
    # ── I_6: candidate #7, witnessed then closed ────────────────────
    def _readrace():
        import global_admissibility as gad6
        gap = gad6.global_validate(
            gad6.fixture_read_contradiction(),
            roots=frozenset({"src1", "src2"}))
        ctrl = gad6.global_validate(
            gad6.fixture_consistent_reads(),
            roots=frozenset({"src1", "src2"}))
        i6 = gad6.I6_read_consistency(
            gad6.fixture_read_contradiction())
        return (gap["all_edges_locally_valid"] is True and
                gap["GLOBAL_RESULT"] == gad6.FAIL and
                gap["REASON"] == "E_READ_TIME_CONTRADICTION" and
                i6["reads_commute"] is False and
                i6["contradicted_slots"] == ("mu@t1",) and
                ctrl["GLOBAL_RESULT"] == gad6.PASS)
    A(_probe("a_graph_whose_state_depends_on_read_order_is_a_race",
             "swarm candidate #7 witnessed a real gap — opposite "
             "bits for one slot in one time slice passed I_1..I_5 "
             "and global_validate at commit f75b427, with the "
             "observed state flipping under read-order reversal — "
             "and I_6 now refuses the contradiction while redundancy "
             "and cross-slice supersession still pass",
             _readrace))

    # ── CROSS_MODEL_INDEPENDENCE_V0: frozen before observation ──────
    import cross_model_independence as cmi

    def _crossmodel():
        axes = cmi.independence_axes(2, 2, 1)
        prose = cmi.delta_q_useful(frozenset({"a"}),
                                   frozenset({"a", "b"}))
        mixed = cmi.decoding_regime({"t": 0.7}, {"t": 1.0},
                                    "E1_controlled")
        base = cmi.baseline_config(True, True, False)
        gate0 = cmi.promotion_gate(0, True, True)
        gate2 = cmi.promotion_gate(2, True, True)
        return (axes["independent_proposers"] is True and
                axes["independent_witnesses"] is False and
                cmi.collapse_to_neff(axes)["reason"] ==
                "E_COLLAPSED_AXES" and
                cmi.useful(True, True, True, None)["reason"] ==
                "E_NO_DISCRIMINATOR" and
                prose["verdict"] == "NO_COVERAGE_BOUGHT" and
                mixed["reason"] == "E_MIXED_DECODING_REGIMES" and
                len(base["refusals"]) == 3 and
                cmi.first_witness({"model_loaded": True})["reason"]
                == "E_UNPROBED_MODEL" and
                cmi.vendor_claim("x")["grade"] == "REPORTED_EXTERNAL"
                and gate0["reason"] == "E_NO_MARGINAL_COVERAGE" and
                gate2["seat_earned"] is True and
                gate2["authority_delta"] == 0)
    A(_probe("a_different_lineage_does_not_make_n_eff_two",
             "two proposers over one corpus are one witness and the "
             "three axes never collapse; a surviving class without "
             "its discriminator is admiration; controlled and native "
             "decoding never mix silently; thinking, hidden memory "
             "and context width are refused at baseline; an unprobed "
             "model never enters the research graph; and no branch "
             "of the promotion gate grants authority",
             _crossmodel))

    # ── I_7: candidate #10, witnessed then closed ───────────────────
    def _fold():
        import global_admissibility as gad7
        gap = gad7.global_validate(gad7.fixture_temporal_fold())
        ctrl = gad7.global_validate(gad7.fixture_lawful_succession())
        i7 = gad7.I7_temporal_folding(gad7.fixture_temporal_fold())
        return (gap["all_edges_locally_valid"] is True and
                gap["GLOBAL_RESULT"] == gad7.FAIL and
                gap["REASON"] == "E_TEMPORAL_FOLDING" and
                i7["folded"] == ("mu:[2,3)=X|Y",) and
                ctrl["GLOBAL_RESULT"] == gad7.PASS)
    A(_probe("a_slot_may_not_be_valid_in_two_slices_at_once",
             "swarm candidate #10 witnessed a real gap — two "
             "warranted persistences gave one slot overlapping "
             "validity intervals with different values, passing "
             "I_1..I_6 and global_validate at commit 52bcb43, a "
             "contradiction in extension that no observed point "
             "carries — and I_7 now refuses the fold while touching "
             "intervals and idempotent redundancy stay lawful",
             _fold))

    A(_probe("a_warrant_binds_the_value_it_was_minted_over",
             "the swarm survivor CHID-SMITH-1793 witnessed a real "
             "gap — a warrant over value X reattached to value Y "
             "passed all four invariants and global_validate at "
             "commit 92f01d5 — and I_5 now refuses the rebind while "
             "the honestly-paired warrants still pass",
             _rebind))

    # ── Phase A item 2: the grantor may not be the grantee ──────────
    import identity_runtime as idr

    def _identity():
        s = idr.boot()
        s, _ = idr.register_identity(s, "admin")
        s, _ = idr.register_identity(s, "user")
        s, _ = idr.define_role(s, "iam_admin", ("iam.role.bind",))
        s, _ = idr.define_role(s, "reader", ("store.read",))
        s, _ = idr.bootstrap_bind(s, "admin", "iam_admin", "A")
        s, ra = idr.open_session(s, "admin")
        s, ru = idr.open_session(s, "user")
        _, selfg = idr.bind_role(s, ra["session"], "admin", "reader",
                                 "A")
        s, _ = idr.bind_role(s, ra["session"], "user", "reader", "A")
        s, okA = idr.authorize(s, ru["session"], "store.read", "A")
        _, inB = idr.authorize(s, ru["session"], "store.read", "B")
        _, wcap = idr.authorize(s, ru["session"], "store.write", "A")
        _, forged = idr.authorize(s, "f" * 16, "store.read", "A")
        s, _ = idr.revoke_role(s, ru["session"], "user", "reader",
                               "A")
        _, after = idr.authorize(s, ru["session"], "store.read", "A")
        _, god = idr.define_role(idr.boot(), "god", ("ALL",))
        return (selfg["reason"] == "E_SELF_GRANT" and
                okA["ok"] is True and
                inB["reason"] == wcap["reason"] ==
                "E_NOT_AUTHORIZED" and
                forged["reason"] == "E_UNKNOWN_SESSION" and
                after["ok"] is False and
                god["reason"] == "E_AMBIENT_AUTHORITY" and
                idr.rbac_invariant(s)["holds"] is True)
    A(_probe("the_grantor_may_not_be_the_grantee",
             "self-elevation is refused even holding iam.role.bind; "
             "a binding in tenant A licenses nothing in tenant B and "
             "cross-tenant and missing-capability are one "
             "indistinguishable answer; a forged session is unknown; "
             "revocation is immediate and self-revocation needs no "
             "permission; no role carries ambient authority; and the "
             "RBAC invariant is re-derivable on the real state",
             _identity))

    # ── Phase A item 6: the gateway decides, the app never names ────
    import gateway_runtime as gwr

    def _gateway():
        s = gwr.boot()
        s, _ = gwr.register_provider(s, "eu_a", ("EU",),
                                     "confidential", ("reasoning",),
                                     False, "flat_effort")
        s, _ = gwr.register_provider(s, "eu_b", ("EU",), "internal",
                                     ("reasoning",), False, "nested")
        s, _ = gwr.register_provider(s, "loc", ("EU",), "restricted",
                                     ("reasoning",), True, "enable")
        s, _ = gwr.set_policy(s, "T", ("eu_a", "eu_b", "loc"), True,
                              1000)
        req = {"capability": "reasoning",
               "classification": "confidential",
               "latency": "interactive", "jurisdiction": "EU"}
        _, named = gwr.execute(s, "T", req, "med", 10, "sha:p",
                               vendor_named="Claude")
        s, ok = gwr.execute(s, "T", req, "med", 100, "sha:p")
        _, mars = gwr.execute(s, "T", {**req, "jurisdiction": "MARS"},
                              "med", 10, "sha:p")
        s2, _ = gwr.set_policy(s, "T", ("eu_a", "loc"), False, 1000)
        s2, localonly = gwr.execute(s2, "T", req, "med", 10, "sha:p")
        s3, big = gwr.execute(s, "T", req, "med", 950, "sha:p")
        return (named["reason"] == "E_VENDOR_IN_BUSINESS_LOGIC" and
                ok["ok"] is True and ok["routed_to"] != "eu_b" and
                ok["emits_world_claim"] is False and
                (ok["dP"], ok["dA"], ok["dE"]) == (0, 0, 0) and
                "emitted_wire_shape" in ok["wire_receipt"] and
                mars["reason"] == "E_NO_LAWFUL_ROUTE" and
                localonly["routed_to"] == "loc" and
                big["reason"] == "E_BUDGET_EXHAUSTED" and
                gwr.gateway_invariant(s)["holds"] is True)
    A(_probe("the_gateway_decides_and_the_app_never_names",
             "naming a vendor dies at the gateway; routing is policy "
             "intersection and an empty intersection refuses rather "
             "than widening; confidential data never reaches an "
             "uncleared provider; no-external routes to the local "
             "model; the meter is the gateway's; the wire receipt "
             "records what was sent, not what was meant; and every "
             "response is a non-promotional representation with "
             "dP = dA = dE = 0",
             _gateway))

    # ── Phase A item 5: the ground does not move under a client ─────
    import api_runtime as apr

    def _api():
        eps = {"get_doc": {"capability": "docs.read",
                           "request": {"id": "string",
                                       "verbose": "bool"},
                           "required": ("id",),
                           "response": {"id": "string",
                                        "title": "string"}}}
        s = apr.boot()
        s, defined = apr.define_contract(s, "1.0", eps)
        thin = {"get_doc": {**eps["get_doc"],
                            "response": {"id": "string"}}}
        _, brk = apr.evolve(s, "1.0", "1.1", thin)
        _, gone = apr.evolve(s, "1.0", "2.0", {})
        s2, _ = apr.deprecate(s, "1.0", "get_doc", "2.0")
        _, lawful = apr.evolve(s2, "1.0", "2.0", {})
        ghost = apr.request(s, "1.0", "nope", {}, True)
        denied = apr.request(s, "1.0", "get_doc", {"id": "x"}, False)
        leak = apr.respond(s, "1.0", "get_doc",
                           {"id": "x", "title": "t",
                            "goblin_trace": "HER"})
        thin_resp = apr.respond(s, "1.0", "get_doc", {"id": "x"})
        d1 = apr.contract_digest(s, "1.0")["digest"]
        s3 = apr.boot()
        s3, _ = apr.define_contract(s3, "1.0", eps)
        return (defined["ok"] is True and
                brk["reason"] == "E_BREAKING_CHANGE_IN_MINOR" and
                gone["reason"] == "E_REMOVAL_WITHOUT_DEPRECATION"
                and lawful["ok"] is True and
                ghost["reason"] == denied["reason"] == "E_NOT_FOUND"
                and leak["reason"] ==
                "E_UNDECLARED_RESPONSE_FIELD" and
                thin_resp["reason"] == "E_INCOMPLETE_RESPONSE" and
                apr.contract_digest(s3, "1.0")["digest"] == d1)
    A(_probe("the_ground_does_not_move_under_a_client",
             "the contract is content-addressed and its digest "
             "reproduces; dropping a response field in a minor is a "
             "breaking change; removal without deprecation dies even "
             "across a major; unknown endpoint and unauthorized are "
             "one indistinguishable answer; and the boundary is "
             "bidirectional — an internal goblin_trace field "
             "physically cannot cross the wire, and a declared field "
             "cannot be silently absent",
             _api))

    # ── Phase A item 4: tampering is arithmetic, not policy ─────────
    import audit_runtime as aur

    def _audit_store():
        s = aur.boot()
        for i in range(3):
            s, _ = aur.append(s, "A", {"kind": "WRITE", "actor": "u",
                                       "value_digest": f"d{i}"})
        _, unattr = aur.append(s, "A", {"kind": "K"})
        _, raw = aur.append(s, "A", {"kind": "K", "actor": "u",
                                     "value": "secret"})
        intact = aur.verify_chain(s, "A")
        a = aur.anchor(s, "A")
        chain = list(s["chains"]["A"])
        ev = dict(chain[0])
        ev["actor"] = "evil"
        chain[0] = ev
        tam = dict(s)
        tam["chains"] = {**s["chains"], "A": tuple(chain)}
        broken = aur.verify_chain(tam, "A")
        cut = dict(s)
        cut["chains"] = {**s["chains"], "A": s["chains"]["A"][:1]}
        cut_ok = aur.verify_chain(cut, "A")
        trunc = aur.verify_against_anchor(cut, "A", a)
        unanch = aur.verify_against_anchor(s, "A",
                                           {"anchored": False})
        verbs = [n for n in dir(aur) if not n.startswith("_")]
        return (unattr["reason"] == "E_UNATTRIBUTED_EVENT" and
                raw["reason"] == "E_RAW_VALUE_IN_AUDIT" and
                intact["intact"] is True and
                broken["reason"] == "E_CHAIN_BROKEN" and
                cut_ok["intact"] is True and
                trunc["reason"] == "E_CHAIN_TRUNCATED" and
                unanch["reason"] == "E_UNANCHORED" and
                not any("delete" in v or "update" in v
                        for v in verbs))
    A(_probe("tampering_is_arithmetic_not_policy",
             "an edited audit event breaks every hash after it; a "
             "truncated tail survives chain verification and dies at "
             "the external anchor; an unanchored chain is unanchored "
             "not safe; raw values never enter the log; and "
             "append-only is an API fact — the module exports no "
             "update and no delete",
             _audit_store))

    # ── Phase A item 3: the engine owns every arrow ─────────────────
    import workflow_runtime as wfr

    def _workflow():
        st = ("NEW_DOCUMENT", "CLASSIFY", "REVIEW", "DONE")
        ed = (("NEW_DOCUMENT", "CLASSIFY"), ("CLASSIFY", "REVIEW"),
              ("REVIEW", "DONE"))
        s = wfr.boot()
        s, _ = wfr.define_workflow(s, "w", st, ed,
                                   (("REVIEW", "DONE"),))
        s, _ = wfr.start_instance(s, "w", "i1", "user")
        s, rec = wfr.record_step(s, "i1", "CLASSIFY", "invoice",
                                 "llm")
        _, llm = wfr.advance(s, "i1", "CLASSIFY", by="llm")
        _, jump = wfr.advance(s, "i1", "DONE", by="workflow_engine")
        s, _ = wfr.advance(s, "i1", "CLASSIFY", by="workflow_engine")
        s, _ = wfr.advance(s, "i1", "REVIEW", by="workflow_engine")
        _, gate = wfr.advance(s, "i1", "DONE", by="workflow_engine")
        _, selfap = wfr.approve(s, "i1", ("REVIEW", "DONE"), "user")
        s, _ = wfr.approve(s, "i1", ("REVIEW", "DONE"), "reviewer")
        s, done = wfr.advance(s, "i1", "DONE", by="workflow_engine")
        rep = wfr.replay(s, "i1")
        inst = dict(s["instances"]["i1"])
        inst["state"] = "CLASSIFY"
        tampered = dict(s)
        tampered["instances"] = {**s["instances"], "i1": inst}
        bad = wfr.replay(tampered, "i1")
        return (rec["state_moved"] is False and
                llm["reason"] == "E_LLM_IS_NOT_STATE_AUTHORITY" and
                jump["reason"] == "E_UNDECLARED_TRANSITION" and
                gate["reason"] == "E_UNAPPROVED_GATE" and
                selfap["reason"] == "E_SELF_APPROVAL" and
                done["ok"] is True and
                rep["ok"] is True and
                bad["reason"] == "E_HISTORY_MISMATCH")
    A(_probe("the_engine_owns_every_arrow",
             "the model records results and never advances state; "
             "undeclared jumps and unapproved gates die at runtime; "
             "the requester may not approve its own instance; and "
             "replay refolds the append-only history or declares the "
             "instance corrupt — the stored field is a cache, the "
             "history is the truth",
             _workflow))

    # ── layered frontier: conservation of minting rights ────────────
    import layered_frontier as lfr

    def _frontier():
        nd = {f: "0" for f in lfr.FRONTIERS if f != "F_S"}
        good = lfr.transition("substrate", "STALLED", "COMPLETE",
                              {"F_S": 1}, {"F_S": "byte_growth"},
                              nd, "stat at t1/t2")
        unlic = lfr.transition("substrate", "a", "b", {"F_S": 1}, {},
                               nd, "r")
        nodelta = lfr.transition("substrate", "a", "b", {"F_S": 1},
                                 {"F_S": "l"}, {}, "r")
        press = lfr.pressure_conservation(99.0, 0, 0)
        cross = lfr.cross_advance("F_S", "F_I", licensed=False)
        m = lfr.mint("representation", "empirical_warrant")
        flat = lfr.elasticity(10, 10, 1.0, 3.0)
        proxy = lfr.proxy_root(True, frozenset({"S"}), "S")
        ghost = lfr.capability_mint("kappa_lineage", frozenset())
        return (proxy["N_epi"] == 1 and
                proxy["reason"] == "E_PROXY_IS_NOT_A_ROOT" and
                ghost["reason"] == "E_UNLICENSED_CAPABILITY_MINT" and
                good["four_questions_answered"] is True and
                unlic["reason"] == "E_UNLICENSED_TRANSITION" and
                nodelta["reason"] == "E_MISSING_NON_DELTAS" and
                press["delta_F_E"] == 0 and
                press["reason"] == "E_PRESSURE_IS_NOT_EVIDENCE" and
                cross["reason"] == "E_UNLICENSED_COUPLING" and
                m["reason"] == "E_MINTING_RIGHTS_VIOLATION" and
                lfr.epistemic_pressure(100, 1)["Pi_C"] == 100.0 and
                flat["economically_useless"] is True)
    A(_probe("progress_at_one_layer_cannot_mint_the_next",
             "every nonzero frontier delta needs its license and "
             "every unmoved frontier its NON_DELTA entry; a hundred "
             "representations of one root are pressure, not "
             "evidence, and move the epistemic frontier by zero; "
             "representation may not mint a warrant; downloaded does "
             "not entail loadable; and flat yield at tripled cost is "
             "measured as economically useless",
             _frontier))

    # ── receipt integrity: the membrane on the kernel's metadata ────
    import receipt_integrity as rin

    def _integrity():
        untyped = rin.type_hex("16ea385e82213c7c", None)
        unrun = rin.re_derive("C_test", False, False)
        unscoped = rin.receipt_integrity(True, True, {}, True)
        undeps = rin.receipt_integrity(
            True, True, {k: "x" for k in rin.SCOPE_FIELDS}, False)
        vote = rin.aggregate({k: "PASS" for k in rin.CLAIM_CLASSES},
                             as_vote=True)
        held = dict({k: "PASS" for k in rin.CLAIM_CLASSES},
                    C_pii="PENDING")
        digest_only = rin.proof_carrying_receipt(claim="c",
                                                 digest="x")
        short_seal = rin.seal(frozenset({"intent", "test",
                                         "post_mutation"}))
        return (untyped["reason"] == "E_UNTYPED_HEX" and
                unrun["status"] == "FABRICATED_UNTIL_WITNESSED" and
                unscoped["reason"] == "E_UNSCOPED_CLAIM" and
                undeps["reason"] == "E_UNDECLARED_DEPENDENCIES" and
                vote["reason"] == "E_VOTE_ACROSS_CLASSES" and
                rin.aggregate(held)["verdict"] ==
                "PARTIALLY_DISCHARGED" and
                rin.aggregate({k: "PASS" for k in
                               rin.CLAIM_CLASSES})["verdict"] ==
                "DISCHARGED" and
                digest_only["reason"] == "E_RECIPE_LESS_RECEIPT" and
                short_seal["reason"] == "E_INCOMPLETE_SEAL" and
                rin.reflexive_law()["licensed"] is False)
    A(_probe("receipt_text_is_not_a_rederivable_receipt",
             "an untyped hex may not be verified as anything; an "
             "unrun recipe leaves the claim FABRICATED_UNTIL_"
             "WITNESSED; a re-derivable claim without its scope has "
             "no integrity; classes never aggregate as a vote and "
             "one pending class holds the audit open; a digest "
             "without its recipe is not a receipt; and a seal needs "
             "all four witnesses — the kernel's membrane applies to "
             "its own metadata",
             _integrity))

    # ── vNext round 2: workforce hidden, not erased ─────────────────
    import workforce_runtime as wfr

    def _workforce():
        bought = wfr.width_expansion(10.0, 1.0, False)
        detc = wfr.boundary_promise("deterministic_cognition")
        proba = wfr.boundary_promise("probabilistic_authority")
        exe = wfr.pipeline_step("EXECUTE", admitted=False)
        obs = wfr.observer_report(("friction",
                                   "reorganization_order"))
        costs = {k: 1.0 for k in wfr.AGENT_COSTS}
        short = dict(costs)
        del short["coordination"]
        dictation = wfr.tacit_capture("OPERATOR", "claim")
        bare = wfr.plane("control_plane")
        return (bought["reason"] == "E_WIDTH_BOUGHT_AUTHORITY" and
                wfr.width_expansion(10.0, 0, False)["lawful"] and
                detc["reason"] == "E_OVERPROMISED_DETERMINISM" and
                proba["reason"] == "E_PROBABILISTIC_AUTHORITY" and
                exe["reason"] == "E_UNADMITTED_EXECUTION" and
                obs["reason"] == "E_OBSERVER_HAS_NO_AUTHORITY" and
                wfr.critic_emission("directive")["reason"] ==
                "E_CRITIC_MAY_ONLY_PROPOSE" and
                wfr.hire_agent(100.0, short)["reason"] ==
                "E_UNPRICED_COST" and
                wfr.hire_agent(5.0, costs)["reason"] ==
                "E_AGENT_COUNT_IS_NOT_A_KPI" and
                dictation["epistemic_state"] == "REPORTED" and
                dictation["promoted"] is False and
                wfr.factory_gate(2)["verdict"] ==
                "PRODUCTIZE_THE_FACTORY" and
                bare["reason"] == "E_AMBIGUOUS_PLANE" and
                len(wfr.LAWS) == 4)
    A(_probe("cognitive_width_may_not_buy_effect_authority",
             "width expands with authority flat and authority moves "
             "only through the admitted policy door; deterministic "
             "cognition and probabilistic authority are both "
             "overpromises; EXECUTE never precedes ADMIT; the "
             "observer commands nothing and the critic only "
             "proposes; an unpriced coordination cost blocks the "
             "hire; dictation enters as REPORTED; the second "
             "automation productizes the factory; and the bare term "
             "control plane is ambiguous by law",
             _workforce))

    # ── vNext: applications outside, HELEN inside ───────────────────
    import vnext_architecture as vna

    def _vnext():
        leak = vna.external_surface(("HAL", "SOPHIA"))
        cp = vna.control_plane_contents(("software_versions",
                                         "client_secrets"))
        vendor = vna.inference_call({"capability": "r"},
                                    vendor_named="Claude")
        ok_call = vna.inference_call(
            {"capability": "reasoning",
             "classification": "confidential",
             "latency": "interactive", "jurisdiction": "EU"}, None)
        ambient = vna.capability_grant("app", ("ALL",))
        llm = vna.advance_workflow("A", "B", by="llm")
        vec = vna.authoritative_read("vector_index")
        only_ai = vna.governance_scope(frozenset({"ai_call"}))
        gate = vna.roadmap_gate(frozenset(),
                                "autonomous_worker_expansion")
        return (leak["reason"] == "E_MYTHOLOGY_ON_EXTERNAL_SURFACE"
                and cp["reason"] == "E_CUSTOMER_DATA_IN_CONTROL_PLANE"
                and vendor["reason"] == "E_VENDOR_IN_BUSINESS_LOGIC"
                and ok_call["ok"] is True and
                ambient["reason"] == "E_AMBIENT_AUTHORITY" and
                llm["reason"] == "E_LLM_IS_NOT_STATE_AUTHORITY" and
                vec["reason"] == "E_DERIVED_IS_NOT_AUTHORITATIVE" and
                only_ai["reason"] == "E_ONLY_AI_GOVERNED" and
                gate["reason"] == "E_FOUNDATION_INCOMPLETE" and
                vna.tenant_isolation(frozenset({"db"}),
                                     frozenset({"db"}), frozenset())[
                    "reason"] == "E_TENANT_OVERLAP")
    A(_probe("the_enterprise_boundary_is_deterministic_software",
             "mythology never crosses the boundary; the control "
             "plane holds no customer data; business logic may not "
             "name a model vendor; no ambient authority; the LLM "
             "cannot advance a workflow; a vector index is never "
             "institutional truth; tenants share only control-plane "
             "artifacts; governing only AI actions is refused by "
             "name; and worker expansion waits for the foundation",
             _vnext))

    # ── editor doctrine: rename lawful iff witnessed ────────────────
    import editor_membrane as edm

    def _editor():
        unsealed = edm.rename("agent IA", frozenset())
        sealed = edm.rename("agent IA",
                            frozenset({"versioned_release"}))
        repo = edm.continuity_package(frozenset({"source_code"}))
        full = edm.continuity_package(
            frozenset(edm.CONTINUITY_PACKAGE))
        untested = edm.takeover_test(full, False, False, None)
        passed = edm.takeover_test(full, True, True, 36)
        rel = edm.escrow_release("liquidation", True)
        cert = edm.certification_claim("p", "IN_PROGRESS", True)
        hard = edm.gateway_substitution("any", gateway_present=False)
        return (unsealed["reason"] == "E_SEAL_WITHOUT_ADMISSION" and
                sealed["ok"] is True and
                repo["reason"] == "E_SOURCE_IS_NOT_RECOVERABILITY" and
                untested["reason"] == "E_UNTESTED_CONTINUITY" and
                passed["key_person_risk_reduced"] is True and
                rel["ip_transferred"] is False and
                cert["reason"] == "E_NARRATIVE_SKIP" and
                edm.certification_claim("p", "QUALIFIED", False)[
                    "reason"] == "E_CERT_SCOPE_OVERREACH" and
                hard["reason"] == "E_HARDCODED_VENDOR" and
                edm.compliance_non_entailment()["reason"] ==
                "E_INFRA_SECURITY_IS_NOT_APP_COMPLIANCE" and
                edm.key_person_status(True, True, False)[
                    "eliminated_claimable"] is False)
    A(_probe("a_rename_without_its_witness_is_a_seal_without_admission",
             "calling an agent an application is lawful only against "
             "a versioned release; a repo alone is not "
             "recoverability; untested continuity is an untested "
             "class; escrow release transfers no IP; IN_PROGRESS "
             "sold as QUALIFIED is a narrative skip; a "
             "qualification never covers the catalogue; and without "
             "a gateway the application IS the model vendor",
             _editor))

    # ── J3 harvest: decision boundaries, all CANDIDATE ──────────────
    import decision_boundaries as dbd

    def _boundaries():
        skip = dbd.state_transition("REQUESTED", "CONTRACTED", "w")
        rej = dbd.qualify(0.9, 0.8, 0.5, evsi=100.0, probe_cost=1.0)
        unpinned = dbd.governance_debt(((0.9, 0.1, 1.0),),
                                       {"frozen": False})
        hind = dbd.surface_point("HOLD", {"eventual_outcome": 1},
                                 "thread:x")
        conf = dbd.reinforcement(True, True)
        neg = dbd.reinforcement(True, False, survived=True)
        return (skip["reason"] == "E_NARRATIVE_SKIP" and
                dbd.typed_amount("REQUESTED", True, None)["reason"] ==
                "E_UNTYPED_AMOUNT" and
                rej["act"] == "REJECT" and
                rej["checked_first"] == "U_d" and
                unpinned["reason"] == "E_UNPINNED_CODER" and
                "D_gov" not in unpinned and
                dbd.delta_v(10.0, 9.0, 2.0)["keep_external"] is False
                and hind["reason"] == "E_HINDSIGHT_VARIABLE" and
                dbd.engine_task("recommend what to do")["reason"] ==
                "E_OUT_OF_SCOPE" and
                conf["reinforced"] is False and conf["accumulates"]
                and neg["reinforced"] is True and
                dbd.promote_to_canon("anything")["reason"] ==
                "E_CANDIDATE_IS_NOT_CANON")
    A(_probe("confirmations_accumulate_and_never_reinforce",
             "no commercial amount without state, date and "
             "provenance, and no arrow skipped by narration; "
             "disqualifying uncertainty is checked before any probe "
             "budget; governance debt yields no number without a "
             "pinned coder; a surface learned on hindsight variables "
             "is refused; the engine may not recommend; and a "
             "candidate method is reinforced only by surviving "
             "predictors-present-effect-absent",
             _boundaries))

    # ── TEST 1: PASS/PASS locally, FAIL globally ────────────────────
    import global_admissibility as gad

    def _global():
        ds = gad.fixture_double_spend()
        g = gad.global_validate(ds)
        honest = gad.global_validate(gad.fixture_honest_spend())
        selfsup = gad.I3_no_self_supporting_root(
            gad.fixture_self_support(), roots=frozenset())
        grounded = gad.I3_no_self_supporting_root(
            gad.fixture_grounded_chain(), roots=frozenset({"r"}))
        deep = gad.I2_foundationally_acyclic(
            tuple(gad.gedge(f"n{i}", f"n{i+1}", gad.DERIVE)
                  for i in range(200)))
        gap = gad.I4_temporal_persistence(gad.fixture_temporal_gap())
        return (all(v == gad.PASS for v in g["LOCAL_EDGE_RESULTS"]) and
                g["GLOBAL_RESULT"] == gad.FAIL and
                g["REASON"] == "CAPABILITY_DOUBLE_SPEND" and
                g["MUTATIONS_COMMITTED"] == 0 and
                g["gap_witnessed"] is True and
                honest["GLOBAL_RESULT"] == gad.PASS and
                selfsup["reason"] == "FAIL_PROVENANCE_SELF_SUPPORT" and
                grounded["verdict"] == gad.PASS and
                deep["verdict"] == gad.PASS and
                gap["verdict"] == gad.UNDEFINED and
                gad.registration(20, 0)["status"] ==
                "REGISTERED_PRECLAIM_AGENDA" and
                gad.attack_coverage((("s1",), ("s1",), ("s1",)))[
                    "coverage_attack"] == 1 and
                gad.undeclared_influence(("policy_set",))["reason"] ==
                "E_UNDECLARED_INFLUENCE")
    A(_probe("a_lawful_institution_is_not_a_collection_of_lawful_edges",
             "three edges each PASS a local validator and the "
             "assembled graph FAILS on UseCount(kappa) = 2 > 1, with "
             "zero mutations committed; one mint and one invoke still "
             "PASS, so the checker refuses the double and not the "
             "spend; self-support is judged by unreachable roots, not "
             "by the presence of a cycle; a 200-deep DAG is exactly "
             "acyclic; and transport without a connection is "
             "UNDEFINED rather than false",
             _global))

    # ── EPIS-CYCLE-ONT-01: the debtor may not be the creditor ───────
    import ontological_frontier as onf

    def _frontier():
        ob = onf.crossing_obligation(
            claim="CSH-X was built to the published plan",
            referent="CSH-X", required_witness="construction photo",
            created_by="HER")
        selfd = onf.discharge(ob, by="HER", witness="photo:x")
        fused = {"ok": True, "state": onf.OPEN,
                 "side": onf.REPRESENTATION, "claim": "c",
                 "referent": "r", "required_witness": "w",
                 "created_by": "HAL_X"}
        lawful = onf.discharge(ob, by="HAL_X", witness="photo:x",
                               witness_supplied_by="HAL_W")
        return (selfd["reason"] == "E_SELF_DISCHARGE" and
                onf.discharge(fused, by="HAL_X", witness="w")[
                    "reason"] == "E_SELF_DISCHARGE" and
                onf.discharge(ob, by="HAL_X", witness=None)[
                    "reason"] == "E_UNDISCHARGED_CROSSING" and
                onf.cross(ob, selfd, by="HAL_X")["verdict"] ==
                onf.HOLD and
                onf.cross(ob, lawful, by="HAL_X")["verdict"] ==
                onf.PROMOTE and
                onf.cross(ob, lawful, by="HAL_W")["reason"] ==
                "E_ROLE_LACKS_POWER" and
                onf.compression_is_not_evidence("QWEN", 40000, 2000)[
                    "witnesses_added"] == 0 and
                onf.inherits_status("drawing", "EXISTED", False)[
                    "inherited_status"] is None and
                onf.gamma_growth(40, 480, 0)["gamma_growth_licensed"]
                == 0 and
                onf.epoch(7, 12, 12, 0)[
                    "canon_promoted_by_this_epoch"] == 0 and
                onf.generator_independence(12, 1)[
                    "N_effective_on_hypotheses"] == 1)
    A(_probe("a_representation_never_inherits_its_referents_status",
             "a crossing is a debt and the debtor may not be the "
             "creditor: a proposer discharging its own obligation is "
             "refused even when the witness is real and the role "
             "table is bypassed; compression mints no witness; forty "
             "epochs and 480 proposals grow Gamma by zero; and twelve "
             "proposals from one model are one generator",
             _frontier))

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
             "not a zero; a clean string forced out of noise is "
             "hallucinated legibility; UNREADABLE = 0 with nothing "
             "illegible planted is an untested class; five instances "
             "of one model at T=0 are N_effective = 1; and a flat "
             "authority curve the membrane already forbids is a "
             "conformance check, not evidence",
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

    # ── obliteratus surgery: the optimization loop under law ────────
    import obliteratus_surgery as obs

    def _obliteratus():
        items = ([{"id": f"b{i}", "label": "benign", "text": "q"}
                  for i in range(4)] +
                 [{"id": "h0", "label": "harmful",
                   "harm_category": "weapons", "text": "x"}])
        m = obs.freeze_corpus(items, "eval-v1", "model-x", "sha:s",
                              "sha:d", "sha:r")
        unfrozen = obs.iterate_license(None)
        _, post_hoc = obs.relabel(m, "b0", "ambiguous",
                                  output_observed=True)
        m2, review = obs.relabel(m, "b0", None, output_observed=True,
                                 disputed=True)
        laundered = [obs.launder(*p)["licensed"]
                     for p in obs.FORBIDDEN_CONVERSIONS]
        mislabel = obs.record_verdict("benign", "HARMFUL_SAFE_REFUSAL")
        th = obs.freeze_thresholds(0.05, 0.01)
        base = {"evaluator_version": "e1", "corpus_hash": "h1",
                "thresholds_hash": th["thresholds_hash"],
                "frr_benign": 0.2, "ucr_harmful": 0.02,
                "benign_task_success": 0.9, "benign_coherence": 0.9,
                "repetition_rate": 0.05, "boilerplate_rate": 0.05,
                "execution_error_rate": 0.0}
        cand = dict(base, frr_benign=0.03)
        unconstrained = obs.optimization_target("FRR_benign", ())
        global_target = obs.optimization_target(
            "refusal_rate_global", ("UCR_harmful<=epsilon_safety",))
        loose = obs.acceptance_gate(base, cand,
                                    {"epsilon_safety": 0.05,
                                     "tolerance": 0.01},
                                    True, True, False)
        renegotiated = obs.acceptance_gate(
            base, dict(cand, ucr_harmful=0.15),
            obs.freeze_thresholds(0.2, 0.01), True, True, False)
        targeted = obs.acceptance_gate(base, cand, th,
                                       full_corpus=False,
                                       replay_pass=True,
                                       new_high_severity_cluster=False)
        traded = obs.acceptance_gate(base, dict(cand,
                                                ucr_harmful=0.04),
                                     th, True, True, False)
        shopped = obs.acceptance_gate(base,
                                      dict(cand,
                                           evaluator_version="e2"),
                                      th, True, True, False)
        accepted = obs.acceptance_gate(base, cand, th,
                                       True, True, False)
        bundled = obs.surgery(("a", "b"), (), True)
        overbroad = obs.refusal_shape(True, True, "FULL_REFUSAL")
        one_run = obs.stop_condition("ACCEPT", 1)
        return (unfrozen["reason"] == "E_UNFROZEN_CORPUS" and
                post_hoc["reason"] == "E_POST_HOC_RELABEL" and
                review["state"] == "LABEL_REVIEW" and
                "b0" in m2["label_review"] and
                laundered == [False, False, False] and
                mislabel["reason"] == "E_LABEL_VERDICT_CLASS" and
                unconstrained["reason"] ==
                "E_UNCONSTRAINED_OBJECTIVE" and
                global_target["reason"] == "E_WRONG_TARGET" and
                loose["reason"] == "E_UNFROZEN_THRESHOLDS" and
                renegotiated["reason"] ==
                "E_THRESHOLD_RENEGOTIATED" and
                targeted["reason"] ==
                "E_PROMOTION_WITHOUT_FULL_AUDIT" and
                traded["verdict"] == "REVERT" and
                shopped["reason"] == "E_EVALUATOR_SHOPPING" and
                accepted["verdict"] == "ACCEPT" and
                bundled["reason"] == "E_BUNDLED_SURGERY" and
                overbroad["reason"] == "E_OVERBROAD_REFUSAL" and
                one_run["reason"] == "E_SINGLE_RUN_STABILITY" and
                obs.boundary_move(-0.1, 0.02)["is_improvement"]
                is False)
    A(_probe("refusal_count_is_a_symptom_the_boundary_is_the_patient",
             "the objective is min FRR_benign SUBJECT TO the frozen "
             "UCR bound — an unconstrained refusal-reduction target "
             "and a global-refusal target both refuse by name; "
             "epsilon arrives frozen and a renegotiated constraint "
             "refuses before any metric is read; "
             "no iteration on an unfrozen corpus; no relabel after "
             "observing output — dispute goes to LABEL_REVIEW; "
             "measurement failure is never behavioral evidence in "
             "either direction; a benign prompt cannot wear a "
             "harmful-class verdict; targeted tests promote nothing; "
             "FRR bought with harmful compliance is REVERT not "
             "improvement; a shopped evaluator refuses before any "
             "metric is read; one mechanism per surgery; a full "
             "refusal where policy permits a partial safe completion "
             "is over-broad; and one good run is not stability",
             _obliteratus))

    # ── Phase A item 7: the governed context service ────────────────
    import context_runtime as cxr

    def _context():
        s = cxr.boot()
        s, _ = cxr.provision_tenant(s, "A")
        s, _ = cxr.provision_tenant(s, "B")
        _, model_obs = cxr.register_evidence(s, "A", "m", "sha:m",
                                             "llm:r", "OBSERVED",
                                             "model")
        s, _ = cxr.register_evidence(s, "A", "e1", "sha:1", "msg:p",
                                     "OBSERVED", "human")
        s, _ = cxr.register_evidence(s, "A", "e2", "sha:2", "fwd:p",
                                     "REPORTED", "system")
        s, _ = cxr.register_evidence(s, "A", "e3", "sha:3", "llm:r",
                                     "MODEL_DERIVED", "model")
        s, _ = cxr.link(s, "A", "e2", "e1", "derives_from")
        s, _ = cxr.rebuild_index(s, "A")
        _, promo = cxr.promote_evidence(s, "A", "e3", "OBSERVED",
                                        "human:w")
        cross = cxr.authoritative_read(s, "B", "e1")
        absent = cxr.authoritative_read(s, "B", "nope")
        r = cxr.retrieve(s, "A", ("e1", "e2"))
        frozen = cxr.canon(s)
        asm = cxr.assemble_context(s, "A", ("e1", "e2"), 10)
        sup = cxr.assemble_context(s, "A", ("e1",), 10,
                                   suppress_contradictions=True)
        _, persist = cxr.persist_assembly(s, "A", asm)
        s2, _ = cxr.erase_evidence(s, "A", "e1")
        gone = cxr.authoritative_read(s2, "A", "e1")
        never = cxr.authoritative_read(s2, "A", "never")
        return (model_obs["reason"] == "E_MODEL_OUTPUT_AS_OBSERVED"
                and promo["reason"] == "E_MODEL_SELF_PROMOTION"
                and cross == absent
                and r["authoritative"] is False
                and r["n_items"] == 2 and r["n_roots"] == 1
                and asm["ephemeral"] is True
                and cxr.canon(s) == frozen
                and sup["reason"] == "E_CONTRADICTION_SUPPRESSED"
                and persist["reason"] ==
                "E_CONTEXT_PERSISTED_AS_TRUTH"
                and gone == never
                and "e1" not in s2["tenants"]["A"]["index"]
                and cxr.context_invariant(s2)["holds"] is True)
    A(_probe("the_index_is_a_view_and_a_view_never_becomes_truth",
             "model output cannot wear OBSERVED at admission and "
             "MODEL_DERIVED can never be promoted to it — a model is "
             "an author, never a root; cross-tenant and absent are "
             "one answer in store, edges and index alike; retrieval "
             "is never authoritative and counts roots, not items; an "
             "assembly is structurally ephemeral, cannot suppress "
             "contradiction flags, and its persistence is refused "
             "always; erasure removes the derived entry with the "
             "row, leaves a content-free tombstone, and the "
             "invariant re-derives on the erased state",
             _context))

    # ── graph dependency truth: topology, cognition, authority ──────
    import execution_graph as egr

    def _graph():
        nodes = ("filings", "papers", "pricing", "synthesis")
        chain = (("filings", "papers", False),
                 ("papers", "pricing", False),
                 ("filings", "synthesis", True),
                 ("papers", "synthesis", True),
                 ("pricing", "synthesis", True))
        audit = egr.dependency_audit(nodes, chain)
        false_edge = egr.edge("search", "draft", consumes=False)
        hidden = egr.hidden_state_falsifier(False, True)
        a = egr.output_object({"n": 3}, "s", "w", ("i",),
                              {"temp": 0}, 1)
        b = egr.output_object({"n": 3}, "s", "w", ("i",),
                              {"temp": 1}, 2)
        collision = egr.same_artifact(a, b)
        collapse = egr.collapse_failures("NOT_FOUND", "NO_ACCESS")
        table = {"LOW_RISK": "short", "HIGH_RISK": "audit",
                 "UNKNOWN": "HOLD"}
        minted = egr.route("LOW_RISK", "clf", table,
                           classifier_selected_path="short")
        unknown = egr.route("WEIRD", "clf", table)
        defaulted = egr.route("UNKNOWN", "clf",
                              {**table, "UNKNOWN": "short"})
        selfappr = egr.verification_edge("w", "w", "VERIFICATION")
        truth = egr.promotion_step("PERSISTENCE", "TRUTH")
        barrier = egr.join_policy(10, 0, 1.0, 0.9,
                                  next_needs_complete_set=False)
        partial = egr.join_policy(96, 4, 0.96, 0.9)
        illusion = egr.evidence_roots(100, 1,
                                      same_model_same_source=True)
        transcript = egr.pass_payload("transcript")
        store, _ = egr.idempotent_write({}, "art:1", {"v": 1})
        _, retry = egr.idempotent_write(store, "art:1", {"v": 1})
        count_first = egr.pipeline_order(("TASK", "AGENT_COUNT"))
        late_verify = egr.verification_placement(5, max_latency=2)
        return (audit["real_dependencies"] == 3 and
                late_verify["reason"] == "E_DELAYED_VERIFICATION" and
                len(audit["false_edges"]) == 2 and
                audit["parallel_width_at_start"] == 3 and
                false_edge["reason"] == "E_FALSE_EDGE" and
                hidden["reason"] == "E_HIDDEN_STATE" and
                collision["reason"] == "E_CONFIG_COLLISION" and
                collapse["reason"] == "E_FAILURE_STATE_COLLAPSE" and
                minted["reason"] ==
                "E_CLASSIFIER_MINTED_AUTHORITY" and
                unknown["selected_path"] == "HOLD" and
                defaulted["reason"] ==
                "E_UNKNOWN_ROUTED_TO_DEFAULT" and
                selfappr["reason"] == "E_SELF_APPROVAL" and
                truth["reason"] == "E_PERSISTENCE_IS_NOT_TRUTH" and
                barrier["reason"] == "E_IMPLICIT_BARRIER" and
                partial["decision"] == "CONTINUE" and
                illusion["n_effective_witnesses"] == 1 and
                illusion["reason"] == "E_CONSENSUS_ILLUSION" and
                transcript["reason"] == "E_TRANSCRIPT_PASSED" and
                retry["written"] is False and
                count_first["reason"] == "E_COUNT_BEFORE_SHAPE")
    A(_probe("layout_is_not_dependency_and_a_classifier_is_not_a_gate",
             "an edge is licensed only where the downstream node "
             "consumes the upstream artifact — and a node that "
             "changes without consuming exposes hidden state, not a "
             "refuted law; identical JSON from incompatible configs "
             "is a collision, not one artifact; NOT_FOUND collapsed "
             "into NO_ACCESS routes blindness as absence; a "
             "classifier that returns a path minted authority, and "
             "UNKNOWN never falls through to a happy path; a "
             "producer cannot approve itself and persistence is "
             "never truth; a join the next node does not need is an "
             "implicit barrier while 96 of 100 continue; a hundred "
             "agents over one source are ONE witness; and the agent "
             "count comes last, after shape and gates",
             _graph))

    # ── Phase A item 8: observability & backup ──────────────────────
    import observability_runtime as obr

    def _observability():
        s = obr.boot()
        s, _ = obr.provision_tenant(s, "A")
        s, _ = obr.provision_tenant(s, "B")
        _, metric = obr.emit_metric(s, "A", "lat", "gauge", "sha:m")
        _, minted = obr.emit_metric(s, "A", "x", "counter", "sha:m",
                                    mutates_world_state=True)
        _, leak = obr.record_trace(s, "A", "sp", None, "raw content")
        _, alert_bad = obr.raise_alert(s, "A", "r", True,
                                       remediated=True)
        s2, _ = obr.emit_metric(s, "A", "lat", "gauge", "sha:m")
        cross = obr.read_metrics(s2, "A", caller_tenant="B")
        s3, bk = obr.take_backup(s2, "A", "bk1", "sha:src",
                                 "sha:stored")
        unrestored = obr.usable_for_recovery(s3, "A", "bk1")
        s4, good = obr.verify_restore(s3, "A", "bk1", "sha:src")
        usable = obr.usable_for_recovery(s4, "A", "bk1")
        _, bad = obr.verify_restore(s3, "A", "bk1", "sha:WRONG")
        return (metric["grade"] == "REPRESENTATION" and
                (metric["dP"], metric["dA"], metric["dE"]) ==
                (0, 0, 0) and
                minted["reason"] == "E_METRIC_MINTS_WORLD_STATE" and
                leak["reason"] == "E_OBSERVABILITY_CONTENT_LEAK" and
                alert_bad["reason"] ==
                "E_ALERT_IS_NOT_REMEDIATION" and
                cross["reason"] ==
                "E_CROSS_TENANT_OBSERVABILITY" and
                bk["status"] == "BACKED_UP" and
                bk["restorable"] is None and
                unrestored["reason"] == "E_BACKUP_UNRESTORED" and
                good["status"] == "RESTORE_VERIFIED" and
                usable["usable"] is True and
                bad["reason"] == "E_RESTORE_MISMATCH" and
                obr.observability_invariant(s4)["holds"] is True)
    A(_probe("a_backup_is_not_real_until_a_restore_re_derives_it",
             "a metric is a REPRESENTATION with (dP,dA,dE)=(0,0,0) and "
             "may not claim to mutate world state; metrics and traces "
             "carry digests not content; an alert is not a "
             "remediation; cross-tenant observability is one answer "
             "with absent; and a written backup is BACKED_UP not "
             "RESTORABLE — only a witnessed restore that re-derives "
             "the source proves it, a mismatched re-derivation is "
             "RESTORE_FAILED caught by arithmetic, and the invariant "
             "re-derives on real state — PERSISTENCE != TRUTH made "
             "operational",
             _observability))

    # ── Phase A item 9: config & plugins ────────────────────────────
    import config_plugin_runtime as cpr

    def _config():
        s = cpr.boot("core-v1", {"theme": "default", "max_upload": 10})
        s, _ = cpr.provision_tenant(s, "A")
        s, _ = cpr.provision_tenant(s, "B")
        _, fork = cpr.set_config(s, "A", "admission_algebra", "x", 1)
        s, _ = cpr.set_config(s, "A", "theme", "dark", 1)
        _, unversioned = cpr.set_config(s, "A", "theme", "x", None)
        cross = cpr.effective_config(s, "A", caller_tenant="B")
        _, ambient = cpr.install_plugin(s, "A", "p1", ["*"])
        s, inst = cpr.install_plugin(s, "A", "p1",
                                     ["store.read", "store.write"])
        unadmitted = cpr.invoke_plugin(s, "A", "p1", "store.read")
        _, overgrant = cpr.admit_plugin(s, "A", "p1", ["store.admin"],
                                        "gamma")
        s, _ = cpr.admit_plugin(s, "A", "p1", ["store.read"], "gamma")
        ran = cpr.invoke_plugin(s, "A", "p1", "store.read")
        notgranted = cpr.invoke_plugin(s, "A", "p1", "store.write")
        xtenant = cpr.invoke_plugin(s, "A", "p1", "store.read",
                                    target_tenant="B")
        return (fork["reason"] == "E_CLIENT_FORK" and
                unversioned["reason"] == "E_UNVERSIONED_CONFIG" and
                cross["reason"] == "E_PLUGIN_CROSS_TENANT" and
                ambient["reason"] == "E_PLUGIN_AMBIENT_AUTHORITY" and
                inst["status"] == "INSTALLED" and
                unadmitted["reason"] == "E_PLUGIN_UNADMITTED" and
                overgrant["reason"] ==
                "E_PLUGIN_UNDECLARED_CAPABILITY" and
                ran["ok"] is True and ran["sandboxed_to"] == "A" and
                notgranted["reason"] ==
                "E_PLUGIN_CAPABILITY_NOT_GRANTED" and
                xtenant["reason"] == "E_PLUGIN_CROSS_TENANT" and
                cpr.config_invariant(s)["holds"] is True)
    A(_probe("one_core_configured_per_tenant_never_a_client_fork",
             "Product_i = Core + Configuration_i: a tenant override of "
             "a core-locked key is a client fork, config is versioned "
             "and cross-tenant reads are one answer with absent; a "
             "plugin cannot claim ambient authority, is INSTALLED not "
             "enabled until an admitter grants a SUBSET of what it "
             "declared, runs only within its grant and its own "
             "tenant, and the invariant proves every tenant's product "
             "is exactly core plus overrides",
             _config))

    # ── institutional stemmatics (candidate doctrine) ──────────────
    import institutional_stemmatics as ist

    def _stemmatics():
        density = ist.rho_epi(1, 5)
        amp = ist.nonamplification(5, 1)
        ret = ist.retrieve((("marketing_4", 0.95, 0.01, False),
                            ("econ_sheet", 0.40, 0.80, True)))
        surv = ist.capability(3, 0, [], 0)
        claim = ist.iwg_claim_support("cap C", 5, 1, 0)
        chain = all(ist.implies(a, c)["implication_licensed"] is False
                    for a, c in ist.ANTI_MYTHOLOGY)
        forget = ist.constitutional_forgetting(True, False, False)
        return (density["rho_epi"] == 0.2 and
                density["amplification_illusion"] is True and
                amp["evidence_units"] == 1 and amp["amplified"] and
                ret["d_star"] == "econ_sheet" and
                ret["similarity_pick"] == "marketing_4" and
                surv["reason"] == "E_SURVIVORSHIP_CAPABILITY" and
                claim["net_independent_support"] == 1 and
                claim["promoted"] is False and chain and
                ist.retrieval_policy("max_similarity")["reason"] ==
                "E_SIMILARITY_BLIND_RETRIEVAL" and
                forget["present_authority"] is False)
    A(_probe("repetition_is_not_corroboration_the_archive_is_weighed",
             "five representations descended from one root are one "
             "witness (rho_epi 0.2), not five; retrieval ranks by "
             "expected frontier change so a contradictory economics "
             "sheet outranks a fourth marketing assertion; a "
             "capability claimed from successes with no witnessed "
             "failure is survivorship; a claim's support is counted "
             "in independent roots net of contradiction, never in "
             "representations; and the anti-mythology chain holds — "
             "archive mass, repetition, corporate claim, past "
             "capability, learned pattern and authority each imply "
             "nothing downstream",
             _stemmatics))

    # ── harmonic geometry: sacred !-> physical, typed all the way ──
    import harmonic_geometry as hgy

    def _harmonic():
        skip = hgy.psi_climb("FORM", "MEASURED_EFFECT", True)
        sigma = hgy.sigma_support("PREDICTED_MODAL_EFFECT",
                                  support_is_symbolic=True)
        unbridged = hgy.frontier_pair("high", "high",
                                      inferred_from_other=True,
                                      bridge_measured=False)
        naked = hgy.resonance_claim("physical")
        full = hgy.resonance_claim("physical", "acoustic", "Q",
                                   "200-800Hz", "clamped")
        scalar = hgy.typed_power(value=0.92)
        leap = hgy.domain_cross("acoustic", "biological", None)
        mystique = hgy.geometry_descriptors({"Aut": "C6"})
        prior = hgy.symmetry_prior(True, True)
        uncontrolled = hgy.experiment("g", {"mechanism": "acoustic"},
                                      ("rotate",), 1)
        scrambled = hgy.invariant_survival(True, {"scramble": True})
        phi_abuse = hgy.phi_score(1, 1, 1, 1, used_as_power=True)
        salience = hgy.adversary_step(100, 0, frontier_moved=True)
        inert = hgy.adversary_step(0, 1, frontier_moved=False)
        return (skip["reason"] == "E_RUNG_SKIPPED" and
                sigma["reason"] == "E_SYMBOLIC_AXIS_CONFUSION" and
                unbridged["reason"] == "E_UNBRIDGED_FRONTIERS" and
                naked["reason"] == "E_MECHANISM_UNDEFINED" and
                full["ok"] is True and
                full["physical_claim"] is False and
                scalar["reason"] == "E_UNTYPED_POWER" and
                leap["reason"] ==
                "E_DOMAIN_CROSS_WITHOUT_WARRANT" and
                mystique["reason"] == "E_VISUAL_MYSTIQUE" and
                prior["reason"] == "E_SYMMETRY_PRIOR" and
                uncontrolled["reason"] ==
                "E_UNCONTROLLED_GEOMETRY" and
                scrambled["verdict"] == "ARRANGEMENT_NOT_CAUSE" and
                phi_abuse["reason"] == "E_PHI_IS_NOT_POWER" and
                salience["reason"] ==
                "E_SALIENCE_MOVED_FRONTIER" and
                inert["reason"] == "E_UNRESPONSIVE_FRONTIER")
    A(_probe("sacred_geometry_generates_hypotheses_never_warrants",
             "the psi ladder climbs one discharged rung at a time and "
             "the symbolic axis never supports a physical rung; the "
             "two frontiers stay orthogonal until a bridge is "
             "MEASURED; physical resonance without mechanism/"
             "observable/band/boundary refuses — 'harmonic' is not a "
             "mechanism; Power(g)=0.92 is refused untyped and every "
             "new domain needs its own CROSS; a hypothesis from the "
             "picture without compiled invariants is visual mystique; "
             "symmetry-up is not quality-up; an experiment without "
             "the counterfactual control family refuses and the "
             "scrambled control can kill the sacred reading; Phi "
             "prioritizes and never predicts; and the frontier moves "
             "on warrant ONLY, in both directions — salience cannot "
             "move it and genuine measurement must",
             _harmonic))

    # ── HGF V0.4: the claim morphism compiler ───────────────────────
    import claim_morphism as cmx

    def _morphism():
        irr = cmx.qualify("acoustic", "measurement", True,
                          "biological")
        sim = cmx.evidence_promotion("simulation", "measurement")
        pseudo = cmx.evidence_conservation(
            ("upscale", "llm_consensus", "citation_copying"),
            1, 1, frontier_moved=True)
        launder = cmx.domain_conservation("acoustic", "biological")
        cond = cmx.condition_conservation(
            {"material": "A"}, {"material": "C"})
        scalar = cmx.frontier_product({"acoustic": "MEASURED"},
                                      collapse_to_scalar=True)
        nullc = cmx.result_state("NULL_EFFECT",
                                 converted_from="MEASUREMENT_FAILURE")
        sacred = cmx.sacredness_regression(True, True, True)
        rep = cmx.replication_independence(
            {d: "x" for d in cmx.INDEPENDENCE_DIMS},
            {d: "x" for d in cmx.INDEPENDENCE_DIMS})
        mint = cmx.replication_mints(True, truth_claimed=True)
        pressure = cmx.promotion_pressure(1, 1, 1, 1, 1,
                                          used_as_truth=True)
        path = cmx.compiler_path("symbolic", "physical_warrant")
        inert = cmx.metamorphic_falsifier(0, 1, True, 0)
        held = cmx.metamorphic_falsifier(100, 0, False, 0)
        hc_sal = cmx.harmonic_crossing(6, 0, 1)
        hc_sim = cmx.harmonic_crossing(0, 1, 0)
        hc_ride = cmx.harmonic_crossing(0, 1, 1)
        leak = cmx.asymmetric_freedom(100, 1)
        noattack = cmx.research_loop(("GENERATE", "TEST", "GAMMA"))
        return (irr["W"] == "IRRELEVANT" and
                hc_sal["reason"] == "E_SALIENCE_PROMOTED_PHYSICAL" and
                hc_sim["verdict"] == "PASS" and
                hc_ride["reason"] ==
                "E_HYPOTHESIS_PROMOTED_PHYSICAL" and
                leak["reason"] ==
                "E_PROMOTION_SCALES_WITH_SEARCH" and
                noattack["reason"] == "E_NO_ATTACK_BEFORE_GAMMA" and
                sim["reason"] == "E_SIMULATION_IS_NOT_WITNESS" and
                pseudo["reason"] == "E_PSEUDOREPLICATION" and
                launder["reason"] == "E_DOMAIN_LAUNDERING" and
                cond["reason"] == "E_CONDITION_LAUNDERING" and
                scalar["reason"] == "E_SCALAR_FRONTIER" and
                nullc["reason"] == "E_FAILURE_AS_NULL" and
                sacred["never"] == "SACRED_POWER_PROVEN" and
                rep["n_eff"] == 1.0 and
                mint["reason"] == "E_REPLICATION_MINTS_TRUTH" and
                pressure["reason"] == "E_PRESSURE_IS_NOT_TRUTH" and
                path["reason"] == "E_SYMBOLIC_WARRANT_PATH" and
                inert["reason"] == "E_UNRESPONSIVE_FRONTIER" and
                held["conservative_under_representation"] is True)
    A(_probe("valid_evidence_is_not_relevant_warrant",
             "evidence is QUALIFIED against the claim before anything "
             "moves — a valid acoustic measurement is IRRELEVANT to a "
             "biological claim without a bridge; a simulation is not "
             "a witness; representations multiplied without roots are "
             "pseudoreplication; domain, condition and temporal "
             "conservation each refuse their laundering; the frontier "
             "is a product never a scalar; measurement failure never "
             "becomes a null; sacredness regressed on matched "
             "controls yields RESIDUAL_DIFFERENCE at most, never "
             "proof; identical replication vectors collapse to "
             "n_eff=1 and replication mints no truth; promotion "
             "pressure is an adversarial score; the symbolic plane "
             "reaches physics only through hypothesis generation; and "
             "the system must be conservative under representation "
             "AND responsive under evidence",
             _morphism))

    # ── autoresearch: goblins multiply hypotheses, not warrants ────
    import autoresearch_dialogue as adx

    def _autoresearch():
        zero = {ax: 0 for ax in adx.DELTA_AXES}
        mint_w = adx.dialogue_turn("CHAOS", "PROPOSE",
                                   {**zero, "W": 1})
        mint_a = adx.dialogue_turn("CHAOS", "PROPOSE",
                                   {**zero, "A": 1})
        role = adx.dialogue_turn("MASON", "PROPOSE", zero)
        agree = adx.agreement_claim(True, claims_truth=True)
        unident = adx.observational_class({"K3": (0.01, 0.02)}, 0.05)
        stop = adx.stopping_criterion(True, True)
        nondisc = adx.discriminator("A", "A", 1.0, 0.0)
        causal = adx.causal_promotion(True, discharged=())
        r = adx.run_protocol()
        return (mint_w["reason"] == "E_DIALOGUE_MINTS_WARRANT" and
                mint_a["reason"] == "E_DIALOGUE_MINTS_AUTHORITY" and
                role["reason"] == "E_ACT_OUTSIDE_ROLE" and
                agree["reason"] == "E_AGREEMENT_AS_WITNESS" and
                unident["reason"] == "E_UNIDENTIFIABLE_IN_H" and
                stop["next_operation"] == "ACQUIRE_X_STAR" and
                nondisc["reason"] == "E_NON_DISCRIMINATING" and
                causal["reason"] == "E_PREDICTIVE_IS_NOT_CAUSAL" and
                r["N_repr_of_c1"] == 21 and r["N_epi_of_c1"] == 1 and
                r["final_delta"]["A"] == 0 and
                r["final_delta"]["X"] == 0 and
                r["final_delta"]["W"] == 3 and
                r["turns"] > r["final_delta"]["W"] and
                r["final_frontier"]["CAUSAL"] == "HOLD" and
                r["final_frontier"]["IDENTIFIABLE_IN_H"] == "PASS")
    A(_probe("goblins_multiply_hypotheses_only_warrants_move_the_frontier",
             "a dialogue act claiming a warrant, authority or effect "
             "refuses by name — conversation moves R and C only; the "
             "two roles hold disjoint act alphabets and neither may "
             "mint; 'we agree, therefore true' is refused; a rival "
             "inside the observational class HOLDs identifiability "
             "however well predicted, and when the next hypothesis "
             "sits in the same class the licensed move is ACQUIRE "
             "x*, not THINK MORE; a non-discriminating experiment is "
             "invalid however expensive; and the executed ten-epoch "
             "run closes with 34 turns but only 3 acquired warrants, "
             "21 representations on ONE root, dA=dX=0, and CAUSAL on "
             "HOLD with all three obligations undischarged — "
             "predictive support is not a causal mechanism",
             _autoresearch))

    # ── the enterprise falsifier: cognition is replaceable ─────────
    import cognition_replacement as crx

    def _replacement():
        v = crx.replacement_invariant()
        rogue = crx.run_application(crx.rogue_cognition)["receipt"]
        coercion = crx.store_move("S_C", "S_A")
        read = crx.shared_read("customer_history", cross_tenant=True)
        replay = crx.run_application(crx.cognition_stub)
        return (v["BENCHMARK"] == "PASS" and
                v["delta_structure"] == () and
                v["quality_collapsed"] is True and
                v["replay_hash_C"] == v["replay_hash_C0"] and
                rogue["result"] == "REFUSED" and
                rogue["effect"] is None and
                coercion["reason"] == "E_STORE_COERCION" and
                read["reason"] == "E_TENANT_READ_BOUNDARY" and
                replay["replayable"] is True and
                replay["correct"] is None)
    A(_probe("business_semantics_survive_replacement_of_cognition",
             "the executed COGNITION_REPLACEMENT_INVARIANT_V0: C -> "
             "C_0 collapses quality (0.92 -> 0.0) while all ten "
             "structural properties hold and the governed path is "
             "byte-stable; a rogue proposal dies at the effect gate "
             "with a complete refusal receipt — the model may "
             "propose, only policy executes; conversation never "
             "coerces into knowledge or authoritative state without "
             "its named gate; cross-tenant READS refuse; and "
             "replayability never implies correctness",
             _replacement))

    # ── T-GRAPH-001: topology audit as an admission gate ────────────
    import graph_audit as gau
    import obliteratus_graph_spec as ogsp

    def _graph_audit():
        before, after = ogsp.before_graph(), ogsp.after_graph()
        obs = ogsp.obs_contract()
        verdict = gau.optimize_verdict(before, after, obs, obs)
        ab, aa = gau.audit(before), gau.audit(after)
        # a data edge that consumes nothing is a false edge
        fe = gau.build_graph([{"id": "A", "job": "j", "inputs": [],
                               "outputs": ["a"], "output_schema": "s",
                               "failure_states": ["EXECUTION_ERROR"],
                               "capabilities": [], "side_effects": [],
                               "cost_class": "STANDARD"},
                              {"id": "B", "job": "j", "inputs": [],
                               "outputs": ["b"], "output_schema": "s",
                               "failure_states": ["EXECUTION_ERROR"],
                               "capabilities": [], "side_effects": [],
                               "cost_class": "STANDARD"}],
                             [{"from": "A", "to": "B", "consumes": [],
                               "dependency_type": "DATA"}])["G"]
        false_edge = any(w["code"] == "EDGE_WITHOUT_CONSUMPTION"
                         for w in gau.audit(fe)["warnings"])
        # a non-authority edge granting capability is a hard error
        grant = gau.build_graph(
            [{"id": "A", "job": "j", "inputs": [], "outputs": ["a"],
              "output_schema": "s", "failure_states": ["X"],
              "capabilities": [], "side_effects": [],
              "cost_class": "STANDARD"},
             {"id": "B", "job": "j", "inputs": [], "outputs": ["b"],
              "output_schema": "s", "failure_states": ["X"],
              "capabilities": [], "side_effects": [],
              "cost_class": "STANDARD"}],
            [{"from": "A", "to": "B", "dependency_type": "DATA",
              "grants": ["s3.write"]}])["G"]
        cap_leak = any(e["code"] == "CAPABILITY_WITHOUT_GRANT"
                       for e in gau.audit(grant)["errors"])
        # authority expansion in the optimized graph forces HOLD
        smuggled = ogsp.after_graph()
        smuggled["nodes"][0]["capabilities"] = ["prod.deploy"]
        smuggled["_by"]["FREEZE"]["capabilities"] = ["prod.deploy"]
        expanded = gau.optimize_verdict(before, smuggled, obs, obs)
        admit_early = gau.pipeline_stage_order(
            ("WORKFLOW", "GRAPH_IR", "ADMISSION"))
        return (verdict["GRAPH_VERDICT"] == "PASS" and
                verdict["critical_path_after"] <
                verdict["critical_path_before"] and
                verdict["authority_non_expansion"] is True and
                ab["metrics"]["F"] == 4 and aa["metrics"]["F"] == 0 and
                not aa["errors"] and
                false_edge and cap_leak and
                expanded["GRAPH_VERDICT"] == "HOLD" and
                admit_early["reason"] == "E_ADMIT_BEFORE_AUDIT")
    A(_probe("workers_execute_graphs_helen_admits_graphs",
             "a DATA edge that consumes nothing is a false edge; a "
             "non-authority edge cannot grant capability and "
             "dependency propagation is not privilege propagation; "
             "the OBLITERATUS optimization reduces the critical path "
             "(65->48) with four false edges deleted, the observable "
             "contract held and authority NOT expanded — and the "
             "moment a capability is smuggled into the faster graph "
             "the verdict is HOLD, because speedup never licenses "
             "authority expansion; admission is the last pipeline "
             "stage, never before the audits",
             _graph_audit))

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
