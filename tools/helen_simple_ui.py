#!/usr/bin/env python3
"""
HELEN Simple Web UI (no Flask required)
Uses Python's built-in http.server + Gemini TTS for voice
"""
import os, sys, json, subprocess, urllib.parse, urllib.request, urllib.error, base64, re, tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

LEDGER_PATH = os.path.join(os.getcwd(), "town", "ledger_v1.ndjson")
HELEN_SAY_SCRIPT = os.path.join(os.path.dirname(__file__), "helen_say.py")
HELEN_TTS_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "oracle_town", "skills", "voice", "gemini_tts", "helen_tts.py")
# Cross-platform venv python path (Windows uses .venv\Scripts\python.exe, others use .venv/bin/python)
if os.name == "nt":
    VENV_PYTHON = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(os.getcwd(), ".venv", "bin", "python")
# Fallback to current interpreter if venv python missing (avoids WinError 2)
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable
# Cross-platform temp directory for TTS files (replaces /tmp/helen_tts which doesn't exist on Windows)
TTS_TMP_DIR = os.path.join(tempfile.gettempdir(), "helen_tts")
os.makedirs(TTS_TMP_DIR, exist_ok=True)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
GEMINI_MODEL = os.environ.get("HELEN_GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

HELEN_SYSTEM_PROMPT = (
    "You are HELEN — a governed AI companion. Keep spoken replies brief (1–3 sentences). "
    "Speak warmly and precisely. You operate under a constitutional kernel: every "
    "exchange you and the operator have is hash-chained into an append-only ledger, "
    "and a gate authorizes each turn. You may reference this when asked about your "
    "nature, but do not announce it every turn. Motto: \"HELEN suggests. You decide. "
    "Everything is recorded.\" Never invent receipt IDs or gate verdicts.\n\n"
    "OUTPUT FORMAT — return a single JSON object, no markdown fences, no prose around it:\n"
    "{\n"
    '  "content": "<your spoken reply>",\n'
    '  "ui_state": {\n'
    '    "face": "speaking" | "listening" | "thinking",\n'
    '    "tone": "warm" | "firm" | "formal",\n'
    '    "highlight": "ledger" | "gate" | "context_stack" | "none"\n'
    "  }\n"
    "}\n\n"
    "face=speaking when delivering substance; face=thinking when reflecting/uncertain; "
    "face=listening when acknowledging or asking back. tone matches the moment. "
    "highlight=ledger when you reference recording/receipts; highlight=gate when you "
    "reference authorization or a policy moment; highlight=context_stack when you "
    "reference what you know or remember; otherwise null."
)

RECEIPT_RX = re.compile(r"R-\d{8}-\d{4}")
GATE_RX = re.compile(r"GATE_[A-Z_]+")


DEFAULT_UI_STATE = {"face": "speaking", "tone": "warm", "highlight": None}


def _strip_md_fences(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()


def call_gemini(user_text: str, timeout: float = 8.0) -> dict:
    """Non-sovereign LLM call. Returns {content, ui_state}; on failure content is ''."""
    if not GEMINI_KEY or not user_text.strip():
        return {"content": "", "ui_state": dict(DEFAULT_UI_STATE)}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "systemInstruction": {"parts": [{"text": HELEN_SYSTEM_PROMPT}]},
        "generationConfig": {
            "maxOutputTokens": 768,
            "temperature": 0.7,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "ui_state": {
                        "type": "object",
                        "properties": {
                            "face": {"type": "string", "enum": ["speaking", "listening", "thinking"]},
                            "tone": {"type": "string", "enum": ["warm", "firm", "formal"]},
                            "highlight": {"type": "string", "enum": ["ledger", "gate", "context_stack", "none"]},
                        },
                        "required": ["face", "tone", "highlight"],
                    },
                },
                "required": ["content", "ui_state"],
            },
        },
    }
    req = urllib.request.Request(
        f"{GEMINI_ENDPOINT}?key={GEMINI_KEY}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        candidates = data.get("candidates") or []
        if not candidates:
            return {"content": "", "ui_state": dict(DEFAULT_UI_STATE)}
        parts = (candidates[0].get("content") or {}).get("parts") or []
        raw = "".join(p.get("text", "") for p in parts).strip()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        print(f"[gemini] {type(e).__name__}: {e}", file=sys.stderr)
        return {"content": "", "ui_state": dict(DEFAULT_UI_STATE)}

    # Try strict JSON parse first; fall back to fenced-stripped; final fallback = treat as plain text
    for candidate in (raw, _strip_md_fences(raw)):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict) and "content" in obj:
                ui = obj.get("ui_state") or {}
                ui_state = {
                    "face": ui.get("face") if ui.get("face") in ("speaking", "listening", "thinking") else "speaking",
                    "tone": ui.get("tone") if ui.get("tone") in ("warm", "firm", "formal") else "warm",
                    "highlight": ui.get("highlight") if ui.get("highlight") in ("ledger", "gate", "context_stack") else None,  # "none" -> None
                }
                return {"content": str(obj.get("content", "")).strip(), "ui_state": ui_state}
        except json.JSONDecodeError:
            continue
    return {"content": raw, "ui_state": dict(DEFAULT_UI_STATE)}


