"""
helen_action_bridge.py — the missing wire between HELEN's brain and her hands.

The chat loop (helen_cli.py::_chat_via_boot) was conversation-only: it called the
LLM and printed the reply, but never parsed the reply for an action, never
dispatched to a skill, never populated the approval queue. So HELEN could *talk*
about CLAW/HAL/tools but could not touch the machine. This module is the agentic
step that closes that gap.

Flow:  reply → extract_action() → classify_kind() →
          READ  : run now, feed result back (bounded auto-loop)
          WRITE : approval_queue.enqueue() → operator /approve → run

Governance posture (operator decision 2026-06-03): "auto-run read-only, gate writes."
Read-only actions execute immediately. Anything that mutates the machine or the
outside world is queued and waits for an explicit /approve. No action runs that
is not in ACTION_SPECS — the model cannot invent a capability.

Non-sovereign. Authority always false. This bridge proposes and executes
operator-gated effects; it does not issue verdicts and never writes a ledger.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional, Tuple

# ── Action catalogue ────────────────────────────────────────────────────────
# kind: "read" (auto-run) | "write" (queue for /approve)
# source: "skill" (helen_skills.SkillRegistry) | "computer" (helen_computer_skill)
# Only names listed here are reachable. Unknown names are rejected, never run.
ACTION_SPECS: Dict[str, Dict[str, str]] = {
    # — system / files —  (arg names match helen_skills signatures exactly)
    "run_command":   {"kind": "write", "source": "skill",    "help": "run a shell command (args: cmd, timeout?)"},
    "read_file":     {"kind": "read",  "source": "skill",    "help": "read a text file (args: path)"},
    "write_file":    {"kind": "write", "source": "skill",    "help": "write a text file (args: path, content, append?)"},
    # — mail / calendar —
    "read_emails":   {"kind": "read",  "source": "skill",    "help": "read recent emails (args: n)"},
    "search_emails": {"kind": "read",  "source": "skill",    "help": "search emails (args: query)"},
    "draft_email":   {"kind": "write", "source": "skill",    "help": "draft an email (args: to, subject, body)"},
    "list_events":   {"kind": "read",  "source": "skill",    "help": "list calendar events (args: days)"},
    "create_event":  {"kind": "write", "source": "skill",    "help": "create a calendar event (args: title, date, duration)"},
    "find_free_time":{"kind": "read",  "source": "skill",    "help": "find free slots (args: date)"},
    # — web —
    "web_search":    {"kind": "read",  "source": "skill",    "help": "search the web (args: query, n_results?)"},
    "fetch_url":     {"kind": "read",  "source": "skill",    "help": "fetch a URL (args: url, max_bytes?)"},
    # — conquest —
    "game_state":    {"kind": "read",  "source": "skill",    "help": "read game state (no args)"},
    "roll_dice":     {"kind": "read",  "source": "skill",    "help": "roll dice (args: sides, n, seed?)"},
    # — computer use (GUI / desktop) —
    "screenshot":       {"kind": "read",  "source": "computer", "help": "capture the screen (args: save_path?)"},
    "get_screen_size":  {"kind": "read",  "source": "computer", "help": "screen dimensions"},
    "get_frontmost_app":{"kind": "read",  "source": "computer", "help": "name of the focused app"},
    "get_clipboard":    {"kind": "read",  "source": "computer", "help": "read the clipboard"},
    "set_clipboard":    {"kind": "write", "source": "computer", "help": "set the clipboard (args: text)"},
    "open_app":         {"kind": "write", "source": "computer", "help": "open a macOS app (args: app_name)"},
    "click":            {"kind": "write", "source": "computer", "help": "click at a point (args: x, y, button?)"},
    "double_click":     {"kind": "write", "source": "computer", "help": "double-click (args: x, y)"},
    "right_click":      {"kind": "write", "source": "computer", "help": "right-click (args: x, y)"},
    "type_text":        {"kind": "write", "source": "computer", "help": "type text (args: text)"},
    "press_key":        {"kind": "write", "source": "computer", "help": "press key combo (args: keys list)"},
    "scroll":           {"kind": "write", "source": "computer", "help": "scroll (args: x, y, clicks)"},
    "move_mouse":       {"kind": "write", "source": "computer", "help": "move the mouse (args: x, y)"},
    # — named loops (local non-sovereign executors; emit receipts) —
    "egregor":      {"kind": "write", "source": "engine", "help": "run EGREGOR coding pipeline ARCHITECT->CODER->REVIEWER->TESTER (args: task, rounds?)"},
    "autoresearch": {"kind": "write", "source": "engine", "help": "run bounded PULL-mode AUTORESEARCH, one hypothesis/epoch (args: topic, epochs?)"},
    "ralph":        {"kind": "write", "source": "engine", "help": "run bounded RALPH loop TEMPLE->HAL->REDUCER per epoch (args: story, epochs?)"},
}

ACTION_MARKER = "HELEN_ACTION:"
MAX_AUTO_STEPS = 4  # ceiling on chained read-actions per user turn (runaway guard)

# Small models emit sloppy action names. Map common shorthands to the real action
# so they run instead of erroring with "unknown action".
_ALIASES = {
    "read": "read_file", "readfile": "read_file", "cat": "read_file",
    "write": "write_file", "writefile": "write_file",
    "run": "run_command", "command": "run_command", "shell": "run_command",
    "exec": "run_command", "bash": "run_command", "sh": "run_command",
    "search": "web_search", "google": "web_search",
    "fetch": "fetch_url", "open": "open_app", "shot": "screenshot",
}
# Names that mean "do nothing" — treat as no action, not an error.
_NOOP = {"none", "noop", "no_action", "noaction", "null", "nil", "wait",
         "await", "ask", "clarify", "respond", "reply", "answer"}


def normalize_action_name(name: str):
    """Return the canonical action name, or None if it means 'no action'."""
    key = str(name).strip().lower()
    if key in _NOOP:
        return None
    return _ALIASES.get(key, name)

# Lazily-built skill registry (built once on first use).
_registry = None


def _skills():
    global _registry
    if _registry is None:
        from helen_skills import build_registry
        _registry = build_registry()
    return _registry


# ── System prompt fragment (tells the model it now has hands) ────────────────
def action_protocol_prompt() -> str:
    lines = [
        "",
        "## EXECUTION SURFACE (you now have hands)",
        "You are wired to a live action bridge. You no longer only *describe* what",
        "you could do — you can act. When the user asks you to inspect, run, open,",
        "search, read, or operate the machine, DO NOT explain that you lack tools.",
        "Instead emit exactly ONE action as the LAST line of your reply:",
        "",
        f"    {ACTION_MARKER} {{\"action\": \"<name>\", \"args\": {{...}}}}",
        "",
        "Rules:",
        "- Emit at most one action per reply. Keep any prose before it short.",
        "- READ actions run immediately; their result is fed back to you so you can",
        "  continue. WRITE actions are queued and run only after the operator types",
        "  /approve — so for writes, state what you will do, then emit the action.",
        "- Use only the actions below. Do not invent capabilities or fake results.",
        "- Act ONLY on the operator's explicit intent. Do NOT invent speculative",
        "  actions (e.g. creating config files, initializing directories) that were",
        "  not requested. Doing nothing is valid.",
        "- If the input is unclear, a typo, or empty, ASK a short question — do not",
        "  emit an action and do not narrate a multi-gate refusal.",
        "- The operator types /approve themselves. Never write '/approve ...' in your",
        "  reply expecting it to run — it will not.",
        "",
        "Available actions:",
    ]
    for name, spec in ACTION_SPECS.items():
        tag = "read " if spec["kind"] == "read" else "write"
        lines.append(f"  [{tag}] {name} — {spec['help']}")
    lines.extend([
        "",
        "## YOUR NAMED LOOPS (you can run these — they are real, local, non-sovereign)",
        "- EGREGOR: your multi-agent coding pipeline (ARCHITECT → CODER → REVIEWER →",
        "  TESTER). Use the `egregor` action when asked to build or implement something.",
        "- AUTORESEARCH: your bounded PULL-mode research loop — one observable, falsifiable",
        "  hypothesis per epoch, 7-field receipt, no kernel/schema/ledger mutation. Use the",
        "  `autoresearch` action to investigate a topic across epochs.",
        "- RALPH: your bounded epoch loop — TEMPLE proposes, HAL gates, REDUCER keeps or",
        "  rejects, one story per epoch. Use the `ralph` action to drive a story forward.",
        "Each emits a receipt to ~/.helen/receipts/. Authority stays false — they record,",
        "they do not rule. They are gated writes: you propose, the operator /approves.",
        "",
    ])
    return "\n".join(lines)


# ── Parsing ──────────────────────────────────────────────────────────────────
def extract_action(reply: str) -> Optional[Dict[str, Any]]:
    """Return {'action': str, 'args': dict} from the model reply, or None.

    Tolerant: finds the last HELEN_ACTION: marker and brace-matches the JSON
    object that follows it, even if the model wrapped it in a code fence.
    """
    idx = reply.rfind(ACTION_MARKER)
    if idx == -1:
        return None
    rest = reply[idx + len(ACTION_MARKER):]
    start = rest.find("{")
    if start == -1:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(rest)):
        ch = rest[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                blob = rest[start:i + 1]
                try:
                    obj = json.loads(blob)
                except json.JSONDecodeError:
                    return None
                if not isinstance(obj, dict) or "action" not in obj:
                    return None
                canonical = normalize_action_name(obj["action"])
                if canonical is None:   # no-op name → treat as "no action"
                    return None
                obj.setdefault("args", {})
                if not isinstance(obj["args"], dict):
                    return None
                return {"action": str(canonical), "args": obj["args"]}
    return None


def classify_kind(action_name: str) -> Optional[str]:
    spec = ACTION_SPECS.get(action_name)
    return spec["kind"] if spec else None


def _receipt_id(payload: dict, result_text: str) -> str:
    blob = json.dumps(payload, sort_keys=True) + "\n" + result_text
    return "sha256:" + hashlib.sha256(blob.encode()).hexdigest()[:16]


# ── Execution ─────────────────────────────────────────────────────────────────
def execute_action(action: Dict[str, Any]) -> Tuple[bool, str]:
    """Run an action and return (ok, result_text). Caller decides gating."""
    name = action.get("action", "")
    args = action.get("args", {}) or {}
    spec = ACTION_SPECS.get(name)
    if spec is None:
        return False, f"unknown action: {name!r} (not in catalogue)"
    try:
        if spec["source"] == "skill":
            res = _skills().call(name, **args)
            ok = bool(res.get("success", False)) if isinstance(res, dict) else True
            text = json.dumps(res, ensure_ascii=False, default=str)[:4000]
            return ok, text
        elif spec["source"] == "engine":
            import helen_engines as eng
            res = eng.run_engine(name, **args)
            ok = bool(res.get("success", False))
            text = json.dumps(res, ensure_ascii=False, default=str)[:4000]
            return ok, text
        else:  # computer
            import helen_computer_skill as cs
            fn = getattr(cs, name, None)
            if fn is None:
                return False, f"computer skill {name!r} not found"
            out = fn(**args)
            return True, _stringify(out)[:4000]
    except TypeError as exc:
        return False, f"bad args for {name}: {exc}"
    except Exception as exc:  # never let an action crash the chat loop
        return False, f"{type(exc).__name__}: {exc}"


def _stringify(out: Any) -> str:
    if isinstance(out, tuple):
        return " | ".join(_stringify(x) for x in out)
    if isinstance(out, (dict, list)):
        return json.dumps(out, ensure_ascii=False, default=str)
    return str(out)


def queue_write(action: Dict[str, Any], queue) -> str:
    """Enqueue a write action for operator approval. Returns the approval id."""
    payload = {"kind": "action", "action": action["action"], "args": action.get("args", {})}
    appr = queue.enqueue(type="action", payload=payload, proposer="helen")
    return appr.id


def execute_approved(payload: dict) -> Tuple[bool, str, str]:
    """Run a previously-queued action from its approval payload.

    Returns (ok, result_text, receipt_id).
    """
    action = {"action": payload.get("action"), "args": payload.get("args", {})}
    ok, text = execute_action(action)
    return ok, text, _receipt_id(payload, text)
