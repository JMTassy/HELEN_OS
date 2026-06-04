#!/usr/bin/env python3
"""
boot_orchestrator.py — HELEN OS Boot Orchestrator
══════════════════════════════════════════════════
Ordered startup and shutdown of HELEN OS subsystems.

Boot order (invariant):
  1. Kernel     (required)
  2. Memory     (required)
  3. HAL        (graceful skip if unavailable)
  4. HERMES/API (graceful skip)
  5. AIRI       (optional, skip if not installed)
  6. TEMPLE     (optional, only if --temple flag)

Authority separation is preserved: Kernel starts first.
BootOrchestrator does NOT write to ledger directly.
"""

import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

# Terminal colours
R = "\033[0m"
B = "\033[1m"
C = "\033[36m"
Y = "\033[33m"
G = "\033[32m"
D = "\033[90m"
M = "\033[35m"


@dataclass
class BootStep:
    name: str
    fn: Callable[[], tuple[bool, str]]
    required: bool
    label: str


class BootOrchestrator:
    """
    Starts HELEN OS in strict order.
    Invariant: authority separation preserved across all steps.
    Kernel starts first. Everything else is optional surface.
    """

    def __init__(
        self,
        registry,
        approval_queue,
        ledger_path: str = None,
        with_temple: bool = False,
        with_airi: bool = False,
    ):
        self.registry = registry
        self.queue = approval_queue
        self.ledger_path = ledger_path or str(Path.home() / ".helen" / "ledger_v1.ndjson")
        self.with_temple = with_temple
        self.with_airi = with_airi
        self.spine = None           # MemorySpine (set during boot)
        self.librarian = None       # HELENLibrarian (set during boot)
        self.renderer = None        # InitRenderer (set during boot)
        self._api_process = None    # subprocess for helen_api.py

    # ── Main entry points ─────────────────────────────────────────────────────

    def start(self) -> bool:
        """Run all boot steps in order. Returns True if kernel+memory started."""
        steps = self._build_steps()
        total = len(steps)
        all_ok = True

        for idx, step in enumerate(steps, start=1):
            label = f"[{idx}/{total}] {step.label:<22}"
            try:
                ok, detail = step.fn()
            except Exception as exc:
                ok = False
                detail = str(exc)

            if ok:
                print(f"{label}{G}✓{R}  {D}{detail}{R}")
            else:
                if step.required:
                    print(f"{label}{Y}✗{R}  {Y}FAILED: {detail}{R}")
                    all_ok = False
                    # Mark remaining steps as skipped
                    remaining = steps[idx:]
                    for rs in remaining:
                        self.registry.mark_skipped(rs.name, "aborted (required step failed)")
                    break
                else:
                    print(f"{label}{D}✗{R}  {D}skipped ({detail}){R}")

        # Build renderer after boot (uses whatever was initialised)
        self._build_renderer()
        return all_ok

    def stop(self) -> None:
        """Graceful shutdown in reverse order."""
        running = [
            name for name in reversed(["kernel", "memory", "hal", "hermes", "airi", "temple"])
            if self.registry.is_running(name)
        ]
        for name in running:
            if name == "hermes" and self._api_process is not None:
                try:
                    self._api_process.terminate()
                    self._api_process.wait(timeout=5)
                except Exception:
                    pass
                self._api_process = None
            self.registry.mark_stopped(name, "shutdown")
            print(f"{D}[stop] {name}{R}")

    def get_renderer(self):
        return self.renderer

    # ── Boot steps ────────────────────────────────────────────────────────────

    def _step_kernel(self) -> tuple[bool, str]:
        """Initialise MemorySpine (kernel + ledger replay)."""
        try:
            from helen_memory_spine import MemorySpine

            # Ensure ledger directory exists
            ledger_path = Path(self.ledger_path)
            ledger_path.parent.mkdir(parents=True, exist_ok=True)

            self.spine = MemorySpine(ledger_path=str(ledger_path))
            boot_state = self.spine.boot()

            seq = boot_state.get("session_count", 0)
            ledger_hash = boot_state.get("ledger_hash", "0" * 64)[:8]
            detail = f"replayed {seq} sessions, hash={ledger_hash}"
            self.registry.mark_running("kernel", detail=detail)
            return True, detail
        except Exception as exc:
            self.registry.mark_error("kernel", str(exc))
            return False, str(exc)

    def _step_memory(self) -> tuple[bool, str]:
        """Initialise HELENLibrarian and ingest recent chat sessions."""
        try:
            from helen_librarian import HELENLibrarian

            self.librarian = HELENLibrarian()

            # Try to ingest helen_chat.ndjson if it exists
            chat_file = Path(__file__).parent / "helen_chat.ndjson"
            ingested = 0
            if chat_file.exists():
                try:
                    # Boot must never hang. add() dedup is O(n) per turn (keyword
                    # fallback since nomic-embed-text isn't pulled), so an unbounded
                    # ingest of a long chat log against a large DB stalls boot at
                    # [2/4]. Bound it to a 3s budget (newest turns first).
                    ingested = self.librarian.ingest_session(chat_file, max_seconds=3.0)
                except Exception:
                    pass

            status = self.librarian.status()
            drawers = status.get("total_drawers", 0)
            entities = status.get("registry", {}).get("entities", 0)
            detail = f"{drawers} drawers, {entities} entities"
            if ingested:
                detail += f" (+{ingested} new, time-bounded)"
            self.registry.mark_running("memory", detail=detail)
            return True, detail
        except Exception as exc:
            self.registry.mark_error("memory", str(exc))
            return False, str(exc)

    def _step_hal(self) -> tuple[bool, str]:
        """HAL = execution gate — approval_queue is the HAL surface in v0."""
        try:
            pending = self.queue.count_pending()
            detail = f"gated via approval_queue ({pending} pending)"
            self.registry.mark_running("hal", detail=detail)
            return True, "gated via approval_queue"
        except Exception as exc:
            self.registry.mark_error("hal", str(exc))
            return False, str(exc)

    def _step_hermes(self) -> tuple[bool, str]:
        """Start helen_api.py as subprocess on port 8765."""
        api_script = Path(__file__).parent / "helen_api.py"
        if not api_script.exists():
            self.registry.mark_skipped("hermes", "helen_api.py not found")
            return False, "helen_api.py not found"

        # Check if port is already in use
        if self._check_port(8765):
            self.registry.mark_running("hermes", port=8765, detail="already running on :8765")
            return True, "already running on :8765"

        try:
            proc = subprocess.Popen(
                [sys.executable, str(api_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._api_process = proc

            # Wait up to 4s for /api/health to respond
            deadline = time.time() + 4.0
            while time.time() < deadline:
                if self._check_port(8765):
                    self.registry.mark_running("hermes", port=8765, pid=proc.pid,
                                               detail="chat/API on :8765")
                    return True, f"chat/API on :8765 (pid={proc.pid})"
                time.sleep(0.25)

            # Didn't come up in time — kill and skip
            try:
                proc.terminate()
            except Exception:
                pass
            self._api_process = None
            self.registry.mark_skipped("hermes", "API failed to start within 4s")
            return False, "API failed to start within 4s"

        except Exception as exc:
            self.registry.mark_skipped("hermes", str(exc))
            return False, str(exc)

    def _step_airi(self) -> tuple[bool, str]:
        """AIRI presence layer — not yet integrated."""
        self.registry.mark_skipped("airi", "not yet integrated")
        return False, "not yet integrated"

    def _step_temple(self) -> tuple[bool, str]:
        """TEMPLE deliberation — output goes to ApprovalQueue, NOT kernel."""
        if not self.with_temple:
            self.registry.mark_skipped("temple", "not requested")
            return False, "not requested"
        try:
            # Verify temple.py is importable
            import importlib.util
            spec = importlib.util.find_spec("temple")
            if spec is None:
                temple_path = Path(__file__).parent / "temple.py"
                if not temple_path.exists():
                    raise ImportError("temple.py not found")
            self.registry.mark_running("temple", detail="deliberation-only mode")
            return True, "deliberation-only mode"
        except Exception as exc:
            self.registry.mark_skipped("temple", str(exc))
            return False, str(exc)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _check_ollama(self) -> bool:
        """Returns True if Ollama is reachable."""
        try:
            with urllib.request.urlopen(
                "http://localhost:11434/api/tags", timeout=2
            ) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _check_port(self, port: int) -> bool:
        """Returns True if something is listening on the given port (localhost)."""
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/api/health", timeout=1
            ) as resp:
                return resp.status in (200, 204)
        except urllib.error.HTTPError as e:
            # Any HTTP response means the server is up
            return True
        except Exception:
            return False

    def _build_renderer(self) -> None:
        """Build InitRenderer with whatever was initialised."""
        try:
            from init_renderer import InitRenderer
            self.renderer = InitRenderer(
                memory_spine=self.spine,
                librarian=self.librarian,
                approval_queue=self.queue,
            )
        except Exception:
            self.renderer = None

    def _build_steps(self) -> list[BootStep]:
        steps = [
            BootStep("kernel",  self._step_kernel,  required=True,  label="Kernel"),
            BootStep("memory",  self._step_memory,  required=True,  label="Memory spine"),
            BootStep("hal",     self._step_hal,     required=False, label="HAL (execution gate)"),
            BootStep("hermes",  self._step_hermes,  required=False, label="HERMES (chat/API)"),
        ]
        if self.with_airi:
            steps.append(BootStep("airi", self._step_airi, required=False, label="AIRI (presence)"))
        if self.with_temple:
            steps.append(BootStep("temple", self._step_temple, required=False, label="TEMPLE (deliberation)"))
        return steps
