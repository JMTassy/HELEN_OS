#!/usr/bin/env python3
"""
Cognitive Kernel CLI.

Entry point for Phase 1A kernel.

Usage:
    python3 main.py
    
Commands:
    help          Show this help
    health        Check model health
    execute       Execute query (interactive)
    export        Export ledger to file
    verify        Verify ledger integrity
    exit/quit     Exit
"""

import json
import sys
from core import CognitiveKernel, KernelError
from model import MistralModel
from roles import list_roles


def print_help():
    print(__doc__)


def cmd_health(kernel: CognitiveKernel):
    """Check if model is healthy."""
    if kernel.model.health_check():
        print(f"✅ {kernel.model.model} is available")
        models = kernel.model.get_available_models()
        print(f"   Available models: {len(models)}")
    else:
        print(f"❌ {kernel.model.model} not found")
        models = kernel.model.get_available_models()
        print(f"   Available: {models}")


def cmd_execute(kernel: CognitiveKernel):
    """Execute a query interactively."""
    print("\nExecute Query")
    print(f"Available roles: {', '.join(list_roles())}")
    print(f"Namespaces: math, world, project\n")
    
    query = input("Query: ").strip()
    if not query:
        print("❌ Empty query")
        return
    
    role = input("Role: ").strip()
    if role not in list_roles():
        print(f"❌ Invalid role: {role}")
        return
    
    namespace = input("Namespace (math|world|project): ").strip()
    if namespace not in ["math", "world", "project"]:
        print(f"❌ Invalid namespace: {namespace}")
        return
    
    print("\n⏳ Executing...")
    
    try:
        entry = kernel.execute(query, role, namespace)
        
        print(f"\n✅ Execution complete")
        print(f"   ID: {entry.get('hash', '?')[:12]}...")
        print(f"   Output: {json.dumps(entry.get('output'), indent=2)}")
    
    except KernelError as e:
        print(f"❌ Execution failed: {e}")


def cmd_export(kernel: CognitiveKernel):
    """Export ledger to file."""
    path = input("Export path (default: ledger.jsonl): ").strip()
    if not path:
        path = "ledger.jsonl"
    
    kernel.export_ledger(path)
    print(f"✅ Exported {len(kernel.get_ledger())} entries to {path}")


def cmd_verify(kernel: CognitiveKernel):
    """Verify ledger integrity."""
    valid = kernel.verify_integrity()
    entries = len(kernel.get_ledger())
    
    if valid:
        print(f"✅ Ledger valid ({entries} entries)")
    else:
        print(f"❌ Ledger corrupted ({entries} entries)")


def cmd_status(kernel: CognitiveKernel):
    """Show kernel status."""
    print(f"\n{kernel}")
    print(f"\nLedger entries: {len(kernel.get_ledger())}")
    print(f"Chain valid: {kernel.verify_integrity()}")
    print(f"\nMemory state:")
    for ns, state in kernel.get_memory().items():
        print(f"  {ns}: {len(state)} keys")


def main():
    print("="*60)
    print("COGNITIVE KERNEL CLI (Phase 1A L1)")
    print("="*60)
    
    # Initialize kernel
    kernel = CognitiveKernel()
    
    if not kernel.model.health_check():
        print(f"⚠️  Warning: {kernel.model.model} not available")
        print("   Run: ollama serve")
    else:
        print(f"✅ {kernel.model.model} ready")
    
    print(f"\nType 'help' for commands\n")
    
    commands = {
        "help": print_help,
        "health": lambda k: cmd_health(k),
        "execute": lambda k: cmd_execute(k),
        "export": lambda k: cmd_export(k),
        "verify": lambda k: cmd_verify(k),
        "status": lambda k: cmd_status(k),
    }
    
    while True:
        try:
            cmd = input("kernel> ").strip()
            
            if not cmd:
                continue
            
            if cmd in ["exit", "quit"]:
                print("✅ Goodbye")
                break
            
            if cmd == "help":
                print_help()
            elif cmd in commands:
                commands[cmd](kernel)
            else:
                print(f"❌ Unknown command: {cmd}")
                print("   Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n✅ Goodbye")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
