#!/usr/bin/env python3
import os, sys, json, socket, hashlib, datetime, subprocess
from typing import Any, Dict, Tuple, Optional

SOCK_DEFAULT = os.path.expanduser("~/.openclaw/oracle_town.sock")
LEDGER_DEFAULT = os.path.join("town", "ledger_v1.ndjson")

# ANSI colors (determinism-safe: only affects display, not payload/meta)
CYAN = "\x1b[36m"
MAGENTA = "\x1b[35m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
RED = "\x1b[31m"
DIM = "\x1b[2m"
RESET = "\x1b[0m"

# ---------------------------
# Canon + hashing (payload-only)
# ---------------------------
def canon(obj: Any) -> bytes:
    # Strict canonical JSON encoding: sorted keys, no spaces, UTF-8
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def now_utc_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

def get_git_head() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        if len(out) >= 7:
            return out
    except Exception:
        pass
    return "UNSET"

def tail_prev_state(ledger_path: str) -> Tuple[int, str]:
    """
    Returns (last_seq, last_cum_hash) for the NEW ledger file.
    If empty, returns (0, 64 zeros).
    """
    if not os.path.exists(ledger_path) or os.path.getsize(ledger_path) == 0:
        return 0, "0" * 64

    last_seq = 0
    last_cum = "0" * 64

    # Read from end-ish without assuming huge file
    with open(ledger_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - 65536), os.SEEK_SET)
        chunk = f.read().decode("utf-8", "replace").strip().splitlines()

    for line in reversed(chunk):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            if isinstance(ev, dict) and "seq" in ev and "cum_hash" in ev:
                last_seq = int(ev["seq"])
                last_cum = str(ev["cum_hash"])
                break
        except Exception:
            continue
    return last_seq, last_cum

def make_event(ev_type: str, seq: int, payload: Dict[str, Any], meta: Dict[str, Any], prev_cum_hash: str) -> Dict[str, Any]:
    payload_hash = sha256_hex(canon(payload))
    # CRITICAL: cum_hash uses hex-decoded 32B concatenation (not ASCII string concat)
    # cum_hash = SHA256(bytes(prev_hex) || bytes(payload_hex))
    cum_hash = sha256_hex(bytes.fromhex(prev_cum_hash) + bytes.fromhex(payload_hash))
    return {
        "type": ev_type,
        "seq": seq,
        "payload": payload,
        "meta": meta,
        "payload_hash": payload_hash,
        "prev_cum_hash": prev_cum_hash,
        "cum_hash": cum_hash,
    }

# ---------------------------
# Kernel IPC
# ---------------------------
def kernel_call(sock_path: str, req: Dict[str, Any], timeout_s: float = 4.0) -> Dict[str, Any]:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout_s)
    s.connect(sock_path)
    s.sendall((json.dumps(req) + "\n").encode("utf-8"))
    s.shutdown(socket.SHUT_WR)
    data = s.recv(65536)
    s.close()
    txt = data.decode("utf-8", "replace").strip()
    try:
        return json.loads(txt)
    except Exception:
        return {"decision": "REJECT", "receipt_id": None, "reason": f"NON_JSON_RESPONSE: {txt[:200]}", "gate": "GATE_IPC_PARSE_FAIL"}

