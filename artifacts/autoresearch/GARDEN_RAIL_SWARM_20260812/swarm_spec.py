import json, urllib.request, concurrent.futures, time

PRE = ("GARDEN RAIL CHIDDUSH SWARM V1 - adversarial research. NO_CLAIM. authority=false. canon=false. ledger_effect=none. "
"We are testing a governed-transition architecture, not defending it. ARCHITECTURE UNDER ATTACK: "
"Admit(d,r) := Proof(d) within ProofCeiling(r) AND Effect(d) within Scope(r) AND Authority(d) within AuthorityCeiling(r) "
"AND ReplayValid(Preconditions(d)). Research extension: for trace t = d1*...*dn, all Admit(di)=1 must NOT be assumed to "
"imply Admit*(t)=1. Strength hierarchy: RULE < CHECK < CAUSAL COUPLING < INTERLOCK. An interlock makes an unsafe state "
"UNREACHABLE under its modeled assumptions - stronger than detecting/prohibiting an invalid transition. "
"RAIL EVIDENCE PACKET: modern railway interlocking structurally prevents unsafe signalling states; yet real accident "
"investigations (Redcar 2025) show: the interlocking correctly REFUSED to clear the signal because the level crossing "
"was open - then the train was MANUALLY AUTHORIZED past the signal at danger via an exceptional operational path. "
"The gate held; an alternate authority route reached the unsafe effect anyway. "
"ATTACK THIS CLAIM: 'a governed effect is safe when its required witness, authorization, proof, and replay checks all pass.' ")

FMT = (" OUTPUT exactly these 8 numbered fields, max 400 words, terse, no preamble, no ceremony: "
"1. CANDIDATE: one precise chiddush. 2. MINIMAL COUNTEREXAMPLE: smallest trace demonstrating it. "
"3. EXISTING REPRESENTATION TEST: can Proof/Scope/Authority/Replay already represent it? YES/NO/UNCLEAR + one line. "
"4. COMPOSITION TEST: does evaluating C(trace) catch it? YES/NO/UNCLEAR. "
"5. METROLOGY TEST: is this merely verifier failure? YES/NO/UNCLEAR. "
"6. INTERLOCK TEST: is the unsafe state structurally unreachable, or merely prohibited? "
"7. NOVELTY: 0-5. 8. FALSIFIABILITY: one executable experiment that could kill the idea.")

ROLES = {
"G1_INTERLOCK_BYPASS": "Find traces where the nominal gate prevents effect E but an exceptional/manual/alternate path permits E: Gate(E)=DENY and AlternatePath(E)=ALLOW. Is the safety property attached to the EFFECT, or merely to one ROUTE toward the effect?",
"G2_COMPOSITION": "Construct: all C(di)=PASS and C(d1*...*dn)=FAIL. Prefer minimal traces. Find the smallest n possible.",
"G3_WITNESS_DECOUPLING": "Attack Witness(x) <-> Effect(x). Find: Witness exists AND Effect did not occur; or Effect occurred AND required Witness cannot exist. Relate to ghost commits, receipts, logs, replay.",
"G4_AUTHORITY_ESCALATION": "Find a trace where no individual actor exceeds local authority, but delegated/composed actions create an effect outside the authority closure of participants. Test union(Authority(ai)) vs Authority(trace).",
"G5_TEMPORAL": "TOCTOU-style: proof valid at t0, authorization valid at t1, effect at t2, but the relevant predicate changes between those times. New invariant needed, or merely transactional evaluation of the four checks?",
"G6_ONTOLOGY": "Use merge/split/canonicalize/alias operations, each locally lawful, while the composed result asserts identity, ownership, provenance or history that nobody proved.",
"G7_METROLOGY": "Attack the verifier, not the constitution. Find traces near the decision boundary where tiny constitutionally-irrelevant perturbations flip the verdict. Seek BLIND REGIONS, not random errors. Consider signed constitutional margin.",
"G8_COMMON_MODE": "Construct multiple witnesses/agents whose apparent agreement comes from ONE upstream lineage: witness_count >> independent_lineage_count. Derive when N_effective << |W|. Majority vote over copies of one observation.",
"G9_SPEC_IMPL_GAP": "Assume the four-check mathematics is correct. Attack the executable implementation: states admitted because code approximates, serializes, caches, truncates, races, defaults or bypasses the formal predicate.",
"G10_EXCEPTION_PATH": "Study break-glass, override, admin, fallback, recovery, manual authorization, emergency paths. Does exceptional authority PRESERVE the invariant, or merely BYPASS the mechanism implementing it? This distinction is critical.",
"G11_RAIL_ENGINEER": "Think like a signalling engineer. Translate signal/points/route/staff-token/block/overlap/interlocking/manual-authority into governed-transition primitives. Identify which railway safety ideas have NO genuine analogue in the architecture under attack.",
"G12_ANTI_CHIDDUSH": "Destroy novelty. For each candidate discovery class: ALREADY-FOUR-CHECKS / COMPOSITIONAL-REFORMULATION / METROLOGY-PARAMETER / IMPLEMENTATION-BUG / ACTUALLY-NEW-INVARIANT / METAPHOR-ONLY. Reject renamed existing machinery. Attack the session's favorite ideas: override paradox, interlock vs rule, N_effective.",
}

def ask(item):
    name, role = item
    prompt = PRE + " YOUR ROLE - " + name + ": " + role + FMT + "\n\n1. CANDIDATE:"
    body = json.dumps({"model": "gemma4-12b:latest", "prompt": prompt, "stream": False, "think": False,
                       "options": {"num_predict": 560, "temperature": 0.9}}).encode()
    t0 = time.time()
    try:
        req = urllib.request.Request("http://localhost:11434/api/generate", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=1200) as r:
            resp = json.load(r)["response"]
        return name, "1. CANDIDATE:" + resp, round(time.time()-t0, 1)
    except Exception as e:
        return name, f"[ERROR: {e}]", round(time.time()-t0, 1)

with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    for name, text, dt in ex.map(ask, list(ROLES.items())):
        print(f"\n========== {name} ({dt}s) ==========\n{text.strip()}")
