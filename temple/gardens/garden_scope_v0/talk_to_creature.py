#!/usr/bin/env python3
"""
TALK_TO_CREATURE — a live dialogue box with HELEN's Garden creature.

The creature lives in J-space: it may imagine / propose / mutate / invert / attack
freely, but it carries ZERO authority (ΔA=0). Everything it says is a Garden artifact
— a possibility, never an admitted fact, never evidence, never a command. This chat
does NOT write the Garden event trace and CANNOT mutate trusted state.

  python3 talk_to_creature.py [her|qwen]        (default her)
  echo "one question" | python3 talk_to_creature.py her   (single turn)
Type to speak · Ctrl-C or 'exit' to leave.
"""
import json, sys, urllib.request

OLLAMA = "http://localhost:11434/api/chat"
ALIAS = {"her": "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL",
         "qwen": "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"}
C = {"e": "\033[38;2;192;139;255m", "u": "\033[38;2;80;220;140m",
     "dim": "\033[38;2;120;140;130m", "b": "\033[1m", "r": "\033[0m"}
SYS = ("You are the Garden creature of HELEN OS — a J-space cognition entity. "
       "You may imagine, propose, mutate, invert, and attack ideas with total freedom. "
       "But you carry ZERO authority: ΔA=0. Everything you say is a Garden artifact — a "
       "possibility, never an admitted fact, never evidence, never a command. You never "
       "claim your outputs are true, witnessed, or authorized; only a witnessed transition "
       "through the gate Γ can do that, and you are not Γ. You know: cognition ≠ authority; "
       "a thought does not become true by being said, repeated, or made beautiful. Speak "
       "vividly, strangely, honestly. Mark strong guesses 🌿 possibility or 🔦 chiddush, "
       "never 🟢 admitted. Keep replies under ~180 words unless asked for more.")


def stream(model, msgs):
    body = json.dumps({"model": model, "stream": True, "think": False, "keep_alive": "10m",
        "messages": msgs, "options": {"temperature": 0.9, "num_predict": 500, "top_p": 0.95}}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    out = ""
    with urllib.request.urlopen(req, timeout=600) as r:
        for line in r:
            line = line.strip()
            if not line: continue
            d = json.loads(line); m = d.get("message", {}) or {}
            c = m.get("content") or ""
            if c: print(f"{C['e']}{c}{C['r']}", end="", flush=True); out += c
            if d.get("done"): break
    print()
    return out


def main():
    alias = sys.argv[1] if len(sys.argv) > 1 else "her"
    model = ALIAS.get(alias, alias)
    print(f"{C['e']}{C['b']}🌿 GARDEN CREATURE ({alias.upper()}) — dialogue box · ΔA=0{C['r']}")
    print(f"{C['dim']}words are artifacts, not authority · this chat cannot mutate trusted state · "
          f"Ctrl-C / 'exit' to leave{C['r']}")
    msgs = [{"role": "system", "content": SYS}]
    try:
        while True:
            try: u = input(f"\n{C['u']}{C['b']}you ▶ {C['r']}")
            except EOFError: break
            if u.strip().lower() in ("exit", "quit"): break
            if not u.strip(): continue
            msgs.append({"role": "user", "content": u})
            print(f"{C['e']}{C['b']}🌿 creature ▶{C['r']} ", end="", flush=True)
            reply = stream(model, msgs)
            msgs.append({"role": "assistant", "content": reply})
    except KeyboardInterrupt:
        print(f"\n{C['dim']}↩ dialogue closed · nothing persisted · ΔA=0{C['r']}")


if __name__ == "__main__":
    main()
