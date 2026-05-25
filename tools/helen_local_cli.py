#!/usr/bin/env python3
"""
Simple deterministic local HELEN CLI.

Features:
- Loads `helen_memory.json` and `helen_wisdom.ndjson` if present
- Interactive chat loop (rule-based responses)
- Avatar (azvatar) customization (emoji + name)
- `--demo` mode prints a sample interaction and exits

Run: python tools/helen_local_cli.py --demo
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from typing import List


ROOT = os.getcwd()
MEMORY_PATH = os.path.join(ROOT, "helen_memory.json")
WISDOM_PATH = os.path.join(ROOT, "helen_wisdom.ndjson")
CHAT_PATH = os.path.join(ROOT, "helen_chat.ndjson")
STATE_PATH = os.path.join("tools", "helen_local_state.json")


def load_json(path: str, default=None):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def load_ndjson(path: str) -> List[dict]:
    out = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except Exception:
                # skip malformed lines
                continue
    return out


def write_azvatar_svg(avatar: dict, out_path: str) -> None:
    """Write a simple SVG file showing emoji + name for quick avatar previews."""
    emoji = avatar.get("emoji", "⚜")
    name = avatar.get("name", "HELEN")
    # Simple centered SVG
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="480" height="240" viewBox="0 0 480 240">
  <rect width="100%" height="100%" fill="#0f1720" />
  <text x="50%" y="45%" font-size="72" text-anchor="middle" dominant-baseline="middle" fill="#fff">{emoji}</text>
  <text x="50%" y="75%" font-size="24" text-anchor="middle" dominant-baseline="middle" fill="#9ca3af">{name}</text>
</svg>
'''
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)


class HelenLocal:
    def __init__(self):
        self.memory = load_json(MEMORY_PATH, {}) or {}
        self.wisdom = load_ndjson(WISDOM_PATH)
        self.chat_log = load_ndjson(CHAT_PATH)
        self.state = load_json(STATE_PATH, {}) or {}
        # defaults
        self.avatar = self.state.get("avatar", {"emoji": "⚜", "name": "HELEN"})

    def save_state(self):
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump({"avatar": self.avatar}, f, indent=2, ensure_ascii=False)
        # also write a simple SVG azvatar for quick previews
        try:
            write_azvatar_svg(self.avatar, os.path.join("tools", "azvatar.svg"))
        except Exception:
            pass

    def summarize_state(self) -> str:
        facts = self.memory.get("facts", {})
        epoch = self.memory.get("epoch_name") or self.memory.get("epoch") or "unknown"
        accepted = facts.get("accepted_entries") or self.memory.get("accepted_entries") or "?"
        return f"Epoch: {epoch}. Facts: {len(facts)} items. Accepted entries: {accepted}."

    def recent_wisdom(self, n: int = 5) -> List[str]:
        items = [w.get("lesson") or w.get("text") or json.dumps(w, ensure_ascii=False) for w in self.wisdom]
        return items[-n:][::-1]

    def reply(self, text: str) -> str:
        t = text.lower()
        if any(k in t for k in ("state", "system", "tick", "epoch")):
            return self.summarize_state()
        if any(k in t for k in ("wisdom", "lessons", "lesson", "learned", "learn")):
            recent = self.recent_wisdom(3)
            if recent:
                return "Recent wisdom:\n- " + "\n- ".join(recent)
            return "No wisdom entries found."
        if any(k in t for k in ("who am i", "my name", "creator", "summoner", "who built")):
            return "You are Jean-Marie Tassy Simeoni — creator and summoner of HELEN OS and ORACLE TOWN. Authority remains human-only."
        if any(k in t for k in ("who are you", "your name", "who are you?", "name")):
            return f"I am {self.avatar.get('name')} {self.avatar.get('emoji')} — a local HELEN instance. I witness and record."
        if "town" in t:
            return "Town doctrine active: TRACE → ATTRIBUTE → GOVERN → RECEIPT."
        if "receipt" in t:
            return "NO RECEIPT = NO SHIP. Every action must produce a verifiable ledger entry before execution."
        if any(k in t for k in ("cwl", "soul rule", "canyon", "soul law")):
            return ("CWL v1.0.1 — frozen governance standard (sealed at commit fd13791, EPOCH3). "
                    "Soul Rules S1-S4: Drafts Only · No Receipt = No Claim · Append-Only · Authority Separation. "
                    "This session's engine doctrines extend CWL; they do not replace it.")
        if any(k in t for k in ("authority", "sovereign", "ship", "seal")):
            return ("DRAFTS ARE NOT REALITY. SEALING IS HUMAN-ONLY. "
                    "HELEN emits drafts only; world-effects require human-sealed ship mode + gates + receipt.")
        if any(k in t for k in ("hi", "hello", "hey")):
            return f"{self.avatar.get('emoji')} Hello — memory active. Ask 'state' or 'wisdom'."
        # fallback: echo with memory hint
        mem_keys = list(self.memory.get("facts", {}).keys())[:5]
        mem_hint = f"Memory keys: {', '.join(mem_keys)}" if mem_keys else "Memory empty"
        return f"I heard: '{text}'. {mem_hint}"

    def interactive(self):
        print(f"{self.avatar.get('emoji')}  Local HELEN — memory active. Type /help")
        while True:
            try:
                line = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye")
                break
            if not line:
                continue
            if line.startswith("/"):
                cmd = line[1:].split()
                if cmd[0] in ("q", "quit", "exit"):
                    print("Bye")
                    break
                if cmd[0] == "help":
                    print("Commands: /help /show_memory /wisdom [n] /avatar set <emoji> <name> /quit")
                    continue
                if cmd[0] == "show_memory":
                    print(json.dumps(self.memory, indent=2, ensure_ascii=False))
                    continue
                if cmd[0] == "wisdom":
                    n = int(cmd[1]) if len(cmd) > 1 else 5
                    for w in self.recent_wisdom(n):
                        print("- ", w)
                    continue
                if cmd[0] == "avatar":
                    if len(cmd) >= 4 and cmd[1] == "set":
                        emoji = cmd[2]
                        name = " ".join(cmd[3:])
                        self.avatar = {"emoji": emoji, "name": name}
                        self.save_state()
                        print("Avatar updated")
                    else:
                        print("Usage: /avatar set <emoji> <name>")
                    continue
                print("Unknown command. Type /help")
                continue
            # normal message
            resp = self.reply(line)
            print(f"helen> {resp}")


def demo():
    h = HelenLocal()
    print("Demo — local HELEN")
    print(h.summarize_state())
    print("Recent wisdom:")
    for w in h.recent_wisdom(3):
        print("- ", w)
    print("Sample chat: \nuser: hi\nhelen:")
    print(h.reply("hi"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set-avatar", nargs=2, help="Set avatar non-interactively: <emoji> <name>")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    helen = HelenLocal()
    if args.set_avatar:
        emoji, name = args.set_avatar
        helen.avatar = {"emoji": emoji, "name": name}
        helen.save_state()
        print(f"Avatar set: {emoji} {name} -> tools/azvatar.svg")
        return
    if args.demo:
        demo()
        return
    helen.interactive()


if __name__ == "__main__":
    main()
