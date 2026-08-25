import json
import unittest
from pathlib import Path

from studio_tts_latino.settings import load_preferences, save_preferences


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


if __name__ == "__main__":
    unittest.main()
