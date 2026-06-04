#!/usr/bin/env python3
"""
helen — HELEN OS unified entrypoint

Usage:
  helen start    [--temple] [--airi] [--ledger PATH]
  helen stop
  helen status
  helen init
  helen chat
  helen temple
  helen approve [APPROVAL_ID]
  helen ledger  [--last N]
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Terminal colours
R = "\033[0m"
B = "\033[1m"
C = "\033[36m"
Y = "\033[33m"
G = "\033[32m"
D = "\033[90m"
M = "\033[35m"


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_start(args):
    """Boot the full HELEN OS stack in order."""
    from service_registry import ServiceRegistry
    from approval_queue import ApprovalQueue
    from boot_orchestrator import BootOrchestrator

    registry = ServiceRegistry()
    queue = ApprovalQueue()

    orchestrator = BootOrchestrator(
        registry=registry,
        approval_queue=queue,
        ledger_path=getattr(args, "ledger", None),
        with_temple=getattr(args, "temple", False),
        with_airi=getattr(args, "airi", False),
    )

    print(f"\n{B}━━━ HELEN OS — booting ━━━━━━━━━━━━━━━━━━━━━━━━{R}")
    ok = orchestrator.start()
    print(f"{D}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}\n")

    if ok:
        renderer = orchestrator.get_renderer()
        if renderer:
            print(renderer.render())
            print()
        # Drop into chat REPL
        cmd_chat(args, orchestrator=orchestrator)
    else:
        print(f"{Y}HELEN OS boot failed — kernel or memory could not start.{R}")
        sys.exit(1)


def cmd_stop(args):
    """Shutdown all running HELEN services."""
    from service_registry import ServiceRegistry
    registry = ServiceRegistry()
    if not registry.any_running():
        print(f"{D}No HELEN services are running.{R}")
        return

    print(f"{B}Stopping HELEN OS...{R}")
    for name in reversed(["kernel", "memory", "hal", "hermes", "airi", "temple"]):
        if registry.is_running(name):
            registry.mark_stopped(name, "shutdown by helen stop")
            print(f"  {D}[stopped] {name}{R}")
    print(f"{G}HELEN OS stopped.{R}")


def cmd_status(args):
    """Show status of all HELEN services."""
    from service_registry import ServiceRegistry
    registry = ServiceRegistry()
    states = registry.all()

    print(f"\n{B}━━━ HELEN OS status ━━━━━━━━━━━━━━━━━━━━━━━━━━{R}")
    fmt = "{:<12} {:<10} {:<8} {}"
    print(f"{D}{fmt.format('SERVICE', 'STATUS', 'PID', 'DETAIL')}{R}")
    print(f"{D}{'─'*52}{R}")

    status_colour = {
        "running": G,
        "stopped": D,
        "error":   Y,
        "skipped": D,
    }

    for name in ["kernel", "memory", "hal", "hermes", "airi", "temple"]:
        svc = states.get(name, {"name": name, "status": "stopped", "pid": None,
                                 "port": None, "detail": "", "started_at": None})
        col = status_colour.get(svc["status"], D)
        pid_str = str(svc["pid"]) if svc.get("pid") else "-"
        detail = svc.get("detail", "")
        print(f"  {col}{fmt.format(name, svc['status'], pid_str, detail)}{R}")

    print(f"{D}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}\n")


def cmd_init(args):
    """Print /init view: identity, threads, tensions, next action, pending approvals."""
    from approval_queue import ApprovalQueue
    from init_renderer import InitRenderer

    # Try to load spine and librarian if available
    spine = None
    librarian = None

    try:
        from helen_memory_spine import MemorySpine
        ledger_path = Path.home() / ".helen" / "ledger_v1.ndjson"
        spine = MemorySpine(ledger_path=str(ledger_path))
        spine.boot()
    except Exception:
        pass

    try:
        from helen_librarian import HELENLibrarian
        librarian = HELENLibrarian()
    except Exception:
        pass

    queue = ApprovalQueue()
    renderer = InitRenderer(memory_spine=spine, librarian=librarian, approval_queue=queue)
    print(renderer.render())


def cmd_chat(args, orchestrator=None):
    """Start HERMES chat REPL (calls helen_api.py /api/chat or falls back to boot.py)."""
    api_available = _check_api_health()

    if api_available:
        _chat_via_api()
    else:
        _chat_via_boot()


def cmd_temple(args):
    """Run one TEMPLE deliberation cycle."""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        import temple
        if hasattr(temple, "repl"):
            temple.repl()
        else:
            print(f"{Y}[temple] repl() not found in temple.py{R}")
    except ImportError as exc:
        print(f"{Y}[temple] Cannot import temple.py: {exc}{R}")
    except Exception as exc:
        print(f"{Y}[temple] Error: {exc}{R}")


def cmd_approve(args):
    """List or approve pending proposals."""
    from approval_queue import ApprovalQueue
    queue = ApprovalQueue()

    approval_id = getattr(args, "approval_id", None)
    if approval_id:
        try:
            approved = queue.approve(approval_id)
            print(f"{G}Approved: {approved.id}{R}")
            print(f"  type:     {approved.type}")
            print(f"  proposer: {approved.proposer}")
            print(f"  at:       {approved.approved_at}")
            # If this was a gated action, run it now and report the receipt.
            if approved.type == "action":
                try:
                    import helen_action_bridge as bridge
                    ok, result, receipt = bridge.execute_approved(approved.payload)
                    tag = G if ok else Y
                    print(f"{tag}  executed: {approved.payload.get('action')} -> ok={ok}{R}")
                    print(f"  receipt:  {receipt}")
                    print(f"  result:   {result[:500]}")
                except Exception as exc:
                    print(f"{Y}  execution failed: {exc}{R}")
        except ValueError as exc:
            print(f"{Y}Error: {exc}{R}")
            sys.exit(1)
    else:
        pending = queue.pending()
        if not pending:
            print(f"{D}No pending approvals.{R}")
            return

        print(f"\n{B}Pending approvals ({len(pending)}){R}")
        print(f"{D}{'─'*52}{R}")
        for appr in pending:
            print(f"  {C}{appr.id}{R}  [{appr.type}] from {appr.proposer}  {D}{appr.ts[:19]}{R}")
            # Show brief payload summary
            payload_preview = json.dumps(appr.payload, separators=(",", ":"))[:80]
            print(f"    {D}{payload_preview}{R}")
        print(f"\n{D}To approve: helen approve <ID>{R}\n")


def cmd_parlor(args):
    """Start HELEN voice server with Parlor real-time integration."""
    import subprocess
    import sys

    print(f"\n{B}━━━ HELEN VOICE — Starting Parlor integration ━━━━━━━━━━━━━━━━━━━━{R}")
    print(f"{D}This boots a real-time voice server with:{R}")
    print(f"{D}  • Silero VAD (voice activity detection){R}")
    print(f"{D}  • Barge-in detection (interrupt mid-response){R}")
    print(f"{D}  • Sentence-level TTS streaming{R}")
    print(f"{D}  • WebSocket bidirectional communication{R}")
    print(f"\n{G}Open browser: http://localhost:8766/parlor.html{R}\n")

    try:
        # Try parlor_voice_server.py first
        from pathlib import Path
        server_path = Path(__file__).parent / "parlor_voice_server.py"
        if server_path.exists():
            subprocess.run([sys.executable, str(server_path)], check=False)
        else:
            print(f"{Y}parlor_voice_server.py not found. Attempting direct import...{R}")
            from parlor_voice_server import app
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8766, log_level="info")
    except KeyboardInterrupt:
        print(f"\n{D}Parlor server stopped.{R}\n")
    except Exception as exc:
        print(f"{Y}Error starting Parlor server: {exc}{R}")
        print(f"{Y}  Install dependencies: pip install fastapi uvicorn websockets numpy silero-vad{R}")
        sys.exit(1)



def cmd_autonomous(args):
    """Launch HELEN autonomous mode daemon in background."""
    import subprocess
    from pathlib import Path

    daemon_path = Path(__file__).parent / "helen_autonomous.py"
    if not daemon_path.exists():
        print(f"{Y}helen_autonomous.py not found at {daemon_path}{R}")
        sys.exit(1)

    foreground = getattr(args, "foreground", False)

    if foreground:
        print(f"\n{B}━━━ HELEN Autonomous Mode — foreground ━━━━━━━━━━━━━━━━━━━━{R}")
        try:
            subprocess.run([sys.executable, str(daemon_path)], check=False)
        except KeyboardInterrupt:
            print(f"\n{D}[autonomous] stopped.{R}\n")
        return

    # Background launch
    log_file = "/tmp/helen_autonomous.log"
    proc = subprocess.Popen(
        [sys.executable, str(daemon_path)],
        stdout=open(log_file, "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    print(f"\n{B}━━━ HELEN Autonomous Mode ━━━━━━━━━━━━━━━━━━━━━━━━{R}")
    print(f"  {G}Daemon started in background (PID {proc.pid}){R}")
    print(f"  Log:  {D}{log_file}{R}")
    print(f"  Stop: {D}kill {proc.pid}{R}")
    print(f"{D}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}\n")


def cmd_council(args):
    """Query all available LLMs and synthesize consensus."""
    from helen_council import HELENCouncil

    council = HELENCouncil()
    council.status()
    print()

    query = getattr(args, "query", None)
    if not query:
        try:
            query = input(f"{Y}{B}Council query ▸ {R}").strip()
        except (KeyboardInterrupt, EOFError):
            return
    if not query:
        return

    result = council.deliberate(query)
    print(result.render())

def cmd_ledger(args):
    """Show recent ledger entries."""
    ledger_path = Path.home() / ".helen" / "ledger_v1.ndjson"
    last_n = getattr(args, "last", 10)

    if not ledger_path.exists():
        print(f"{D}Ledger not found: {ledger_path}{R}")
        return

    entries = []
    try:
        with open(ledger_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
    except Exception as exc:
        print(f"{Y}Error reading ledger: {exc}{R}")
        return

    recent = entries[-last_n:]
    print(f"\n{B}━━━ Ledger (last {last_n}) ━━━━━━━━━━━━━━━━━━━━━{R}")
    for entry in recent:
        seq = entry.get("seq", "?")
        ts = entry.get("timestamp", entry.get("ts", ""))[:19]
        cum_hash = entry.get("cum_hash", "")[:8]
        payload = entry.get("payload", {})
        ptype = payload.get("type", "?") if isinstance(payload, dict) else "?"
        print(f"  {D}seq={seq:<4} {ts}  hash={cum_hash}  type={ptype}{R}")
    print(f"{D}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}\n")


# ── Chat helpers ─────────────────────────────────────────────────────────────

def _check_api_health() -> bool:
    """Returns True if helen_api.py is running on :8765."""
    try:
        with urllib.request.urlopen("http://localhost:8780/api/health", timeout=1) as resp:
            return resp.status in (200, 204)
    except urllib.error.HTTPError:
        return True   # Server is up even if it returned an HTTP error code
    except Exception:
        return False


def _chat_via_api() -> None:
    """Chat REPL using the local Flask API."""
    print(f"{D}[chat] Connected to HERMES API on :8780{R}")
    print(f"{D}Commands: /status /init /temple /approve /ledger /quit{R}\n")

    history = []
    while True:
        try:
            user_input = input(f"{Y}{B}JMT ▸ {R}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{D}[session closed]{R}\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "exit", "quit", "q"):
            print(f"\n{D}[session closed]{R}\n")
            break

        if _handle_slash_command(user_input):
            continue

        history.append({"role": "user", "content": user_input})

        try:
            payload = json.dumps({
                "message": user_input,
                "history": history[-20:],
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://localhost:8780/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                body = json.loads(resp.read())
                reply = body.get("reply") or body.get("response") or body.get("content") or str(body)
        except Exception as exc:
            reply = f"[HERMES error: {exc}]"

        print(f"{C}{B}HELEN ▸ {R}{C}{reply}{R}\n")
        history.append({"role": "assistant", "content": reply})


def _chat_via_boot() -> None:
    """Fallback chat REPL using boot.py inline (Ollama direct)."""
    print(f"{D}[chat] HERMES not available — using direct Ollama connection{R}")
    print(f"{D}Commands: /status /init /temple /approve /ledger /quit{R}\n")

    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from boot import preflight, build_system_prompt, ollama_chat, log_turn, HELEN_MODEL
    except ImportError as exc:
        print(f"{Y}[chat] Cannot import boot.py: {exc}{R}")
        return

    ok, model = preflight()
    if not ok:
        print(f"{Y}[chat] Ollama not reachable: {model}{R}")
        print(f"{Y}       Run: ollama serve{R}")
        return

    print(f"{D}[chat] model: {model}{R}\n")
    try:
        import helen_action_bridge as bridge
        from approval_queue import ApprovalQueue
        _action_queue = ApprovalQueue()
        system_prompt = build_system_prompt() + bridge.action_protocol_prompt()
        print(f"{D}[chat] action bridge ON — read auto-runs, writes need /approve{R}\n")
    except Exception as exc:
        bridge = None
        _action_queue = None
        system_prompt = build_system_prompt()
        print(f"{Y}[chat] action bridge unavailable ({exc}) — chat only{R}\n")
    history = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input(f"{Y}{B}JMT ▸ {R}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{D}[session closed]{R}\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "exit", "quit", "q"):
            print(f"\n{D}[session closed]{R}\n")
            break

        if _handle_slash_command(user_input):
            continue

        # Paste guard: when transcript text is pasted in (HELEN's own markers,
        # action echoes, commit lines, box-drawing), the line-based REPL would
        # treat each fragment as a turn and act on it. Drop these before they
        # ever reach the model.
        if _is_noise_line(user_input):
            print(f"{D}·{R}", end="", flush=True)
            continue

        log_turn("user", user_input)
        history.append({"role": "user", "content": user_input})

        print(f"{C}{B}HELEN ▸ {R}", end="", flush=True)
        response = ollama_chat(history, model=model)
        # ollama_chat now streams tokens inline — just add spacing
        print()
        history.append({"role": "assistant", "content": response})
        log_turn("helen", response)

        # ── Agentic step: turn HELEN's words into actions ──────────────────
        steps = 0
        while bridge is not None and steps < bridge.MAX_AUTO_STEPS:
            action = bridge.extract_action(response)
            if action is None:
                break
            name = action["action"]
            kind = bridge.classify_kind(name)

            if kind == "read":
                ok, result = bridge.execute_action(action)
                tag = G if ok else Y
                print(f"{tag}  > auto-run [read] {name} -> {result[:300]}{R}")
                history.append({"role": "user",
                                "content": f"[ACTION RESULT · {name} · ok={ok}]\n{result}"})
                steps += 1
                print(f"{C}{B}HELEN ▸ {R}", end="", flush=True)
                response = ollama_chat(history, model=model)
                print()
                history.append({"role": "assistant", "content": response})
                log_turn("helen", response)
                continue

            if kind == "write":
                appr_id = bridge.queue_write(action, _action_queue)
                print(f"{Y}  ⛬ [write] queued {appr_id} — type {B}/approve {appr_id}{R}{Y} to run{R}")
                break

            # unknown action — tell HELEN so she can correct, bounded by steps
            print(f"{Y}  ✗ unknown action: {name}{R}")
            history.append({"role": "user",
                            "content": f"[ACTION ERROR] '{name}' is not a real action. "
                                       f"Use only catalogued actions, or answer in prose."})
            steps += 1
            print(f"{C}{B}HELEN ▸ {R}", end="", flush=True)
            response = ollama_chat(history, model=model)
            print()
            history.append({"role": "assistant", "content": response})
            log_turn("helen", response)

        if len(history) > 21:
            history = [history[0]] + history[-20:]


_NOISE_PREFIXES = (
    "JMT ▸", "HELEN ▸", "HELEN_ACTION:", "[chat]", "===", "⛬", "✗",
    "> auto-run", "auto-run [", "SHIP:", "ABORT:", "Co-Authored", "⏺", "⎿",
    "━", "│", "╭", "╮", "╯", "╰", "├", "└", "┃",
    "queued appr_", "type /approve", "PENDING:", "[helen_computer]",
)


def _is_noise_line(s: str) -> bool:
    """True if the line is obviously pasted transcript/UI chrome, not a real prompt.

    Conservative: only matches markers a human would never type as input
    (HELEN's own prompt/action echoes, commit trailers, box-drawing).
    """
    t = s.strip()
    if t.startswith(_NOISE_PREFIXES):
        return True
    if t.startswith(">") and "auto-run" in t:
        return True
    return False


def _handle_slash_command(user_input: str) -> bool:
    """Handle /commands inline. Returns True if handled."""
    if user_input == "/status":
        cmd_status(None)
        return True
    if user_input == "/init":
        cmd_init(None)
        return True
    if user_input == "/approve":
        cmd_approve(type("args", (), {"approval_id": None})())
        return True
    if user_input.startswith("/approve "):
        parts = user_input.split(None, 1)
        cmd_approve(type("args", (), {"approval_id": parts[1] if len(parts) > 1 else None})())
        return True
    if user_input == "/ledger":
        cmd_ledger(type("args", (), {"last": 10})())
        return True
    if user_input.startswith("/ledger "):
        try:
            n = int(user_input.split()[1])
        except (IndexError, ValueError):
            n = 10
        cmd_ledger(type("args", (), {"last": n})())
        return True
    if user_input == "/temple":
        cmd_temple(None)
        return True
    return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="helen",
        description="HELEN OS — unified entrypoint",
    )
    sub = parser.add_subparsers(dest="command")

    # helen start
    p_start = sub.add_parser("start", help="Boot the full HELEN OS stack")
    p_start.add_argument("--temple", action="store_true", help="Enable TEMPLE deliberation")
    p_start.add_argument("--airi",   action="store_true", help="Enable AIRI presence layer")
    p_start.add_argument("--ledger", default=None, help="Path to ledger NDJSON")
    p_start.set_defaults(func=cmd_start)

    # helen stop
    p_stop = sub.add_parser("stop", help="Shutdown all running HELEN services")
    p_stop.set_defaults(func=cmd_stop)

    # helen status
    p_status = sub.add_parser("status", help="Show status of all HELEN services")
    p_status.set_defaults(func=cmd_status)

    # helen init
    p_init = sub.add_parser("init", help="Print /init view")
    p_init.set_defaults(func=cmd_init)

    # helen chat
    p_chat = sub.add_parser("chat", help="Start HERMES chat REPL")
    p_chat.set_defaults(func=cmd_chat)

    # helen temple
    p_temple = sub.add_parser("temple", help="Run one TEMPLE deliberation cycle")
    p_temple.set_defaults(func=cmd_temple)

    # helen approve [ID]
    p_approve = sub.add_parser("approve", help="List or approve pending proposals")
    p_approve.add_argument("approval_id", nargs="?", default=None,
                           help="Approval ID to approve (omit to list all pending)")
    p_approve.set_defaults(func=cmd_approve)

    # helen ledger [--last N]
    p_ledger = sub.add_parser("ledger", help="Show recent ledger entries")
    p_ledger.add_argument("--last", type=int, default=10, help="Number of entries to show")
    p_ledger.set_defaults(func=cmd_ledger)

    # helen parlor
    p_parlor = sub.add_parser("parlor", help="Start HELEN voice server (real-time Parlor integration)")
    p_parlor.set_defaults(func=cmd_parlor)

    # helen autonomous
    p_auto = sub.add_parser("autonomous", help="Launch HELEN autonomous mode daemon (background)")
    p_auto.add_argument("--foreground", action="store_true",
                        help="Run in foreground (blocking) instead of background")
    p_auto.set_defaults(func=cmd_autonomous)

    # helen council
    p_council = sub.add_parser("council", help="Multi-LLM consensus (GLM-5.1 + GPT-4 + Claude)")
    p_council.add_argument("query", nargs="*", help="Question to deliberate")
    p_council.set_defaults(func=lambda a: cmd_council(type("a", (), {"query": " ".join(a.query) if a.query else None})()))

    args = parser.parse_args()

    if not args.command:
        # Default: helen start
        args.command = "start"
        args.temple = False
        args.airi = False
        args.ledger = None
        cmd_start(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
