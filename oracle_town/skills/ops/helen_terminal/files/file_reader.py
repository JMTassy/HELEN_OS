"""
HELEN Terminal — safe file and folder reader.
Read-only. Emits receipts for every inspection.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..receipts.action_receipts import build_receipt

_POLICY_PATH = Path(__file__).resolve().parent.parent / "policy.json"
_POLICY = json.loads(_POLICY_PATH.read_text())
_MAX_BYTES = _POLICY["files"]["max_read_bytes"]
_ALLOWED_EXT = set(_POLICY["files"]["extensions_allowed"])


def _check_ext(path: Path) -> None:
    if path.suffix not in _ALLOWED_EXT and path.suffix != "":
        raise PermissionError(f"Extension {path.suffix!r} not in allowed list")


def inspect_folder(path: str | Path, depth: int = 2) -> dict:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    def _walk(p: Path, d: int) -> dict:
        node: dict = {"name": p.name, "type": "dir", "children": []}
        if d <= 0:
            node["children"] = ["..."]
            return node
        try:
            entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
        except PermissionError:
            node["children"] = ["[permission denied]"]
            return node
        for entry in entries[:50]:
            if entry.is_dir():
                node["children"].append(_walk(entry, d - 1))
            else:
                node["children"].append({"name": entry.name, "type": "file", "size": entry.stat().st_size})
        if len(list(p.iterdir())) > 50:
            node["children"].append({"name": "...", "type": "truncated"})
        return node

    tree = _walk(root, depth)
    artifact = {
        "type": "FOLDER_INSPECTION",
        "path": str(root),
        "tree": tree,
        "content_preview": f"Inspected {root.name} at depth {depth}",
    }
    receipt = build_receipt("INSPECT_FOLDER", {"path": str(root), "depth": depth}, artifact)
    return {"artifact": artifact, "receipt_id": receipt["receipt_id"]}


def read_file(path: str | Path, offset: int = 0, limit: Optional[int] = None) -> dict:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    if not p.is_file():
        raise IsADirectoryError(f"Not a file: {p}")
    _check_ext(p)

    raw = p.read_bytes()
    if len(raw) > _MAX_BYTES:
        raw = raw[:_MAX_BYTES]
        truncated = True
    else:
        truncated = False

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise PermissionError(f"Binary file not readable as text: {p}")

    lines = text.splitlines()
    if limit is not None:
        lines = lines[offset : offset + limit]
    elif offset:
        lines = lines[offset:]
    content = "\n".join(lines)

    artifact = {
        "type": "FILE_READ",
        "path": str(p),
        "lines": len(lines),
        "truncated": truncated,
        "content": content,
        "content_preview": content[:300],
    }
    receipt = build_receipt("READ_FILE", {"path": str(p), "offset": offset, "limit": limit}, artifact)
    return {"artifact": artifact, "receipt_id": receipt["receipt_id"]}
