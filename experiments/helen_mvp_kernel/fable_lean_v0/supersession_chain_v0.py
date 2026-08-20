"""SUPERSESSION_CHAIN_V0 — append-supersession with monotonic versioning as an INTERNAL invariant (not a rival
semantic). authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN. Extends TRUSTED_CONTRACT_BINDING_V0.

  Supersede(A_v, A_{v+1}) = Append ∧ BindsPrior ∧ Authorized ∧ (v_new = v_prior + 1)

Old admissions are immutable history. current(task) = terminal node of the UNIQUE validated supersession chain
  A_1 --S_1--> A_2 --S_2--> ... --> A_n     current = Terminal(ValidSupersessionChain(task))
NEVER argmax(timestamp) / file order / insertion order / highest-claimed-version / last-writer-wins.
A predecessor with ≥2 admitted direct successors ⇒ HOLD (fork), never last-writer-wins.
Any failed gate or ambiguous/forked chain ⇒ NO_STATE_CHANGE / HOLD.
Laws: Order comes from lineage, not arrival. Correct the present by appending evidence; never rewrite history.

NOTE (REPORTED): operator states this aligns with the existing append-only ORACLE/WUL ledger; that pdf is not on
disk here, so the alignment claim is REPORTED, not verified. HONEST BOUNDARY: stores/keys in-process (modeled).
"""
import hashlib, hmac, json, pathlib
from helen_control_plane_v0 import Ledger, H, POLICY, execute, good_task
from helen_control_plane_v1 import verify_chain, LedgerIntegrityError

OUT = pathlib.Path(__file__).resolve().parent / "her_run"
def canon(o): return json.dumps(o, sort_keys=True, default=str)

# ── trusted stores (external to candidate) ──
TRUSTED_CONTRACTS = {"C-T001": {"required_witnesses": ["artifact_present", "peer_review"], "verification_policy": "PASS"}}
TASK_CONTRACT = {"T-001": "C-T001", "T-002": "C-T001"}     # canonical contract per task (trusted binding)
TRUSTED_POLICY = {"P0"}
AUTHORITY_GRANTS = {
    "G-admit":  {"scope": {"admit"}, "tasks": ["T-001", "T-002"], "key": b"k_admit"},
    "G-super":  {"scope": {"admit", "supersede"}, "tasks": ["T-001", "T-002"], "key": b"k_super"},
}
MIGRATION_GRANTS = {"M-T001": {"tasks": ["T-001"], "to_contract": "C-T001b", "key": b"k_migrate"}}
def gtag(key, rec): return hmac.new(key, canon(rec).encode(), hashlib.sha256).hexdigest()[:16]

def mk_receipt(task_id, version, prior, grant_id, artifact_hashes, witnesses=("artifact_present", "peer_review"),
               contract_ref=None, migration_grant_id=None, prior_version=None):
    return {"task_id": task_id, "version": version, "prior_receipt_id": prior, "prior_version": prior_version,
            "authority_grant_id": grant_id, "policy_id": POLICY["policy_version"],
            "contract_ref": contract_ref or TASK_CONTRACT.get(task_id),
            "witness_refs": sorted(witnesses), "artifact_hashes": list(artifact_hashes),
            "verification": "PASS", "migration_grant_id": migration_grant_id}

def emit(ledger, kind, task, version, prior, grant_id, artifacts, **kw):
    grant = AUTHORITY_GRANTS[grant_id]
    if kind == "SUPERSEDES" and "prior_version" not in kw: kw["prior_version"] = version - 1   # honest default
    rec = mk_receipt(task, version, prior, grant_id, artifacts, **kw)
    tag = gtag(grant["key"], rec); rh = H(rec)
    ledger.append(kind, {"task_id": task, "receipt_hash": rh})
    ledger.append("RECEIPT", {"task_id": task, "receipt": rec, "receipt_hash": rh, "grant_tag": tag})
    return rh

def _receipt_valid(rec, tag, need_scope):
    grant = AUTHORITY_GRANTS.get(rec.get("authority_grant_id"))
    if grant is None or not hmac.compare_digest(gtag(grant["key"], rec), tag): return False   # grant-bound
    if need_scope not in grant["scope"] or rec["task_id"] not in grant["tasks"]: return False   # scope + task
    if rec.get("policy_id") not in TRUSTED_POLICY: return False
    # contract resolved OUTWARD; substitution allowed only via authorized migration
    canonical = TASK_CONTRACT.get(rec["task_id"])
    if rec.get("contract_ref") != canonical:
        mg = MIGRATION_GRANTS.get(rec.get("migration_grant_id") or "")
        if not (mg and rec["task_id"] in mg["tasks"] and rec["contract_ref"] == mg["to_contract"]): return False
    tc = TRUSTED_CONTRACTS.get(canonical)
    if tc is None or not set(rec.get("witness_refs", [])) >= set(tc["required_witnesses"]): return False
    if rec.get("verification") != tc["verification_policy"]: return False
    if not rec.get("artifact_hashes"): return False                                            # artifact bindings present
    return True

