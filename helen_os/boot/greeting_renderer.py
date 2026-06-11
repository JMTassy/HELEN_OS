"""greeting_renderer.py — render boot greeting from RUNTIME_BOOT_CONTEXT_V1.

Law: reads ONLY RuntimeBootContext. No provider memory. No improvisation.
Graceful degradation: missing field → null-honest placeholder, never fiction.
"""
from __future__ import annotations
from .runtime_boot_context import RuntimeBootContext


def render_greeting(ctx: RuntimeBootContext) -> str:
    """Render greeting string from boot context. Null-honest on missing data."""
    if ctx.is_empty():
        return "HELEN: No prior context. Starting fresh."

    parts: list[str] = ["HELEN:"]

    name = ctx.person_name()
    if name:
        parts.append(f"Welcome back, {name}.")
    else:
        parts.append("Session resumed.")

    epoch_id = ctx.last_epoch_id()
    if epoch_id:
        parts.append(f"Last epoch: {epoch_id}.")
    else:
        parts.append("Epoch: unavailable.")

    if ctx.last_session:
        session_id = ctx.last_session.get("session_id")
        if session_id:
            parts.append(f"Last session: {session_id}.")

    parts.append(f"[loaded_from={ctx.loaded_from}]")
    return " ".join(parts)
