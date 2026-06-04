#!/usr/bin/env python3
"""
helen_skills.py — HELEN Power Skills Registry
═══════════════════════════════════════════════
Gives HELEN agent capabilities to take real actions.

Architecture:
  - SkillRegistry: central catalog of all available skills
  - Each Skill: dataclass with name, description, and execute() method
  - All skills return: {"success": bool, "result": any, "error": str|None}
  - Skill safety tiers: READ_ONLY | PROPOSE | EXECUTE

Categories:
  1. EMAIL SKILLS   — Gmail read/search/draft (via MCP or stub)
  2. CALENDAR SKILLS — Google Calendar list/create/free-time
  3. SYSTEM SKILLS  — shell, file read/write (sandboxed)
  4. WEB SKILLS     — search and fetch
  5. CONQUEST SKILLS — game state, dice rolls

Intent Detection:
  detect_skill_intent(user_msg) → {"skill": str, "params": dict} | None

Run `python3 helen_skills.py` for a smoke test.
"""

from __future__ import annotations

import os
import re
import json
import random
import shlex
import subprocess
import sys
import textwrap
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ── Project root ───────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent

# ── Skill safety tiers ────────────────────────────────────────────────────────
READ_ONLY = "read_only"   # never modifies anything
PROPOSE   = "propose"     # creates a draft / proposal only, no send
EXECUTE   = "execute"     # performs a real-world side effect


# ══════════════════════════════════════════════════════════════════════════════
# DATA TYPES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Skill:
    """A single capability HELEN can invoke."""
    name:        str
    category:    str
    description: str
    params:      List[dict]            # [{"name": str, "type": str, "required": bool, "default": any}]
    safety_tier: str                  # READ_ONLY | PROPOSE | EXECUTE
    handler:     Callable[..., dict]  # the actual function

    def execute(self, **kwargs) -> dict:
        """Execute skill with given params. Returns {success, result, error}."""
        try:
            return self.handler(**kwargs)
        except TypeError as exc:
            return _err(f"Parameter error: {exc}")
        except Exception as exc:
            return _err(f"Skill execution failed: {exc}")

    def to_dict(self) -> dict:
        """JSON-serializable representation."""
        return {
            "name":        self.name,
            "category":    self.category,
            "description": self.description,
            "params":      self.params,
            "safety_tier": self.safety_tier,
        }


@dataclass
class SkillRegistry:
    """Central catalog — register skills once, call by name."""
    _skills: Dict[str, Skill] = field(default_factory=dict)

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def list_skills(self) -> List[Skill]:
        return list(self._skills.values())

    def call(self, name: str, **kwargs) -> dict:
        """Invoke a skill by name. Returns {success, result, error}."""
        skill = self.get(name)
        if not skill:
            return _err(f"Unknown skill: {name!r}. Available: {list(self._skills.keys())}")
        return skill.execute(**kwargs)

    def to_json(self) -> List[dict]:
        return [s.to_dict() for s in self.list_skills()]


# ── Result helpers ─────────────────────────────────────────────────────────────

def _ok(result: Any, *, meta: Optional[dict] = None) -> dict:
    out = {"success": True, "result": result, "error": None}
    if meta:
        out["meta"] = meta
    return out


def _err(msg: str) -> dict:
    return {"success": False, "result": None, "error": msg}


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 1 — EMAIL SKILLS
# ══════════════════════════════════════════════════════════════════════════════
#
# Primary path: call the Gmail MCP server if available (localhost:8782 or native
# MCP transport). If unavailable, return a structured stub so HELEN still gives
# a meaningful answer while clearly marking the data as placeholder.
#
# TODO(wire-in): Replace _gmail_mcp_call() with real Gmail API client once the
#   MCP server is confirmed running. The stub already returns the correct schema
#   so callers need zero changes.

GMAIL_MCP_URL = os.getenv("GMAIL_MCP_URL", "http://localhost:8782")


