#!/usr/bin/env python3
"""tools/hal_driver.py — HAL inference via Ollama. Non-sovereign. authority=false.

Env vars (override defaults):
    HAL_MODEL   = deepseek-r1:14b
    OLLAMA_URL  = http://localhost:11434/api/chat

LAN routing (GeForce PC example):
    OLLAMA_URL=http://192.168.1.X:11434/api/chat python3 tools/hal_driver.py "prompt"

Usage:
    python3 tools/hal_driver.py "your prompt"
    python3 tools/hal_driver.py --health
"""
import os, sys, json, time, urllib.request, urllib.error

HAL_MODEL_DEFAULT  = 'deepseek-r1:14b'
OLLAMA_URL_DEFAULT = 'http://localhost:11434/api/chat'


class HalDriver:
    def __init__(self, model: str = None, url: str = None):
        self.model = model or os.getenv('HAL_MODEL',  HAL_MODEL_DEFAULT)
        self.url   = url   or os.getenv('OLLAMA_URL', OLLAMA_URL_DEFAULT)

    def health(self) -> bool:
        """Returns True if Ollama is reachable."""
        try:
            base = self.url.split('/api/')[0]
            req  = urllib.request.Request(base + '/api/tags', method='GET')
            with urllib.request.urlopen(req, timeout=4):
                return True
        except Exception:
            return False

    def chat(self, messages: list, system: str = None) -> str:
        """Multi-turn inference. Returns assistant text or raises RuntimeError."""
        full_messages = []
        if system:
            full_messages.append({'role': 'system', 'content': system})
        full_messages.extend(messages)

        payload = json.dumps({
            'model':    self.model,
            'messages': full_messages,
            'stream':   False,
        }).encode()

        req = urllib.request.Request(
            self.url, data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = json.loads(r.read())
            return body['message']['content']
        except urllib.error.URLError as exc:
            raise RuntimeError(f'Ollama unreachable: {exc}') from exc
        except (KeyError, json.JSONDecodeError) as exc:
            raise RuntimeError(f'Unexpected Ollama response: {exc}') from exc

    def think(self, prompt: str, system: str = None) -> str:
        """Single user-turn convenience wrapper."""
        return self.chat([{'role': 'user', 'content': prompt}], system=system)


# ── CLI shim ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='HAL inference driver — non-sovereign')
    ap.add_argument('prompt', nargs='*', help='Prompt text')
    ap.add_argument('--health', action='store_true', help='Health check only')
    ap.add_argument('--system', default=None, help='System prompt override')
    args = ap.parse_args()

    hal = HalDriver()
    print(f'HAL_MODEL  : {hal.model}')
    print(f'OLLAMA_URL : {hal.url}')

    ok = hal.health()
    print(f'HEALTH     : {"OK" if ok else "OFFLINE — Ollama unreachable"}')
    if args.health or not ok:
        sys.exit(0 if ok else 1)

    prompt = ' '.join(args.prompt) or 'Identify yourself in one sentence.'
    print(f'PROMPT     : {prompt[:100]}')
    print('─' * 60)

    t0  = time.time()
    out = hal.think(prompt, system=args.system)
    dt  = time.time() - t0

    print(out)
    print('─' * 60)
    print(f'model={hal.model}  elapsed={dt:.1f}s  authority=false  sovereign=false')
