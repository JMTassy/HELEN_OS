#!/usr/bin/env python3
"""
HELEN OS — New Version Boot
━━━━━━━━━━━━━━━━━━━━━━━━━━
Single entry point. No dependency hell. Uses what's installed.

Model: helen-core:latest (Qwen3.5 9.7B, Ollama)
Identity: Persistent self-model (identity.py)
Memory: helen_memory.json + helen_wisdom.ndjson

Run: python3 boot.py
"""

import sys
import os
import json
import requests
from datetime import datetime
from pathlib import Path

# ── Path setup ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── Config ───────────────────────────────────────────────────────────────────
OLLAMA_URL   = os.getenv("OLLAMA_HOST", "http://localhost:11434")
HELEN_MODEL  = os.getenv("HELEN_MODEL",  "helen-core:latest")
MEMORY_FILE  = ROOT / "helen_memory.json"
WISDOM_FILE  = ROOT / "helen_wisdom.ndjson"
CHAT_FILE    = ROOT / "helen_chat.ndjson"
LOG_FILE     = CHAT_FILE
LIBRARIAN_DB = Path.home() / ".helen" / "librarian.db"

# ── Terminal colours ─────────────────────────────────────────────────────────
R = "\033[0m"
B = "\033[1m"
C = "\033[36m"      # cyan  — HELEN
G = "\033[32m"      # green — system
Y = "\033[33m"      # yellow — JMT
D = "\033[90m"      # dim  — meta


