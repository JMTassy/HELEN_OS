#!/usr/bin/env python3
"""
GOBLIN_CLI_V0 — live streaming viewer for HELEN garden models.

Shows EVERYTHING, live, token by token:
  • 🧠 THINK lane  — the hidden reasoning_content / thinking stream (usually discarded)
  • 🔊 SAY lane    — the visible content stream

Constitution:  pure presentation · P↛T · ΔEvidence=ΔWarrant=ΔAuthority=0 · NO_CLAIM.
This is an L4 world/UI surface (stage_render / context_drawer): it RENDERS a provider
stream. It never writes governed state, never emits a receipt, never admits anything.
Nothing the goblin says here is a claim; nothing it thinks here is truth.

Usage:
  python3 goblin_cli.py hal "invent a strange but formal mathematical object"
  python3 goblin_cli.py her --think "what object wants to exist here but is unnamed?"
  python3 goblin_cli.py hal --no-think "collapse this object into its counterfeit: ..."
  echo "your prompt" | python3 goblin_cli.py her
Models: hal | her | <any ollama model id>.  Flags: --think/--no-think, --temp N, --system "..."
"""
import json, sys, time, urllib.request

OLLAMA = "http://localhost:11434/api/chat"
ALIAS = {
    "hal": "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K",
    "her": "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL",
}
# WULmath-consistent ANSI palette (color = f(lane), a pure function — presentation only)
C = {
    "think": "\033[38;5;103m",   # dim periwinkle — 🌿 possibility / pre-claim reasoning
    "say":   "\033[38;5;231m",   # bright white   — 🔊 the spoken object
    "hal":   "\033[38;5;208m",   # HAL orange (adversarial)
    "her":   "\033[38;5;79m",    # HER teal (constructive)
    "rule":  "\033[38;5;240m",   # dim rule
    "law":   "\033[38;5;141m",   # constitutional violet
    "dim":   "\033[2m", "b": "\033[1m", "r": "\033[0m",
}
SYS_DEFAULT = {
    "hal": ("You are HAL, adversarial heterodoxy in a NO-CLAIM math Garden. Attack the "
            "frame. Weirdness is not novelty. authority=0, evidence=0. Think out loud."),
    "her": ("You are HER, constructive heterodoxy in a NO-CLAIM math Garden. Ask what "
            "object wants to exist but is unnamed. authority=0, evidence=0. Think out loud."),
}


def banner(alias, model, think):
    col = C.get(alias, C["law"])
    print(f"{C['rule']}{'─'*72}{C['r']}")
    print(f"{col}{C['b']} ▶ GOBLIN: {alias.upper()}{C['r']}  {C['dim']}{model}{C['r']}")
    print(f"{C['law']} law: pure presentation · P↛T · ΔAuthority=0 · NO_CLAIM · "
          f"think={'ON' if think else 'OFF'}{C['r']}")
    print(f"{C['rule']}{'─'*72}{C['r']}", flush=True)


def stream(alias, model, system, user, think, temp, maxtok):
    banner(alias, model, think)
    body = json.dumps({
        "model": model, "stream": True, "think": think,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "options": {"temperature": temp, "top_p": 0.95, "num_predict": maxtok},
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    lane = None            # track lane switches to print a header once per switch
    n_think = n_say = 0
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as resp:
        for raw in resp:                       # ollama streams one JSON object per line
            raw = raw.strip()
            if not raw:
                continue
            try:
                d = json.loads(raw)
            except json.JSONDecodeError:
                continue
            m = d.get("message", {}) or {}
            th = m.get("thinking") or m.get("reasoning_content") or ""
            sa = m.get("content") or ""
            if th:
                if lane != "think":
                    print(f"\n\n{C['think']}{C['b']}🧠 THINK{C['r']}{C['think']} ", end="")
                    lane = "think"
                print(f"{C['think']}{th}{C['r']}", end="", flush=True)
                n_think += len(th)
            if sa:
                if lane != "say":
                    print(f"\n\n{C['say']}{C['b']}🔊 SAY{C['r']}{C['say']} ", end="")
                    lane = "say"
                print(f"{C['say']}{sa}{C['r']}", end="", flush=True)
                n_say += len(sa)
            if d.get("done"):
                break
    dt = round(time.time() - t0, 1)
    print(f"\n{C['rule']}{'─'*72}{C['r']}")
    print(f"{C['dim']}⏱ {dt}s · 🧠 {n_think} think-chars (normally hidden) · "
          f"🔊 {n_say} say-chars · ΔAuthority=0 · NO_CLAIM{C['r']}", flush=True)


def main(argv):
    if not argv:
        print(__doc__); return
    alias = argv[0]
    model = ALIAS.get(alias, alias)
    think, temp, system, maxtok = True, 0.9, None, 3072
    prompt_parts = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--think": think = True
        elif a == "--no-think": think = False
        elif a == "--temp": i += 1; temp = float(argv[i])
        elif a == "--max": i += 1; maxtok = int(argv[i])
        elif a == "--system": i += 1; system = argv[i]
        else: prompt_parts.append(a)
        i += 1
    user = " ".join(prompt_parts).strip()
    if not user and not sys.stdin.isatty():
        user = sys.stdin.read().strip()
    if not user:
        user = "Invent one strange-but-formal mathematical object. Emit NAME, FORMAL_SEED, STRANGE_PROPERTY."
    if system is None:
        system = SYS_DEFAULT.get(alias, "You are a NO-CLAIM garden model. Think out loud. authority=0.")
    try:
        stream(alias, model, system, user, think, temp, maxtok)
    except urllib.error.URLError as e:
        print(f"{C['hal']}✗ ollama unreachable at {OLLAMA} — is `ollama serve` up? ({e}){C['r']}")
    except KeyboardInterrupt:
        print(f"\n{C['dim']}↩ interrupted — goblin silenced, nothing persisted.{C['r']}")


if __name__ == "__main__":
    main(sys.argv[1:])