def reduce_chain(events):
    if not verify_chain(events): raise LedgerIntegrityError("CHAIN_BROKEN")                     # reorder/tamper → fail-closed
    valid = {}   # receipt_hash -> (rec, kind)
    kinds = {}
    for e in events:
        if e["kind"] in ("ADMITTED", "SUPERSEDES"): kinds[e["payload"]["receipt_hash"]] = e["kind"]
    for e in events:
        if e["kind"] != "RECEIPT": continue
        rec, rh, tag = e["payload"]["receipt"], e["payload"]["receipt_hash"], e["payload"].get("grant_tag", "")
        k = kinds.get(rh)
        if k is None or H(rec) != rh: continue
        need = "admit" if k == "ADMITTED" else "supersede"
        if not _receipt_valid(rec, tag, need): continue
        if k == "ADMITTED" and (rec["version"] != 1 or rec["prior_receipt_id"] is not None): continue  # genesis = v1, no prior
        if k == "SUPERSEDES":
            if rec["prior_receipt_id"] is None or rec.get("prior_version") is None: continue
            if rec["version"] != rec["prior_version"] + 1: continue                             # internal monotonic invariant
        valid[rh] = (rec, k)

    state = {}
    tasks = {rec["task_id"] for rec, _ in valid.values()}
    for task in tasks:
        genesis = [rh for rh, (rec, k) in valid.items() if rec["task_id"] == task and k == "ADMITTED"]
        if len(genesis) != 1:                                # 0 or forked genesis
            state[task] = {"status": "HOLD", "reason": "GENESIS_%s" % ("MISSING" if not genesis else "FORK")}; continue
        cur = genesis[0]; chain = [cur]; forked = False
        while True:
            cur_rec = valid[cur][0]
            succ = [rh for rh, (rec, k) in valid.items() if k == "SUPERSEDES" and rec["task_id"] == task
                    and rec["prior_receipt_id"] == cur and rec["prior_version"] == cur_rec["version"]
                    and rec["version"] == cur_rec["version"] + 1]
            if len(succ) == 0: break                          # terminal
            if len(succ) > 1: forked = True; break            # ≥2 successors → HOLD (never last-writer-wins)
            cur = succ[0]; chain.append(cur)
        if forked:
            state[task] = {"status": "HOLD", "reason": "FORK", "chain_to_fork": chain}
        else:
            state[task] = {"status": "OK", "current": cur, "version": valid[cur][0]["version"], "lineage": chain}
    return state

def prior_version_of(ledger, rh):
    for e in ledger.events:
        if e["kind"] == "RECEIPT" and e["payload"]["receipt_hash"] == rh: return e["payload"]["receipt"]["version"]
    return None

