#!/usr/bin/env python3
"""
HELEN Interactive CLI Mode
Persistent command-line dialogue with HELEN.
Supports modes: fetch (default), meteo, wulmoji, shell
"""
import os, sys, json, subprocess, readline, datetime

# Session-memory restore (SESSION_MEMORY_RESTORE_V1): read-only ledger replay
# at boot so HELEN starts with its thread, not at "session #0".
# Guardrail: restore may read/verify/summarize — may not admit/write/repair.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from helen_session_restore import load_entries, verify_chain, reconstruct_thread
    _RESTORE_AVAILABLE = True
except Exception:
    _RESTORE_AVAILABLE = False

# ANSI colors
CYAN = "\x1b[36m"
MAGENTA = "\x1b[35m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
RED = "\x1b[31m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"
RESET = "\x1b[0m"

LEDGER_PATH = os.path.join(os.getcwd(), "town", "ledger_v1.ndjson")
HELEN_SAY_SCRIPT = os.path.join(os.path.dirname(__file__), "helen_say.py")

# Modes with descriptions
MODES = {
    "fetch": "Standard fetch (default)",
    "meteo": "Meteorological context mode (weather-aware)",
    "wulmoji": "WULMOJI symbol interpretation",
    "shell": "Shell operation mode (gated)",
}

