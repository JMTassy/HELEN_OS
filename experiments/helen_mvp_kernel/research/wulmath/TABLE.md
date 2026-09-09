| # | WULmath | probe | vib |
|---|---|---|---|
| 001 | `¬Path(s) ⊢ Orphan(s)` | `orphan_state` | 1 red_oxide |
| 002 | `Lease ∈ Linear · Spent(ℓ) ⊬ Avail(ℓ, m₂)` | `duplicated_lease` | 3 ochre_gold |
| 003 | `E(t₁) ⊬ A(t₀)` | `retroactive_authority` | 3 ochre_gold |
| 004 | `T deterministic ⇒ rank_E(Tx) ≤ rank_E(x)` | `evidence_cloning` | 5 blue_slate |
| 005 | `≡_const ⊊ ≡_ext` | `equal_state_different_history` | 1 red_oxide |
| 006 | `Prov = append-only` | `history_rewrite` | 1 red_oxide |
| 007 | `Refuse ⊢ Ledger · Refuse ⊬ ΔS` | `negative_receipt` | 5 blue_slate |
| 008 | `Receipt ⊨_local · Replay ∧ Conserv ⊨_global` | `local_valid_global_invalid` | 5 blue_slate |
| 009 | `Gates alone ⊬ ¬Reach(forbidden)` | `gate_coverage_hole` | 7 violet_white |
| 010 | `⊥ ↦ Type ≻ Gate ≻ Prose` | `structurally_impossible` | 1 red_oxide |
| 011 | `Adm(a) ∧ Adm(b) ⊬ Adm(a ∥ b)` | `compositional_admissibility` | 4 green_deep |
| 012 | `Repr \ NS ⊬ Sem_sov` | `no_namespace_no_semantics` | 1 red_oxide |
| 013 | `density_retrieval ⊬ indep_epi` | `authority_gravity` | 6 indigo |
| 014 | `Motif ⊢ describe · Flow ⊢ govern` | `motif_has_no_authority` | 6 indigo |
| 015 | `Label ⊬ Type · 5 witnessed fields ∨ ∅` | `label_is_not_a_type` | 6 indigo |
| 016 | `Promote ⊢ Name(loss)` | `undeclared_gate` | 7 violet_white |
| 017 | `Cycle(intel) ✓ · Acyclic(A) required` | `authority_acyclic` | 3 ochre_gold |
| 018 | `|Proj| ⊬ |E|` | `projection_is_not_evidence` | 6 indigo |
| 019 | `Receipt_exec ⊬ Authz` | `receipt_is_not_permission` | 3 ochre_gold |
| 020 | `Learn ⊬ Mint(A_install)` | `learning_mints_no_lease` | 3 ochre_gold |
| 021 | `∀τ · conf > τ ⊬ Admit` | `confidence_admits_nothing` | 5 blue_slate |
| 022 | `Capability ⊬ Licence · Gate @ effect layer` | `bypass_text_deny` | 3 ochre_gold |
| 023 | `Prod: fail → act · Gov: fail → HOLD` | `unrecoverable_loss_holds` | 7 violet_white |
| 024 | `s₁ = s₂ ⊬ h₁ = h₂` | `causal_aliasing` | 1 red_oxide |
| 025 | `o ∉ S ⊬ Discharged(o)` | `obligation_survives_wrong_contract` | 7 violet_white |
| 026 | `rank_R ↓ ✓ · rank_E ↑ ∅` | `reducer_conservation` | 5 blue_slate |
| 027 | `Cursor ⊢ ack(closure) · Cursor ⊬ promise(closure)` | `cursor_before_closure` | 1 red_oxide |
| 028 | `Valid ∧ Authz ∧ ¬Capacity ⊢ ¬Effect` | `capacity_precondition` | 3 ochre_gold |
| 029 | `Σ ⊢ ↓info · Σ ⊬ ↑status` | `summary_is_not_a_verdict` | 6 indigo |
| 030 | `EXECUTED ⊥ DECIDED` | `executed_without_decision` | 7 violet_white |
| 031 | `HOLD ⊢ next(obligation)` | `hold_is_not_deadlock` | 7 violet_white |
| 032 | `¬Event ⊬ ¬Obligation` | `critical_obligation_stays_live` | 7 violet_white |
| 033 | `rank ← obligation · rank ⊬ beauty` | `scheduler_ranks_deadline_over_theorem` | 7 violet_white |
| 034 | `assert(⊥) ⊬ drop(o) · witness(⊥) required` | `impossibility_must_be_witnessed` | 5 blue_slate |
| 035 | `min d ⊬ ADMIT · crit fail = ∞` | `min_distance_does_not_admit` | 6 indigo |
| 036 | `Mint(κ) ⊢ UseCount(κ) ≤ 1` | `capability_is_one_shot` | 3 ochre_gold |
| 037 | `Memory ⊬ State · Replay ⊢ State` | `replay_wins_over_narrative` | 5 blue_slate |
| 038 | `EFFECT ≠ AUTHORIZED EFFECT` | `captured_is_not_lawfully_captured` | 3 ochre_gold |
| 039 | `Judgment ⊢ ΔS_inst · Judgment ⊬ Δfact` | `judgment_does_not_rewrite_history` | 1 red_oxide |
| 040 | `L_i → L_j ⊢ witness(prov)` | `unwitnessed_cross_layer_join_refused` | 4 green_deep |
| 041 | `name= ∧ pass ⊬ identity=` | `name_is_not_identity` | 1 red_oxide |
| 042 | `cond(ship) ⊬ cond(cargo)` | `verdict_scope_does_not_propagate` | 7 violet_white |
| 043 | `root(trans) = root(orig) · hash≠ ⊬ indep` | `derived_doc_is_not_new_witness` | 5 blue_slate |
| 044 | `8 oracles ↦ enforcer · ∀ reject` | `eight_gold_oracles_hold` | 5 blue_slate |
| 045 | `E ⊬ |Vessel| = 1` | `cardinality_is_not_assumed` | 6 indigo |
| 046 | `Merge ∈ rewrite · Merge ∉ preprocess` | `merge_is_a_governed_transition` | 4 green_deep |
| 047 | `RELAY(s) ⊬ OBSERVED(s)` | `relay_is_not_direct_observation` | 5 blue_slate |
| 048 | `Admit ⟺ P ≤ P̄ ∧ E ≤ Scope ∧ A ≤ Ā ∧ Replay` | `three_ceilings_bound_admission` | 7 violet_white |
| 049 | `O_t ⊊ P_t` | `observed_is_a_proper_subset_of_possible` | 2 orange_earth |
| 050 | `¬cat ⊬ ¬allowed · neg E witnessed` | `absence_is_unknown_not_forbidden` | 2 orange_earth |
| 051 | `Gen(G) ⊢ candidate · Gen(G) ⊬ fact` | `generable_is_not_historically_observed` | 2 orange_earth |
| 052 | `∀ prohibition ↦ one of 4 ceilings` | `safety_census_is_total` | 7 violet_white |
| 053 | `HOLD ≠ DEADLOCK · □ ⊥ ◇` | `liveness_is_a_distinct_axis` | 7 violet_white |
| 054 | `ΔOntology ∈ Effect ⊢ Admit` | `ontology_change_is_an_effect` | 4 green_deep |
| 055 | `¬∃ ctrex ⊬ Complete` | `completeness_is_unknown_not_proven` | 7 violet_white |
| 056 | `corpus₁₉₁₈ ↦ 0 · need(C₅) = 0 · evidence ⊬ proof` | `vendor_corpus_maps_completely` | 5 blue_slate |
| 057 | `lawful ∘ lawful ⊬ lawful ⇒ eval_txn` | `ceilings_not_closed_under_composition` | 4 green_deep |
| 058 | `∀ ctrex ↦ eval_txn(C₁₋₄) · Complete = UNKNOWN` | `fifth_ceiling_not_earned` | 7 violet_white |
| 059 | `∀ c ∃ δ · catches(δ) = {c}` | `no_ceiling_is_removable` | 7 violet_white |
| 060 | `Replay ⊬ SemPersist` | `replayability_is_not_semantic_persistence` | 5 blue_slate |
| 061 | `Q₀ = UNKNOWN · Trust_t(a) ⊬ A_{t+1}(a)` | `trust_is_earned_never_declared` | 5 blue_slate |
| 062 | `Admitted ⊬ RobustlyAdmitted · margin measured` | `gate_tolerances_are_measured` | 6 indigo |
| 063 | `Heir ⊢ craft · Heir ⊬ grant` | `memory_transfers_craft_never_authority` | 3 ochre_gold |
| 064 | `margin signed · α₋ @ boundary · replay ⊢ ¬PASS` | `unknown_resolution_is_not_new_law` | 6 indigo |
| 065 | `↓resolution ⊢ HOLD · ↓resolution ⊬ ADMIT` | `authority_contracts_below_resolution` | 6 indigo |
| 066 | `|W| = 5 ∧ |root| = 1 ⇒ N_eff = 1 · √N ← ancestry` | `consensus_is_not_independence` | 5 blue_slate |
| 067 | `Gen ⊋ Prod ⊋ Surv ⊋ Obs` | `observed_is_not_survived_is_not_produced` | 2 orange_earth |
| 068 | `A_K ⊢ read ∨ propose · A_K ⊬ effect` | `cognition_never_crosses_the_membrane` | 7 violet_white |
| 069 | `Palette frozen · rivals ⊥ axis` | `palette_is_factored_never_replaced` | 6 indigo |
| 070 | `Adm_local ⊬ Adm_global · DATA ⊬ A` | `locally_admissible_is_not_globally_admissible` | 4 green_deep |
| 071 | `Isolation ∈ state · Isolation ⊬ promise` | `isolation_is_a_property_of_the_state_not_a_promise` | 1 red_oxide |
| 072 | `order-dependent(G) ⊢ RACE` | `a_graph_whose_state_depends_on_read_order_is_a_race` | 4 green_deep |
| 073 | `|proposers| = 2 ∧ |corpus| = 1 ⇒ N_eff = 1` | `a_different_lineage_does_not_make_n_eff_two` | 5 blue_slate |
| 074 | `¬∃ slot · valid(σ₁) ∧ valid(σ₂) ∧ σ₁ ∩ σ₂ ≠ ∅` | `a_slot_may_not_be_valid_in_two_slices_at_once` | 1 red_oxide |
| 075 | `W(X) ⊬ W(Y)` | `a_warrant_binds_the_value_it_was_minted_over` | 5 blue_slate |
| 076 | `grantor ≠ grantee · bind(A) ⊬ licence(B)` | `the_grantor_may_not_be_the_grantee` | 3 ochre_gold |
| 077 | `App ⊬ name(vendor) · ∩policy = ∅ ⊢ refuse` | `the_gateway_decides_and_the_app_never_names` | 3 ochre_gold |
| 078 | `Contract = content-addressed · drop(field) ⊢ BREAKING` | `the_ground_does_not_move_under_a_client` | 1 red_oxide |
| 079 | `Δevent ⊢ break(hash_{>i}) · unanchored ⊬ safe` | `tampering_is_arithmetic_not_policy` | 5 blue_slate |
| 080 | `Model ⊢ record · Model ⊬ advance` | `the_engine_owns_every_arrow` | 4 green_deep |
| 081 | `Δfrontier(L_i) ⊬ licence(L_{i+1})` | `progress_at_one_layer_cannot_mint_the_next` | 7 violet_white |
| 082 | `text ⊬ rederivable · unrun ⇒ FABRICATED_UNTIL_WITNESSED` | `receipt_text_is_not_a_rederivable_receipt` | 5 blue_slate |
| 083 | `↑width ∧ A = const` | `cognitive_width_may_not_buy_effect_authority` | 3 ochre_gold |
| 084 | `Boundary ∈ det(software) · ⊬ ambient A` | `the_enterprise_boundary_is_deterministic_software` | 1 red_oxide |
| 085 | `rename ⊬ release · repo ⊬ recoverability` | `a_rename_without_its_witness_is_a_seal_without_admission` | 7 violet_white |
| 086 | `Σ confirmations ⊬ reinforcement` | `confirmations_accumulate_and_never_reinforce` | 5 blue_slate |
| 087 | `∀e PASS(e) ⊬ PASS(G) · UseCount(κ) = 2 > 1` | `a_lawful_institution_is_not_a_collection_of_lawful_edges` | 4 green_deep |
| 088 | `status(ref) ⊬ status(repr) · debtor ≠ creditor` | `a_representation_never_inherits_its_referents_status` | 6 indigo |
| 089 | `Percept ⊬ ΔWorld · ladder = 1 yes, 4 noes` | `no_perceptual_property_mints_a_world_state` | 6 indigo |
| 090 | `Proj ∉ Σ_N · ↑A \ witness = inflation` | `a_projection_is_not_a_measurement` | 6 indigo |
| 091 | `Plausible ⊬ OBSERVED · abstain-all ⊢ fail(+control)` | `plausibility_never_becomes_history` | 2 orange_earth |
| 092 | `Predict \ Compress ⊢ HOLD` | `a_grammar_must_predict_what_it_never_saw` | 2 orange_earth |
| 093 | `Seal ⊬ Admit · ¬state-by-colour` | `beautiful_seal_is_not_admission` | 7 violet_white |
| 094 | `Σ sincere ⊬ PROOF   ⟨1844⟩` | `sincere_witnesses_do_not_sum_to_proof` | 5 blue_slate |
| 095 | `min FRR_benign s.t. UCR_harmful ≤ ε_safety` | `refusal_count_is_a_symptom_the_boundary_is_the_patient` | 7 violet_white |
| 096 | `View ⊬ Truth · MODEL_DERIVED ⊬ OBSERVED` | `the_index_is_a_view_and_a_view_never_becomes_truth` | 6 indigo |
| 097 | `edge(u,v) ⟺ consumes(v,u)` | `layout_is_not_dependency_and_a_classifier_is_not_a_gate` | 4 green_deep |
| 098 | `Exists ⊬ Restorable ⊬ Restored · (dP,dA,dE) = 0` | `a_backup_is_not_real_until_a_restore_re_derives_it` | 1 red_oxide |
| 099 | `Product_i = Core + Config_i` | `one_core_configured_per_tenant_never_a_client_fork` | 1 red_oxide |
| 100 | `|repr| = 5 ∧ |root| = 1 ⇒ ρ_epi = 0.2` | `repetition_is_not_corroboration_the_archive_is_weighed` | 5 blue_slate |
| 101 | `σ ⊥ ψ · F*_symbolic ⊬ rung_physical` | `sacred_geometry_generates_hypotheses_never_warrants` | 6 indigo |
| 102 | `Valid ⊬ Relevant · bridge required` | `valid_evidence_is_not_relevant_warrant` | 5 blue_slate |
| 103 | `Dialogue ⊢ ΔR, ΔC · Dialogue ⊬ ΔW` | `goblins_multiply_hypotheses_only_warrants_move_the_frontier` | 2 orange_earth |
| 104 | `C → C₀ · quality 0.92 → 0.0 · 10/10 structure held` | `business_semantics_survive_replacement_of_cognition` | 4 green_deep |
| 105 | `Worker ⊢ execute · HELEN ⊢ admit` | `workers_execute_graphs_helen_admits_graphs` | 4 green_deep |
| 106 | `D_NI = D_cross + D_local` | `no_coordinate_acquires_institutional_force_by_itself` | 4 green_deep |
| 107 | `Retain ⊬ Admit ⊬ Authorize` | `an_alternative_may_survive_without_being_true_or_permitted` | 2 orange_earth |
| 108 | `¬CanRise(c) ⇒ Info(c = 0) = 0` | `a_safety_counter_that_cannot_rise_reports_nothing` | 7 violet_white |
