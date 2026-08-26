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


def _word_timed_captions(
    word_timings: list[tuple[str, float, float]], max_chars: int = 42, max_words: int = 7
) -> list[tuple[str, float, float]]:
    """Agrupa límites de palabra de Edge en subtítulos cortos y legibles."""
    captions: list[tuple[str, float, float]] = []
    words: list[str] = []
    start = end = 0.0
    for word, word_start, word_end in word_timings:
        cleaned = str(word).strip()
        if not cleaned:
            continue
        if words and (len(words) >= max_words or len(" ".join(words + [cleaned])) > max_chars):
            captions.append((" ".join(words), start, max(start, end)))
            words = []
        if not words:
            start = max(0.0, float(word_start))
        words.append(cleaned)
        end = max(start, float(word_end))
    if words:
        captions.append((" ".join(words), start, max(start, end)))
    return captions


def write_srt(
    text: str,
    audio_path: Path,
    subtitle_path: Path,
    word_timings: list[tuple[str, float, float]] | None = None,
) -> Path:
    """Escribe un SRT con marcas de Edge o una estimación basada en el audio."""
    timed_captions = _word_timed_captions(word_timings) if word_timings else []
    if timed_captions:
        lines: list[str] = []
        for index, (caption, start, end) in enumerate(timed_captions, start=1):
            lines.extend([str(index), f"{_timestamp(start)} --> {_timestamp(end)}", caption, ""])
        subtitle_path.parent.mkdir(parents=True, exist_ok=True)
        subtitle_path.write_text("\n".join(lines), encoding="utf-8")
        return subtitle_path

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