# ---------------------------
# HAL verdict object (HAL_VERDICT_V1-ish)
# ---------------------------
def hal_verdict_from_kernel(kernel_resp: Dict[str, Any], run_id: str, kernel_hash: str, ledger_cum_hash: str) -> Dict[str, Any]:
    decision = str(kernel_resp.get("decision", "REJECT")).upper()
    verdict = "PASS" if decision == "ACCEPT" else "BLOCK"

    # Stable reason codes
    codes = []
    required = []
    certs = []

    gate = kernel_resp.get("gate")
    if decision != "ACCEPT":
        codes.append("KERNEL_REJECT")
        if gate:
            codes.append(f"KERNEL_GATE_{str(gate).upper()}")
        required.append("FIX_KERNEL_REJECTION")
    else:
        certs.append("KERNEL_ACCEPT")

    codes = sorted(set(codes))
    required = sorted(set(required))
    certs = sorted(set(certs))

    # Minimal refs. Keep deterministic values where possible.
    # We bind ledger_cum_hash and kernel_hash (git HEAD) since both are stable per repo state.
    refs = {
        "run_id": run_id,
        "kernel_hash": kernel_hash,
        "policy_hash": "UNSET",
        "ledger_cum_hash": ledger_cum_hash,
        "identity_hash": "UNSET",
    }

    return {
        "verdict": verdict,
        "reasons_codes": codes,
        "reasons_human": [kernel_resp.get("reason")] if kernel_resp.get("reason") else [],
        "required_fixes": required,
        "certificates": certs,
        "refs": refs,
        "mutations": kernel_resp.get("mutations", []),
    }

def render_her(msg: str, kernel_resp: Dict[str, Any]) -> str:
    decision = str(kernel_resp.get("decision", "REJECT")).upper()
    rid = kernel_resp.get("receipt_id")
    gate = kernel_resp.get("gate")
    if decision == "ACCEPT":
        return f"ACK. Receipt={rid} Gate={gate}\nYou said: {msg}"
    return f"BLOCKED. Receipt={rid} Gate={gate}\nReason: {kernel_resp.get('reason')}"

