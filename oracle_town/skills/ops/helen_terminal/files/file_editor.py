"""
HELEN Terminal — proposal-then-confirm file editor.
Edits are NEVER applied without explicit operator confirmation.
Every proposed and applied edit emits a receipt.
"""
from __future__ import annotations

import difflib
import json
import uuid
from pathlib import Path

from ..receipts.action_receipts import build_receipt

_PENDING_DIR = Path(__file__).resolve().parent.parent / "data" / "pending_edits"
_POLICY_PATH = Path(__file__).resolve().parent.parent / "policy.json"
_POLICY = json.loads(_POLICY_PATH.read_text())
_ALLOWED_EXT = set(_POLICY["files"]["extensions_allowed"])

_FORBIDDEN_OPS = {"rm", "unlink", "rmdir", "rename", "move"}


def _check_ext(path: Path) -> None:
    if path.suffix not in _ALLOWED_EXT and path.suffix != "":
        raise PermissionError(f"Extension {path.suffix!r} not in allowed list for editing")


def propose_edit(path: str | Path, old_string: str, new_string: str, reason: str = "") -> dict:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    _check_ext(p)

    current = p.read_text(encoding="utf-8")
    if old_string not in current:
        raise ValueError(f"old_string not found in {p.name}")

    proposed = current.replace(old_string, new_string, 1)
    diff = list(difflib.unified_diff(
        current.splitlines(keepends=True),
        proposed.splitlines(keepends=True),
        fromfile=f"{p.name} (current)",
        tofile=f"{p.name} (proposed)",
    ))

    proposal_id = "EP-" + uuid.uuid4().hex[:12]
    proposal = {
        "proposal_id": proposal_id,
        "path": str(p),
        "old_string": old_string[:200],
        "new_string": new_string[:200],
        "reason": reason,
        "diff_preview": "".join(diff[:30]),
        "status": "PENDING_CONFIRM",
        "authority": "NON_SOVEREIGN",
    }

    _PENDING_DIR.mkdir(parents=True, exist_ok=True)
    (_PENDING_DIR / f"{proposal_id}.json").write_text(json.dumps(proposal, indent=2))

    artifact = {
        "type": "EDIT_PROPOSAL",
        "proposal_id": proposal_id,
        "path": str(p),
        "diff_lines": len(diff),
        "content_preview": proposal["diff_preview"],
    }
    receipt = build_receipt("PROPOSE_EDIT", {"path": str(p), "proposal_id": proposal_id}, artifact)

    return {
        "proposal_id": proposal_id,
        "diff": "".join(diff),
        "receipt_id": receipt["receipt_id"],
        "status": "PENDING_CONFIRM",
        "confirm_command": f"helen-terminal confirm {proposal_id}",
    }


def confirm_edit(proposal_id: str) -> dict:
    proposal_path = _PENDING_DIR / f"{proposal_id}.json"
    if not proposal_path.exists():
        raise FileNotFoundError(f"Proposal {proposal_id} not found or already applied")

    proposal = json.loads(proposal_path.read_text())
    if proposal["status"] != "PENDING_CONFIRM":
        raise ValueError(f"Proposal {proposal_id} is not in PENDING_CONFIRM state")

    p = Path(proposal["path"])
    current = p.read_text(encoding="utf-8")
    updated = current.replace(proposal["old_string"], proposal["new_string"], 1)
    p.write_text(updated, encoding="utf-8")

    proposal["status"] = "APPLIED"
    proposal_path.write_text(json.dumps(proposal, indent=2))

    artifact = {
        "type": "EDIT_APPLIED",
        "proposal_id": proposal_id,
        "path": str(p),
        "content_preview": f"Edit applied to {p.name}",
    }
    receipt = build_receipt("APPLY_EDIT", {"path": str(p), "proposal_id": proposal_id}, artifact)
    return {"proposal_id": proposal_id, "status": "APPLIED", "receipt_id": receipt["receipt_id"]}


def reject_edit(proposal_id: str) -> dict:
    proposal_path = _PENDING_DIR / f"{proposal_id}.json"
    if not proposal_path.exists():
        raise FileNotFoundError(f"Proposal {proposal_id} not found")
    proposal = json.loads(proposal_path.read_text())
    proposal["status"] = "REJECTED"
    proposal_path.write_text(json.dumps(proposal, indent=2))
    artifact = {"type": "EDIT_REJECTED", "proposal_id": proposal_id, "content_preview": "Edit rejected by operator"}
    receipt = build_receipt("REJECT_EDIT", {"proposal_id": proposal_id}, artifact)
    return {"proposal_id": proposal_id, "status": "REJECTED", "receipt_id": receipt["receipt_id"]}