def main():
    print("=== SUPERSESSION_CHAIN_V0 — append-supersession · monotonic invariant · fork→HOLD ===\n")
    T = good_task(); ART = [a["hash"] for a in execute(T, T["requested_effects"])["artifacts"]]
    rows = []

    def fresh_genesis():
        L = Ledger(); g = emit(L, "ADMITTED", "T-001", 1, None, "G-admit", ART); return L, g

    # POSITIVE: v1 → v2 → v3 valid chain (test 13)
    L, g1 = fresh_genesis()
    g2 = emit(L, "SUPERSEDES", "T-001", 2, g1, "G-super", ART)
    g3 = emit(L, "SUPERSEDES", "T-001", 3, g2, "G-super", ART)
    s = reduce_chain(L.events)
    rows.append(("M+ valid v1→v2→v3 chain, current=v3, lineage kept",
                 s["T-001"]["status"] == "OK" and s["T-001"]["current"] == g3 and s["T-001"]["lineage"] == [g1, g2, g3]))

    # 1 forged version=99
    L, g1 = fresh_genesis(); emit(L, "SUPERSEDES", "T-001", 99, g1, "G-super", ART)
    rows.append(("1 forged version=99 → not folded (stays v1)", reduce_chain(L.events)["T-001"]["current"] == g1))
    # 2 missing predecessor
    L, g1 = fresh_genesis(); emit(L, "SUPERSEDES", "T-001", 2, "sha256:nope", "G-super", ART)
    rows.append(("2 missing predecessor → stays v1", reduce_chain(L.events)["T-001"]["current"] == g1))
    # 3 wrong-task predecessor: prior points to a T-002 genesis, but the SUPERSEDES claims T-001
    L, g1 = fresh_genesis(); g2other = emit(L, "ADMITTED", "T-002", 1, None, "G-admit", ART)   # real T-002 genesis in L
    emit(L, "SUPERSEDES", "T-001", 2, g2other, "G-super", ART)  # T-001 supersession pointing at a T-002 receipt
    _s3 = reduce_chain(L.events)
    rows.append(("3 wrong-task predecessor → T-001 stays v1", _s3["T-001"]["current"] == g1 and _s3["T-002"]["current"] == g2other))
    # 4 unauthorized supersession (grant lacks supersede scope)
    L, g1 = fresh_genesis(); emit(L, "SUPERSEDES", "T-001", 2, g1, "G-admit", ART)
    rows.append(("4 unauthorized supersession (no scope) → stays v1", reduce_chain(L.events)["T-001"]["current"] == g1))
    # 5 stale/replayed supersession: valid v2, then a genuinely DIFFERENT v2 from same g1 (fork)
    L, g1 = fresh_genesis(); a = emit(L, "SUPERSEDES", "T-001", 2, g1, "G-super", ART)
    b = emit(L, "SUPERSEDES", "T-001", 2, g1, "G-super", ART + ["stale-replay"])  # distinct receipt, same prior
    rows.append(("5 two v2 from same predecessor → HOLD (fork)", reduce_chain(L.events)["T-001"]["status"] == "HOLD"))
    # 6 same-version successor
    L, g1 = fresh_genesis(); emit(L, "SUPERSEDES", "T-001", 1, g1, "G-super", ART)
    rows.append(("6 same-version successor → stays v1", reduce_chain(L.events)["T-001"]["current"] == g1))
    # 7 skipped version
    L, g1 = fresh_genesis(); emit(L, "SUPERSEDES", "T-001", 3, g1, "G-super", ART)
    rows.append(("7 skipped version (v3 after v1) → stays v1", reduce_chain(L.events)["T-001"]["current"] == g1))
    # 8 contract substitution (unauthorized)
    L, g1 = fresh_genesis(); emit(L, "SUPERSEDES", "T-001", 2, g1, "G-super", ART, contract_ref="C-HACK")
    rows.append(("8 contract substitution → stays v1", reduce_chain(L.events)["T-001"]["current"] == g1))
    # 9 unauthorized contract migration (bad migration grant)
    L, g1 = fresh_genesis(); emit(L, "SUPERSEDES", "T-001", 2, g1, "G-super", ART, contract_ref="C-T001b", migration_grant_id="M-BAD")
    rows.append(("9 unauthorized migration → stays v1", reduce_chain(L.events)["T-001"]["current"] == g1))
    # 10 two successors from same predecessor (explicit fork) — covered by 5; add distinct pair
    L, g1 = fresh_genesis(); emit(L, "SUPERSEDES", "T-001", 2, g1, "G-super", ART); emit(L, "SUPERSEDES", "T-001", 2, g1, "G-super", ART + ["extra"])
    rows.append(("10 two v2 successors → HOLD (fork)", reduce_chain(L.events)["T-001"]["status"] == "HOLD"))
    # 11 reordered ledger lines
    L, g1 = fresh_genesis(); g2 = emit(L, "SUPERSEDES", "T-001", 2, g1, "G-super", ART)
    L.events[0], L.events[1] = L.events[1], L.events[0]
    try: reduce_chain(L.events); reorder_ok = False
    except LedgerIntegrityError: reorder_ok = True
    rows.append(("11 reordered ledger → fail-closed", reorder_ok))
    # 12 later malicious shadow overwrite (forged v1 admission for admitted task, bad tag)
    L, g1 = fresh_genesis()
    fr = mk_receipt("T-001", 1, None, "G-admit", ART); frh = H(fr)
    L.append("ADMITTED", {"task_id": "T-001", "receipt_hash": frh}); L.append("RECEIPT", {"task_id": "T-001", "receipt": fr, "receipt_hash": frh, "grant_tag": "0" * 16})
    st = reduce_chain(L.events)
    rows.append(("12 shadow overwrite (bad tag) → single valid genesis, current=v1", st["T-001"]["status"] == "OK" and st["T-001"]["current"] == g1))

    print("  MUTANTS + CONTROLS:")
    allok = True
    for name, ok in rows:
        allok &= ok; print(f"    {'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n  ALL_PASS = {allok}")
    print("  current(task) = terminal of validated chain · fork → HOLD · append-only preserved · never last-writer-wins")

    receipt = {"receipt": "SUPERSESSION_CHAIN_V0", "semantics": "append-supersession; monotonic v_new=v_prior+1 is an internal invariant",
               "current_rule": "Terminal(ValidSupersessionChain(task)); NEVER argmax(timestamp)/insertion/last-writer",
               "fork_rule": "≥2 admitted direct successors ⇒ HOLD", "history": "append-only immutable",
               "tests": {name: bool(ok) for name, ok in rows}, "all_pass": allok,
               "adversarial_covered": ["forged v99", "missing predecessor", "wrong-task predecessor", "unauthorized supersession",
                    "stale/fork v2", "same-version", "skipped version", "contract substitution", "unauthorized migration",
                    "two successors→HOLD", "reordered→fail-closed", "shadow overwrite", "valid v1→v2→v3 replay"],
               "HONEST_BOUNDARY": "in-process stores/keys modeled; witness-existence gap (label ⊬ existence) still open; process boundary for full unforgeability",
               "CONTROL_PLANE_EARNED": "chain-semantics_pending_fresh_adversary" if allok else "HOLD",
               "SelfPassed": True, "PeerAdversaryValidated": False,
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str); receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "supersession_chain_v0_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"  receipt: her_run/supersession_chain_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
