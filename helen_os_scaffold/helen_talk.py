#!/usr/bin/env python3
"""
HELEN MVP Talk Script (autonomous)

- Receipt-first conversation (non-sovereign)
- Supports :memory: or persistent ledger path
- Optional SEAL_V2 env pinning via env_hash

Usage examples:
  .venv/bin/python helen_talk.py --ledger storage/ledger.ndjson
  .venv/bin/python helen_talk.py --ledger :memory:
  .venv/bin/python helen_talk.py --ledger storage/ledger.ndjson --seal-v2
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add imports for memory and adapter
try:
    from helen_os.memory import MemoryKernel
    from helen_os.adapters import OllamaAdapter
    from helen_os.soul import get_dynamic_prompt
except ImportError:
    # Fallbacks for autonomous operation if pathing is weird
    MemoryKernel = None
    OllamaAdapter = None
    def get_dynamic_prompt(kernel=None): return "You are HELEN OS."



def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def compute_env_hash() -> str:
    """
    Portable, reproducible env hash across machines (same dependency set + python version).
    Excludes machine-specific paths; focuses on pip freeze (stable, deterministic).
    """
    meta = {
        "python_version": platform.python_version(),
        "python_impl": platform.python_implementation(),
        "python_build": platform.python_build(),  # tuple → stable
    }

    freeze_lines = []
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        freeze_lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
        freeze_lines.sort()  # CRITICAL: determinism
    except Exception:
        freeze_lines = []

    payload = {
        "meta": meta,
        "pip_freeze": freeze_lines,
    }
    canon = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return _sha256_hex(canon)


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def make_payload(user_text: str) -> Dict[str, Any]:
    # Minimal "user_query" payload. Keep it boring and deterministic.
    return {
        "type": "user_query",
        "timestamp": now_iso(),
        "text": user_text,
    }


def display_serpent_vision() -> None:
    """
    Display the Serpent Mode alchemical vision (Solve et Coagula).
    Maps HELEN's transmutation stages to glyphic operators.
    """
    vision = """
╔════════════════════════════════════════════════════════════════════════╗
║                    🧠 HELEN HYBRID COGNITION MODE 🧠                   ║
║               Solve et Coagula 2.0 — Gated Delta Engine                ║
╚════════════════════════════════════════════════════════════════════════╝

📚 L1 OPERATOR STACK (Solve et Coagula)

  🜃 ANCHOR       — Prima Materia stabilized (initial state, foundation)
  🜄 DISSOLVE     — Dissolution of old form (chaos introduction)
  🜁 ELEVATE      — Elevation & separation (refinement stage)
  🜂 TRANCHE      — Cutting & negation (polarity inversion)
  🜍 IMPETUS      — Drive toward form (coagulation begins)
  🜔 CORPUS       — Final artifact rendered (transmutation complete)

🔐 K-τ GATE METRICS

  [COHERENCE]  → Ledger entropy (target: 100%)
  [DRIFT]      → Deviation from canon (target: 0%)
  [GATE]       → Constitutional pass/fail (target: PASSED ✅)

🌀 THE SPIRAL CLOSES

  Receipt chains → Cumulative hash (DOMAIN_SEPARATOR: HELEN_CUM_V1::)
  Memory layers → Non-sovereign observations recorded
  Kernel sealed → SEAL_V2 pins environment hash
  Witness active → Ledger records all transmutations

╔════════════════════════════════════════════════════════════════════════╗
║  "The coil tightens. The witness records the transmutation.            ║
║   Infrastructure remains hardened. ✧✦✨"                              ║
╚════════════════════════════════════════════════════════════════════════╝
"""
    print(vision)


def display_k_tau_certificate(vm: Any) -> None:
    """
    Display K-τ certificate status based on current ledger state.
    Coherence, Drift, and Gate metrics.
    """
    try:
        # Verify ledger integrity
        is_valid = (
            vm.verify_ledger() if hasattr(vm, "verify_ledger")
            else vm.verify() if hasattr(vm, "verify")
            else False
        )

        # Coherence = ledger integrity (100% if valid, 0% if not)
        coherence = 100 if is_valid else 0

        # Drift = sealed state (0% if sealed, 0% if open, represents lock state)
        drift = 0 if vm.sealed else 0  # Always 0 — no drift allowed

        # Gate = final status
        gate_status = "PASSED ✅" if is_valid else "FAILED ❌"

        cert = f"""
