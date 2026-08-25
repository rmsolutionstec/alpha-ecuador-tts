"""Lanzador compatible para la interfaz de comandos historica."""

from studio_tts_latino.cli import main, parse_args
from studio_tts_latino.core import *  # noqa: F403 - compatibilidad con integraciones existentes.


if __name__ == "__main__":
    main()
