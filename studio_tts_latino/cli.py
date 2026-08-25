"""Interfaz de comandos de Studio TTS Latino."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from . import APP_NAME, __version__
from .core import (
    DEFAULT_MASTERING_PRESET,
    DEFAULT_PROFILE,
    DEFAULT_PRONUNCIATION_FILE,
    DELIVERY_MODES,
    EDGE_STYLES,
    EMOTION_PRESETS,
    MASTERING_PRESETS,
    VOICE_PROFILES,
    has_ffmpeg,
    normalize_output_path,
    synthesize,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="studio-tts",
        description="Convierte texto en audio MP3 con voces latinas.",
    )
    parser.add_argument("-t", "--text", help="Texto a convertir")
    parser.add_argument("-f", "--file", help="Ruta a un archivo de texto UTF-8")
    parser.add_argument("-o", "--output", default="salida.mp3", help="Archivo MP3 de salida")
    parser.add_argument("--rate", type=int, default=None, help="Velocidad de la voz")
    parser.add_argument("--volume", type=float, default=None, help="Volumen entre 0.0 y 1.0")
    parser.add_argument("--voice-hint", default=None, help="Voz sugerida, por ejemplo es-MX-JorgeNeural")
    parser.add_argument(
        "--male",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Preferir una voz masculina cuando no se elige una voz concreta",
    )
    parser.add_argument(
        "--provider",
        choices=["local", "edge"],
        default="edge",
        help="local funciona sin internet; edge ofrece voces neurales en linea",
    )
    parser.add_argument(
        "--format",
        choices=["mp3", "wav"],
        default="mp3",
        help="Compatibilidad: la exportacion final siempre se normaliza a MP3",
    )
    parser.add_argument(
        "--profile",
        choices=sorted(VOICE_PROFILES),
        default=DEFAULT_PROFILE,
        help="Perfil de locucion preconfigurado",
    )
    parser.add_argument("--style", choices=EDGE_STYLES, default=None, help="Perfil de ritmo y tono")
    parser.add_argument(
        "--pause-ms",
        type=int,
        default=None,
        help="Intensidad orientativa de pausa entre frases; Edge no garantiza milisegundos exactos",
    )
    parser.add_argument("--no-mastering", action="store_true", help="Desactiva el postproceso")
    parser.add_argument(
        "--mastering-preset",
        choices=sorted(MASTERING_PRESETS),
        default=DEFAULT_MASTERING_PRESET,
        help="Preset de mastering de voz",
    )
    parser.add_argument("--no-natural-mode", action="store_true", help="Desactiva la normalizacion por frases")
    parser.add_argument(
        "--delivery-mode",
        choices=sorted(DELIVERY_MODES),
        default="podcast",
        help="Forma de entrega del locutor",
    )
    parser.add_argument(
        "--emotion",
        choices=sorted(EMOTION_PRESETS),
        default="neutro",
        help="Color emocional de la locucion",
    )
    parser.add_argument(
        "--pronunciation-file",
        default=DEFAULT_PRONUNCIATION_FILE,
        help="Archivo JSON con reemplazos de pronunciacion",
    )
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {__version__}")
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.text and not args.file:
        parser.error("Debe proporcionar --text o --file")
    if args.text and args.file:
        parser.error("Use solo una fuente de texto")
    if args.volume is not None and not 0.0 <= args.volume <= 1.0:
        parser.error("--volume debe estar entre 0.0 y 1.0")
    if args.rate is not None and not 130 <= args.rate <= 230:
        parser.error("--rate debe estar entre 130 y 230")
    return args


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)

    try:
        output_path, final_format = normalize_output_path(
            args.provider,
            Path(args.output),
            args.format,
        )
        if final_format != args.format:
            print(
                f"[aviso] La exportacion se fija en {final_format}; "
                f"se ajusta la salida a {output_path.name}."
            )

        pause_ms = max(0, args.pause_ms) if args.pause_ms is not None else None
        if args.text:
            text_source = args.text
        else:
            input_path = Path(args.file)
            if not input_path.is_file():
                raise ValueError(f"No existe el archivo de texto: {input_path}")
            text_source = input_path.read_text(encoding="utf-8")

        synthesize(
            text_source,
            output_path,
            args.rate,
            args.volume,
            args.voice_hint,
            prefer_male=args.male,
            provider=args.provider,
            audio_format=args.format,
            style=args.style,
            pause_ms=pause_ms,
            profile=args.profile,
            enable_mastering=not args.no_mastering,
            natural_mode=not args.no_natural_mode,
            delivery_mode=args.delivery_mode,
            emotion=args.emotion,
            pronunciation_file=args.pronunciation_file,
            mastering_preset=args.mastering_preset,
        )
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        raise SystemExit(f"[error] {exc}") from None
    except Exception as exc:
        raise SystemExit(f"[error] No se pudo generar el audio: {exc}") from None

    mastering_note = "con mastering" if not args.no_mastering and has_ffmpeg() else "sin mastering"
    print(f"Audio guardado en {output_path.resolve()} ({mastering_note})")


if __name__ == "__main__":
    main()