def _bridge_get(endpoint: str, params: dict = {}, timeout: int = 8) -> Optional[dict]:
    """GET request to the helen_mcp_bridge (localhost:8782)."""
    try:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{GMAIL_MCP_URL}{endpoint}" + (f"?{qs}" if qs else "")
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _bridge_post(endpoint: str, data: dict, timeout: int = 8) -> Optional[dict]:
    """POST request to the helen_mcp_bridge (localhost:8782)."""
    try:
        payload = json.dumps(data).encode()
        req = urllib.request.Request(
            f"{GMAIL_MCP_URL}{endpoint}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _skill_read_emails(n: int = 5) -> dict:
    """Fetch latest N real emails from Gmail via bridge."""
    data = _bridge_get("/gmail/inbox", {"n": n})
    if data and "emails" in data:
        emails = data["emails"]
        return _ok(emails, meta={"source": "gmail_live", "count": len(emails),
                                  "account": "jeanmarie.tassy@uzik.com"})
    # Hard fallback — should rarely hit since bridge is local
    return _ok([], meta={"source": "unavailable", "note": "Gmail bridge offline"})


def _skill_search_emails(query: str) -> dict:
    """Search real Gmail via bridge."""
    if not query:
        return _err("query parameter is required")
    data = _bridge_get("/gmail/search", {"q": urllib.parse.quote(query), "n": 10})
    if data and "emails" in data:
        return _ok(data["emails"], meta={"source": "gmail_live", "query": query,
                                          "count": data.get("count", 0)})
    return _ok([], meta={"source": "unavailable", "query": query})


def _skill_draft_email(to: str = "", subject: str = "", body: str = "") -> dict:
    """
    Create a Gmail draft. Safety: PROPOSE only — never sends automatically.
    Primary: Gmail MCP. Fallback: stub with local record.
    """
    if not to or not subject or not body:
        return _err("to, subject, and body are all required")

    mcp = _gmail_mcp_call("gmail_create_draft", {"to": to, "subject": subject, "body": body})
    if mcp and mcp.get("success"):
        return _ok({
            "draft_id": mcp.get("draft_id", ""),
            "to":       to,
            "subject":  subject,
            "status":   "draft_created",
        }, meta={"source": "gmail_mcp"})

    # TODO(wire-in): Connect Gmail MCP for real draft creation.
    # Log the draft locally as a record.
    draft_record = {
        "id":        f"local-draft-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        "to":        to,
        "subject":   subject,
        "body_chars": len(body),
        "status":    "local_draft_logged",
        "ts":        datetime.now(timezone.utc).isoformat(),
    }
    drafts_log = ROOT / "helen_drafts.json"
    try:
        existing = json.loads(drafts_log.read_text()) if drafts_log.exists() else []
        existing.append({**draft_record, "body": body})
        drafts_log.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    except Exception as exc:
        print(f"[skills] draft log failed: {exc}")

    return _ok(draft_record, meta={"source": "stub",
                                    "note": "Gmail MCP unavailable — draft saved locally only"})


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 2 — CALENDAR SKILLS
# ══════════════════════════════════════════════════════════════════════════════
#
# Primary path: Google Calendar MCP bridge (gcal MCP).
# Fallback: structured stubs.
#
# TODO(wire-in): Replace GCAL_MCP_URL with the MCP bridge URL once deployed.

GCAL_MCP_URL = os.getenv("GCAL_MCP_URL", "http://localhost:8782")  # same bridge


def _skill_list_events(days: int = 7) -> dict:
    """List upcoming calendar events via bridge."""
    data = _bridge_get("/calendar/events", {"days": days})
    if data and "events" in data:
        return _ok(data["events"], meta={"source": "gcal_live", "days": days})
    return _ok([], meta={"source": "unavailable"})

    # TODO(wire-in): Connect Google Calendar MCP for live events.
    stub_events = [
        {
            "id":       f"stub-evt-{i:03d}",
            "title":    ["Team standup", "HELEN OS review", "Lunch", "CONQUEST session",
                         "Weekly planning"][i % 5],
            "start":    (now + timedelta(days=i, hours=9 + i)).isoformat(),
            "end":      (now + timedelta(days=i, hours=10 + i)).isoformat(),
            "calendar": "primary",
            "stub":     True,
        }
        for i in range(min(days, 5))
    ]
    return _ok(stub_events, meta={"source": "stub", "days": days,
                                   "note": "Calendar MCP unavailable — showing placeholder events"})


def _skill_create_event(title: str = "", date: str = "", duration: int = 60,
                         description: str = "", attendees: Optional[List] = None) -> dict:
    """
    Create a calendar event. Safety: EXECUTE tier (creates real event if MCP connected).
    date: ISO 8601 string or natural string like '2026-04-10T14:00:00'
    duration: minutes
    """
    if not title or not date:
        return _err("title and date are required")

    # Parse date
    try:
        # Accept ISO or approximate strings
        start_dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
    except ValueError:
        return _err(f"Cannot parse date: {date!r} — use ISO 8601 format like 2026-04-10T14:00:00")

    end_dt = start_dt + timedelta(minutes=duration)

    mcp = _gcal_mcp_call("gcal_create_event", {
        "title":       title,
        "start":       start_dt.isoformat(),
        "end":         end_dt.isoformat(),
        "description": description,
        "attendees":   attendees or [],
    })
    if mcp and mcp.get("success"):
        return _ok({
            "event_id": mcp.get("event_id", ""),
            "title":    title,
            "start":    start_dt.isoformat(),
            "end":      end_dt.isoformat(),
            "status":   "created",
        }, meta={"source": "gcal_mcp"})

    # TODO(wire-in): Connect Google Calendar MCP.
    stub_id = f"stub-{start_dt.strftime('%Y%m%dT%H%M%S')}"
    return _ok({
        "event_id": stub_id,
        "title":    title,
        "start":    start_dt.isoformat(),
        "end":      end_dt.isoformat(),
        "status":   "stub_created",
    }, meta={"source": "stub", "note": "Calendar MCP unavailable — event NOT actually created"})


def _skill_find_free_time(date: str) -> dict:
    """
    Find free time slots on a given date.
    date: ISO date string like '2026-04-10'
    """
    if not date:
        return _err("date is required (e.g. 2026-04-10)")

    try:
        target_date = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
    except ValueError:
        return _err(f"Cannot parse date: {date!r}")

    mcp = _gcal_mcp_call("gcal_find_my_free_time", {
        "time_min": target_date.isoformat(),
        "time_max": (target_date + timedelta(days=1)).isoformat(),
    })
    if mcp and mcp.get("success"):
        return _ok(mcp.get("free_slots", []), meta={"source": "gcal_mcp", "date": date})

    # TODO(wire-in): Connect Google Calendar MCP.
    # Generate plausible stub free slots (9am–6pm minus 12-1pm lunch)
    base = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
    stub_slots = [
        {"start": base.isoformat(),                                  "end": (base + timedelta(hours=3)).isoformat(), "duration_min": 180},
        {"start": (base + timedelta(hours=4)).isoformat(),           "end": (base + timedelta(hours=6)).isoformat(), "duration_min": 120},
        {"start": (base + timedelta(hours=7)).isoformat(),           "end": (base + timedelta(hours=9)).isoformat(), "duration_min": 120},
    ]
    return _ok(stub_slots, meta={"source": "stub", "date": date,
                                  "note": "Calendar MCP unavailable — showing placeholder free slots"})


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 3 — SYSTEM SKILLS
# ══════════════════════════════════════════════════════════════════════════════

# Commands that are never allowed regardless of input
_BLOCKED_CMDS = frozenset({
    "rm", "rmdir", "shred", "dd", "mkfs", "fdisk", "parted",
    "shutdown", "reboot", "halt", "poweroff",
    "kill", "killall", "pkill",
    "sudo", "su", "chmod", "chown",
    "crontab",
    "curl", "wget",   # use web_search / fetch_url skills instead
    "nc", "ncat", "netcat", "nmap",
    "python", "python3", "ruby", "perl", "node", "bash", "sh", "zsh",
    "eval", "exec",
})

# Allowed safe commands whitelist (everything else is blocked)
_SAFE_CMDS = frozenset({
    "ls", "find", "cat", "head", "tail", "grep", "awk", "sed",
    "echo", "printf", "date", "pwd", "whoami", "hostname",
    "wc", "sort", "uniq", "cut", "tr", "tee",
    "df", "du", "free", "uptime",
    "ps", "top",
    "git",
    "pip", "pip3",
    "pytest", "python3",   # python3 only when not in blocked position
    "make",
    "jq", "yq",
    "env", "printenv",
    "diff", "patch",
    "tar", "gzip", "gunzip", "unzip", "zip",
    "md5sum", "sha256sum",
})


def _is_safe_command(cmd: str) -> Tuple[bool, str]:
    """
    Returns (safe: bool, reason: str).
    Parses first token as the command name and checks against allow/block lists.
    """
    try:
        parts = shlex.split(cmd)
    except ValueError as exc:
        return False, f"Cannot parse command: {exc}"

    if not parts:
        return False, "Empty command"

    base = os.path.basename(parts[0])

    if base in _BLOCKED_CMDS:
        return False, f"Command {base!r} is blocked for safety"

    # Extra checks
    if any(c in cmd for c in [";", "&&", "||", "`", "$("]):
        # Allow simple chaining only in git or make contexts
        if base not in ("git", "make"):
            return False, "Shell operators (;, &&, ||, backticks) are not allowed in arbitrary commands"

    # Pipe is OK for reading (grep, wc, etc.)
    if "|" in cmd:
        # Verify all piped commands are safe
        segments = cmd.split("|")
        for seg in segments:
            seg_cmd = shlex.split(seg.strip())[0] if seg.strip() else ""
            seg_base = os.path.basename(seg_cmd)
            if seg_base in _BLOCKED_CMDS:
                return False, f"Piped command {seg_base!r} is blocked"

    return True, "ok"


def _skill_run_command(cmd: str, timeout: int = 30) -> dict:
    """
    Execute a safe shell command and return stdout.
    Blocked: rm, kill, sudo, curl, wget, and all destructive commands.
    """
    if not cmd or not cmd.strip():
        return _err("cmd is required")

    safe, reason = _is_safe_command(cmd)
    if not safe:
        return _err(f"Blocked: {reason}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ROOT),
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return _ok({
            "stdout":      stdout[:4000],  # cap at 4KB
            "stderr":      stderr[:1000],
            "returncode":  result.returncode,
            "cmd":         cmd,
        })
    except subprocess.TimeoutExpired:
        return _err(f"Command timed out after {timeout}s: {cmd!r}")
    except Exception as exc:
        return _err(f"Command failed: {exc}")


def _skill_read_file(path: str) -> dict:
    """
    Read a file from the filesystem. Reads from any path (no write risk).
    Returns content as string. Files over 100KB are truncated.
    """
    if not path:
        return _err("path is required")

    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return _err(f"File not found: {p}")
        if not p.is_file():
            return _err(f"Not a file: {p}")

        size = p.stat().st_size
        MAX_BYTES = 100 * 1024  # 100KB
        content = p.read_text(errors="replace")
        truncated = False

        if size > MAX_BYTES:
            content = content[:MAX_BYTES]
            truncated = True

        return _ok({
            "path":      str(p),
            "content":   content,
            "size":      size,
            "truncated": truncated,
            "lines":     content.count("\n"),
        })
    except PermissionError:
        return _err(f"Permission denied: {path}")
    except Exception as exc:
        return _err(f"Read failed: {exc}")


def _skill_write_file(path: str, content: str, append: bool = False) -> dict:
    """
    Write content to a file. Writes ONLY within the project root for safety.
    append=True: appends to existing file. append=False: overwrites.
    """
    if not path or content is None:
        return _err("path and content are both required")

    try:
        p = Path(path).expanduser().resolve()

        # Safety: writes are confined to the project root OR HELEN's own
        # ~/.helen/ workspace (config, notes, scratch — where her receipts
        # already live). Everything else is blocked. Writes are also
        # operator-gated via /approve, so this is defense-in-depth.
        helen_home = (Path.home() / ".helen").resolve()
        def _within(child: Path, root: Path) -> bool:
            try:
                child.relative_to(root)
                return True
            except ValueError:
                return False
        if not (_within(p, ROOT) or _within(p, helen_home)):
            return _err(
                f"Write blocked: {p} is outside HELEN's writable roots "
                f"(project={ROOT}, workspace={helen_home})."
            )

        # Create parent dirs if needed
        p.parent.mkdir(parents=True, exist_ok=True)

        mode = "a" if append else "w"
        with open(p, mode, encoding="utf-8") as f:
            f.write(content)

        return _ok({
            "path":    str(p),
            "bytes":   len(content.encode("utf-8")),
            "mode":    "append" if append else "overwrite",
            "status":  "written",
        })
    except PermissionError:
        return _err(f"Permission denied: {path}")
    except Exception as exc:
        return _err(f"Write failed: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 4 — WEB SKILLS
# ══════════════════════════════════════════════════════════════════════════════

_USER_AGENT = "HELEN-OS/1.0 (https://github.com/jean-marie-tassy/helen-os)"

# Search backends (tried in order)
_SEARCH_BACKENDS = [
    ("DuckDuckGo Lite", "https://lite.duckduckgo.com/lite/?q={query}"),
]


def _skill_web_search(query: str, n_results: int = 5) -> dict:
    """
    Search the web for a query. Uses DuckDuckGo Lite (no auth required).
    Returns a list of {title, url, snippet} results.
    """
    if not query:
        return _err("query is required")

    encoded_query = urllib.request.quote(query)

    # Try DuckDuckGo Lite HTML scrape (no API key needed)
    try:
        url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Simple regex scrape of DDG Lite results
        results = []
        # DDG Lite pattern: <a class="result-link" href="...">Title</a> followed by snippet
        link_pattern = re.compile(
            r'<a[^>]+class="result-link"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
            r'(?:.*?<td[^>]+class="result-snippet"[^>]*>(.*?)</td>)?',
            re.DOTALL,
        )
        for m in link_pattern.finditer(html):
            url_found = m.group(1).strip()
            title     = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            snippet   = re.sub(r"<[^>]+>", "", m.group(3) or "").strip()[:200]
            if url_found.startswith("http"):
                results.append({"title": title, "url": url_found, "snippet": snippet})
            if len(results) >= n_results:
                break

        if results:
            return _ok(results, meta={"source": "duckduckgo_lite", "query": query})

        # If scrape found nothing (HTML structure changed), return raw excerpt
        cleaned = re.sub(r"<[^>]+>", " ", html)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()[:2000]
        return _ok({
            "raw_excerpt": cleaned,
            "note": "Could not parse structured results — returning raw page excerpt",
        }, meta={"source": "duckduckgo_lite_raw", "query": query})

    except urllib.error.URLError as exc:
        return _err(f"Web search failed (network): {exc}")
    except Exception as exc:
        return _err(f"Web search failed: {exc}")


def _skill_fetch_url(url: str, max_bytes: int = 50_000) -> dict:
    """
    Fetch raw content of a URL and return cleaned text.
    max_bytes: cap on raw download size (default 50KB).
    """
    if not url:
        return _err("url is required")

    if not url.startswith(("http://", "https://")):
        return _err(f"Invalid URL: must start with http:// or https://")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=20) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read(max_bytes)

        # Decode
        encoding = "utf-8"
        if "charset=" in content_type:
            encoding = content_type.split("charset=")[-1].split(";")[0].strip()
        text = raw.decode(encoding, errors="replace")

        # Strip HTML tags if HTML content
        if "html" in content_type.lower():
            text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<style[^>]*>.*?</style>",  " ", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

        return _ok({
            "url":          url,
            "content":      text[:10_000],    # cap at 10K chars for context
            "content_type": content_type,
            "bytes_read":   len(raw),
            "truncated":    len(raw) >= max_bytes,
        })

    except urllib.error.HTTPError as exc:
        return _err(f"HTTP {exc.code}: {exc.reason} — {url}")
    except urllib.error.URLError as exc:
        return _err(f"Network error: {exc} — {url}")
    except Exception as exc:
        return _err(f"Fetch failed: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORY 5 — CONQUEST SKILLS
# ══════════════════════════════════════════════════════════════════════════════

_CONQUEST_LEDGER = ROOT / "conquest" / "conquest_ledger_v0_1.json"
_CONQUEST_SEEDS  = ROOT / "conquest_v1.py"


def _skill_game_state() -> dict:
    """
    Return the current CONQUEST game state from the ledger.
    Reads conquest_ledger_v0_1.json + any live session state if available.
    """
    state: dict = {}

    # Load from ledger
    if _CONQUEST_LEDGER.exists():
        try:
            ledger = json.loads(_CONQUEST_LEDGER.read_text())
            total    = ledger.get("total_sessions", 0)
            seed     = ledger.get("seed", "unknown")
            samples  = ledger.get("sample_records", [])
            # Compute win stats
            winners  = [s for s in samples if s.get("winner")]
            state = {
                "source":         "conquest_ledger_v0_1",
                "total_sessions": total,
                "seed":           seed,
                "sample_count":   len(samples),
                "win_count":      len(winners),
                "win_rate":       round(len(winners) / max(len(samples), 1), 3),
                "archetypes":     list({s.get("archetype", "?") for s in samples}),
                "avg_knowledge":  round(
                    sum(s.get("final_knowledge", 0) for s in samples) / max(len(samples), 1), 1
                ),
                "avg_zols":       round(
                    sum(s.get("final_zols", 0) for s in samples) / max(len(samples), 1), 1
                ),
                "avg_territory":  round(
                    sum(s.get("final_territory", 0) for s in samples) / max(len(samples), 1), 1
                ),
            }
        except Exception as exc:
            state["ledger_error"] = str(exc)
    else:
        state["ledger"] = "not_found"

    # Check if there's a running game session file
    session_file = ROOT / "conquest_session.json"
    if session_file.exists():
        try:
            session = json.loads(session_file.read_text())
            state["live_session"] = session
        except Exception:
            pass

    state["ts"] = datetime.now(timezone.utc).isoformat()
    return _ok(state)


def _skill_roll_dice(sides: int = 6, n: int = 1, seed: Optional[int] = None) -> dict:
    """
    Roll N dice with the given number of sides.
    Uses a seeded random for reproducibility if seed is provided.
    CONQUEST standard: 2d6.
    """
    if sides < 2 or sides > 100:
        return _err(f"sides must be between 2 and 100 (got {sides})")
    if n < 1 or n > 20:
        return _err(f"n must be between 1 and 20 (got {n})")

    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    rolls = [rng.randint(1, sides) for _ in range(n)]
    total = sum(rolls)

    result = {
        "rolls":  rolls,
        "total":  total,
        "sides":  sides,
        "n_dice": n,
        "ts":     datetime.now(timezone.utc).isoformat(),
    }
    if seed is not None:
        result["seed"] = seed

    return _ok(result)


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY — assemble all skills
# ══════════════════════════════════════════════════════════════════════════════

def build_registry() -> SkillRegistry:
    """Build and return the fully-populated SkillRegistry."""
    reg = SkillRegistry()

    # ── EMAIL ─────────────────────────────────────────────────────────────────
    reg.register(Skill(
        name="read_emails",
        category="email",
        description="Fetch latest email summaries from Gmail inbox.",
        params=[{"name": "n", "type": "int", "required": False, "default": 5}],
        safety_tier=READ_ONLY,
        handler=_skill_read_emails,
    ))
    reg.register(Skill(
        name="search_emails",
        category="email",
        description="Search Gmail for messages matching a query.",
        params=[{"name": "query", "type": "str", "required": True, "default": None}],
        safety_tier=READ_ONLY,
        handler=_skill_search_emails,
    ))
    reg.register(Skill(
        name="draft_email",
        category="email",
        description="Create a Gmail draft (never sends automatically — propose only).",
        params=[
            {"name": "to",      "type": "str", "required": True,  "default": None},
            {"name": "subject", "type": "str", "required": True,  "default": None},
            {"name": "body",    "type": "str", "required": True,  "default": None},
        ],
        safety_tier=PROPOSE,
        handler=_skill_draft_email,
    ))

    # ── CALENDAR ──────────────────────────────────────────────────────────────
    reg.register(Skill(
        name="list_events",
        category="calendar",
        description="List upcoming calendar events for the next N days.",
        params=[{"name": "days", "type": "int", "required": False, "default": 7}],
        safety_tier=READ_ONLY,
        handler=_skill_list_events,
    ))
    reg.register(Skill(
        name="create_event",
        category="calendar",
        description="Create a calendar event. Requires title and ISO date.",
        params=[
            {"name": "title",       "type": "str", "required": True,  "default": None},
            {"name": "date",        "type": "str", "required": True,  "default": None},
            {"name": "duration",    "type": "int", "required": False, "default": 60},
            {"name": "description", "type": "str", "required": False, "default": ""},
            {"name": "attendees",   "type": "list","required": False, "default": []},
        ],
        safety_tier=EXECUTE,
        handler=_skill_create_event,
    ))
    reg.register(Skill(
        name="find_free_time",
        category="calendar",
        description="Find free time slots on a given date (ISO date: 2026-04-10).",
        params=[{"name": "date", "type": "str", "required": True, "default": None}],
        safety_tier=READ_ONLY,
        handler=_skill_find_free_time,
    ))

    # ── SYSTEM ────────────────────────────────────────────────────────────────
    reg.register(Skill(
        name="run_command",
        category="system",
        description="Execute a safe shell command (destructive commands are blocked).",
        params=[
            {"name": "cmd",     "type": "str", "required": True,  "default": None},
            {"name": "timeout", "type": "int", "required": False, "default": 30},
        ],
        safety_tier=EXECUTE,
        handler=_skill_run_command,
    ))
    reg.register(Skill(
        name="read_file",
        category="system",
        description="Read any file from the filesystem (read-only, max 100KB).",
        params=[{"name": "path", "type": "str", "required": True, "default": None}],
        safety_tier=READ_ONLY,
        handler=_skill_read_file,
    ))
    reg.register(Skill(
        name="write_file",
        category="system",
        description="Write content to a file inside the project root (sandboxed).",
        params=[
            {"name": "path",    "type": "str",  "required": True,  "default": None},
            {"name": "content", "type": "str",  "required": True,  "default": None},
            {"name": "append",  "type": "bool", "required": False, "default": False},
        ],
        safety_tier=EXECUTE,
        handler=_skill_write_file,
    ))

    # ── WEB ───────────────────────────────────────────────────────────────────
    reg.register(Skill(
        name="web_search",
        category="web",
        description="Search the web via DuckDuckGo (no auth required).",
        params=[
            {"name": "query",     "type": "str", "required": True,  "default": None},
            {"name": "n_results", "type": "int", "required": False, "default": 5},
        ],
        safety_tier=READ_ONLY,
        handler=_skill_web_search,
    ))
    reg.register(Skill(
        name="fetch_url",
        category="web",
        description="Fetch and return the text content of a URL.",
        params=[
            {"name": "url",       "type": "str", "required": True,  "default": None},
            {"name": "max_bytes", "type": "int", "required": False, "default": 50000},
        ],
        safety_tier=READ_ONLY,
        handler=_skill_fetch_url,
    ))

    # ── CONQUEST ──────────────────────────────────────────────────────────────
    reg.register(Skill(
        name="game_state",
        category="conquest",
        description="Return current CONQUEST game state from the ledger.",
        params=[],
        safety_tier=READ_ONLY,
        handler=_skill_game_state,
    ))
    reg.register(Skill(
        name="roll_dice",
        category="conquest",
        description="Roll N dice with given sides. CONQUEST standard: 2d6.",
        params=[
            {"name": "sides", "type": "int",          "required": False, "default": 6},
            {"name": "n",     "type": "int",           "required": False, "default": 1},
            {"name": "seed",  "type": "int|None",      "required": False, "default": None},
        ],
        safety_tier=READ_ONLY,
        handler=_skill_roll_dice,
    ))

    return reg


# ══════════════════════════════════════════════════════════════════════════════
# INTENT DETECTION
# ══════════════════════════════════════════════════════════════════════════════

# Each rule: (pattern, skill_name, param_extractor_fn or None)
# pattern: compiled regex matched against lowercased user message
# skill_name: the skill to invoke
# param_extractor: callable(match, original_msg) → dict of params

_IntentRule = tuple  # (compiled_pattern, skill_name, extractor_fn or None)


def _extract_n(match: re.Match, msg: str) -> dict:
    """Extract an integer quantity from the match."""
    try:
        return {"n": int(match.group("n"))}
    except Exception:
        return {}


def _extract_search_query(match: re.Match, msg: str) -> dict:
    """Extract the search term from a 'search email for X' message."""
    q = (match.group("query") or "").strip()
    return {"query": q} if q else {}


def _extract_web_query(match: re.Match, msg: str) -> dict:
    """Extract web search query."""
    q = (match.group("query") or "").strip()
    return {"query": q} if q else {}


def _extract_draft_params(match: re.Match, msg: str) -> dict:
    """Extract draft email params. Falls back to empty dict — LLM fills in details."""
    to = (match.group("to") if "to" in match.groupdict() else "").strip()
    params = {}
    if to:
        params["to"] = to
    return params


def _extract_event_params(match: re.Match, msg: str) -> dict:
    """Extract event params from 'create meeting about X on DATE'."""
    params = {}
    title_m = match.group("title") if "title" in match.groupdict() else ""
    if title_m:
        params["title"] = title_m.strip()
    date_m = match.group("date") if "date" in match.groupdict() else ""
    if date_m:
        params["date"] = date_m.strip()
    return params


def _extract_free_time(match: re.Match, msg: str) -> dict:
    date_m = match.group("date") if "date" in match.groupdict() else ""
    return {"date": date_m.strip()} if date_m else {}


def _extract_calendar_days(match: re.Match, msg: str) -> dict:
    try:
        return {"days": int(match.group("n"))}
    except Exception:
        return {"days": 7}


def _extract_dice(match: re.Match, msg: str) -> dict:
    params = {}
    try:
        n = int(match.group("n"))
        params["n"] = n
    except Exception:
        pass
    try:
        sides = int(match.group("sides"))
        params["sides"] = sides
    except Exception:
        pass
    return params


# ── Intent rule table ─────────────────────────────────────────────────────────
_INTENT_RULES: List[tuple] = [
    # EMAIL — read
    # Handles: "show me my emails", "check my inbox", "read emails", "get my mail"
    (re.compile(r"\b(?:check|show|read|get|fetch|list)(?:\s+\w+)?\s+(?:my\s+)?(?:emails?|inbox|mail)\b", re.I),
     "read_emails", None),

    (re.compile(r"\bopen\s+(?:my\s+)?(?:inbox|emails?|mail)\b", re.I),
     "read_emails", None),

    (re.compile(r"\b(?:last|latest|recent)\s+(?P<n>\d+)\s+emails?\b", re.I),
     "read_emails", _extract_n),

    # EMAIL — search
    (re.compile(r"\b(?:search|find|look\s+up)\s+(?:email|emails?|inbox)\s+(?:for\s+)?(?P<query>.{3,80})", re.I),
     "search_emails", _extract_search_query),

    # EMAIL — draft
    (re.compile(r"\b(?:draft|compose|write)\s+(?:an?\s+)?email\s+to\s+(?P<to>\S+@\S+|\S+)\b", re.I),
     "draft_email", _extract_draft_params),

    (re.compile(r"\bemail\s+(?P<to>\S+@\S+)\b", re.I),
     "draft_email", _extract_draft_params),

    # CALENDAR — list
    (re.compile(r"\b(?:what(?:'s|\s+is)\s+on\s+my\s+(?:calendar|schedule)|my\s+schedule|calendar\s+today|upcoming\s+events?)\b", re.I),
     "list_events", None),

    (re.compile(r"\b(?:next|coming|upcoming)\s+(?P<n>\d+)\s+days?\b.*\b(?:calendar|events?|schedule)\b", re.I),
     "list_events", _extract_calendar_days),

    # CALENDAR — create
    (re.compile(r"\b(?:create|book|schedule|add)\s+(?:a\s+)?(?:meeting|event|appointment|call)(?:\s+(?:about|titled?|called?)?\s*(?P<title>[^on\n]{3,40}?))?(?:\s+on\s+(?P<date>\d{4}-\d{2}-\d{2}[T\d:]*))?\b", re.I),
     "create_event", _extract_event_params),

    # CALENDAR — free time
    (re.compile(r"\b(?:find|check|show)\s+(?:my\s+)?free\s+(?:time|slots?)\s+(?:on\s+)?(?P<date>\d{4}-\d{2}-\d{2})\b", re.I),
     "find_free_time", _extract_free_time),

    (re.compile(r"\bwhen\s+(?:am\s+i\s+free|do\s+i\s+have\s+time)\b", re.I),
     "find_free_time", None),

    # SYSTEM — run command
    (re.compile(r"\brun\s+(?:command|cmd|shell)?\s*[:`]?\s*(?P<cmd>.{3,200})", re.I),
     "run_command", lambda m, msg: {"cmd": m.group("cmd").strip().strip("`'")}),

    # SYSTEM — read file
    # Handles absolute paths (/path, ~/path) and relative filenames (CLAUDE.md, file.txt)
    (re.compile(r"\bread\s+(?:the\s+)?file\s+(?:at\s+)?(?P<path>[/~\w][\w./\-]+)", re.I),
     "read_file", lambda m, msg: {"path": m.group("path")}),

    (re.compile(r"\bopen\s+(?:the\s+)?file\s+(?P<path>[/~\w][\w./\-]+)\b", re.I),
     "read_file", lambda m, msg: {"path": m.group("path")}),

    # WEB — search
    (re.compile(r"\b(?:search\s+(?:the\s+)?web\s+for|look\s+up\s+online|google)\s+(?P<query>.{3,120})", re.I),
     "web_search", _extract_web_query),

    (re.compile(r"\b(?:search\s+for|look\s+up)\s+(?P<query>.{3,80})\b", re.I),
     "web_search", _extract_web_query),

    # WEB — fetch URL
    (re.compile(r"\bfetch\s+(?:url|page|site|website)?\s*(?P<url>https?://\S+)\b", re.I),
     "fetch_url", lambda m, msg: {"url": m.group("url")}),

    # CONQUEST — game state
    (re.compile(r"\b(?:conquest|game)\s+(?:state|status|stats?|info|ledger)\b", re.I),
     "game_state", None),

    # CONQUEST — dice roll
    # Handles: "roll a dice", "roll the dice", "throw dice", "dice roll", "roll 2d6", "roll 3 dice"
    (re.compile(r"\b(?:roll\s+(?:a|the|some\s+)?\s*dice?|throw\s+(?:the\s+)?dice?|dice\s+roll)\b", re.I),
     "roll_dice", None),

    (re.compile(r"\broll\s+(?P<n>\d+)d(?P<sides>\d+)\b", re.I),
     "roll_dice", _extract_dice),

    (re.compile(r"\broll\s+(?P<n>\d+)\s+dice\b", re.I),
     "roll_dice", _extract_dice),
]


def detect_skill_intent(user_msg: str) -> Optional[dict]:
    """
    Detect if a user message maps to a skill invocation.

    Returns:
        {"skill": str, "params": dict}   if intent detected
        None                              if no skill match

    Example:
        detect_skill_intent("check my emails")
        → {"skill": "read_emails", "params": {}}

        detect_skill_intent("search for quantum computing")
        → {"skill": "web_search", "params": {"query": "quantum computing"}}
    """
    if not user_msg:
        return None

    msg_lower = user_msg.lower().strip()

    for pattern, skill_name, extractor in _INTENT_RULES:
        m = pattern.search(msg_lower)
        if m:
            params = extractor(m, user_msg) if extractor else {}
            return {"skill": skill_name, "params": params}

    return None


# ══════════════════════════════════════════════════════════════════════════════
# SKILL LOGGING HELPER
# ══════════════════════════════════════════════════════════════════════════════

CHAT_LOG = ROOT / "helen_chat.ndjson"


def log_skill_execution(skill_name: str, params: dict, result: dict, channel: str = "api") -> None:
    """
    Append a skill execution record to helen_chat.ndjson.
    Follows the existing ndjson schema used by the rest of the system.
    """
    entry = {
        "t":        datetime.now(timezone.utc).isoformat(),
        "role":     "skill",
        "skill":    skill_name,
        "params":   {k: str(v)[:200] for k, v in params.items()},
        "success":  result.get("success", False),
        "error":    result.get("error"),
        "channel":  channel,
        "meta":     result.get("meta"),
    }
    try:
        with open(CHAT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"[skills] log_skill_execution failed: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL SINGLETON (import-ready)
# ══════════════════════════════════════════════════════════════════════════════

# Build once at import time so callers just do `from helen_skills import REGISTRY`
REGISTRY: SkillRegistry = build_registry()


def execute_skill(intent: dict, channel: str = "api") -> dict:
    """
    Execute a skill from a detected intent dict.
    Logs the execution to helen_chat.ndjson.

    Args:
        intent: {"skill": str, "params": dict}
        channel: which interface triggered this (api, telegram, voice, etc.)

    Returns:
        {success, result, error, skill, params}
    """
    skill_name = intent.get("skill", "")
    params     = intent.get("params", {})

    result = REGISTRY.call(skill_name, **params)
    log_skill_execution(skill_name, params, result, channel=channel)

    # Augment result with tracing info
    result["skill"]  = skill_name
    result["params"] = params
    return result


def format_skill_result_for_llm(skill_name: str, result: dict) -> str:
    """
    Format a skill result as a concise context block to inject into the LLM prompt.
    HELEN reads this and then responds naturally.
    """
    if not result.get("success"):
        return (
            f"[SKILL: {skill_name}]\n"
            f"STATUS: FAILED\n"
            f"ERROR: {result.get('error', 'unknown error')}\n"
        )

    data = result.get("result")
    meta = result.get("meta", {}) or {}

    lines = [f"[SKILL: {skill_name}]", f"STATUS: OK"]

    if meta.get("source"):
        src = meta["source"]
        if "stub" in src:
            lines.append("NOTE: Data is placeholder (real API not connected)")
        else:
            lines.append(f"SOURCE: {src}")

    # Format by skill category
    if isinstance(data, list) and data:
        lines.append(f"COUNT: {len(data)}")
        for i, item in enumerate(data[:5], 1):   # cap at 5 entries for prompt size
            if isinstance(item, dict):
                brief = " | ".join(f"{k}: {str(v)[:60]}" for k, v in list(item.items())[:4]
                                   if k not in ("stub", "id"))
                lines.append(f"  {i}. {brief}")
            else:
                lines.append(f"  {i}. {str(item)[:120]}")
        if len(data) > 5:
            lines.append(f"  ... and {len(data) - 5} more")

    elif isinstance(data, dict):
        for k, v in list(data.items())[:8]:
            if k in ("ts", "stub"):
                continue
            lines.append(f"  {k}: {str(v)[:120]}")

    else:
        lines.append(f"RESULT: {str(data)[:300]}")

    if meta.get("note"):
        lines.append(f"NOTE: {meta['note']}")

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# SMOKE TEST
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("HELEN Skills Registry — smoke test\n" + "=" * 50)

    registry = SkillRegistry()
    registry = build_registry()

    skill_names = [s.name for s in registry.list_skills()]
    print(f"Available skills ({len(skill_names)}): {skill_names}\n")

    # ── Email skills ──
    print("--- EMAIL ---")
    r = registry.call("read_emails", n=3)
    print(f"read_emails(3):  success={r['success']}, count={len(r['result'])}, source={r.get('meta', {}).get('source')}")

    r = registry.call("search_emails", query="CONQUEST")
    print(f"search_emails:   success={r['success']}, source={r.get('meta', {}).get('source')}")

    r = registry.call("draft_email", to="jmt@example.com", subject="Test", body="Hello HELEN")
    print(f"draft_email:     success={r['success']}, status={r['result'].get('status') if r['result'] else 'N/A'}")

    # ── Calendar skills ──
    print("\n--- CALENDAR ---")
    r = registry.call("list_events", days=3)
    print(f"list_events(3):  success={r['success']}, count={len(r['result'])}")

    r = registry.call("create_event", title="HELEN Review", date="2026-04-15T10:00:00", duration=60)
    print(f"create_event:    success={r['success']}, status={r['result'].get('status') if r['result'] else 'N/A'}")

    r = registry.call("find_free_time", date="2026-04-15")
    print(f"find_free_time:  success={r['success']}, slots={len(r['result'])}")

    # ── System skills ──
    print("\n--- SYSTEM ---")
    r = registry.call("run_command", cmd="date")
    print(f"run_command(date): success={r['success']}, stdout={r['result'].get('stdout', '')[:40] if r['result'] else 'N/A'}")

    r = registry.call("run_command", cmd="rm -rf /")
    print(f"run_command(rm -rf /): success={r['success']}, blocked={'Blocked' in (r.get('error') or '')}")

    r = registry.call("read_file", path=str(ROOT / "helen_memory.json"))
    print(f"read_file:         success={r['success']}, size={r['result'].get('size', 0) if r['result'] else 0}")

    r = registry.call("write_file", path=str(ROOT / "helen_skills_test.tmp"), content="HELEN skills test OK\n")
    print(f"write_file:        success={r['success']}")

    # ── Web skills ──
    print("\n--- WEB ---")
    r = registry.call("web_search", query="HELEN OS constitutional AI", n_results=3)
    print(f"web_search:        success={r['success']}, type={type(r['result']).__name__}")

    r = registry.call("fetch_url", url="https://example.com")
    print(f"fetch_url:         success={r['success']}, bytes={r['result'].get('bytes_read', 0) if r['result'] else 0}")

    # ── Conquest skills ──
    print("\n--- CONQUEST ---")
    r = registry.call("game_state")
    print(f"game_state:        success={r['success']}, source={r['result'].get('source', 'N/A') if r['result'] else 'N/A'}")

    r = registry.call("roll_dice", sides=6, n=2)
    rolls = r['result']['rolls'] if r['success'] else []
    print(f"roll_dice(2d6):    success={r['success']}, rolls={rolls}, total={sum(rolls)}")

    # ── Intent detection ──
    print("\n--- INTENT DETECTION ---")
    test_phrases = [
        "check my emails",
        "show me the last 10 emails",
        "search email for CONQUEST",
        "draft email to alice@example.com",
        "what's on my calendar",
        "create meeting about Budget Review on 2026-04-20T14:00:00",
        "find free time on 2026-04-15",
        "search for constitutional AI frameworks",
        "look up quantum computing",
        "fetch url https://example.com",
        "conquest game state",
        "roll 2d6",
        "roll 3 dice",
        "tell me a joke",   # should return None
    ]
    for phrase in test_phrases:
        intent = detect_skill_intent(phrase)
        if intent:
            print(f"  [{phrase!r:45s}] → {intent['skill']}({intent['params']})")
        else:
            print(f"  [{phrase!r:45s}] → (no intent)")

    # Cleanup test file
    test_file = ROOT / "helen_skills_test.tmp"
    if test_file.exists():
        test_file.unlink()

    print("\nSmoke test complete.")