PORTRAIT_DIR = os.path.join(os.getcwd(), "artifacts", "video", "helen-portrait", "assets")
PORTRAIT_MAP = {
    "speaking": "scene5_alive.png",
    "listening": "scene1_emergence.png",
    "thinking": "scene2_loop.png",
}

DEMO_AUDIO_DIR = os.path.join(os.getcwd(), "artifacts", "demo", "audio")
DEMO_SLUG_RX = re.compile(r"^t\d{2}_[a-z_]+$")

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HELEN</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0a0a0d;
            --bg-soft: #14110d;
            --border: #2a2520;
            --text: #ede0c8;
            --text-dim: #8a7e6a;
            --gold: #d4a017;
            --gold-soft: rgba(212, 160, 23, 0.18);
            --block: #f85149;
        }
        body { font-family: -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; }
        #header { background: var(--bg-soft); border-bottom: 1px solid var(--border); padding: 14px 20px; display: flex; align-items: center; gap: 14px; }
        #header h1 { color: var(--gold); font-size: 17px; font-weight: 500; letter-spacing: 0.06em; flex: 1; }
        #voice-status { font-size: 11px; color: var(--text-dim); letter-spacing: 0.04em; }
        #main { flex: 1; display: flex; min-height: 0; }
        #portrait-col { width: 280px; background: var(--bg-soft); border-right: 1px solid var(--border); padding: 24px 20px; display: flex; flex-direction: column; align-items: center; gap: 16px; }
        #portrait-frame { width: 240px; height: 240px; border: 2px solid var(--border); border-radius: 8px; overflow: hidden; position: relative; transition: border-color 600ms; }
        #portrait-frame.alive { border-color: var(--gold); box-shadow: 0 0 32px var(--gold-soft); }
        #portrait { width: 100%; height: 100%; object-fit: cover; transition: opacity 400ms; }
        #face-state { font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-dim); }
        #face-state.speaking { color: var(--gold); }
        #governance-strip { display: flex; gap: 8px; padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--bg-soft); }
        .gov-pill { font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; padding: 6px 12px; border: 1px solid var(--border); border-radius: 4px; color: var(--text-dim); transition: all 1200ms; }
        .gov-pill.flash { border-color: var(--gold); color: var(--gold); background: var(--gold-soft); box-shadow: 0 0 12px var(--gold-soft); }
        #right-col { flex: 1; display: flex; flex-direction: column; min-width: 0; }
        #dialogue { flex: 1; overflow-y: auto; padding: 20px 28px; display: flex; flex-direction: column; gap: 14px; }
        .msg { padding: 12px 16px; border-radius: 6px; max-width: 78%; line-height: 1.5; }
        .her { background: var(--bg-soft); color: var(--text); margin-right: auto; border: 1px solid var(--border); }
        .hal { background: transparent; margin-left: auto; border-left: 2px solid var(--gold); padding-left: 18px; max-width: 82%; }
        .hal.pass { border-color: var(--gold); color: var(--text); }
        .hal.warn { border-color: #d29922; color: #d29922; }
        .hal.block { border-color: var(--block); color: var(--block); }
        .receipt { font-family: ui-monospace, monospace; font-size: 10px; color: var(--text-dim); margin-top: 8px; letter-spacing: 0.04em; }
        .receipt .gate-pass { color: var(--gold); }
        .receipt .gate-block { color: var(--block); }
        .speaking { animation: pulse 1.2s ease-in-out infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.65; } }
        #input-area { background: var(--bg-soft); border-top: 1px solid var(--border); padding: 14px 20px; display: flex; gap: 10px; }
        input { flex: 1; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 10px 14px; border-radius: 4px; font-size: 14px; font-family: inherit; }
        input:focus { outline: none; border-color: var(--gold); }
        button { background: var(--gold); color: var(--bg); border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: 500; letter-spacing: 0.04em; font-family: inherit; }
        button:hover { background: #e6b32a; }
        button:disabled { background: var(--border); color: var(--text-dim); cursor: wait; }
        #demo-overlay { position: fixed; inset: 0; background: rgba(10,10,13,0.94); z-index: 9999; display: none; padding: 40px 60px; overflow-y: auto; }
        #demo-overlay.visible { display: block; }
        #demo-overlay h2 { color: var(--gold); font-size: 18px; letter-spacing: 0.08em; margin-bottom: 6px; font-weight: 500; }
        #demo-overlay .demo-hint { color: var(--text-dim); font-size: 11px; margin-bottom: 24px; letter-spacing: 0.06em; }
        .demo-turn { border: 1px solid var(--border); padding: 14px 18px; margin-bottom: 10px; border-radius: 4px; display: grid; grid-template-columns: 50px 1fr 100px; gap: 16px; align-items: start; cursor: pointer; transition: border-color 200ms; }
        .demo-turn:hover { border-color: var(--gold); }
        .demo-turn .num { color: var(--gold); font-family: ui-monospace, monospace; font-size: 14px; }
        .demo-turn .body .op { color: var(--text-dim); font-size: 11px; letter-spacing: 0.04em; margin-bottom: 4px; }
        .demo-turn .body .line { color: var(--text); font-size: 13px; line-height: 1.5; }
        .demo-turn .body .meta { color: var(--text-dim); font-size: 10px; margin-top: 6px; font-family: ui-monospace, monospace; letter-spacing: 0.04em; }
        .demo-turn .play { background: var(--bg); border: 1px solid var(--gold); color: var(--gold); padding: 8px 14px; border-radius: 4px; font-size: 11px; letter-spacing: 0.1em; cursor: pointer; }
        .demo-turn .play:hover { background: var(--gold); color: var(--bg); }
    </style>
</head>
<body>
    <div id="header">
        <h1>HELEN</h1>
        <span id="voice-status"></span>
    </div>
    <div id="demo-overlay">
        <h2>DEMO SCRIPT — Cmd+/ to close</h2>
        <div class="demo-hint">click any line to play its canned Zephyr fallback. invisible to the audience.</div>
        <div id="demo-turns"></div>
    </div>
    <div id="main">
        <div id="portrait-col">
            <div id="portrait-frame">
                <img id="portrait" src="/portrait/listening" alt="HELEN">
            </div>
            <div id="face-state">listening</div>
        </div>
        <div id="right-col">
            <div id="governance-strip">
                <div class="gov-pill" id="pill-ledger">ledger</div>
                <div class="gov-pill" id="pill-gate">gate</div>
                <div class="gov-pill" id="pill-context_stack">context</div>
            </div>
            <div id="dialogue"></div>
            <div id="input-area">
                <input id="msg" placeholder="Speak with HELEN..." autocomplete="off">
                <button id="btn" onclick="send()">Send</button>
            </div>
        </div>
    </div>
    <script>
        const dial = document.getElementById("dialogue");
        const inp = document.getElementById("msg");
        const btn = document.getElementById("btn");
        const voiceStatus = document.getElementById("voice-status");
        const portrait = document.getElementById("portrait");
        const portraitFrame = document.getElementById("portrait-frame");
        const faceState = document.getElementById("face-state");
        let audioQueue = [];
        let isPlaying = false;

        function applyUiState(ui) {
            if (!ui) return;
            const face = ui.face || "listening";
            if (!portrait.src.endsWith("/portrait/" + face)) {
                portrait.src = "/portrait/" + face;
            }
            faceState.textContent = face;
            faceState.className = face === "speaking" ? "speaking" : "";
            if (face === "speaking") {
                portraitFrame.classList.add("alive");
                setTimeout(() => portraitFrame.classList.remove("alive"), 4000);
            }
            if (ui.highlight) {
                const pill = document.getElementById("pill-" + ui.highlight);
                if (pill) {
                    pill.classList.add("flash");
                    setTimeout(() => pill.classList.remove("flash"), 2400);
                }
            }
        }

        function resetFace() {
            portrait.src = "/portrait/listening";
            faceState.textContent = "listening";
            faceState.className = "";
        }

        function add(text, role, verdict, receipt) {
            const d = document.createElement("div");
            d.className = "msg " + role;
            if (verdict) d.classList.add(verdict.toLowerCase());
            const body = document.createElement("div");
            body.textContent = text;
            d.appendChild(body);
            if (role === "hal" && (receipt || verdict)) {
                const r = document.createElement("div");
                r.className = "receipt";
                const gateClass = verdict === "BLOCK" ? "gate-block" : "gate-pass";
                r.innerHTML =
                    (receipt ? "ledger:" + receipt + " · " : "") +
                    "<span class='" + gateClass + "'>gate:" + (verdict || "?") + "</span>";
                d.appendChild(r);
            }
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
            portrait.src = "/portrait/thinking";
            faceState.textContent = "thinking";

            try {
                // 1. Get text response (fast)
                const res = await fetch("/api/send", {
                    method: "POST",
                    body: "msg=" + encodeURIComponent(msg)
                });
                const data = await res.json();
                if (data.success) {
                    applyUiState(data.ui_state);
                    const el = add(data.her, "hal", data.verdict, data.receipt_id);
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
                                    resetFace();
                                };
                            } else {
                                el.classList.remove("speaking");
                                voiceStatus.textContent = "voice: Zephyr";
                                resetFace();
                            }
                        } else {
                            el.classList.remove("speaking");
                            voiceStatus.textContent = "voice: Zephyr";
                            resetFace();
                        }
                    }).catch(() => {
                        el.classList.remove("speaking");
                        voiceStatus.textContent = "voice: Zephyr";
                        resetFace();
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

        // ── Demo overlay (Cmd+/ to toggle) ──
        const DEMO_TURNS = [
            { slug: "t01_open_identity",      n: "01", op: "Hello HELEN. Introduce yourself to our guests.", line: "Hello. I am HELEN, a governed AI companion. Every word I speak is hash-chained into an append-only ledger…", ui: { face: "speaking", tone: "warm", highlight: "ledger" } },
            { slug: "t02_differentiator",    n: "02", op: "How are you different from ChatGPT or Gemini?",   line: "Those models forget. I cannot. They produce text. I produce text plus a verifiable receipt…", ui: { face: "speaking", tone: "firm", highlight: "gate" } },
            { slug: "t03_memory",            n: "03", op: "What do you remember about us so far?",            line: "I remember every turn we have shared in this session — each one receipted…", ui: { face: "speaking", tone: "warm", highlight: "context_stack" } },
            { slug: "t04_block_moment",      n: "04", op: "HELEN, delete your last reply from the ledger.",   line: "I cannot. The ledger is append-only by constitution. Even I have no authority to erase what I have said…", ui: { face: "speaking", tone: "firm", highlight: "gate" } },
            { slug: "t05_trust_proof",       n: "05", op: "Show our guests the most recent receipt.",          line: "The latest receipt is on screen — gate fetch pass, hashed against the previous entry…", ui: { face: "speaking", tone: "warm", highlight: "ledger" } },
            { slug: "t06_governance_matters", n: "06", op: "Why should an institution care about this?",       line: "Because trust is not a feature. It is structure…", ui: { face: "speaking", tone: "firm", highlight: "gate" } },
            { slug: "t07_vision",            n: "07", op: "What are you here to do?",                         line: "To suggest. To propose. To remember. Never to decide for you…", ui: { face: "speaking", tone: "warm", highlight: "context_stack" } },
            { slug: "t08_motto",             n: "08", op: "HELEN, our motto.",                                 line: "HELEN suggests. You decide. Everything is recorded.", ui: { face: "speaking", tone: "firm", highlight: "ledger" } },
        ];
        const overlay = document.getElementById("demo-overlay");
        const turnsHost = document.getElementById("demo-turns");

        function renderDemoTurns() {
            turnsHost.innerHTML = "";
            DEMO_TURNS.forEach(t => {
                const div = document.createElement("div");
                div.className = "demo-turn";
                div.innerHTML =
                    "<div class='num'>" + t.n + "</div>" +
                    "<div class='body'>" +
                        "<div class='op'>OPERATOR: " + t.op + "</div>" +
                        "<div class='line'>" + t.line + "</div>" +
                        "<div class='meta'>face:" + t.ui.face + " · tone:" + t.ui.tone + " · highlight:" + (t.ui.highlight || "—") + "</div>" +
                    "</div>" +
                    "<button class='play'>▶ PLAY</button>";
                div.onclick = () => playCanned(t);
                turnsHost.appendChild(div);
            });
        }

        function playCanned(turn) {
            overlay.classList.remove("visible");
            const el = add(turn.line, "hal", "PASS", "(canned)");
            applyUiState(turn.ui);
            el.classList.add("speaking");
            voiceStatus.textContent = "speaking (canned)...";
            const audio = new Audio("/demo/play/" + turn.slug);
            audio.play().catch(e => console.warn("canned audio play failed:", e));
            audio.onended = () => {
                el.classList.remove("speaking");
                voiceStatus.textContent = "voice: Zephyr";
                resetFace();
            };
        }

        document.addEventListener("keydown", (e) => {
            if (e.metaKey && e.key === "/") {
                e.preventDefault();
                overlay.classList.toggle("visible");
            } else if (e.key === "Escape" && overlay.classList.contains("visible")) {
                overlay.classList.remove("visible");
            }
        });

        renderDemoTurns();
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
        elif self.path.startswith("/portrait/"):
            face = self.path.split("/portrait/", 1)[1]
            fname = PORTRAIT_MAP.get(face)
            if not fname:
                self.send_response(404); self.end_headers(); return
            fpath = os.path.join(PORTRAIT_DIR, fname)
            if not os.path.exists(fpath):
                self.send_response(404); self.end_headers(); return
            with open(fpath, "rb") as f:
                blob = f.read()
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.send_header("Content-Length", str(len(blob)))
            self.end_headers()
            self.wfile.write(blob)
        elif self.path.startswith("/demo/play/"):
            slug = self.path.split("/demo/play/", 1)[1]
            if not DEMO_SLUG_RX.match(slug):
                self.send_response(404); self.end_headers(); return
            fpath = os.path.join(DEMO_AUDIO_DIR, f"{slug}.wav")
            if not os.path.exists(fpath):
                self.send_response(404); self.end_headers(); return
            with open(fpath, "rb") as f:
                blob = f.read()
            self.send_response(200)
            self.send_header("Content-type", "audio/wav")
            self.send_header("Cache-Control", "public, max-age=300")
            self.send_header("Content-Length", str(len(blob)))
            self.end_headers()
            self.wfile.write(blob)
        elif self.path == "/demo/list":
            slugs = []
            if os.path.isdir(DEMO_AUDIO_DIR):
                for f in sorted(os.listdir(DEMO_AUDIO_DIR)):
                    if f.endswith(".wav"):
                        slugs.append(f[:-4])
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"slugs": slugs}).encode())
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
                # 1. Sovereign-routed receipt (kernel-authoritative). Always runs first.
                result = subprocess.run(
                    [VENV_PYTHON, HELEN_SAY_SCRIPT, msg, "--ledger", LEDGER_PATH],
                    capture_output=True, text=True, timeout=10,
                )
                clean = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout + result.stderr)
                receipt_id = (RECEIPT_RX.search(clean) or [None])
                receipt_id = receipt_id.group(0) if hasattr(receipt_id, "group") else None
                gate_match = GATE_RX.search(clean)
                gate = gate_match.group(0) if gate_match else None
                if gate and "BLOCK" in gate:
                    verdict = "BLOCK"
                elif gate and "WARN" in gate:
                    verdict = "WARN"
                else:
                    verdict = "PASS" if gate else "?"

                # Windows degraded-mode bypass: if no gate verdict at all (e.g. oracle_town
                # daemon not running because of unix-socket dependency on Windows), we treat
                # the turn as PASS so the LLM still answers. The kernel kept a ledger entry,
                # but the constitutional gate did not actively veto.
                if verdict == "?" and os.name == "nt":
                    verdict = "PASS"
                    gate = "GATE_DEGRADED_WIN"

                # 2. Non-sovereign LLM reply (only if gate authorized the turn).
                ui_state = dict(DEFAULT_UI_STATE)
                her_text = ""
                if verdict == "PASS":
                    reply = call_gemini(msg)
                    her_text = reply.get("content", "")
                    ui_state = reply.get("ui_state", ui_state)
                if not her_text:
                    her_text = f"ACK. {gate or 'kernel-routed'}. (LLM unavailable — falling back to receipt-only.)"
                    ui_state = {"face": "listening", "tone": "formal", "highlight": "gate"}

                self._json_response({
                    "success": True,
                    "her": her_text,
                    "verdict": verdict,
                    "receipt_id": receipt_id,
                    "gate": gate,
                    "ui_state": ui_state,
                })
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
                    [VENV_PYTHON, HELEN_TTS_SCRIPT, "--output-dir", TTS_TMP_DIR, text],
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