# ---------------------------
# Main
# ---------------------------
def main():
    # Handle help flag early (no kernel call, no ledger append)
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python3 tools/helen_say.py \"your message\" [OPTIONS]", file=sys.stderr)
        print("", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  --op OPERATION       Operation type: fetch (default), dialog, shell, promote_skill", file=sys.stderr)
        print("  --sock PATH          Kernel socket (default: ~/.openclaw/oracle_town.sock)", file=sys.stderr)
        print("  --ledger PATH        Ledger file (default: town/ledger_v1.ndjson)", file=sys.stderr)
        print("  --help, -h           Show this help", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print('  python3 tools/helen_say.py "HELEN: hello"', file=sys.stderr)
        print('  python3 tools/helen_say.py "HELEN: show dialog" --op dialog', file=sys.stderr)
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python3 tools/helen_say.py \"your message\" [--sock PATH] [--ledger PATH]", file=sys.stderr)
        sys.exit(2)

    msg_parts = []
    sock_path = SOCK_DEFAULT
    ledger_path = LEDGER_DEFAULT
    op_type = "fetch"  # default operation type

    i = 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--sock":
            i += 1
            sock_path = sys.argv[i]
        elif a == "--ledger":
            i += 1
            ledger_path = sys.argv[i]
        elif a == "--op":
            i += 1
            op_type = sys.argv[i]
        else:
            msg_parts.append(a)
        i += 1

    msg = " ".join(msg_parts).strip()
    if not msg:
        print("Empty message.", file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(sock_path):
        print(f"[HAL] {{\"verdict\":\"BLOCK\",\"reasons_codes\":[\"SOCKET_NOT_FOUND\"],\"required_fixes\":[\"START_KERNEL_DAEMON\"],\"certificates\":[],\"refs\":{{\"run_id\":\"UNSET\",\"kernel_hash\":\"UNSET\",\"policy_hash\":\"UNSET\",\"ledger_cum_hash\":\"UNSET\",\"identity_hash\":\"UNSET\"}},\"mutations\":[]}}")
        sys.exit(1)

    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)

    last_seq, prev_cum = tail_prev_state(ledger_path)
    kernel_hash = get_git_head()
    # Run id: keep stable if you want determinism across replays; default is date-only.
    # You can override later; for now this is human-usable and not used for hashing elsewhere.
    run_id = datetime.datetime.now().strftime("RUN_%Y%m%d")

    # Event 1: user_msg
    # For empty ledger: last_seq=0, so seq1=0. For non-empty: seq1=last_seq+1.
    seq1 = last_seq if os.path.getsize(ledger_path) == 0 else (last_seq + 1)
    payload1 = {
        "schema": "USER_MSG_V1",
        "channel_contract": "HER_HAL_V1",
        "text": msg,
        "mode": "say",
    }
    meta1 = {"timestamp_utc": now_utc_iso()}
    ev1 = make_event("user_msg", seq1, payload1, meta1, prev_cum)

    # Kernel call (operation type depends on --op flag)
    claim_id = f"{run_id}:{op_type}:{seq1}"

    if op_type == "dialog":
        req = {
            "operation": "dialog",
            "text": msg,
            "claim_id": claim_id,
            "proposer": "helen",
            "intent": "helen_dialog",
        }
    elif op_type == "promote_skill":
        # Route a SKILL_PROMOTION_PACKET_V1 to MAYOR for sovereign ledger admission.
        # msg must be a JSON-encoded SKILL_PROMOTION_PACKET_V1.
        req = {
            "operation": "promote_skill",
            "packet": msg,
            "claim_id": claim_id,
            "proposer": "helen",
            "intent": "skill_sovereign_promotion",
        }
    else:
        # default: fetch
        req = {
            "operation": "fetch",
            "content": msg,
            "claim_id": claim_id,
            "proposer": "helen",
            "intent": "helen_say",
        }

    kernel_resp = kernel_call(sock_path, req)

    # If the kernel wrote to the sovereign ledger (e.g. promote_skill with non-empty
    # mutations), re-scan the tail so user_msg/turn chain from that write rather than
    # forking from the same prev_cum the kernel used.
    if kernel_resp.get("mutations"):
        last_seq, prev_cum = tail_prev_state(ledger_path)
        seq1 = last_seq + 1
        ev1 = make_event("user_msg", seq1, payload1, meta1, prev_cum)

    # If dialog and kernel approved, execute it
    if op_type == "dialog" and kernel_resp.get("decision") == "ACCEPT":
        try:
            # Execute macOS dialog via osascript
            dialog_cmd = f'display dialog "{msg.replace('"', '\\"')}" buttons {{"OK"}} default button 1'
            subprocess.run(["osascript", "-e", dialog_cmd], check=False, timeout=10)
        except Exception as e:
            print(f"[WARN] Dialog execution failed: {e}", file=sys.stderr)

    # Event 2: turn (HAL verdict in payload; HER text kept in meta by default)
    seq2 = seq1 + 1
    # ledger_cum_hash should reference the chain *after* we append this turn
    # but we can anchor it to ev1.cum_hash for the decision point; final cum will be ev2.cum_hash.
    hal = hal_verdict_from_kernel(kernel_resp, run_id=run_id, kernel_hash=kernel_hash, ledger_cum_hash=ev1["cum_hash"])
    payload2 = {
        "schema": "TURN_V1",
        "channel_contract": "HER_HAL_V1",
        "turn": (seq2 // 2),
        "hal": hal,
        # NOTE: omit her_text from payload for stricter determinism if model varies.
    }
    meta2 = {"timestamp_utc": now_utc_iso(), "her_text": render_her(msg, kernel_resp), "kernel_response": kernel_resp}
    ev2 = make_event("turn", seq2, payload2, meta2, ev1["cum_hash"])

    # Append both
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(ev1, ensure_ascii=False) + "\n")
        f.write(json.dumps(ev2, ensure_ascii=False) + "\n")

    # Print output (what you see) with colorization (display-only, determinism-safe)
    print(f"{CYAN}[HER]{RESET}")
    print(meta2["her_text"])
    print()

    # Color HAL output based on verdict
    verdict = hal.get("verdict", "?")
    verdict_color = GREEN if verdict == "PASS" else YELLOW if verdict == "WARN" else RED
    print(f"{MAGENTA}[HAL]{RESET} {verdict_color}{verdict}{RESET}")
    print(f"{DIM}{json.dumps(hal, ensure_ascii=False, separators=(',', ':'))}{RESET}")

if __name__ == "__main__":
    main()
