"""
/init HELEN — Cold boot state recovery

Single deterministic output:
  - identity
  - top_3_threads
  - unresolved_tensions
  - recent_movement
  - next_action

NO prose. NO decoration. NO parallel logic.
"""

import json
from datetime import datetime
from typing import TypedDict


class InitOutput(TypedDict):
    """Frozen schema for /init response."""
    identity: str
    top_3_threads: list[str]
    unresolved_tensions: list[str]
    recent_movement: str
    next_action: str


def init_helen(corpus: dict, epoch_state: dict, boot_context: dict) -> InitOutput:
    """
    Cold-boot HELEN state from corpus.

    Args:
        corpus: Full weighted_corpus (laws, districts, projects, threads, topics)
        epoch_state: Last replay state (skill_library_state_v1)
        boot_context: Boot metadata (timestamp, session_id, etc.)

    Returns:
        InitOutput: 5 fields, deterministic, no hallucination.
    """

    # 1. Identity: from corpus canon + epoch_state
    identity = _synthesize_identity(corpus, epoch_state)

    # 2. Top 3 threads: by salience + unresolved status
    top_3 = _top_threads(corpus, n=3)

    # 3. Unresolved tensions: explicit corpus field
    tensions = _extract_tensions(corpus)

    # 4. Recent movement: delta from corpus timestamps
    movement = _recent_delta(corpus, boot_context)

    # 5. Next action: from skills output + corpus weight
    next_act = _propose_action(corpus, epoch_state)

    return InitOutput(
        identity=identity,
        top_3_threads=top_3,
        unresolved_tensions=tensions,
        recent_movement=movement,
        next_action=next_act
    )


def _synthesize_identity(corpus: dict, epoch_state: dict) -> str:
    """
    One-sentence identity from:
      - canon personality (from corpus metadata)
      - current epoch skills (from epoch_state)
      - authority status (from corpus.authority)

    NO hallucination. Trace every claim.
    """
    # Read from corpus
    canon_name = corpus.get("metadata", {}).get("name", "HELEN")
    canon_role = corpus.get("metadata", {}).get("role", "governance agent")
    canon_authority = corpus.get("metadata", {}).get("authority", "NONE")

    # Read from epoch state
    active_skills = epoch_state.get("skill_library_state_v1", {}).get("active_skills", {})
    skill_count = len(active_skills)

    # One sentence
    return f"{canon_name}: {canon_role} (authority={canon_authority}, {skill_count} active skills)"


def _top_threads(corpus: dict, n: int = 3) -> list[str]:
    """
    Top N threads by:
      1. unresolved status (exclude resolved/closed)
      2. salience score
      3. recent activity

    Return thread IDs only, no prose.

    CRITICAL: Resolved/closed threads MUST be excluded.
    """
    threads = corpus.get("threads", {})

    scored = []
    for thread_id, thread_obj in threads.items():
        status = thread_obj.get("status", "")
        salience = thread_obj.get("salience", 0)
        last_updated = thread_obj.get("last_updated", "")

        # SKIP resolved/closed threads
        if status in ("resolved", "closed"):
            continue

        # Score: unresolved threads first, then by salience
        is_unresolved = 1 if status == "unresolved" else 0
        score = (is_unresolved * 1000) + salience

        scored.append((thread_id, score, last_updated))

    # Sort by score descending; use last_updated as tiebreaker (newer first).
    # Empty/missing last_updated ("") sorts last under reverse=True — safe fallback.
    scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return [tid for tid, *_ in scored[:n]]


def _extract_tensions(corpus: dict) -> list[str]:
    """
    Unresolved tensions from corpus.

    Source: corpus.tensions (explicit, curated).
    Filter: status == "unresolved" only.
    Return: List of tension descriptions.
    """
    tensions = corpus.get("tensions", {})

    unresolved = []
    for tension_id, tension_obj in tensions.items():
        if tension_obj.get("status") == "unresolved":
            # Get human-readable description
            desc = tension_obj.get("description", tension_id)
            unresolved.append(desc)

    return unresolved


def _recent_delta(corpus: dict, boot_context: dict) -> str:
    """
    Recent movement: what changed since last boot?

    Compare:
      - last boot timestamp (from boot_context)
      - corpus recent_events

    Return: one summary line.
    """
    last_boot = boot_context.get("last_boot_timestamp", None)
    from datetime import timezone
    current_time = datetime.now(timezone.utc).isoformat()

    recent_events = corpus.get("recent_events", [])

    # Filter events newer than last boot
    if last_boot:
        newer = [e for e in recent_events if e.get("timestamp", "") > last_boot]
    else:
        newer = recent_events[:3]  # No prior boot, take 3 most recent

    if not newer:
        return "No recent changes since last boot."

    # Summarize
    event_types = [e.get("type", "unknown") for e in newer]
    return f"Recent: {', '.join(event_types)}"


def _propose_action(corpus: dict, epoch_state: dict) -> str:
    """
    Next action: from corpus + epoch state.

    Priority:
      1. Unresolved tension with highest weight
      2. Unresolved (active) thread needing continuation
      3. Await user input

    CRITICAL: Only suggest unresolved threads (exclude resolved/closed).

    Return: One actionable sentence.
    """
    # Get highest-weight unresolved tension
    tensions = corpus.get("tensions", {})
    unresolved_weights = [
        (tid, t.get("weight", 0))
        for tid, t in tensions.items()
        if t.get("status") == "unresolved"
    ]

    if unresolved_weights:
        top_tension = max(unresolved_weights, key=lambda x: x[1])
        tension_id, weight = top_tension
        return f"Address tension: {tension_id} (weight={weight})"

    # Fallback: continue unresolved thread with highest salience
    threads = corpus.get("threads", {})
    unresolved_threads = [
        tid for tid, t in threads.items()
        if t.get("status") not in ("resolved", "closed")
    ]
    if unresolved_threads:
        # Prefer highest salience
        best = max(unresolved_threads, key=lambda tid: threads[tid].get("salience", 0))
        return f"Continue thread: {best}"

    # Fallback: generic
    return "Await user input."


def init_to_json(output: InitOutput) -> str:
    """
    Serialize InitOutput to JSON, deterministically.

    Used for:
      - API response
      - Replay verification (bit-for-bit comparison)
    """
    return json.dumps(
        output,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=True
    )


# FastAPI endpoint — optional; core functions remain importable without fastapi installed
try:
    from fastapi import FastAPI

    app = FastAPI()

    @app.post("/init")
    async def api_init_helen(boot_ctx: dict):
        """
        POST /init with boot_context → returns deterministic state.

        Idempotent: same boot_context → same response (bit-for-bit).
        """
        corpus = load_corpus()
        epoch_state = load_epoch_state()
        output = init_helen(corpus, epoch_state, boot_ctx)
        return json.loads(init_to_json(output))

except ImportError:
    app = None


def load_corpus() -> dict:
    """Stub: load actual corpus from helen_knowledge_registry.json"""
    import json
    try:
        with open("helen_os/corpus/helen_knowledge_registry.json") as f:
            return json.load(f)
    except:
        return {}


def load_epoch_state() -> dict:
    """Stub: load actual epoch state from ledger replay."""
    import json
    try:
        with open("helen_os/state/epoch_state.json") as f:
            return json.load(f)
    except:
        return {}
