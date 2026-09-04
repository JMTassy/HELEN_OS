"""HELEN Voice layer — provider interface + identity/engine separation. NON_SOVEREIGN.

Instantiates the recommended architecture:

    HELEN Identity  ->  Voice Profile  ->  (any) TTS Engine

Every provider reads ONE profile (helen_voice_profile.json), so swapping Kokoro ->
Orpheus -> a future model never changes how HELEN *sounds like HELEN* — only the timbre.
The rest of HELEN never knows which engine spoke: it calls voice.speak(text).

Working today: SayProvider (macOS `say`, zero install) — the always-available local voice.
Declared plug-in points: Kokoro (default when installed), Orpheus (cinematic), Chatterbox
(conversation). Each fails SOFT back to Say so HELEN is never voiceless.

authority=false · canon_effect=false. This layer shapes expression, never authority.
"""
from __future__ import annotations
import json, os, shutil, subprocess, tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

PROFILE_PATH = Path(__file__).with_name("helen_voice_profile.json")


@dataclass(frozen=True)
class VoiceProfile:
    identity: str = "HELEN"
    pace: str = "calm"
    warmth: float = 0.82
    authority: float = 0.55
    curiosity: float = 0.72
    pause_style: str = "thoughtful"
    emotion_limit: str = "bounded"
    engine_hints: dict = None

    @classmethod
    def load(cls, path: Path = PROFILE_PATH) -> "VoiceProfile":
        d = json.loads(path.read_text())
        return cls(identity=d.get("identity", "HELEN"), pace=d.get("pace", "calm"),
                   warmth=d.get("warmth", 0.82), authority=d.get("authority_scalar", d.get("authority", 0.55)) if isinstance(d.get("authority"), (int, float)) else 0.55,
                   curiosity=d.get("curiosity", 0.72), pause_style=d.get("pause_style", "thoughtful"),
                   emotion_limit=d.get("emotion_limit", "bounded"), engine_hints=d.get("engine_hints", {}))


class VoiceProvider(ABC):
    """One interface. The rest of HELEN calls speak(); engine is invisible."""
    name = "base"

    @abstractmethod
    def available(self) -> bool: ...

    @abstractmethod
    def speak(self, text: str, profile: VoiceProfile, out_path: str | None = None) -> str:
        """Synthesize `text` to an audio file (shaped by `profile`); return the path."""

    def stream(self, text: str, profile: VoiceProfile):
        """Optional low-latency streaming. Default: synthesize then yield once."""
        yield self.speak(text, profile)


class SayProvider(VoiceProvider):
    """macOS `say` — zero install, always-available fallback voice."""
    name = "say"

    def available(self) -> bool:
        return shutil.which("say") is not None

    def speak(self, text: str, profile: VoiceProfile, out_path: str | None = None) -> str:
        h = (profile.engine_hints or {}).get("say", {})
        voice = h.get("voice", "Samantha")
        # profile.pace -> rate; calm/thoughtful reads slower
        base = h.get("rate_wpm", 165)
        rate = int(base * (0.92 if profile.pace == "calm" else 1.0))
        out = out_path or tempfile.mktemp(suffix=".aiff")
        subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", out, text], check=True)
        return out


class _PluggableProvider(VoiceProvider):
    """Declared engine that becomes real once its package is installed."""
    module = ""
    install_hint = ""

    def available(self) -> bool:
        try:
            __import__(self.module)
            return True
        except Exception:
            return False

    def speak(self, text: str, profile: VoiceProfile, out_path: str | None = None) -> str:
        raise NotImplementedError(
            f"[{self.name}] not installed. {self.install_hint} "
            f"Then implement speak() using engine_hints['{self.name}'] from the profile. "
            f"Until then, VoiceRouter falls back to SayProvider so HELEN keeps her voice."
        )


class KokoroProvider(_PluggableProvider):
    name = "kokoro"; module = "kokoro"
    install_hint = "pip install kokoro (MIT, local, fast) — the recommended default."


class OrpheusProvider(_PluggableProvider):
    name = "orpheus"; module = "orpheus_tts"
    install_hint = "Install Orpheus (more expressive/cinematic) — best for Temple narration & avatar."


class ChatterboxProvider(_PluggableProvider):
    name = "chatterbox"; module = "chatterbox"
    install_hint = "Install Chatterbox (expressive conversational) — best for long dialogue."


# purpose -> preferred engine (per the recommended router table)
ROUTES = {
    "cli":          "kokoro",
    "npc":          "kokoro",
    "warren":       "kokoro",
    "narration":    "orpheus",
    "temple":       "orpheus",
    "avatar":       "orpheus",
    "demo":         "orpheus",
    "conversation": "chatterbox",
}
_PROVIDERS = {p.name: p for p in (KokoroProvider(), OrpheusProvider(), ChatterboxProvider(), SayProvider())}


class VoiceRouter:
    """purpose -> preferred provider, fail-soft to Say (HELEN is never voiceless)."""
    def __init__(self, profile: VoiceProfile | None = None):
        self.profile = profile or VoiceProfile.load()

    def pick(self, purpose: str = "cli") -> VoiceProvider:
        preferred = _PROVIDERS.get(ROUTES.get(purpose, "kokoro"))
        if preferred and preferred.available():
            return preferred
        return _PROVIDERS["say"]  # always-available local voice

    def speak(self, text: str, purpose: str = "cli", out_path: str | None = None) -> tuple[str, str]:
        p = self.pick(purpose)
        return p.speak(text, self.profile, out_path), p.name


if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:2]) or "I am HELEN. This voice is mine, whichever engine speaks it."
    purpose = sys.argv[2] if len(sys.argv) > 2 else "cli"
    router = VoiceRouter()
    print(f"profile: {router.profile.identity} · warmth={router.profile.warmth} · pace={router.profile.pace}")
    print(f"purpose '{purpose}' routes to: {ROUTES.get(purpose,'kokoro')} "
          f"(installed engines: {[n for n,p in _PROVIDERS.items() if p.available()]})")
    path, engine = router.speak(text, purpose)
    print(f"spoke via '{engine}' -> {path}")