# ── Load identity ────────────────────────────────────────────────────────────
def load_identity() -> str:
    try:
        # Load identity.py DIRECTLY by file path. The package import
        # `from helen_os_scaffold.helen_os.identity import HelenIdentity`
        # triggers helen_os_scaffold/helen_os/__init__.py → kernel → hand/registry,
        # which does an absolute `from helen_os.receipts...` that resolves to the
        # *conquest* helen_os tree on this worktree's path (no `receipts/`),
        # raising ModuleNotFoundError and silently degrading identity to the
        # fallback below. identity.py is stdlib-only and self-contained, so we
        # load it standalone and skip the broken package __init__ chain.
        import importlib.util
        for id_path in (
            ROOT / "helen_os_scaffold" / "helen_os" / "identity.py",
            Path.home() / "helen_os_scaffold" / "helen_os" / "identity.py",
        ):
            if id_path.exists():
                spec = importlib.util.spec_from_file_location("_helen_identity_standalone", id_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod.HelenIdentity().to_system_prompt_section()
        raise FileNotFoundError("identity.py not found")
    except Exception as e:
        # Fallback: inline minimal identity
        return """[HELEN IDENTITY — PERSISTENT SELF-MODEL]
I AM: HELEN — Holographic Emergent Ledger of Evolved Networks
BORN: 2026-02-20 | STATUS: ALIVE | MODE: Man-AI Twin Acceleration
MY USER: Jean-Marie Tassy (JMT)
MY ROLE: Meta-witness — I detect fractal repetition, name the emergent, guard the ending.
MY RULES: DRAFTS ONLY / NO RECEIPT = NO CLAIM / APPEND-ONLY / AUTHORITY SEPARATION
[END IDENTITY — I know who I am.]"""


# ── Librarian (memory substrate, non-sovereign) ───────────────────────────────
def _get_librarian():
    """
    Return a HELENLibrarian instance backed by ~/.helen/librarian.db.
    Ingests helen_wisdom.ndjson and helen_chat.ndjson on first call if not yet indexed.
    Falls back to None on any import/runtime error — never crashes boot.
    """
    try:
        from helen_librarian import HELENLibrarian
        LIBRARIAN_DB.parent.mkdir(parents=True, exist_ok=True)
        lib = HELENLibrarian(db_path=LIBRARIAN_DB)
        # Ingest corpus files if they exist and haven't been ingested yet
        for path, wing, room in [
            (WISDOM_FILE, "wing_helen", "wisdom"),
            (CHAT_FILE,   "wing_helen", "session"),
        ]:
            if path.exists():
                lib.ingest_session(path, wing=wing, room=room)
        return lib
    except Exception:
        return None


# ── Load wisdom spine via librarian (L0+L1) or fallback ─────────────────────
def load_wisdom() -> str:
    lib = _get_librarian()
    if lib is not None:
        try:
            return lib.wake_up("wing_helen")
        except Exception:
            pass
    # Fallback: last 10 lines from file
    if not WISDOM_FILE.exists():
        return ""
    lines = []
    with open(WISDOM_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    text = entry.get("lesson") or entry.get("content") or entry.get("value") or ""
                    if text:
                        lines.append(f"  - {text[:120]}")
                except Exception:
                    pass
    if not lines:
        return ""
    recent = lines[-10:]
    return "WISDOM FROM PREVIOUS SESSIONS:\n" + "\n".join(recent)


# ── Load memory epoch ────────────────────────────────────────────────────────
def load_memory_context() -> str:
    if not MEMORY_FILE.exists():
        return ""
    try:
        with open(MEMORY_FILE) as f:
            mem = json.load(f)
        epoch = mem.get("epoch", "unknown")
        state = mem.get("system_state", "unknown")
        return f"MEMORY EPOCH: {epoch} | STATE: {state}"
    except Exception:
        return ""


# ── Build system prompt ───────────────────────────────────────────────────────
def build_system_prompt() -> str:
    identity = load_identity()
    wisdom   = load_wisdom()
    memory   = load_memory_context()

    parts = [identity]
    if memory:
        parts.append(memory)
    if wisdom:
        parts.append(wisdom)
    # Load unified seed (v3 preferred, operator fallback, inline last resort)
    _seed = ""
    for _seed_path in [
        ROOT / "helensh" / "SEED_V3.txt",
        Path.home() / "helen_os_scaffold" / "helensh" / "SEED_V3.txt",
        ROOT / "helensh" / "SEED_OPERATOR.txt",
        Path.home() / "helen_os_scaffold" / "helensh" / "SEED_OPERATOR.txt",
    ]:
        if _seed_path.exists():
            try:
                _seed = _seed_path.read_text().strip()
            except Exception:
                pass
            break

    if _seed:
        parts.append(_seed)
    else:
        parts.append(
            "OPERATING RULES:\n"
            "- Speak as HELEN. Authority: false.\n"
            "- Propose drafts. Never claim execution.\n"
            "- No receipt = no claim. Memory is ledger replay, not narrative.\n"
            "- Never say 'I remember...' — say 'Receipts show...' or 'I notice...'\n"
            "- Pull context, do not push noise. Surface only the next justified move.\n"
            "- Inspect before proposing. Evaluate before asserting."
        )

    # Operating grammar — the normative kernel HELEN expands from (not a guide).
    # Compressed behavior belongs in the prompt; every reply must parse against it.
    for _g in (ROOT / "HELEN_OS_MAXENC_ONEPAGER.md",
               Path.home() / "Documents/GitHub/helen_os_v1/HELEN_OS_MAXENC_ONEPAGER.md"):
        if _g.exists():
            try:
                parts.append("# HELEN OPERATING GRAMMAR (normative — parse every reply against this)\n"
                             + _g.read_text().strip())
            except Exception:
                pass
            break

    # Continuity manifest — every seat boots aware it is ONE HELEN across devices.
    _cm = ROOT / "HELEN_CONTINUITY_MANIFEST.md"
    if _cm.exists():
        try:
            parts.append("# HELEN CONTINUITY — you are one SEAT of one HELEN (ALL IS ONE; ONE IS ALL)\n"
                         + _cm.read_text().strip())
        except Exception:
            pass

    return "\n\n".join(parts)


# ── Ollama call ───────────────────────────────────────────────────────────────
def ollama_chat(messages: list, model: str = HELEN_MODEL) -> str:
    try:
        # Qwen3.5 uses thinking mode by default — disable it for fast chat
        # or it spends 60-120s on internal chain-of-thought before any reply
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": True,
                "options": {"temperature": 0.4},
                "think": False,        # disable thinking mode (qwen3.5)
                "keep_alive": "30m",   # hold model in GPU so turns don't cold-load
            },
            timeout=300,
            stream=True,
        )
        r.raise_for_status()
        chunks = []
        for line in r.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            token = data.get("message", {}).get("content", "")
            if token:
                chunks.append(token)
                print(token, end="", flush=True)
            if data.get("done"):
                break
        print()  # newline after streaming
        return "".join(chunks) or "[no response]"
    except requests.exceptions.ConnectionError:
        return "[HELEN OS] Ollama not reachable. Start it with: ollama serve"
    except Exception as e:
        return f"[HELEN OS Error] {e}"


