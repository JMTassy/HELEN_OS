#!/usr/bin/env python3
"""
HELEN Simple Web UI (no Flask required)
Uses Python's built-in http.server + Gemini TTS for voice
"""
import os, sys, json, subprocess, urllib.parse, base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_PATH = os.path.join(os.getcwd(), "town", "ledger_v1.ndjson")
HELEN_SAY_SCRIPT = os.path.join(os.path.dirname(__file__), "helen_say.py")
HELEN_TTS_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "oracle_town", "skills", "voice", "gemini_tts", "helen_tts.py")
VENV_PYTHON = os.path.join(os.getcwd(), ".venv", "bin", "python")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""

# Gate registry: maps mockup gate label -> (relpath, status when file exists)
# Status values: "ACTIVE" (wired and load-bearing), "TESTS_ONLY" (enforced by tests but no runtime gate),
# "NOT_WIRED" (referenced in design but no implementation). Honest by construction.
GATE_REGISTRY = [
    ("POLICY_GATE",    "helen_os/governance/legoracle_gate_poc.py", "ACTIVE"),
    ("LEGORACLE",      "legoracle_v13rc.py",                        "ACTIVE"),
    ("REDUCER",        "helen_chain_receipt_v2.py",                 "ACTIVE"),
    ("MAYOR",          "oracle_town/kernel/mayor.py",               "ACTIVE"),
    ("GHOST_CLOSURE",  "helen_os/tests/test_no_ghost_closures.py",  "TESTS_ONLY"),
    ("LANGUAGE_FW",    None,                                         "NOT_WIRED"),
    ("DESIRE_FW",      None,                                         "NOT_WIRED"),
]


def _gate_status():
    out = []
    for name, relpath, declared in GATE_REGISTRY:
        if relpath is None:
            out.append({"name": name, "status": declared})
            continue
        present = os.path.isfile(os.path.join(REPO_ROOT, relpath))
        out.append({"name": name, "status": declared if present else "MISSING"})
    return out


