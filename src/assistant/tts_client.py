"""
Local text-to-speech (TTS) client abstraction.

Phase 1 focuses on a *working local voice path*, not a perfect celebrity clone.
We provide a small abstraction with several interchangeable backends so the
client can pick whatever runs best on their Mac Mini:

* ``piper``  - Piper: fast, fully local neural TTS. Recommended default.
* ``coqui``  - Coqui XTTS v2: supports voice *styling* from a short reference
               sample (this is where legally provided voice samples plug in).
* ``say``    - macOS built-in ``say`` command. Zero setup, great for a first
               smoke test even before installing a neural engine.
* ``none``   - No-op backend (text only), useful in headless CI/Docker.

Each backend implements ``synthesize(text, out_path)`` and writes a WAV/AIFF
file to disk. Generated audio always lands in the git-ignored ``outputs/``
directory.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from .config import TTSConfig


class TTSError(RuntimeError):
    """Raised when speech synthesis fails."""


class BaseTTS:
    """Common interface for all TTS backends."""

    def __init__(self, config: TTSConfig) -> None:
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str, out_path: Optional[Path] = None) -> Path:
        raise NotImplementedError

    def _resolve_out_path(self, out_path: Optional[Path], suffix: str) -> Path:
        if out_path is None:
            out_path = self.config.output_dir / f"assistant_reply{suffix}"
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        return out_path


class PiperTTS(BaseTTS):
    """
    Piper backend. Requires the ``piper`` binary and a downloaded voice model.

    See setup/voice_setup.md for how to install Piper and fetch a voice.
    """

    def synthesize(self, text: str, out_path: Optional[Path] = None) -> Path:
        out_path = self._resolve_out_path(out_path, ".wav")

        if shutil.which(self.config.piper_binary) is None:
            raise TTSError(
                f"Piper binary '{self.config.piper_binary}' not found on PATH. "
                "Install Piper (see setup/voice_setup.md) or switch TTS_BACKEND "
                "to 'say' for a quick local test on macOS."
            )
        if not Path(self.config.piper_model).exists():
            raise TTSError(
                f"Piper voice model not found at '{self.config.piper_model}'. "
                "Download a voice (.onnx + .onnx.json) as described in "
                "setup/voice_setup.md and set PIPER_MODEL in your .env."
            )

        # Piper reads text on stdin and writes a WAV to --output_file.
        cmd = [
            self.config.piper_binary,
            "--model",
            self.config.piper_model,
            "--output_file",
            str(out_path),
        ]
        try:
            subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as exc:  # pragma: no cover
            raise TTSError(
                f"Piper failed: {exc.stderr.decode('utf-8', errors='replace')}"
            ) from exc
        return out_path


class CoquiTTS(BaseTTS):
    """
    Coqui XTTS v2 backend with optional voice styling from a reference sample.

    XTTS can imitate the *style* of a short reference clip. This is the path
    for legally provided voice samples. It is heavier than Piper and pulls in
    the ``TTS`` Python package plus a model download on first run.
    """

    def synthesize(self, text: str, out_path: Optional[Path] = None) -> Path:
        out_path = self._resolve_out_path(out_path, ".wav")

        try:
            from TTS.api import TTS as CoquiEngine  # type: ignore
        except ImportError as exc:
            raise TTSError(
                "Coqui TTS is not installed. Install it with "
                "`pip install TTS` (see setup/voice_setup.md), or switch "
                "TTS_BACKEND to 'piper' or 'say'."
            ) from exc

        engine = CoquiEngine(self.config.coqui_model)

        kwargs = {
            "text": text,
            "file_path": str(out_path),
            "language": self.config.coqui_language,
        }
        speaker_wav = self.config.coqui_speaker_wav.strip()
        if speaker_wav:
            if not Path(speaker_wav).exists():
                raise TTSError(
                    f"COQUI_SPEAKER_WAV points to a missing file: {speaker_wav}. "
                    "Place a legally provided sample in voice_samples/ and update .env."
                )
            kwargs["speaker_wav"] = speaker_wav

        try:
            engine.tts_to_file(**kwargs)
        except Exception as exc:  # pragma: no cover - heavy runtime path
            raise TTSError(f"Coqui XTTS synthesis failed: {exc}") from exc
        return out_path


class MacSayTTS(BaseTTS):
    """
    macOS built-in ``say`` command. Requires no installation on a Mac and is
    the fastest way to verify the end-to-end demo before adding a neural voice.
    Produces AIFF (Apple's native format for ``say``).
    """

    def synthesize(self, text: str, out_path: Optional[Path] = None) -> Path:
        out_path = self._resolve_out_path(out_path, ".aiff")
        if shutil.which("say") is None:
            raise TTSError(
                "The macOS `say` command was not found. This backend only works "
                "on macOS. On other platforms use 'piper' or 'coqui'."
            )
        cmd = ["say", "-o", str(out_path), text]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:  # pragma: no cover
            raise TTSError(
                f"macOS `say` failed: {exc.stderr.decode('utf-8', errors='replace')}"
            ) from exc
        return out_path


class NoopTTS(BaseTTS):
    """Text-only backend that writes a .txt transcript instead of audio.

    Useful in headless environments (CI, Docker) where no audio engine is set
    up but the demo flow should still complete without error.
    """

    def synthesize(self, text: str, out_path: Optional[Path] = None) -> Path:
        out_path = self._resolve_out_path(out_path, ".txt")
        out_path.write_text(text, encoding="utf-8")
        return out_path


def build_tts_client(config: TTSConfig) -> BaseTTS:
    """Factory returning the TTS backend selected by ``TTS_BACKEND``."""
    backend = config.backend.lower()
    backends = {
        "piper": PiperTTS,
        "coqui": CoquiTTS,
        "say": MacSayTTS,
        "none": NoopTTS,
    }
    if backend not in backends:
        raise TTSError(
            f"Unsupported TTS backend '{config.backend}'. "
            f"Choose one of: {', '.join(sorted(backends))}."
        )
    return backends[backend](config)
