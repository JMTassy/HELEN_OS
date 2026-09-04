#!/usr/bin/env python3
"""
HELEN Interactive CLI Mode
Persistent command-line dialogue with HELEN.
Supports modes: fetch (default), meteo, wulmoji, shell
"""
import os, sys, json, subprocess, readline, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.helen_readonly_executor import ReadOnlyExecutionRejected, run_readonly

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
        self.print_welcome()
    
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

        if self.mode == "shell" and msg.strip().startswith("run:"):
            self.run_readonly_shell_command(msg.strip()[4:].strip())
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
    
    def run_readonly_shell_command(self, command: str):
        """Run a bounded read-only command through HELEN's executor."""
        if not command:
            print(f"{RED}Rejected: empty read-only command{RESET}")
            print()
            return

        proposal = (
            "COMPUTER_USE_READONLY_EXECUTION — "
            f"ACTION: {command}. "
            "SCOPE: ~/helen-conquest. MUTATION: forbidden. RECEIPT_REQUIRED: yes."
        )

        print()
        print(f"{YELLOW}[PROPOSAL]{RESET} {proposal}")

        try:
            receipt = subprocess.run(
                ["python3", HELEN_SAY_SCRIPT, proposal, "--op", "shell", "--ledger", LEDGER_PATH],
                capture_output=True,
                text=True,
                timeout=10,
            )
            receipt_output = receipt.stdout + receipt.stderr
            print(f"{CYAN}[RECEIPT]{RESET}")
            print(receipt_output.strip())
            print()

            if "[HAL] BLOCK" in receipt_output:
                print(f"{RED}[EXECUTION BLOCKED BY HAL]{RESET}")
                print()
                return

            result = run_readonly(command, cwd=os.getcwd())

            print(f"{GREEN}[READONLY EXECUTION]{RESET} {' '.join(result.command)}")
            print(f"{DIM}returncode={result.returncode}{RESET}")

            if result.stdout:
                print(f"{CYAN}[STDOUT]{RESET}")
                print(result.stdout.rstrip())

            if result.stderr:
                print(f"{YELLOW}[STDERR]{RESET}")
                print(result.stderr.rstrip())

            print()

        except ReadOnlyExecutionRejected as exc:
            print(f"{RED}[REJECTED]{RESET} {exc}")
            print()
        except subprocess.TimeoutExpired:
            print(f"{RED}Error: receipt timeout{RESET}")
            print()
        except Exception as exc:
            print(f"{RED}Error: {exc}{RESET}")
            print()


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
