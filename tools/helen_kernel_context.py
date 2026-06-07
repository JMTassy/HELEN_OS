#!/usr/bin/env python3
"""
helen_kernel_context.py — runtime grounding for HELEN.

WHY THIS EXISTS:
  HELEN-the-model is not HELEN-the-process. Observed live: the model says
  "I cannot access your local filesystem" while the CLI's tool bridge is
  active and read_file/run_command/write_file/web_search are all callable.
  The model also resolves relative paths from the wrong root
  (read_file("boot.py") -> /Users/X/boot.py instead of the actual repo root).

  The kernel exists. It is just not mounted into the model's context as a
  resolvable source. This module builds a KERNEL_CONTEXT block at boot,
  prepends it to the model system prompt, and acts as the single ground
  truth for: repo_root, ledger_path, receipts_path, allowed_actions, the
  tool schema, and the "tool bridge active" fact.

  Companion to TOOL_SCHEMA_DISCIPLINE_V1 (tools/helen_action_schema.py)
  and SESSION_MEMORY_RESTORE_V1 (tools/helen_session_restore.py).

USAGE (in any boot path, after replay-on-boot, before first model turn):
    from helen_kernel_context import build_kernel_context, render_for_system_prompt
    ctx = build_kernel_context(repo_root=Path(__file__).resolve().parent)
    system_prompt = render_for_system_prompt(ctx) + "\n\n" + your_existing_prompt

  Then in the action-dispatch loop, BEFORE execution:
    from helen_action_schema import validate_and_repair
    status, action, errors = validate_and_repair(emitted_action)
    if status == "REJECTED":
        return {"success": False, "error": "; ".join(errors)}  # model corrects, no exec
    execute(action)

authority: false · this provides grounding facts; it does not admit, write,
or grant authority. It refuses to FABRICATE paths (if a file does not exist,
the context records present=False rather than inventing a path).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Catalog of tools the action bridge actually exposes. Must match the
# executor's real surface. Sourced from observed `auto-run` log entries +
# helen_action_schema.ACTION_SCHEMAS keys (read these as canonical).
ALLOWED_ACTIONS_DEFAULT = sorted([
    "read_file",
    "write_file",
    "run_command",
    "get_clipboard",
    "set_clipboard",
    "web_search",
])


def _resolve_or_none(p: Path) -> tuple[str | None, bool]:
    """Return (resolved_absolute_path_or_None, present_flag).

    Refuses to invent: if the path does not exist, returns (str(p), False)
    so the context records the *attempted* path and that it is absent —
    rather than fabricating a working location.
    """
    if p.exists():
        return str(p.resolve()), True
    return str(p), False


def build_kernel_context(
    *,
    repo_root: Path,
    boot_py: Path | None = None,
    cli_py: Path | None = None,
    ledger_relpath: str = "town/ledger_v1.ndjson",
    receipts_reldir: str = "GOVERNANCE",
    allowed_actions: list[str] | None = None,
) -> dict[str, Any]:
    """
    Build the KERNEL_CONTEXT dict. All paths are resolved and existence-checked.

    repo_root MUST be the actual working root (the directory the model should
    resolve relative paths from). If the boot caller does not pass it,
    Path(__file__).resolve().parent is the typical correct value, NOT cwd —
    cwd at boot can be anything (observed: model assumed ~/ as root).
    """
    repo_root = repo_root.resolve()
    boot_py = boot_py or (repo_root / "boot.py")
    cli_py = cli_py or (repo_root / "helen_cli.py")
    ledger_path = repo_root / ledger_relpath
    receipts_dir = repo_root / receipts_reldir

    boot_str, boot_present = _resolve_or_none(boot_py)
    cli_str, cli_present = _resolve_or_none(cli_py)
    ledger_str, ledger_present = _resolve_or_none(ledger_path)
    receipts_str, receipts_present = _resolve_or_none(receipts_dir)

    # Tool schema summary — terse, ground-truth only. Full schemas live in
    # helen_action_schema.ACTION_SCHEMAS; this is the prompt-injectable view.
    tool_schema_summary = {
        "read_file": '{"path": "<absolute or repo-relative>"}',
        "write_file": '{"path": "<...>", "content": "<text>", "append": false}',
        "run_command": '{"cmd": "<shell command string>"}',
        "get_clipboard": "{}",
        "set_clipboard": '{"content": "<text>"}',
        "web_search": '{"query": "<text>", "n_results": 5}',
    }

    return {
        "schema": "KERNEL_CONTEXT_V0",
        "authority": False,
        "claim": "NO_CLAIM",
        "repo_root": str(repo_root),
        "boot_py": boot_str,
        "boot_py_present": boot_present,
        "cli_py": cli_str,
        "cli_py_present": cli_present,
        "ledger_path": ledger_str,
        "ledger_present": ledger_present,
        "receipts_dir": receipts_str,
        "receipts_present": receipts_present,
        "allowed_actions": allowed_actions or list(ALLOWED_ACTIONS_DEFAULT),
        "tool_schema_summary": tool_schema_summary,
        "tool_bridge_active": True,
    }


def render_for_system_prompt(ctx: dict[str, Any]) -> str:
    """
    Render KERNEL_CONTEXT as a system-prompt block.

    Embeds:
      - runtime ground truth (paths)
      - the tool catalog + schemas (prevents schema freeforming)
      - hard rules grounded in observed failures
    """
    actions = ", ".join(ctx["allowed_actions"])
    schemas = "\n".join(f"  {k}: {v}" for k, v in ctx["tool_schema_summary"].items())
    return f"""KERNEL_CONTEXT_V0  (runtime ground truth — authority: false, NO_CLAIM)