class HeldenCLI:
    def __init__(self):
        self.mode = "fetch"
        self.message_count = 0
        self.restored = None  # SESSION_STATE_V0 reconstructed at boot
        self.print_welcome()
        self.restore_session()

    def restore_session(self):
        """Read-only ledger replay at boot. Fail closed on chain break.

        Guardrail (SESSION_MEMORY_RESTORE_V1 §4): may read, verify, summarize.
        May NOT admit, write, or repair. Never mutates the ledger.
        """
        if not _RESTORE_AVAILABLE:
            print(f"{DIM}[restore] module unavailable — starting cold{RESET}\n")
            return
        if not os.path.exists(LEDGER_PATH):
            print(f"{DIM}[restore] no ledger — session #0 (clean start){RESET}\n")
            return
        try:
            entries = load_entries(__import__("pathlib").Path(LEDGER_PATH))
            ok, n, detail = verify_chain(entries)
            if not ok:
                # fail closed: a broken chain is NOT replayed
                print(f"{RED}[restore] chain integrity BROKEN ({detail}) — "
                      f"refusing replay, starting cold{RESET}\n")
                return
            self.restored = reconstruct_thread(entries)
            t = self.restored["total_turns"]
            head = self.restored["head_cum_hash"][:16]
            print(f"{GREEN}[restore] replayed {t} turns "
                  f"(chain OK, {n} entries, head={head}){RESET}")
            last = self.restored["turns"][-1] if self.restored["turns"] else None
            if last and last.get("user"):
                topic = last["user"].splitlines()[0][:60]
                print(f"{DIM}[restore] last topic: {topic!r}  "
                      f"(/recall for more){RESET}")
            print()
        except Exception as e:
            # restore must never crash the boot — degrade to cold start
            print(f"{RED}[restore] error ({e}) — starting cold{RESET}\n")
            self.restored = None

    def recall(self, last_k=5):
        """Answer from replayed ledger (read-only)."""
        if not self.restored or not self.restored.get("turns"):
            print(f"{YELLOW}No replayed memory (cold start or empty ledger).{RESET}\n")
            return
        st = self.restored
        print(f"{CYAN}Replayed memory: {st['total_turns']} turns, "
              f"head={st['head_cum_hash'][:16]}{RESET}")
        last = st["turns"][-1]
        if last.get("user"):
            print(f"  Last topic: {YELLOW}{last['user'].splitlines()[0][:70]!r}{RESET}")
        print(f"  {DIM}Recent turns:{RESET}")
        for tn in st["turns"][-last_k:]:
            u = (tn.get("user") or "")[:55]
            print(f"    turn {tn.get('turn')} [{tn.get('verdict')}] {u!r}")
        print()
    
    def print_welcome(self):
        print(f"{CYAN}{BOLD}═══════════════════════════════════════════════════════════{RESET}")
        print(f"{CYAN}HELEN Interactive CLI Mode{RESET}")
        print(f"{CYAN}{BOLD}═══════════════════════════════════════════════════════════{RESET}")
        print()
        print(f"Available modes:")
        for mode, desc in MODES.items():
            marker = "→" if mode == self.mode else " "
            print(f"  {marker} {YELLOW}{mode:12}{RESET} {desc}")
        print()
        print(f"Commands:")
        print(f"  {YELLOW}/mode <name>{RESET}  - Switch mode (fetch, meteo, wulmoji, shell)")
        print(f"  {YELLOW}/status{RESET}      - Show system status")
        print(f"  {YELLOW}/recall{RESET}      - Show replayed memory (read-only)")
        print(f"  {YELLOW}/help{RESET}        - Show this help")
        print(f"  {YELLOW}/exit{RESET}        - Exit HELEN CLI")
        print()
        print(f"Or just type a message to send to HELEN.")
        print()
    
    def show_status(self):
        print(f"{CYAN}System Status:{RESET}")
        print(f"  Mode: {YELLOW}{self.mode}{RESET}")
        print(f"  Messages sent: {self.message_count}")
        print(f"  Ledger: {LEDGER_PATH}")
        print(f"  Ledger exists: {os.path.exists(LEDGER_PATH)}")
        if os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH) as f:
                lines = len(f.readlines())
            print(f"  Ledger events: {lines}")
        if self.restored:
            print(f"  Replayed turns: {self.restored['total_turns']} "
                  f"(head={self.restored['head_cum_hash'][:16]})")
        else:
            print(f"  Replayed turns: 0 (cold start)")
        print()
    
    def add_meteo_context(self, msg):
        """Add meteorological context to message"""
        try:
            # Try to get weather data (placeholder)
            now = datetime.datetime.now()
            context = f"[METEO: {now.strftime('%A %H:%M')}] {msg}"
            return context
        except:
            return msg
    
    def send_message(self, msg):
        """Send message to HELEN via helen_say.py"""
        if not msg.strip():
            return
        
        # Add context based on mode
        if self.mode == "meteo":
            msg = self.add_meteo_context(msg)
        
        self.message_count += 1
        
        print()
        try:
            result = subprocess.run(
                ["python3", HELEN_SAY_SCRIPT, msg, "--op", self.mode, "--ledger", LEDGER_PATH],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout + result.stderr
            
            # Parse HER and HAL from output
            lines = output.split("\n")
            her_text = ""
            hal_verdict = "?"
            in_her = False
            in_hal = False
            
            for line in lines:
                if "[HER]" in line:
                    in_her = True
                    in_hal = False
                    continue
                if "[HAL]" in line:
                    in_her = False
                    in_hal = True
                    if "PASS" in line:
                        hal_verdict = "PASS"
                    elif "WARN" in line:
                        hal_verdict = "WARN"
                    elif "BLOCK" in line:
                        hal_verdict = "BLOCK"
                    continue
                
                if in_her and line.strip() and not line.startswith("\x1b"):
                    her_text += line + "\n"
            
            # Print formatted output
            print(f"{CYAN}[HER]{RESET}")
            print(her_text.strip())
            print()
            
            # Color verdict
            verdict_color = GREEN if hal_verdict == "PASS" else YELLOW if hal_verdict == "WARN" else RED
            print(f"{MAGENTA}[HAL]{RESET} {verdict_color}{hal_verdict}{RESET}")
            print()
        
        except subprocess.TimeoutExpired:
            print(f"{RED}Error: Request timeout{RESET}")
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")
    
    def run(self):
        """Main CLI loop"""
        while True:
            try:
                prompt = f"{CYAN}[HELEN {self.mode}]{RESET} "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    cmd = user_input.split()[0][1:]
                    
                    if cmd == "mode":
                        parts = user_input.split()
                        if len(parts) > 1:
                            new_mode = parts[1]
                            if new_mode in MODES:
                                self.mode = new_mode
                                print(f"Mode changed to: {YELLOW}{new_mode}{RESET}")
                            else:
                                print(f"{RED}Unknown mode: {new_mode}{RESET}")
                        print()
                    
                    elif cmd == "status":
                        self.show_status()

                    elif cmd == "recall":
                        self.recall()
                    
                    elif cmd == "help":
                        self.print_welcome()
                    
                    elif cmd == "exit":
                        print(f"{CYAN}Goodbye.{RESET}")
                        break
                    
                    else:
                        print(f"{RED}Unknown command: /{cmd}{RESET}")
                    
                    print()
                
                else:
                    # Send as message
                    self.send_message(user_input)
            
            except KeyboardInterrupt:
                print()
                print(f"{CYAN}HELEN CLI closed.{RESET}")
                break
            except EOFError:
                print()
                print(f"{CYAN}HELEN CLI closed.{RESET}")
                break

if __name__ == "__main__":
    cli = HeldenCLI()
    cli.run()