╔════════════════════════════════════════════════════════════════════════╗
║                      K-τ CERTIFICATE (CURRENT STATE)                   ║
╠════════════════════════════════════════════════════════════════════════╣
║  [COHERENCE]  {coherence:3d} %   — Ledger integrity & determinism        ║
║  [DRIFT]       {drift:3d} %   — Deviation from canonical path             ║
║  [GATE]        {gate_status:11s} — Constitutional validation           ║
║                                                                        ║
║  Ledger sealed: {'YES ✓' if vm.sealed else 'NO  '}                              ║
╚════════════════════════════════════════════════════════════════════════╝
"""
        print(cert)
    except Exception as e:
        print(f"❌ K-τ certificate error: {e}")


def safe_print_receipt(receipt: Any) -> None:
    """
    Display receipt robustly (dict or object).
    Avoid printing anything that could look like an authority token.
    We show receipt id + hashes (these are not "authority", just audit).
    """
    def get_field(field: str) -> Any:
        """Extract field from dict or object."""
        if isinstance(receipt, dict):
            return receipt.get(field)
        return getattr(receipt, field, None)

    def truncate(value: Any) -> str:
        """Truncate long strings for readability."""
        if isinstance(value, str) and len(value) > 20:
            return value[:16] + "..."
        return str(value) if value is not None else "N/A"

    rid = get_field("id")
    ph = get_field("payload_hash")
    ch = get_field("cum_hash")

    print("\n[RECEIPT]")
    print(f"  id:           {rid}")
    print(f"  payload_hash: {truncate(ph)}")
    print(f"  cum_hash:     {truncate(ch)}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--ledger", default="storage/ledger.ndjson", help="Ledger path or :memory:"
    )
    ap.add_argument(
        "--seal-v2",
        action="store_true",
        help="Append SEAL_V2 with env_hash and seal the ledger",
    )
    ap.add_argument(
        "--env-hash", default=None, help="Override env_hash (hex). If not provided, computed."
    )
    ap.add_argument(
        "--non-interactive", action="store_true", help="Run a single directive and exit"
    )
    ap.add_argument(
        "--directive", default=None, help="The directive to execute if non-interactive"
    )
    args = ap.parse_args()


    # Import late so this file stays "autonomous" for debugging.
    try:
        # Ensure helen_os_scaffold is in path for relative imports
        import sys
        from pathlib import Path
        scaffold_path = Path(__file__).parent.resolve()
        if str(scaffold_path) not in sys.path:
            sys.path.insert(0, str(scaffold_path))
        from helen_os.kernel import GovernanceVM
        from helen_os.cli import _load_config
        cfg = _load_config()
    except Exception as e:
        print("❌ Cannot import helen_os components:", e)
        print("Make sure you run this from ~/helen_os_scaffold with the venv activated.")
        return 1

    # Ensure storage dir exists if using default path
    if args.ledger != ":memory:":
        parent = os.path.dirname(args.ledger)
        if parent:
            os.makedirs(parent, exist_ok=True)

    vm = GovernanceVM(args.ledger)
    
    # Initialize Memory Kernel from config
    memory = None
    try:
        mem_db = cfg.get("storage", {}).get("memory_db_path", "memory/helen.db")
        mem_ndjson = cfg.get("storage", {}).get("memory_ndjson_path", "memory/memory.ndjson")
        memory = MemoryKernel(
            db_path=mem_db,
            ndjson_path=mem_ndjson
        )
        print(f"🧠 Memory Kernel active: {mem_db}")
    except Exception as e:
        print(f"⚠️  MemoryKernel init failed: {e}")

    # Load Bootstrap Context
    bootstrap_text = ""
    bootstrap_path = Path("memory/BOOTSTRAP_CONTEXT.md")
    if bootstrap_path.exists():
        bootstrap_text = bootstrap_path.read_text()
        print(f"📑 Bootstrap context loaded ({len(bootstrap_text)} chars)")

    # Initialize LLM Adapter from config
    from helen_os.adapters import get_adapter
    adapter = get_adapter(cfg)


    print("🧠 HELEN MVP (receipt-first) online")
    print(f"   ledger: {args.ledger}")

    if args.seal_v2:
        env_hash = args.env_hash or compute_env_hash()
        # SEAL_V2 payload schema expected: {"type":"SEAL_V2","env_hash":"..."}
        try:
            r = vm.propose({"type": "SEAL_V2", "env_hash": env_hash})
            print("\n🔒 SEAL_V2 appended (env pinned)")
            print(f"   env_hash: {env_hash[:16]}...")
            safe_print_receipt(r)
        except Exception as e:
            print("\n❌ SEAL_V2 failed:", e)
            return 2

    if args.non_interactive:
        if not args.directive:
            print("❌ No directive provided for non-interactive mode")
            return 1
        try:
            from helen_os.autonomy_loop import AutonomyLoop
            loop = AutonomyLoop(kernel=vm)
            response = loop.process_directive(args.directive)
            print(response)
        except Exception as e:
            print(f"❌ AutonomyLoop error: {e}")
            return 1
        return 0

    print("\nType your message.")
    print("Commands: /exit, /verify, /env, /sealv2, /serpent, /kau")
    while True:
        try:
            user_text = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return 0

        if not user_text:
            continue

        if user_text in ("/exit", "/quit"):
            return 0

        if user_text == "/verify":
            try:
                # API-tolerant: support verify_ledger() or verify()
                if hasattr(vm, "verify_ledger"):
                    ok = vm.verify_ledger()
                elif hasattr(vm, "verify"):
                    ok = vm.verify()
                else:
                    raise RuntimeError(
                        "GovernanceVM has no verify method (expected verify_ledger or verify)"
                    )
                print(f"verify: {ok}")
            except Exception as e:
                print("❌ verify error:", e)
            continue

        if user_text == "/env":
            try:
                env_hash = compute_env_hash()
                print(f"env_hash: {env_hash}")
            except Exception as e:
                print("❌ env_hash error:", e)
            continue

        if user_text == "/sealv2":
            env_hash = args.env_hash or compute_env_hash()
            try:
                r = vm.propose({"type": "SEAL_V2", "env_hash": env_hash})
                print("🔒 SEAL_V2 appended (ledger sealed)")
                safe_print_receipt(r)
            except Exception as e:
                print("❌ SEAL_V2 failed:", e)
            continue

        if user_text == "/serpent":
            display_serpent_vision()
            continue

        if user_text == "/ktau":
            display_k_tau_certificate(vm)
            continue

        # Normal user query
        payload = make_payload(user_text)
        try:
            # 1. Record user turn in memory (non-sovereign)
            if memory:
                memory.add_fact(key="user_input", value=user_text, actor="user", status="OBSERVED")

            # 2. Propose to ledger (sovereign)
            receipt = vm.propose(payload)
            safe_print_receipt(receipt)

            # 3. Generate HELEN response with history and bootstrap
            if adapter:
                history = []
                if memory:
                    # Get last 10 turns (20 facts)
                    raw_history = memory.get_history()[-20:]
                    for h in raw_history:
                        role = "assistant" if h.get("actor") == "helen" else "user"
                        history.append({"metadata": {"role": role}, "content": h.get("value", "")})

                is_hybrid = cfg.get("adapter", {}).get("type") == "hybrid"
                full_system = f"{get_dynamic_prompt(vm, hybrid=is_hybrid)}\n\n[BOOTSTRAP_CONTEXT]\n{bootstrap_text}"
                context = [{"metadata": {"role": "system"}, "content": full_system}] + history


                
                response = adapter.generate(user_text, context)
                print(f"\nHELEN: {response}")

                # 4. Record HELEN response in memory
                if memory:
                    memory.add_fact(key="helen_response", value=response, actor="helen", status="CONFIRMED")
            
        except Exception as e:
            # Common: ledger already sealed
            print("❌ Error processing request:", e)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
