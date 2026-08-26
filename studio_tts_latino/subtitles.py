"""Generación de subtítulos SRT sin conservar el guion en preferencias."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


def split_subtitle_chunks(text: str, max_chars: int = 90) -> list[str]:
    """Divide el texto en frases legibles para subtítulos."""
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]
    chunks: list[str] = []
    for sentence in sentences:
        words = sentence.split()
        current: list[str] = []
        for word in words:
            if current and len(" ".join(current + [word])) > max_chars:
                chunks.append(" ".join(current))
                current = []
            current.append(word)
        if current:
            chunks.append(" ".join(current))
    return chunks


def get_audio_duration(path: Path) -> float | None:
    """Obtiene la duración real con ffprobe cuando está disponible."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            check=True, capture_output=True, text=True,
        )
        duration = float(result.stdout.strip())
        return duration if duration > 0 else None
    except (OSError, ValueError, subprocess.CalledProcessError):
        return None


def _timestamp(seconds: float) -> str:
    millis = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def write_srt(text: str, audio_path: Path, subtitle_path: Path) -> Path:
    """Escribe subtítulos por frase distribuidos sobre la duración del audio."""
    chunks = split_subtitle_chunks(text)
    if not chunks:
        raise ValueError("No hay texto para generar subtítulos.")
    duration = get_audio_duration(audio_path)
    if duration is None:
        duration = max(1.0, len(text.split()) / 170 * 60)
    weights = [max(1, len(chunk.split())) for chunk in chunks]
    total_weight = sum(weights)
    current = 0.0
    lines: list[str] = []
    for index, (chunk, weight) in enumerate(zip(chunks, weights), start=1):
        end = duration if index == len(chunks) else current + duration * weight / total_weight
        lines.extend([str(index), f"{_timestamp(current)} --> {_timestamp(end)}", chunk, ""])
        current = end
    subtitle_path.parent.mkdir(parents=True, exist_ok=True)
    subtitle_path.write_text("\n".join(lines), encoding="utf-8")
    return subtitle_path
