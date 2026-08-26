"""Preferencias y registros locales, siempre fuera del repositorio."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


LOGGER = logging.getLogger(__name__)
APPLICATION_DIRECTORY = "AlphaStudioTTSLatino"
LEGACY_APPLICATION_DIRECTORY = "StudioTTSLatino"
RENDER_HISTORY_FILENAME = "render_history.json"


def get_app_data_directory() -> Path:
    """Obtiene una carpeta privada de configuracion adecuada al sistema."""
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / APPLICATION_DIRECTORY
    return Path.home() / ".config" / APPLICATION_DIRECTORY


def get_preferences_path() -> Path:
    return get_app_data_directory() / "preferences.json"


def get_render_history_path() -> Path:
    """Ruta del historial local; contiene solo metadatos, nunca el guion."""
    return get_app_data_directory() / RENDER_HISTORY_FILENAME


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


def load_render_history(path: Optional[Path] = None) -> list[dict[str, Any]]:
    history_path = path or get_render_history_path()
    if not history_path.is_file():
        return []
    try:
        value = json.loads(history_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.warning("No se pudo leer el historial de renders: %s", exc)
        return []
    if not isinstance(value, list):
        return []
    return [entry for entry in value if isinstance(entry, dict)]


def append_render_history(
    metadata: dict[str, Any],
    path: Optional[Path] = None,
    max_entries: int = 20,
) -> Path:
    """Añade metadatos permitidos al historial y descarta cualquier texto."""
    allowed = {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "output_name": str(metadata.get("output_name", "")),
        "provider": str(metadata.get("provider", "")),
        "profile": str(metadata.get("profile", "")),
        "voice": str(metadata.get("voice", "")),
        "duration_seconds": float(metadata.get("duration_seconds", 0.0) or 0.0),
    }
    history_path = path or get_render_history_path()
    history = load_render_history(history_path)
    history.append(allowed)
    history = history[-max(1, max_entries):]
    history_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = history_path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(history_path)
    return history_path


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
