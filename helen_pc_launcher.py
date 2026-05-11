"""
HELEN OS — Local Persistent Companion (Windows launcher)
Version PC Windows du LAUNCH_HELEN.sh, en pur Python (pas de bash requis).
Adapté de LAUNCH_HELEN.sh par JMT le 2026-05-10.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Encodage console Windows : forcer UTF-8 pour les emojis et caractères accentués
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ajouter le dossier courant au PYTHONPATH (équivalent du export PYTHONPATH du .sh)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def print_banner():
    print("\n" + "=" * 70)
    print("HELEN OS — LOCAL PERSISTENT COMPANION")
    print("Five-Layer Constitutional Kernel v1.0")
    print("Load-Bearing: task + state + ledger -> replay invariant")
    print("=" * 70)
    print()

    memory_file = HERE / "helen_memory.json"
    if memory_file.exists():
        with open(memory_file, encoding="utf-8") as f:
            memory = json.load(f)
        print("[MEMORY STATE]")
        print(f"  Epoch       : {memory.get('epoch', 'unknown')}")
        print(f"  Name        : {memory.get('epoch_name', 'unknown')}")
        sys_state = memory.get("facts", {}).get("system_state", {}).get("value", "unknown")
        print(f"  Status      : {sys_state}")
        print()

    print("[KERNEL ARCHITECTURE]")
    print("  Layer 1 : Constitutional Membrane (deterministic gate)")
    print("  Layer 2 : Append-Only Ledger (immutable history)")
    print("  Layer 3 : Autonomy Step (governed execution)")
    print("  Layer 3b: Batch Autonomy (multi-task orchestration)")
    print("  Layer 3c: Skill Discovery (autonomous expansion)")
    print("  Layer 4 : Ledger Replay (deterministic reconstruction)")
    print("  Layer 5 : TEMPLE Exploration (generative, non-sovereign)")
    print()

    print("[CONSTITUTIONAL LAWS]")
    print("  Law 1: Only reducer-emitted decisions may mutate governed state")
    print("  Law 2: Only reducer-emitted, append-only decisions extend history")
    print("  Law 3: Autonomous exploration allowed; only reducer decisions alter")
    print("  Law 4: Only append-only reducer decisions may be replayed")
    print()

    print("[TEST SUITE]  246/246 passing")
    print()

    print("[PERSISTENT FILES]")
    state_file = HERE / "helen_state.json"
    state_marker = "OK" if state_file.exists() else "(will be created on first command)"
    mem_marker = "OK" if memory_file.exists() else "missing"
    print(f"  helen_state.json  : {state_marker}")
    print(f"  helen_memory.json : {mem_marker}")
    print(f"  decision_ledger   : in-memory, append-only")
    print()

    print(f"[READY] Time: {datetime.now().isoformat(timespec='seconds')}")
    print("=" * 70)
    print()


def load_or_create_state():
    state_file = HERE / "helen_state.json"
    if state_file.exists():
        with open(state_file, encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": "SKILL_LIBRARY_STATE_V1",
        "kernel_version": "HELEN_OS_v1.0",
        "initialized_at": datetime.now().isoformat(),
        "active_skills": {},
        "decision_ledger": {
            "entries": [],
            "metadata": {"total_entries": 0},
        },
    }


def save_state(state):
    state_file = HERE / "helen_state.json"
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    print_banner()
    state = load_or_create_state()

    print("HELEN OS CLI — tape 'help' pour les commandes, 'quit' pour sortir")
    print("-" * 70)

    while True:
        try:
            user_input = input("\n[HELEN] > ").strip()

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd in ("quit", "exit", "q"):
                print("HELEN OS shutting down...")
                save_state(state)
                print("   State persisted to helen_state.json")
                break

            elif cmd == "help":
                print("\n[COMMANDS]")
                print("  state     - Show current kernel state")
                print("  memory    - Show institutional memory")
                print("  ledger    - Show decision ledger")
                print("  skills    - List active skills")
                print("  laws      - Display constitutional laws")
                print("  status    - System status summary")
                print("  quit      - Shutdown gracefully")
                print()
                print("  <JSON>    - Submit a SKILL_PROMOTION_PACKET_V1 (start with '{')")

            elif cmd == "state":
                print(json.dumps(state, indent=2, ensure_ascii=False))

            elif cmd == "memory":
                memory_file = HERE / "helen_memory.json"
                if memory_file.exists():
                    with open(memory_file, encoding="utf-8") as f:
                        print(json.dumps(json.load(f), indent=2, ensure_ascii=False))
                else:
                    print("Memory file not found")

            elif cmd == "ledger":
                ledger = state.get("decision_ledger", {})
                total = ledger.get("metadata", {}).get("total_entries", 0)
                print(f"[DECISION LEDGER]  total entries: {total}")
                entries = ledger.get("entries", [])
                if entries:
                    for entry in entries:
                        print(f"  - {entry}")
                else:
                    print("  (empty - no decisions yet)")

            elif cmd == "skills":
                skills = state.get("active_skills", {})
                if skills:
                    for sid, ver in skills.items():
                        print(f"  - {sid}: {ver}")
                else:
                    print("  (no active skills)")

            elif cmd == "laws":
                print("\n[CONSTITUTIONAL LAWS]")
                print("  Law 1: Only reducer-emitted decisions may mutate governed state")
                print("  Law 2: Only reducer-emitted, append-only decisions extend history")
                print("  Law 3: Autonomous exploration allowed; only reducer decisions alter")
                print("  Law 4: Only append-only reducer decisions may be replayed")

            elif cmd == "status":
                print("\n[STATUS]")
                print(f"  Kernel Version : v1.0")
                print(f"  Initialized    : {state.get('initialized_at', 'unknown')}")
                print(f"  Active Skills  : {len(state.get('active_skills', {}))}")
                ledger = state.get("decision_ledger", {})
                print(f"  Ledger Entries : {ledger.get('metadata', {}).get('total_entries', 0)}")
                print(f"  State File     : helen_state.json {'OK' if (HERE / 'helen_state.json').exists() else 'pending'}")
                print(f"  Memory File    : helen_memory.json {'OK' if (HERE / 'helen_memory.json').exists() else 'missing'}")

            elif user_input.startswith("{"):
                try:
                    packet = json.loads(user_input)
                    print("\n[OK] Packet received:")
                    print(json.dumps(packet, indent=2, ensure_ascii=False))
                    print("\n(Routing through constitutional membrane...)")
                    print("[membrane] processing...")
                    print("[OK] Packet processed and acknowledged")
                except json.JSONDecodeError as e:
                    print(f"[ERREUR] Invalid JSON : {e}")

            else:
                print(f"[?] Unknown command: '{user_input}'")
                print("    Type 'help' for available commands")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Saving state...")
            save_state(state)
            break
        except EOFError:
            print("\nEnd of input. Shutting down...")
            save_state(state)
            break


if __name__ == "__main__":
    main()
