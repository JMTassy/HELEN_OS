#!/usr/bin/env python3
"""
helen_action_schema.py — action-schema validator + repairer (boundary enforcement).

WHY THIS EXISTS:
  A HELEN runtime emits tool actions as JSON. The model drifts the schema even
  when the correct schema is in its context (observed live: `read_clipboard`
  instead of `get_clipboard`; `text` instead of `content`; `run_command` with
  empty args; `read_file` with `query` instead of `path`). Prose in context does
  not stop this — the doctrine was in context and still drifted.

  The fix is code at the executor boundary: validate every emitted action against
  the canonical schema BEFORE execution. Repair known drift; reject the rest with
  a precise, correctable error. Don't trust the model — enforce the contract.

  This is the tool-layer analog of Gate 8: admission/execution is gated in code,
  not narrated in prose.

USAGE (in any runtime, before executing an emitted action):
    from helen_action_schema import validate_and_repair
    status, action, errors = validate_and_repair(emitted_action)
    if status == "REJECTED":
        # hand `errors` back to the model to correct — do NOT execute
        ...
    else:  # OK or REPAIRED
        execute(action)  # action is the canonical, repaired form

authority: false · this validates/repairs tool actions; it does not admit, write,
or grant authority. Admission remains the operator's act through Gate 8.
"""
from __future__ import annotations

from typing import Any

# Canonical action schemas. Grounded in the observed catalog + observed failures.
# required: args that MUST be present and non-empty.
# optional: args that MAY be present (with defaults applied if absent).
# arg_aliases: wrong-arg-name -> correct-arg-name (auto-repaired).
ACTION_SCHEMAS: dict[str, dict[str, Any]] = {
    "write_file": {
        "required": ["path", "content"],
        "optional": {"append": False},
        "arg_aliases": {"text": "content", "data": "content", "body": "content"},
    },
    "read_file": {
        "required": ["path"],
        "optional": {},
        "arg_aliases": {"file": "path", "filepath": "path"},
    },
    "run_command": {
        "required": ["cmd"],
        "optional": {},
        "arg_aliases": {"command": "cmd", "shell": "cmd"},
    },
    "get_clipboard": {"required": [], "optional": {}, "arg_aliases": {}},
    "set_clipboard": {"required": ["content"], "optional": {},
                      "arg_aliases": {"text": "content"}},
    "web_search": {"required": ["query"], "optional": {"n_results": 5},
                   "arg_aliases": {"q": "query", "search": "query"}},
}

# Wrong-action-name -> correct-action-name (auto-repaired).
ACTION_ALIASES: dict[str, str] = {
    "write": "write_file",
    "writefile": "write_file",
    "read": "read_file",
    "readfile": "read_file",
    "read_clipboard": "get_clipboard",   # observed: not in catalog
    "clipboard": "get_clipboard",
    "command": "run_command",
    "shell": "run_command",
    "exec": "run_command",
    "search": "web_search",
}

# Placeholder values the model emits that are not real targets.
_PLACEHOLDERS = {
    "your_file_path_here", "path", "...", "filename", "command_string",
    "relative_or_absolute_path", "text",
}


def validate_and_repair(action: dict[str, Any]) -> tuple[str, dict[str, Any], list[str]]:
    """
    Validate + repair an emitted action against the canonical schema.

    Returns (status, repaired_action, errors):
      status == "OK"        -> valid as emitted
      status == "REPAIRED"  -> valid after alias/default repair (errors lists fixes)
      status == "REJECTED"  -> cannot execute (errors lists why, for model to correct)
    """
    errors: list[str] = []
    notes: list[str] = []

    if not isinstance(action, dict):
        return "REJECTED", {}, ["action is not an object"]

    name = action.get("action")
    if not name or not isinstance(name, str):
        return "REJECTED", {}, ["missing 'action' name"]

    # Repair action name
    if name not in ACTION_SCHEMAS:
        if name in ACTION_ALIASES:
            notes.append(f"action '{name}' -> '{ACTION_ALIASES[name]}'")
            name = ACTION_ALIASES[name]
        else:
            return "REJECTED", {}, [
                f"unknown action '{name}'. Valid: {sorted(ACTION_SCHEMAS)}"
            ]

    schema = ACTION_SCHEMAS[name]
    args = dict(action.get("args", {}) or {})

    # Repair arg aliases
    for bad, good in schema["arg_aliases"].items():
        if bad in args and good not in args:
            args[good] = args.pop(bad)
            notes.append(f"arg '{bad}' -> '{good}'")

    # Reject unknown args (catches read_file{query})
    allowed = set(schema["required"]) | set(schema["optional"])
    unknown = [k for k in args if k not in allowed]
    if unknown:
        errors.append(
            f"unknown arg(s) {unknown} for '{name}'. "
            f"Expected: required={schema['required']} optional={list(schema['optional'])}"
        )

    # Apply optional defaults
    for k, default in schema["optional"].items():
        if k not in args:
            args[k] = default

    # Check required present + non-empty + not a placeholder
    for r in schema["required"]:
        if r not in args:
            errors.append(f"missing required arg '{r}' for '{name}'")
        elif args[r] in ("", None):
            errors.append(f"required arg '{r}' is empty for '{name}'")
        elif isinstance(args[r], str) and args[r].strip().lower() in _PLACEHOLDERS:
            errors.append(f"arg '{r}' is a placeholder ({args[r]!r}) — resolve real value")

    if errors:
        # surface repairs already applied so the model sees both what was
        # auto-fixed and what it still must correct
        combined = ([f"(auto-repaired: {n})" for n in notes] + errors) if notes else errors
        return "REJECTED", {"action": name, "args": args}, combined

    repaired = {"action": name, "args": args}
    if notes:
        return "REPAIRED", repaired, notes
    return "OK", repaired, []


# --- self-test against the EXACT failures observed in the live terminal log ---
if __name__ == "__main__":
    cases = [
        ("write w/ text (should repair text->content, write->write_file)",
         {"action": "write", "args": {"text": "hello"}}),  # also missing path -> REJECTED
        ("write_file w/ text+path (repair text->content)",
         {"action": "write_file", "args": {"path": "a.txt", "content": None, "text": "hi"}}),
        ("run_command empty (REJECT — missing cmd)",
         {"action": "run_command", "args": {}}),
        ("run_command ok",
         {"action": "run_command", "args": {"cmd": 'find . -name "boot.py"'}}),
        ("read_clipboard (repair -> get_clipboard)",
         {"action": "read_clipboard", "args": {}}),
        ("read_file w/ query (REJECT — unknown arg)",
         {"action": "read_file", "args": {"query": "x"}}),
        ("read_file placeholder path (REJECT)",
         {"action": "read_file", "args": {"path": "YOUR_FILE_PATH_HERE"}}),
        ("write_file valid",
         {"action": "write_file", "args": {"path": "a.txt", "content": "x"}}),
    ]
    print("=" * 64)
    print("ACTION-SCHEMA CANARY  (grounded in observed terminal failures)")
    print("=" * 64)
    for label, a in cases:
        status, repaired, msgs = validate_and_repair(a)
        print(f"\n{label}")
        print(f"  in:     {a}")
        print(f"  status: {status}")
        if msgs:
            print(f"  notes:  {msgs}")
        if status != "REJECTED":
            print(f"  out:    {repaired}")
