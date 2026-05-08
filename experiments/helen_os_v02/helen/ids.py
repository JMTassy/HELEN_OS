import uuid
from datetime import datetime, timezone


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()
