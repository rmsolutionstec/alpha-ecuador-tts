import json
import unittest
from pathlib import Path
from unittest.mock import patch

from studio_tts_latino.settings import (
    append_render_history, load_preferences, load_render_history, save_preferences,
)


FIXTURES_DIRECTORY = Path(__file__).resolve().parent / "fixtures"


class TestLocalSettings(unittest.TestCase):
    def test_preferences_round_trip_without_creating_temporary_files(self):
        preferences_path = FIXTURES_DIRECTORY / "preferences-roundtrip.json"
        self.addCleanup(preferences_path.unlink, missing_ok=True)
        expected = {"profile": "documental", "rate": 164, "natural_mode": True}

        written_path = save_preferences(expected, preferences_path)

        self.assertEqual(written_path, preferences_path)
        self.assertEqual(load_preferences(preferences_path), expected)
        self.assertFalse(preferences_path.with_suffix(".tmp").exists())

    def test_missing_preferences_return_an_empty_configuration(self):
        preferences_path = FIXTURES_DIRECTORY / "missing-preferences.json"
        self.assertEqual(load_preferences(preferences_path), {})

    def test_invalid_preferences_are_ignored(self):
        preferences_path = FIXTURES_DIRECTORY / "invalid-preferences.json"
        self.addCleanup(preferences_path.unlink, missing_ok=True)
        preferences_path.write_text("{invalid", encoding="utf-8")
        with self.assertLogs("studio_tts_latino.settings", level="WARNING"):
            self.assertEqual(load_preferences(preferences_path), {})

    def test_non_object_preferences_are_ignored(self):
        preferences_path = FIXTURES_DIRECTORY / "array-preferences.json"
        self.addCleanup(preferences_path.unlink, missing_ok=True)
        preferences_path.write_text(json.dumps(["documental"]), encoding="utf-8")
        self.assertEqual(load_preferences(preferences_path), {})

    def test_legacy_preferences_are_loaded_when_the_new_path_is_missing(self):
        new_preferences_path = FIXTURES_DIRECTORY / "new-preferences.json"
        legacy_preferences_path = FIXTURES_DIRECTORY / "legacy-preferences.json"
        self.addCleanup(new_preferences_path.unlink, missing_ok=True)
        self.addCleanup(legacy_preferences_path.unlink, missing_ok=True)
        legacy_preferences_path.write_text('{"profile": "documental"}', encoding="utf-8")

        with patch("studio_tts_latino.settings.get_preferences_path", return_value=new_preferences_path):
            with patch(
                "studio_tts_latino.settings.get_legacy_preferences_path",
                return_value=legacy_preferences_path,
            ):
                self.assertEqual(load_preferences(), {"profile": "documental"})

    def test_render_history_keeps_metadata_without_script_text(self):
        history_path = FIXTURES_DIRECTORY / "render-history.json"
        self.addCleanup(history_path.unlink, missing_ok=True)
        append_render_history(
            {
                "output_name": "locucion.mp3",
                "provider": "edge",
                "profile": "locutor-latino",
                "voice": "es-MX-JorgeNeural",
                "script": "Este texto nunca debe guardarse",
            },
            history_path,
        )

        history = load_render_history(history_path)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["output_name"], "locucion.mp3")
        self.assertNotIn("script", history[0])
        self.assertNotIn("Este texto", history_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
