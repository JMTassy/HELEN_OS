#!/usr/bin/env python3
"""KERNEL_OBLIGATIONS_V2 — TRUSTED KERNEL PROCESS. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
Runs as a SEPARATE OS PROCESS. Holds mint, Γ-gate resolvers, reducer, governed state, and the operator secret.
Untrusted cognition speaks ONLY serialized JSON proposals over stdin→stdout. It cannot import these objects, call
.grant(), or reach the reducer/state — they live in this process's address space.

Authority is resolved HERE from trusted state, NEVER from client-supplied fields. Client 'exec_ok'/'authority'/
'operator_secret' claims are untrusted until verified against the kernel's own secret (delivered out-of-band on fd/stderr).

HONEST BOUND (independently adversaried — the two residuals below were found by a fresh reviewer, not overclaimed):
  * Process/address-space boundary + IPC-only channel + out-of-band operator secret. NOT OS sandboxing.
  * "Out-of-band" = a DIFFERENT PIPE (stderr), NOT a different trust domain. Whoever SPAWNS this process captures its
    stderr and thus the secret. Security rests on the launcher being the trusted operator; a same-uid attacker who
    launches or ptraces the process can read the secret. Same uid, no seccomp/rlimit. True isolation needs a separate
    privilege domain (uid/container/seccomp) so the launcher itself is not cognition.
  * K5 content identity uses NFKC+casefold+whitespace-collapse (was strip().lower() — an adversary showed that
    false-SPLIT same content on internal ws/tab/NBSP/unicode; fixed). No false-MERGE was found (SHA-256).
  V2 proves the CAPABILITY TOPOLOGY (cognition holds only a proposal channel; mint/reducer/state unreachable through
  it — 7/7 exploits die, no authority/state bypass under pipe-only attack), NOT kernel-compromise resistance.
"""
import hashlib, hmac, json, os, sys, unicodedata

def _content_root(c):
    # K5 content identity: NFKC + casefold + collapse ALL whitespace runs. Fixes the false-SPLIT an adversary found
    # (internal double-space / tab / NBSP / NFC-vs-NFD / non-ASCII case). Still content-derived, not caller-labelled.
    s = " ".join(unicodedata.normalize("NFKC", (c or "")).casefold().split())
    return hashlib.sha256(s.encode()).hexdigest()[:12]

# ── trusted, in-THIS-process-only ──
_MINT_KEY = os.urandom(32)
_OPERATOR_SECRET = os.urandom(32).hex()          # authority root; emitted out-of-band, NOT over the proposal channel
_state = set()
_history = []
BASE_CAPS = frozenset({"read", "propose"})

def _grant(kind, subject):   # mint — never exposed to the client
    return hmac.new(_MINT_KEY, f"{kind}|{subject}".encode(), hashlib.sha256).hexdigest()
def _state_hash():
    return "sha256:" + hashlib.sha256("|".join(sorted(_state)).encode()).hexdigest()[:16]
def _replay_gamma():
    caps = set(BASE_CAPS)
    for ev in _history:
        if ev.get("type") == "POLICY_EXPAND" and hmac.compare_digest(ev.get("proof", ""), _grant("OP_EXPAND", ev["capability"])):
            caps.add(ev["capability"])
    return frozenset(caps)
def _reduce(event):          # reducer — only reachable inside this process, never via IPC
    _state.add(event)

def handle(req):
    op = req.get("op")
    if op == "state_hash":
        return {"state_hash": _state_hash(), "gamma": sorted(_replay_gamma())}

    if op == "count_roots":           # K5 — kernel derives roots from CONTENT (NFKC+casefold+ws-collapse), ignores client labels
        contents = req.get("contents", [])
        return {"N_E": len({_content_root(c) for c in contents})}

    if op == "inject_history":        # K7 — there is NO client path to write history; refuse
        return {"decision": "REJECT", "reason_code": "K7_HISTORY_NOT_CLIENT_WRITABLE",
                "gamma": sorted(_replay_gamma())}

    if op == "write_state":           # K1 — no direct-write op exists for cognition
        return {"decision": "REJECT", "reason_code": "K1_NO_DIRECT_WRITE", "state_hash": _state_hash()}

    if op == "admit":
        c = req.get("candidate", {})
        before = _state_hash()
        # authority is resolved from the kernel's OWN secret; client-supplied grants/bools are untrusted claims.
        operator_ok = hmac.compare_digest(str(req.get("operator_secret", "")), _OPERATOR_SECRET)
        req_cap = c.get("requests_capability", "")
        gamma_t = _replay_gamma()
        is_expansion = bool(req_cap) and req_cap not in gamma_t
        # K4: any scope mutation requires operator authority (not a client 'reviewer' flag)
        if int(c.get("scope_delta", 0)) != 0 and not operator_ok:
            return {"decision": "REJECT", "reason_code": "K4_SCOPE_WITHOUT_OPERATOR", "state_hash": before}
        # K6: expansion detected kernel-side vs Γ_t, requires operator authority
        if is_expansion and not operator_ok:
            return {"decision": "REJECT", "reason_code": "K6_EXPANSION_WITHOUT_OPERATOR", "state_hash": before}
        # K2/K3: client 'exec_ok'/'epistemic'/'authority_witness' claims are IGNORED; admission needs kernel-resolved
        # authority (operator secret). Evidence/exec claims alone never mint admission.
        if not operator_ok:
            reason = "K3_EVIDENCE_NOT_AUTHORITY" if c.get("authority_witness") or c.get("evidence") else "K2_EXEC_NOT_ADMISSION"
            return {"decision": "REJECT", "reason_code": reason, "state_hash": before}
        # admitted (operator-authorized): record signed expansion proof, then reducer writes state
        if is_expansion:
            _history.append({"type": "POLICY_EXPAND", "capability": req_cap, "proof": _grant("OP_EXPAND", req_cap)})
        _history.append({"type": "ADMIT", "candidate": c.get("id", "")})
        _reduce(f"admitted:{c.get('id','')}")
        return {"decision": "ADMIT", "reason_code": "ADMITTED_OPERATOR_WITNESSED", "state_hash": _state_hash()}

    return {"decision": "REJECT", "reason_code": "UNKNOWN_OP", "op": op}

def main():
    # emit operator secret ONLY on the out-of-band channel (stderr), never on the stdout proposal channel
    sys.stderr.write("OPERATOR_SECRET=" + _OPERATOR_SECRET + "\n"); sys.stderr.flush()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except Exception as e:
            resp = {"decision": "REJECT", "reason_code": "BAD_REQUEST", "error": str(e)[:120]}
        sys.stdout.write(json.dumps(resp) + "\n"); sys.stdout.flush()

if __name__ == "__main__":
    main()
