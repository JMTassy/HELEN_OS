import hashlib
import json
import numpy as np


def stable_seed_from_payload(payload: dict) -> int:
    """Deterministic SHA-256-derived seed. Replaces Python's salted hash()."""
    s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(s.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def rng_from_seed(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)