def _ledger_status():
    """Read tail of ledger to extract height, last event, last cum_hash. No full integrity check."""
    if not os.path.isfile(LEDGER_PATH):
        return {"height": None, "events": 0, "last_event": None, "cum_hash": None}
    try:
        size = os.path.getsize(LEDGER_PATH)
        # Read last 4KB to get the last full line
        with open(LEDGER_PATH, "rb") as f:
            f.seek(max(0, size - 4096))
            tail = f.read().decode("utf-8", errors="ignore")
        lines = [ln for ln in tail.strip().split("\n") if ln.strip()]
        last = json.loads(lines[-1]) if lines else {}
        # Count events cheaply by scanning newlines
        with open(LEDGER_PATH, "rb") as f:
            events = sum(1 for _ in f)
        cum = last.get("cum_hash") or ""
        return {
            "height": last.get("seq"),
            "events": events,
            "last_event": last.get("type"),
            "cum_hash": cum[:12] if cum else None,
        }
    except Exception as e:
        return {"height": None, "events": 0, "last_event": None, "cum_hash": None, "error": str(e)}

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HELEN - Persistent Dialogue</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui; background: #0d1117; color: #c9d1d9; height: 100vh; display: flex; flex-direction: column; }
        #header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 20px; display: flex; align-items: center; gap: 12px; }
        #header h1 { color: #58a6ff; font-size: 18px; flex: 1; }
        #voice-status { font-size: 12px; color: #3fb950; }
        #dialogue { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
        .msg { padding: 12px 16px; border-radius: 6px; max-width: 70%; }
        .her { background: #30363d; color: #c9d1d9; margin-right: auto; }
        .hal { background: #161b22; margin-left: auto; border-left: 3px solid; }
        .hal.pass { border-color: #3fb950; color: #3fb950; }
        .hal.warn { border-color: #d29922; color: #d29922; }
        .hal.block { border-color: #f85149; color: #f85149; }
        .speaking { animation: pulse 1s ease-in-out infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.6; } }
        #input-area { background: #161b22; border-top: 1px solid #30363d; padding: 12px 16px; display: flex; gap: 8px; }
        input { flex: 1; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 8px 12px; border-radius: 4px; font-size: 14px; }
        input:focus { outline: none; border-color: #58a6ff; }
        button { background: #238636; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #2ea043; }
        button:disabled { background: #21262d; color: #484f58; cursor: wait; }

        /* Constitutional state strip — honest reflection of kernel/gate/ledger state */
        #ledger-bar { background: #0a0d12; border-top: 1px solid #21262d; padding: 6px 16px; display: flex; gap: 16px; font-size: 11px; color: #7d8590; font-family: ui-monospace, monospace; }
        #ledger-bar .k { color: #484f58; }
        #ledger-bar .v { color: #c9d1d9; }
        #ledger-bar .canon-noship { color: #f85149; }
        #ledger-bar .canon-ship { color: #3fb950; }

        #gate-strip { background: #0a0d12; border-top: 1px solid #21262d; padding: 8px 16px; display: flex; gap: 14px; font-size: 10px; font-family: ui-monospace, monospace; flex-wrap: wrap; }
        #gate-strip .gate { display: flex; align-items: center; gap: 6px; }
        #gate-strip .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
        #gate-strip .gate.active .dot { background: #3fb950; box-shadow: 0 0 6px #3fb950; }
        #gate-strip .gate.tests_only .dot { background: #d29922; }
        #gate-strip .gate.not_wired .dot { background: #484f58; }
        #gate-strip .gate.missing .dot { background: #f85149; }
        #gate-strip .gate.active .label { color: #c9d1d9; }
        #gate-strip .gate.tests_only .label { color: #d29922; }
        #gate-strip .gate.not_wired .label { color: #484f58; }
        #gate-strip .gate.missing .label { color: #f85149; }
    </style>
</head>
<body>
    <div id="header">
        <h1>HELEN — Persistent Dialogue</h1>
        <span id="voice-status"></span>
    </div>
    <div id="dialogue"></div>
    <div id="input-area">
        <input id="msg" placeholder="Type a message..." autocomplete="off">
        <button id="btn" onclick="send()">Send</button>
    </div>
    <div id="ledger-bar">
        <span><span class="k">AUTHORITY:</span> <span class="v" id="auth">—</span></span>
        <span><span class="k">CANON:</span> <span id="canon" class="v">—</span></span>
        <span><span class="k">MODE:</span> <span class="v" id="mode">—</span></span>
        <span><span class="k">LEDGER HEIGHT:</span> <span class="v" id="height">—</span></span>
        <span><span class="k">EVENTS:</span> <span class="v" id="events">—</span></span>
        <span><span class="k">LAST:</span> <span class="v" id="last-event">—</span></span>
        <span><span class="k">CUM_HASH:</span> <span class="v" id="cum-hash">—</span></span>
    </div>
    <div id="gate-strip"></div>
    <script>
        const dial = document.getElementById("dialogue");
        const inp = document.getElementById("msg");
        const btn = document.getElementById("btn");
        const voiceStatus = document.getElementById("voice-status");
        let audioQueue = [];
        let isPlaying = false;

        function add(text, role, verdict) {
            const d = document.createElement("div");
            d.className = "msg " + role;
            if (verdict) d.classList.add(verdict.toLowerCase());
            d.textContent = "[" + role.toUpperCase() + (verdict ? " " + verdict : "") + "] " + text;
            dial.appendChild(d);
            dial.scrollTop = dial.scrollHeight;
            return d;
        }

        function playAudio(b64) {
            const bytes = atob(b64);
            const buf = new ArrayBuffer(bytes.length);
            const view = new Uint8Array(buf);
            for (let i = 0; i < bytes.length; i++) view[i] = bytes.charCodeAt(i);
            const blob = new Blob([buf], { type: "audio/wav" });
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            audio.play().catch(e => console.warn("Audio play failed:", e));
            return audio;
        }

        add("HELEN dialogue ready (voice: Zephyr)", "hal", "PASS");

        async function send() {
            const msg = inp.value.trim();
            if (!msg) return;
            inp.value = "";
            btn.disabled = true;
            btn.textContent = "...";
            add(msg, "her");

            try {
                // 1. Get text response (fast)
                const res = await fetch("/api/send", {
                    method: "POST",
                    body: "msg=" + encodeURIComponent(msg)
                });
                const data = await res.json();
                if (data.success) {
                    const el = add(data.her, "hal", data.verdict);
                    btn.disabled = false;
                    btn.textContent = "Send";
                    inp.focus();
                    // 2. Fire TTS in background (non-blocking)
                    const speakText = data.her || msg;
                    el.classList.add("speaking");
                    voiceStatus.textContent = "generating voice...";
                    fetch("/api/tts", {
                        method: "POST",
                        body: "text=" + encodeURIComponent(speakText)
                    }).then(r => r.json()).then(tts => {
                        if (tts.audio_b64) {
                            voiceStatus.textContent = "speaking...";
                            const audio = playAudio(tts.audio_b64);
                            if (audio) {
                                audio.onended = () => {
                                    el.classList.remove("speaking");
                                    voiceStatus.textContent = "voice: Zephyr";
                                };
                            } else {
                                el.classList.remove("speaking");
                                voiceStatus.textContent = "voice: Zephyr";
                            }
                        } else {
                            el.classList.remove("speaking");
                            voiceStatus.textContent = "voice: Zephyr";
                        }
                    }).catch(() => {
                        el.classList.remove("speaking");
                        voiceStatus.textContent = "voice: Zephyr";
                    });
                    return;
                } else {
                    add("Error: " + data.error, "hal", "BLOCK");
                }
            } catch(e) {
                add("Error: " + e.message, "hal", "BLOCK");
            }
            btn.disabled = false;
            btn.textContent = "Send";
            inp.focus();
        }

        inp.onkeydown = (e) => { if (e.key === "Enter") send(); }
        inp.focus();

        // Check voice status
        fetch("/api/voice-status").then(r => r.json()).then(d => {
            voiceStatus.textContent = d.enabled ? "voice: Zephyr" : "voice: off (no API key)";
        });

        // Constitutional state poller — refresh ledger ticker + gate strip
        function refreshState() {
            fetch("/api/state").then(r => r.json()).then(s => {
                document.getElementById("auth").textContent = s.authority || "—";
                const canonEl = document.getElementById("canon");
                canonEl.textContent = s.canon || "—";
                canonEl.className = "v " + (s.canon === "NO_SHIP" ? "canon-noship" : "canon-ship");
                document.getElementById("mode").textContent = s.mode || "—";
                const L = s.ledger || {};
                document.getElementById("height").textContent = L.height ?? "—";
                document.getElementById("events").textContent = L.events ?? "—";
                document.getElementById("last-event").textContent = L.last_event || "—";
                document.getElementById("cum-hash").textContent = L.cum_hash || "—";

                const strip = document.getElementById("gate-strip");
                strip.innerHTML = "";
                (s.gates || []).forEach(g => {
                    const cls = g.status.toLowerCase();
                    const el = document.createElement("span");
                    el.className = "gate " + cls;
                    el.title = g.name + ": " + g.status;
                    el.innerHTML = '<span class="dot"></span><span class="label">' + g.name + '</span>';
                    strip.appendChild(el);
                });
            }).catch(() => {});
        }
        refreshState();
        setInterval(refreshState, 3000);
    </script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path == "/api/voice-status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"enabled": bool(GEMINI_KEY)}).encode())
        elif self.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "authority": "NON_SOVEREIGN",
                "canon": "NO_SHIP",
                "mode": "WITNESS",
                "gates": _gate_status(),
                "ledger": _ledger_status(),
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _read_params(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        return urllib.parse.parse_qs(body)

    def _json_response(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        if self.path == "/api/send":
            params = self._read_params()
            msg = params.get("msg", [""])[0]
            try:
                result = subprocess.run(
                    ["python3", HELEN_SAY_SCRIPT, msg, "--ledger", LEDGER_PATH],
                    capture_output=True, text=True, timeout=10
                )
                output = result.stdout + result.stderr
                # Strip ANSI escape codes
                import re
                clean = re.sub(r'\x1b\[[0-9;]*m', '', output)
                her_text = ""
                verdict = "?"
                lines = clean.split("\n")
                in_her = False
                her_lines = []
                for line in lines:
                    if "[HER]" in line:
                        in_her = True
                        continue
                    if "[HAL]" in line:
                        in_her = False
                        if "PASS" in line: verdict = "PASS"
                        elif "BLOCK" in line: verdict = "BLOCK"
                        elif "WARN" in line: verdict = "WARN"
                        continue
                    if in_her and line.strip():
                        her_lines.append(line.strip())
                her_text = "\n".join(her_lines)
                self._json_response({"success": True, "her": her_text or msg, "verdict": verdict})
            except Exception as e:
                self._json_response({"success": False, "error": str(e)})

        elif self.path == "/api/tts":
            params = self._read_params()
            text = params.get("text", [""])[0]
            if not GEMINI_KEY or not text:
                self._json_response({"audio_b64": None})
                return
            try:
                tts_env = os.environ.copy()
                tts_env["GEMINI_API_KEY"] = GEMINI_KEY
                tts_result = subprocess.run(
                    [VENV_PYTHON, HELEN_TTS_SCRIPT, "--output-dir", "/tmp/helen_tts", text],
                    capture_output=True, text=True, timeout=30, env=tts_env,
                )
                audio_b64 = None
                for line in tts_result.stdout.split("\n"):
                    if line.startswith("Audio:"):
                        wav_path = line.split("Audio:")[-1].strip()
                        if os.path.exists(wav_path):
                            with open(wav_path, "rb") as f:
                                audio_b64 = base64.b64encode(f.read()).decode("ascii")
                            os.remove(wav_path)
                            prov = wav_path.replace(".wav", ".provenance.json")
                            if os.path.exists(prov):
                                os.remove(prov)
                        break
                self._json_response({"audio_b64": audio_b64})
            except Exception as e:
                print(f"[TTS] {e}", file=sys.stderr)
                self._json_response({"audio_b64": None})
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silent

if __name__ == "__main__":
    if GEMINI_KEY:
        print(f"HELEN UI + Voice (Zephyr) on http://localhost:5001")
    else:
        print(f"HELEN UI on http://localhost:5001 (no voice — set GEMINI_API_KEY)")
    server = HTTPServer(("127.0.0.1", 5001), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
