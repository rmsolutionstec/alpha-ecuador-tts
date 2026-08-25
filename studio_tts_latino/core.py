"""Motor TTS para GUI/CLI con salida profesional en MP3.

Incluye dos modos:
- edge (Microsoft neural en linea, mas natural)
- local (pyttsx3/SAPI, offline, convertido a MP3)
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Optional

from edge_tts import Communicate
import pyttsx3


LOGGER = logging.getLogger(__name__)

EDGE_DEFAULT_VOICE = "es-MX-JorgeNeural"
EDGE_MALE_VOICES = [
    "es-MX-JorgeNeural",
    "es-CO-GonzaloNeural",
    "es-AR-TomasNeural",
    "es-CL-LorenzoNeural",
    "es-PE-AlexNeural",
    "es-US-AlonsoNeural",
]
EDGE_FEMALE_VOICES = [
    "es-MX-DaliaNeural",
    "es-CO-SalomeNeural",
    "es-AR-ElenaNeural",
    "es-CL-CatalinaNeural",
    "es-PE-CamilaNeural",
    "es-US-PalomaNeural",
]
EDGE_VOICE_OPTIONS = list(dict.fromkeys([*EDGE_MALE_VOICES, *EDGE_FEMALE_VOICES, EDGE_DEFAULT_VOICE]))
EDGE_STYLES = [
    "narration-professional",
    "documentary-narration",
    "newscast-casual",
    "newscast-formal",
]

VOICE_PROFILES = {
    "locutor-latino": {
        "rate": 176,
        "volume": 1.0,
        "voice_hint": "es-MX-JorgeNeural",
        "prefer_male": True,
        "style": "newscast-formal",
        "pause_ms": 250,
    },
    "documental": {
        "rate": 164,
        "volume": 1.0,
        "voice_hint": "es-CO-GonzaloNeural",
        "prefer_male": True,
        "style": "documentary-narration",
        "pause_ms": 380,
    },
    "comercial-energetico": {
        "rate": 196,
        "volume": 1.0,
        "voice_hint": "es-MX-DaliaNeural",
        "prefer_male": False,
        "style": "newscast-casual",
        "pause_ms": 160,
    },
    "narracion-calida": {
        "rate": 168,
        "volume": 0.96,
        "voice_hint": "es-US-PalomaNeural",
        "prefer_male": False,
        "style": "narration-professional",
        "pause_ms": 320,
    },
}

DEFAULT_PROFILE = "locutor-latino"
OUTPUT_FORMAT = "mp3"
OUTPUT_BITRATE = "192k"
SUPPORTED_PROVIDERS = {"edge", "local"}
DEFAULT_PRONUNCIATION_FILE = str(
    Path(__file__).resolve().parent / "data" / "pronunciation_es_mx.json"
)
DEFAULT_MASTERING_PRESET = "suave"

MASTERING_PRESETS = {
    "suave": (
        "highpass=f=65,"
        "acompressor=threshold=-20dB:ratio=2.0:attack=20:release=180:makeup=2dB,"
        "loudnorm=I=-16:TP=-1.5:LRA=9"
    ),
    "anti-sibilancia": (
        "highpass=f=65,"
        "equalizer=f=7000:t=q:w=1.2:g=-4,"
        "acompressor=threshold=-21dB:ratio=1.9:attack=20:release=190:makeup=2dB,"
        "loudnorm=I=-16:TP=-1.5:LRA=9"
    ),
    "voz-profunda": (
        "highpass=f=55,"
        "equalizer=f=170:t=q:w=1.0:g=1.8,"
        "acompressor=threshold=-20dB:ratio=2.2:attack=20:release=180:makeup=2dB,"
        "loudnorm=I=-16:TP=-1.5:LRA=9"
    ),
}

DELIVERY_MODES = {
    "noticia": {"rate_delta": 2, "pause_delta": -20},
    "documental": {"rate_delta": -6, "pause_delta": 90},
    "comercial": {"rate_delta": 8, "pause_delta": -80},
    "podcast": {"rate_delta": -2, "pause_delta": 30},
}

EMOTION_PRESETS = {
    "neutro": {"pitch_delta": 0, "tempo_delta": 0},
    "serio": {"pitch_delta": -1, "tempo_delta": -2},
    "calido": {"pitch_delta": 1, "tempo_delta": -1},
    "energetico": {"pitch_delta": 3, "tempo_delta": 3},
}

STYLE_PRESETS = {
    "narration-professional": {"rate_delta": -3, "pitch_delta": 0, "pause_delta": 45},
    "documentary-narration": {"rate_delta": -8, "pitch_delta": -2, "pause_delta": 120},
    "newscast-casual": {"rate_delta": 5, "pitch_delta": 1, "pause_delta": -35},
    "newscast-formal": {"rate_delta": -1, "pitch_delta": -1, "pause_delta": 30},
}


def _sentence_chunks(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part.strip() for part in parts if part and part.strip()]


def _edge_rate(rate_wpm: int) -> str:
    # Edge espera un porcentaje relativo; 180 wpm como base.
    delta = int((rate_wpm - 180) / 180 * 100)
    delta = max(-50, min(50, delta))  # evita distorsión extrema
    return f"{delta:+d}%"


def _edge_volume(volume_0_1: float) -> str:
    delta = int((volume_0_1 - 1.0) * 100)
    delta = max(-50, min(20, delta))
    return f"{delta:+d}%"


def _edge_pitch(pitch_hz: int) -> str:
    pitch_hz = max(-20, min(20, int(pitch_hz)))
    return f"{pitch_hz:+d}Hz"


def _is_male_voice(voice: pyttsx3.voice.Voice) -> bool:
    gender = getattr(voice, "gender", None)
    if gender:
        normalized_gender = str(gender).lower()
        if normalized_gender.startswith("female"):
            return False
        if normalized_gender.startswith("male"):
            return True

    name = (voice.name or "").lower()
    vid = (voice.id or "").lower()
    return bool(re.search(r"\b(male|hombre|masculino|man|varon)\b", f"{name} {vid}"))


def pick_voice(engine: pyttsx3.Engine, hint: Optional[str], prefer_male: bool = False) -> Optional[str]:
    voices = engine.getProperty("voices") or []
    if not voices:
        return None

    hint_lower = hint.lower() if hint else None

    def matches_hint(v: pyttsx3.voice.Voice) -> bool:
        if not hint_lower:
            return False
        languages = []
        for language in getattr(v, "languages", []) or []:
            if isinstance(language, bytes):
                languages.append(language.decode("utf-8", errors="ignore"))
            else:
                languages.append(str(language))
        name_parts = [v.name or "", v.id or "", " ".join(languages)]
        return any(hint_lower in part.lower() for part in name_parts)

    male = [v for v in voices if _is_male_voice(v)] if prefer_male else []

    # Una voz elegida explicitamente siempre tiene prioridad sobre el genero.
    for bucket in (
        [v for v in male if matches_hint(v)],
        [v for v in voices if matches_hint(v)],
        male,
        voices,
    ):
        if bucket:
            return bucket[0].id
    return None


def pick_edge_voice(hint: Optional[str], prefer_male: bool) -> str:
    if hint:
        normalized_hint = hint.strip()
        hint_lower = normalized_hint.lower()
        for voice in EDGE_VOICE_OPTIONS:
            if hint_lower == voice.lower():
                return voice
        for voice in EDGE_VOICE_OPTIONS:
            if hint_lower in voice.lower():
                return voice
        if re.fullmatch(r"[a-z]{2}-[A-Z]{2}-[A-Za-z0-9]+Neural", normalized_hint):
            return normalized_hint

    if prefer_male:
        return EDGE_MALE_VOICES[0]
    return EDGE_FEMALE_VOICES[0]


def load_pronunciation_map(path: Optional[str]) -> dict[str, str]:
    if not path:
        return {}

    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return {}

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("No se pudo cargar el diccionario de pronunciacion %s: %s", file_path, exc)
        return {}

    if not isinstance(data, dict):
        return {}

    normalized: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, str):
            continue
        src = key.strip()
        dst = value.strip()
        if src and dst:
            normalized[src] = dst
    return normalized


def apply_pronunciation_map(text: str, pronunciation_map: dict[str, str]) -> str:
    if not pronunciation_map:
        return text

    out = text
    for src in sorted(pronunciation_map, key=len, reverse=True):
        dst = pronunciation_map[src]
        pattern = re.compile(rf"\b{re.escape(src)}\b", flags=re.IGNORECASE)
        out = pattern.sub(dst, out)
    return out


def preprocess_text(text: str) -> str:
    cleaned = (text or "").replace("\r\n", "\n").strip()
    if not cleaned:
        return ""

    replacements = {
        "Sr.": "senor",
        "Sra.": "senora",
        "Dra.": "doctora",
        "Dr.": "doctor",
        "Lic.": "licenciado",
    }
    for key, value in replacements.items():
        cleaned = cleaned.replace(key, value)

    # Uniforma espacios y evita saltos excesivos.
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def apply_delivery_tuning(
    rate: int,
    pause_ms: int,
    delivery_mode: str,
    emotion: str,
) -> tuple[int, int]:
    mode_cfg = DELIVERY_MODES.get(delivery_mode, DELIVERY_MODES["podcast"])
    emo_cfg = EMOTION_PRESETS.get(emotion, EMOTION_PRESETS["neutro"])

    tuned_rate = int(rate + mode_cfg["rate_delta"] + emo_cfg["tempo_delta"])
    tuned_pause = int(pause_ms + mode_cfg["pause_delta"])

    tuned_rate = max(130, min(230, tuned_rate))
    tuned_pause = max(40, min(900, tuned_pause))
    return tuned_rate, tuned_pause


def apply_style_tuning(
    rate: int,
    pause_ms: int,
    style: Optional[str],
    emotion: str,
) -> tuple[int, int, int]:
    """Convierte estilos descriptivos en ajustes reales soportados por Edge."""
    style_cfg = STYLE_PRESETS.get(style or "", {})
    emotion_cfg = EMOTION_PRESETS.get(emotion, EMOTION_PRESETS["neutro"])

    styled_rate = max(130, min(230, rate + int(style_cfg.get("rate_delta", 0))))
    styled_pause = max(40, min(900, pause_ms + int(style_cfg.get("pause_delta", 0))))
    styled_pitch = int(emotion_cfg["pitch_delta"]) + int(style_cfg.get("pitch_delta", 0))
    return styled_rate, styled_pause, styled_pitch


def _with_pauses(text: str, pause_ms: int) -> str:
    pause_ms = max(0, min(2000, pause_ms))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return " ".join(lines)

    normalized_lines: list[str] = []
    for line in lines[:-1]:
        if pause_ms >= 750:
            line = line.rstrip(".,;:") + "... ..."
        elif pause_ms >= 450:
            line = line.rstrip(".,;:") + "..."
        elif pause_ms >= 180 and line[-1] not in ".!?;:":
            line += "."
        normalized_lines.append(line)
    normalized_lines.append(lines[-1])
    return " ".join(normalized_lines)


async def _synthesize_edge_async(
    text: str,
    output_path: Path,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
    style: Optional[str],
    pause_ms: int,
) -> None:
    # Edge no permite SSML personalizado: los estilos se aplican a prosodia real.
    del style
    processed = _with_pauses(text, pause_ms)
    tts = Communicate(text=processed, voice=voice, rate=rate, volume=volume, pitch=pitch)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(f".{output_path.name}.part")
    try:
        received_audio = False
        with temporary_path.open("wb") as audio_file:
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                    received_audio = True
        if not received_audio:
            raise RuntimeError("El proveedor no devolvio datos de audio.")
        temporary_path.replace(output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def _naturalize_text(text: str) -> str:
    sentences = _sentence_chunks(text)
    if not sentences:
        return text

    # Evita concatenacion por archivos para prevenir artefactos; la naturalidad
    # se fuerza con puntuacion respirable y saltos entre ideas.
    normalized: list[str] = []
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue
        if s[-1] not in ".!?":
            s += "."
        normalized.append(s)

    return "\n".join(normalized)


def synthesize_edge_natural(
    text: str,
    output_path: Path,
    voice: str,
    rate_wpm: int,
    volume: float,
    style: Optional[str],
    pause_ms: int,
    emotion: str,
    pitch_hz: Optional[int] = None,
) -> bool:
    emotion_pitch = (
        pitch_hz
        if pitch_hz is not None
        else int(EMOTION_PRESETS.get(emotion, EMOTION_PRESETS["neutro"])["pitch_delta"])
    )
    processed = _naturalize_text(text)

    asyncio.run(
        _synthesize_edge_async(
            processed,
            output_path,
            voice=voice,
            rate=_edge_rate(rate_wpm),
            volume=_edge_volume(volume),
            pitch=_edge_pitch(emotion_pitch),
            style=style,
            pause_ms=pause_ms,
        )
    )
    return True


def synthesize_edge(
    text: str,
    output_path: Path,
    rate_wpm: int,
    volume: float,
    voice_hint: Optional[str],
    prefer_male: bool,
    style: Optional[str],
    pause_ms: int,
    natural_mode: bool,
    emotion: str,
) -> None:
    voice = pick_edge_voice(voice_hint, prefer_male)
    styled_rate, styled_pause, styled_pitch = apply_style_tuning(
        rate_wpm, pause_ms, style, emotion
    )
    if natural_mode and synthesize_edge_natural(
        text,
        output_path,
        voice,
        styled_rate,
        volume,
        style,
        styled_pause,
        emotion,
        pitch_hz=styled_pitch,
    ):
        return

    rate = _edge_rate(styled_rate)
    vol = _edge_volume(volume)
    asyncio.run(
        _synthesize_edge_async(
            text,
            output_path,
            voice=voice,
            rate=rate,
            volume=vol,
            pitch=_edge_pitch(styled_pitch),
            style=style,
            pause_ms=styled_pause,
        )
    )


def has_ffmpeg() -> bool:
    return get_ffmpeg_executable() is not None


def get_ffmpeg_executable() -> Optional[str]:
    found = shutil.which("ffmpeg")
    if found:
        return found

    local_appdata = os.getenv("LOCALAPPDATA")
    if not local_appdata:
        return None

    links_ffmpeg = Path(local_appdata) / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe"
    if links_ffmpeg.exists():
        return str(links_ffmpeg)

    package_root = Path(local_appdata) / "Microsoft" / "WinGet" / "Packages"
    if package_root.exists():
        candidates = sorted(
            package_root.glob("Gyan.FFmpeg_*/ffmpeg-*/bin/ffmpeg.exe"),
            key=lambda p: str(p),
            reverse=True,
        )
        if candidates:
            return str(candidates[0])

    return None


def convert_wav_to_mp3(source_wav: Path, target_mp3: Path) -> None:
    ffmpeg_exe = get_ffmpeg_executable()
    if not ffmpeg_exe:
        raise RuntimeError(
            "No se encontro ffmpeg. Instale ffmpeg para usar el proveedor local con salida MP3."
        )

    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(source_wav),
        "-codec:a",
        "libmp3lame",
        "-b:a",
        OUTPUT_BITRATE,
        str(target_mp3),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def build_mastering_chain(preset: str) -> str:
    return MASTERING_PRESETS.get(preset, MASTERING_PRESETS[DEFAULT_MASTERING_PRESET])


def master_mp3_inplace(path: Path, preset: str = DEFAULT_MASTERING_PRESET) -> bool:
    ffmpeg_exe = get_ffmpeg_executable()
    if not ffmpeg_exe:
        return False

    mastered = path.with_name(f"{path.stem}.master.mp3")
    audio_chain = build_mastering_chain(preset)
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(path),
        "-af",
        audio_chain,
        "-codec:a",
        "libmp3lame",
        "-b:a",
        OUTPUT_BITRATE,
        str(mastered),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        mastered.replace(path)
        return True
    except (OSError, subprocess.CalledProcessError) as exc:
        LOGGER.warning("No se pudo aplicar el mastering a %s: %s", path, exc)
        if mastered.exists():
            mastered.unlink(missing_ok=True)
        return False


def apply_profile(
    profile: Optional[str],
    rate: Optional[int],
    volume: Optional[float],
    voice_hint: Optional[str],
    prefer_male: Optional[bool],
    style: Optional[str],
    pause_ms: Optional[int],
) -> tuple[int, float, Optional[str], bool, Optional[str], int]:
    if not profile:
        return (
            int(rate if rate is not None else 180),
            float(volume if volume is not None else 1.0),
            voice_hint,
            bool(prefer_male) if prefer_male is not None else False,
            style,
            int(pause_ms if pause_ms is not None else 300),
        )

    preset = VOICE_PROFILES.get(profile)
    if not preset:
        raise ValueError(f"Perfil no soportado: {profile}")

    # El perfil aporta defaults, pero no debe pisar ajustes explicitos del usuario.
    final_rate = int(rate if rate is not None else preset.get("rate", 180))
    final_volume = float(volume if volume is not None else preset.get("volume", 1.0))
    final_voice_hint = voice_hint if voice_hint else preset.get("voice_hint")
    final_prefer_male = bool(prefer_male) if prefer_male is not None else bool(preset.get("prefer_male", False))
    final_style = style if style else preset.get("style")
    final_pause = int(pause_ms if pause_ms is not None else preset.get("pause_ms", 300))
    return final_rate, final_volume, final_voice_hint, final_prefer_male, final_style, final_pause


def synthesize(
    text: str,
    output_path: Path,
    rate: Optional[int],
    volume: Optional[float],
    voice_hint: Optional[str],
    prefer_male: Optional[bool] = None,
    provider: str = "local",
    audio_format: str = "mp3",
    style: Optional[str] = None,
    pause_ms: Optional[int] = None,
    profile: Optional[str] = None,
    enable_mastering: bool = True,
    natural_mode: bool = True,
    delivery_mode: str = "podcast",
    emotion: str = "neutro",
    pronunciation_file: Optional[str] = DEFAULT_PRONUNCIATION_FILE,
    mastering_preset: str = DEFAULT_MASTERING_PRESET,
) -> None:
    provider = provider.lower().strip()
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Proveedor no soportado: {provider}")

    rate, volume, voice_hint, prefer_male, style, pause_ms = apply_profile(
        profile,
        rate,
        volume,
        voice_hint,
        prefer_male,
        style,
        pause_ms,
    )

    rate, pause_ms = apply_delivery_tuning(rate, pause_ms, delivery_mode, emotion)

    text = preprocess_text(text)
    pronunciation_map = load_pronunciation_map(pronunciation_file)
    text = apply_pronunciation_map(text, pronunciation_map)
    if not text:
        raise ValueError("No hay texto valido para sintetizar")

    output_path, audio_format = normalize_output_path(provider, output_path, audio_format)

    if provider == "edge":
        synthesize_edge(
            text,
            output_path,
            rate,
            volume,
            voice_hint,
            prefer_male,
            style,
            pause_ms,
            natural_mode,
            emotion,
        )
        if enable_mastering:
            master_mp3_inplace(output_path, mastering_preset)
        return

    if not has_ffmpeg():
        raise RuntimeError(
            "El proveedor local necesita ffmpeg para convertir WAV a MP3. "
            "Use provider=edge o instale ffmpeg."
        )

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    voice_id = pick_voice(engine, voice_hint, prefer_male=prefer_male)
    if voice_id:
        engine.setProperty("voice", voice_id)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_wav = Path(tmpdir) / "local_output.wav"
        engine.save_to_file(text, str(tmp_wav))
        engine.runAndWait()
        convert_wav_to_mp3(tmp_wav, output_path)

    if enable_mastering:
        master_mp3_inplace(output_path, mastering_preset)


def normalize_output_path(provider: str, output_path: Path, audio_format: str) -> tuple[Path, str]:
    provider = provider.lower().strip()
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Proveedor no soportado: {provider}")

    final_format = OUTPUT_FORMAT
    final_path = output_path.with_suffix(f".{final_format}")
    return final_path, final_format


