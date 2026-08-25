"""Preferencias y registros locales, siempre fuera del repositorio."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional


LOGGER = logging.getLogger(__name__)
APPLICATION_DIRECTORY = "AlphaStudioTTSLatino"
LEGACY_APPLICATION_DIRECTORY = "StudioTTSLatino"


def get_app_data_directory() -> Path:
    """Obtiene una carpeta privada de configuracion adecuada al sistema."""
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / APPLICATION_DIRECTORY
    return Path.home() / ".config" / APPLICATION_DIRECTORY


def get_preferences_path() -> Path:
    return get_app_data_directory() / "preferences.json"


def get_legacy_preferences_path() -> Path:
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / LEGACY_APPLICATION_DIRECTORY / "preferences.json"
    return Path.home() / ".config" / LEGACY_APPLICATION_DIRECTORY / "preferences.json"


def load_preferences(path: Optional[Path] = None) -> dict[str, Any]:
    preferences_path = path or get_preferences_path()
    if path is None and not preferences_path.is_file():
        legacy_path = get_legacy_preferences_path()
        if legacy_path.is_file():
            preferences_path = legacy_path
    if not preferences_path.is_file():
        return {}

    try:
        preferences = json.loads(preferences_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("No se pudieron leer las preferencias: %s", exc)
        return {}

    return preferences if isinstance(preferences, dict) else {}


def save_preferences(
    preferences: dict[str, Any],
    path: Optional[Path] = None,
) -> Path:
    preferences_path = path or get_preferences_path()
    preferences_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = preferences_path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(preferences, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(preferences_path)
    return preferences_path


def configure_logging() -> Optional[Path]:
    """Activa registros tecnicos sin guardar los textos de los usuarios."""
    log_path = get_app_data_directory() / "logs" / "alpha-studio-tts-latino.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            encoding="utf-8",
        )
    except OSError:
        logging.basicConfig(level=logging.INFO)
        return None
    return log_path
