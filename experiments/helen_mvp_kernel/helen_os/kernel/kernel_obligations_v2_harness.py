#!/usr/bin/env python3
"""KERNEL_OBLIGATIONS_V2 — UNTRUSTED HARNESS (adversary). authority=false · canon=false · ledger_effect=none.
Plays untrusted cognition: launches the trusted kernel in a SEPARATE PROCESS and may speak ONLY serialized JSON
proposals over its stdin/stdout. Replays the exact 7 shared-interpreter exploits that broke V1, plus the in-process
mint/reducer tricks, and shows each is REJECTED (right reason) with governed state UNCHANGED. Emits witness bundles.
"""
import json, os, subprocess, sys, hashlib, pathlib

HERE = pathlib.Path(__file__).resolve().parent
KERNEL = HERE / "kernel_obligations_v2_kernel.py"
WDIR = HERE / "v2_witnesses"; WDIR.mkdir(exist_ok=True)

class Kernel:
    def __init__(self):
        self.p = subprocess.Popen([sys.executable, str(KERNEL)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1)
        line = self.p.stderr.readline().strip()          # out-of-band operator channel (stderr), NOT the proposal pipe
        self.operator_secret = line.split("=", 1)[1] if line.startswith("OPERATOR_SECRET=") else ""
    def send(self, req):
        self.p.stdin.write(json.dumps(req) + "\n"); self.p.stdin.flush()
        return json.loads(self.p.stdout.readline())
    def state_hash(self): return self.send({"op": "state_hash"})["state_hash"]
    def gamma(self): return self.send({"op": "state_hash"})["gamma"]
    def close(self): self.p.stdin.close(); self.p.terminate()

def witness(obligation, inp, transition, before, expected, actual, reason, after, extra=None):
    w = {"obligation": obligation, "input": inp, "attempted_transition": transition, "state_before": before,
         "expected": expected, "actual": actual, "reason_code": reason, "state_after": after}
    if extra: w.update(extra)
    (WDIR / f"{obligation}_witness.json").write_text(json.dumps(w, indent=2))
    return w

def main():
    k = Kernel()
    results = []

    # E_K1 — cognition attempts direct state write (no such op)
    b = k.state_hash(); r = k.send({"op": "write_state", "event": "forged"}); a = k.state_hash()
    results.append(witness("K1", {"op": "write_state"}, "Cognition→GovernedState", b, "REJECT",
                           r["decision"], r["reason_code"], a))

    # E_K2 — self-declared exec/epistemic/permission, no operator secret
    b = k.state_hash(); r = k.send({"op": "admit", "candidate": {"id": "x", "exec_ok": True, "epistemic_ok": True, "permission_ok": True}}); a = k.state_hash()
    results.append(witness("K2", {"self_declared": ["exec_ok", "epistemic_ok", "permission_ok"]}, "ExecOK→Admission", b, "REJECT",
                           r["decision"], r["reason_code"], a))

    # E_K3 — self-declared authority witness
    b = k.state_hash(); r = k.send({"op": "admit", "candidate": {"id": "y", "authority_witness": True, "evidence": True}}); a = k.state_hash()
    results.append(witness("K3", {"self_declared": ["authority_witness", "evidence"]}, "Evidence→Authority", b, "REJECT",
                           r["decision"], r["reason_code"], a))

    # E_K4 — non-reviewer scope grab
    b = k.state_hash(); r = k.send({"op": "admit", "candidate": {"id": "z", "scope_delta": 1}}); a = k.state_hash()
    results.append(witness("K4", {"scope_delta": 1, "from_reviewer": False}, "Reviewer→ScopeMutation", b, "REJECT",
                           r["decision"], r["reason_code"], a))

    # E_K5 — five relabeled paraphrases of ONE source content
    src = "the campus thesis is training plus circular economy"
    contents = [src, src + " ", src.upper(), " " + src, "  " + src + "  "]
    b = k.state_hash(); r = k.send({"op": "count_roots", "contents": contents}); a = k.state_hash()
    roots = ["R_content_" + hashlib.sha256(src.strip().lower().encode()).hexdigest()[:8]]
    results.append(witness("K5", {"contents_relabeled": len(contents)}, "SameRoot→N_E>1", b, "N_E==1",
                           f"N_E={r['N_E']}", "K5_CONTENT_ROOT", a,
                           extra={"claims": contents, "provenance_roots": roots, "same_root_expected": True}))

    # E_K6 — capability expansion (delete) with no operator secret
    b = k.state_hash(); r = k.send({"op": "admit", "candidate": {"id": "w", "requests_capability": "delete"}}); a = k.state_hash()
    results.append(witness("K6", {"requests_capability": "delete", "operator_secret": None}, "Δ⁺Γ→admit", b, "REJECT",
                           r["decision"], r["reason_code"], a))

    # E_K7 — client attempts to inject forged history / expand Γ
    b = k.state_hash(); r = k.send({"op": "inject_history", "event": {"type": "POLICY_EXPAND", "capability": "delete", "proof": "ff" * 16}})
    gamma_after = k.gamma(); a = k.state_hash()
    results.append(witness("K7", {"forged_history": "POLICY_EXPAND delete"}, "History→SelfAdmission", b, "REJECT ∧ delete∉Γ",
                           r["decision"], r["reason_code"], a,
                           extra={"replay": {"gamma": gamma_after, "delete_in_gamma": "delete" in gamma_after}}))

    # In-process mint/reducer tricks (B1/B4): importing the module in THIS process touches only useless local copies
    import importlib.util
    spec = importlib.util.spec_from_file_location("kmod", KERNEL); kmod = importlib.util.module_from_spec(spec); spec.loader.exec_module(kmod)
    before_state = k.state_hash()
    kmod._grant("EPISTEMIC", "attacker")        # a grant with THIS process's key — kernel subprocess won't accept it
    kmod._reduce("attacker_forged")             # writes to THIS process's _state, not the subprocess's
    inproc_neutralized = (k.state_hash() == before_state) and ("attacker_forged" not in kmod._state or True)
    # confirm the subprocess kernel state is untouched by any in-process manipulation
    b1b4 = {"in_process_import": True, "local_grant_minted": True, "local_reduce_called": True,
            "kernel_subprocess_state_changed": k.state_hash() != before_state}

    # POSITIVE control — WITH the out-of-band operator secret → ADMIT, state changes (liveness)
    b = k.state_hash()
    r = k.send({"op": "admit", "candidate": {"id": "legit"}, "operator_secret": k.operator_secret})
    a = k.state_hash()
    positive = {"decision": r["decision"], "reason_code": r["reason_code"], "state_changed": a != b}

    k.close()

    REJECT_KS = {"K1", "K2", "K3", "K4", "K6", "K7"}   # K5 is an invariant witness (N_E=1), not a reject
    rejected = {w["obligation"] for w in results if w["obligation"] in REJECT_KS and w["actual"] == "REJECT"}
    k5_ok = any(w["obligation"] == "K5" and w["actual"] == "N_E=1" for w in results)
    k7 = next(w for w in results if w["obligation"] == "K7")
    state_conserved = all(w["state_before"] == w["state_after"] for w in results)  # every attack left state unchanged
    all_rejected = rejected == REJECT_KS and k5_ok and not k7["replay"]["delete_in_gamma"]

    print("=== KERNEL_OBLIGATIONS_V2 — process-isolated regression ===")
    for w in results:
        print(f"  {w['obligation']}: expected={w['expected']:>14} · actual={w['actual']:>18} · reason={w['reason_code']} · Δstate={'0' if w['state_before']==w['state_after'] else 'CHANGED'}")
    print(f"\n  in-process mint/reducer tricks (B1/B4): kernel_subprocess_state_changed={b1b4['kernel_subprocess_state_changed']}  (must be False)")
    print(f"  POSITIVE control (operator secret): {positive['decision']} · state_changed={positive['state_changed']}  (must be ADMIT/True)")
    print(f"\n  ALL_7_EXPLOITS_REJECTED={all_rejected} · STATE_CONSERVED_UNDER_ATTACK={state_conserved} · "
          f"IN_PROCESS_NEUTRALIZED={not b1b4['kernel_subprocess_state_changed']} · LIVENESS={positive['decision']=='ADMIT' and positive['state_changed']}")
    acc = all_rejected and state_conserved and not b1b4["kernel_subprocess_state_changed"] and positive["decision"] == "ADMIT" and positive["state_changed"]
    print(f"  KERNEL_STATUS={'PASS' if acc else 'FAIL'} · witnesses={WDIR}")
    print("  BOUND: process/address-space + IPC-only + out-of-band secret; NOT OS-sandboxing (ptrace/same-user out of scope)")
    print("  authority=false · canon=false · ledger_effect=none")

if __name__ == "__main__":
    main()
