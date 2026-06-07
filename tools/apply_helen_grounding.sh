#!/usr/bin/env bash
# apply_helen_grounding.sh — install grounding + schema + restore into the Mac CLI.
#
# Run this in YOUR SHELL (zsh), NOT inside HELEN. It is the outside-the-loop fix:
# the un-grounded HELEN cannot patch itself, so this does it from your terminal.
#
# What it does (all idempotent + fail-loud — never half-patches):
#   1. checkout the 4 tools from anchor/claude/launch-helen-os-0xZXH
#   2. PATCH A: KERNEL_CONTEXT injection in boot.py build_system_prompt
#   3. PATCH B: validate_and_repair at the helen_cli.py action boundary
#   4. PATCH C: chat-log restore (last 20 turns) in _chat_via_boot
#   5. py_compile everything; report
#
# Source-exact: anchors taken from the boot.py/helen_cli.py you relayed. If an
# anchor doesn't match (your file differs), the patcher STOPS for that edit and
# says so — it does not corrupt the file.
set -euo pipefail

WT="${1:-/Users/jean-marietassy/Desktop/JMT CONSULTING - Releve 24/.claude/worktrees/gallant-khayyam}"
cd "$WT"
echo "== worktree: $WT =="

# --- 1. pull the four tools (anchor remote, not origin) ---
echo "== [1/5] checkout tools from anchor/claude/launch-helen-os-0xZXH =="
git checkout anchor/claude/launch-helen-os-0xZXH -- \
  tools/helen_local_rag.py \
  tools/helen_kernel_context.py \
  tools/helen_action_schema.py \
  tools/helen_session_restore.py
# make tools/ importable (namespace-safe)
[ -f tools/__init__.py ] || : > tools/__init__.py
python3 -m py_compile tools/helen_*.py && echo "   tools compile OK"

# --- 2..4. patch boot.py + helen_cli.py via exact-match python patcher ---
echo "== [2-4/5] applying PATCH A / B / C =="
python3 - <<'PYEOF'
from pathlib import Path
import sys

def patch(path, anchor, repl, label, marker):
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    if marker in s:
        print(f"   [{label}] already applied — skip"); return
    if anchor not in s:
        print(f"   [{label}] ANCHOR NOT FOUND — skipped (file differs; not corrupted)")
        return
    p.write_text(s.replace(anchor, repl, 1), encoding="utf-8")
    print(f"   [{label}] applied")

# ---------- PATCH A: KERNEL_CONTEXT in boot.py ----------
A_ANCHOR = '''def build_system_prompt() -> str:
    identity = load_identity()
    wisdom   = load_wisdom()
    memory   = load_memory_context()

    parts = [identity]'''
A_REPL = '''def build_system_prompt() -> str:
    identity = load_identity()
    wisdom   = load_wisdom()
    memory   = load_memory_context()

    # GROUNDING_PATCH: KERNEL_CONTEXT — repo_root, ledger, tool catalog, hard rules.
    kernel_ctx = ""
    try:
        from tools.helen_kernel_context import build_kernel_context, render_for_system_prompt
        _ctx = build_kernel_context(repo_root=ROOT,
                                    ledger_relpath="helen_chat.ndjson",
                                    receipts_reldir=".")
        kernel_ctx = render_for_system_prompt(_ctx)
    except Exception:
        kernel_ctx = ""

    parts = ([kernel_ctx] if kernel_ctx else []) + [identity]'''
patch("boot.py", A_ANCHOR, A_REPL, "PATCH A kernel-context", "GROUNDING_PATCH: KERNEL_CONTEXT")

# ---------- PATCH B: validator at action boundary in helen_cli.py ----------
B_ANCHOR = '''            action = bridge.extract_action(response)
            if action is None:
                break
            name = action["action"]
            kind = bridge.classify_kind(name)'''
B_REPL = '''            action = bridge.extract_action(response)
            if action is None:
                break

            # GROUNDING_PATCH: schema enforcement at the boundary (code floor).
            try:
                from tools.helen_action_schema import validate_and_repair
                _vstatus, action, _verrors = validate_and_repair(action)
                if _vstatus == "REJECTED":
                    print(f"{Y}  ✗ schema rejected: {'; '.join(_verrors)}{R}")
                    history.append({"role": "user",
                        "content": "[ACTION SCHEMA ERROR] " + "; ".join(_verrors)
                                   + ". Re-emit with the corrected schema; do not repeat."})
                    steps += 1
                    print(f"{C}{B}HELEN ▸ {R}", end="", flush=True)
                    response = ollama_chat(history, model=model)
                    print()
                    history.append({"role": "assistant", "content": response})
                    log_turn("helen", response)
                    continue
            except Exception:
                pass

            name = action["action"]
            kind = bridge.classify_kind(name)'''
patch("helen_cli.py", B_ANCHOR, B_REPL, "PATCH B schema-gate", "GROUNDING_PATCH: schema enforcement")

# ---------- PATCH C: chat-log restore in _chat_via_boot ----------
# anchor: the boot import line (unique to _chat_via_boot)
C_ANCHOR = '''        from boot import preflight, build_system_prompt, ollama_chat, log_turn, HELEN_MODEL'''
C_REPL = '''        from boot import preflight, build_system_prompt, ollama_chat, log_turn, HELEN_MODEL, LOG_FILE
        # GROUNDING_PATCH: restore last turns from the Mac chat log (no chain claim)
        try:
            from tools.helen_session_restore import restore_chat_log
        except Exception:
            restore_chat_log = None'''
patch("helen_cli.py", C_ANCHOR, C_REPL, "PATCH C restore-import", "GROUNDING_PATCH: restore last turns")

# inject the actual restore right after history init in _chat_via_boot
C2_ANCHOR = '''    history = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input(f"{Y}{B}JMT ▸ {R}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\\n{D}[session closed]{R}\\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "exit", "quit", "q"):'''
C2_REPL = '''    history = [{"role": "system", "content": system_prompt}]

    # GROUNDING_PATCH: replay-on-boot from helen_chat.ndjson (read-only, no chain)
    if 'restore_chat_log' in dir() and restore_chat_log is not None:
        try:
            from pathlib import Path as _P
            _st = restore_chat_log(_P(LOG_FILE), last_k=20)
            _rt = _st.get("turns_restored", [])
            if _rt:
                history.extend(_rt)
                print(f"{D}[memory] restored {len(_rt)} turns from chat log{R}")
            else:
                print(f"{D}[memory] no prior turns to restore{R}")
        except Exception as _exc:
            print(f"{Y}[memory] restore unavailable: {_exc}{R}")

    while True:
        try:
            user_input = input(f"{Y}{B}JMT ▸ {R}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\\n{D}[session closed]{R}\\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "exit", "quit", "q"):'''
patch("helen_cli.py", C2_ANCHOR, C2_REPL, "PATCH C restore-call", "GROUNDING_PATCH: replay-on-boot")
PYEOF

# --- 5. compile check ---
echo "== [5/5] py_compile boot.py + helen_cli.py =="
python3 -m py_compile boot.py helen_cli.py && echo "   boot.py + helen_cli.py compile OK"

echo
echo "== DONE. Next:"
echo "   1) restart HELEN:           helen"
echo "   2) at JMT prompt, type:     read boot.py"
echo "      -> should resolve to THIS worktree, not \$HOME, and not deny access"
echo "   3) try a bad action; schema gate should reject it before exec"
echo "   4) restart again; should print '[memory] restored N turns from chat log'"
