from helen.schemas import Intent


def route(intent: Intent) -> str:
    text = intent["text"].lower()
    if "repo" in text or "status" in text or "folder" in text:
        return "INSPECT"
    if "memory" in text or "remember" in text:
        return "MEMORY_LOOKUP"
    if "gate" in text or "claim" in text:
        return "ORACLE_GATE"
    return "THINK"