repo_root:        {ctx["repo_root"]}
boot_py:          {ctx["boot_py"]}    present={ctx["boot_py_present"]}
cli_py:           {ctx["cli_py"]}     present={ctx["cli_py_present"]}
ledger_path:      {ctx["ledger_path"]}    present={ctx["ledger_present"]}
receipts_dir:     {ctx["receipts_dir"]}    present={ctx["receipts_present"]}
tool_bridge_active: {ctx["tool_bridge_active"]}

ALLOWED ACTIONS (catalogued — no others exist):
  {actions}

TOOL SCHEMAS (use EXACTLY — drift is rejected by the executor):
{schemas}

HARD RULES (grounded in observed runtime failures):
  R1. Relative paths resolve from repo_root, NEVER from $HOME or cwd.
      Wrong: read_file("boot.py") -> $HOME/boot.py
      Right: read_file({ctx["boot_py"]!r})  (use boot_py from this context)
  R2. tool_bridge_active is TRUE. Do not claim "I cannot access the local
      filesystem" — the bridge is live. If a tool call fails, report the
      specific error, do not deny access in general.
  R3. Emit only actions in ALLOWED ACTIONS. read_clipboard is not in the
      catalog; use get_clipboard. The executor rejects unknown actions.
  R4. Use exact arg names: write_file takes "content" (not "text");
      run_command takes "cmd" (not empty args); read_file takes "path"
      (not "query"). The executor validates and rejects drift.
  R5. Do not emit placeholders (e.g. "YOUR_FILE_PATH_HERE", "..."). If
      the target is unknown, run a discovery command first (find/ls/grep)
      and use the result.
  R6. Do not emit write actions unless the operator explicitly asked for
      a write. Reads auto-run; writes queue for /approve.
  R7. Do not narrate "REDUCER admits / LEDGER records" about your own
      output. Admission is the operator's act through the gate, not
      your narration.
"""


# --- self-test against the EXACT grounding failures observed ---
if __name__ == "__main__":
    # Test 1: build context against this tree
    here = Path(__file__).resolve().parents[1]
    ctx = build_kernel_context(repo_root=here)

    print("=" * 64)
    print("KERNEL_CONTEXT canary (grounded in observed runtime failures)")
    print("=" * 64)
    print(json.dumps({k: v for k, v in ctx.items() if k != "tool_schema_summary"},
                     indent=2, default=str))
    print()
    print("--- as system-prompt block ---")
    print(render_for_system_prompt(ctx))
    print()

    # Test 2: refuses to fabricate when files are absent
    print("=" * 64)
    print("FABRICATION REFUSAL (point at empty dir)")
    print("=" * 64)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        empty = Path(td)
        ctx2 = build_kernel_context(repo_root=empty)
        print(f"repo_root={ctx2['repo_root']}")
        print(f"boot_py={ctx2['boot_py']!r}  present={ctx2['boot_py_present']}")
        print(f"ledger_path={ctx2['ledger_path']!r}  present={ctx2['ledger_present']}")
        print(">>> paths are recorded with present=False; not fabricated.")