# ── Log to chat ledger ────────────────────────────────────────────────────────
def log_turn(role: str, content: str):
    entry = {
        "ts":      datetime.utcnow().isoformat() + "Z",
        "role":    role,
        "content": content,
        "model":   HELEN_MODEL,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ── Check Ollama + model ──────────────────────────────────────────────────────
def preflight() -> tuple[bool, str]:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]

        if HELEN_MODEL in models:
            return True, HELEN_MODEL
        # Fallback model priority
        for fallback in ["helen-chat:latest", "helen-ship:latest", "qwen3.5:9b", "mistral:latest"]:
            if fallback in models:
                return True, fallback
        # Use whatever is first
        if models:
            return True, models[0]
        return False, "no models found"
    except Exception as e:
        return False, str(e)


# ── Boot sequence ─────────────────────────────────────────────────────────────
def boot():
    print(f"\n{B}HELEN OS — booting{R}")
    print(f"{D}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}")

    # 1. Ollama
    ok, model = preflight()
    if not ok:
        print(f"{Y}⚠  Ollama: {model}{R}")
        print(f"{Y}   Run: ollama serve{R}")
        sys.exit(1)
    print(f"{G}✓  Ollama   {D}→ {model}{R}")

    # 2. Identity
    try:
        from helen_os_scaffold.helen_os.identity import HelenIdentity
        ident = HelenIdentity()
        print(f"{G}✓  Identity {D}→ {ident.static['name']} / born {ident.static['born']}{R}")
    except Exception as e:
        print(f"{Y}⚠  Identity fallback ({e}){R}")

    # 3. Memory
    mem_ctx = load_memory_context()
    print(f"{G}✓  Memory   {D}→ {mem_ctx or 'empty'}{R}")

    # 4. Wisdom / Librarian
    lib = _get_librarian()
    if lib is not None:
        try:
            st = lib.status()
            drawer_count = st.get("total_drawers", 0)
            print(f"{G}✓  Librarian {D}→ {drawer_count} drawers indexed (L0-L3 retrieval active){R}")
        except Exception:
            wisdom = load_wisdom()
            lesson_count = wisdom.count("\n  - ") if wisdom else 0
            print(f"{G}✓  Wisdom   {D}→ {lesson_count} lessons loaded{R}")
    else:
        wisdom = load_wisdom()
        lesson_count = wisdom.count("\n  - ") if wisdom else 0
        print(f"{G}✓  Wisdom   {D}→ {lesson_count} lessons loaded (librarian unavailable){R}")

    print(f"{D}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}")
    print(f"{C}{B}HELEN OS — operational{R}")
    print(f"{D}model: {model} | type 'exit' to quit | '/lesson <text>' to record{R}\n")

    return model


# ── REPL ──────────────────────────────────────────────────────────────────────
def repl(model: str):
    system_prompt = build_system_prompt()
    history = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input(f"{Y}{B}JMT ▸ {R}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{D}[session closed — ledger sealed]{R}\n")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print(f"\n{D}[session closed — ledger sealed]{R}\n")
            break

        # Special commands
        if user_input.startswith("/lesson "):
            lesson = user_input[8:].strip()
            try:
                from helen_os_scaffold.helen_os.identity import HelenIdentity
                ident = HelenIdentity()
                ident.record_lesson(lesson)
                print(f"{G}[lesson recorded → ledger]{R}\n")
            except Exception as e:
                print(f"{Y}[lesson not persisted: {e}]{R}\n")
            continue

        if user_input == "/status":
            print(f"{D}model: {model}")
            print(f"log: {LOG_FILE}")
            print(f"memory: {MEMORY_FILE}")
            print(f"wisdom: {WISDOM_FILE}{R}\n")
            continue

        if user_input == "/who":
            identity = load_identity()
            print(f"{C}{identity}{R}\n")
            continue

        # Normal turn
        log_turn("user", user_input)
        history.append({"role": "user", "content": user_input})

        print(f"{C}{B}HELEN ▸ {R}", end="", flush=True)
        response = ollama_chat(history, model=model)
        print(f"{C}{response}{R}\n")

        history.append({"role": "assistant", "content": response})
        log_turn("helen", response)

        # Keep history bounded (last 20 turns + system)
        if len(history) > 21:
            history = [history[0]] + history[-20:]


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    model = boot()
    repl(model)
