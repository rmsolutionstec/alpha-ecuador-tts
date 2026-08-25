import unittest
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import tts
from studio_tts_latino import core


FIXTURES_DIRECTORY = Path(__file__).resolve().parent / "fixtures"


class TestTTSUnit(unittest.TestCase):
    def test_preprocess_text_applies_replacements(self):
        source = "Sr. Gomez\n\n\nDr. Perez\t\thabla"
        out = tts.preprocess_text(source)
        self.assertIn("senor Gomez", out)
        self.assertIn("doctor Perez habla", out)

    def test_apply_pronunciation_map_case_insensitive(self):
        text = "OpenAI usa SQL"
        mapping = {"openai": "open ei ai", "SQL": "sequel"}
        out = tts.apply_pronunciation_map(text, mapping)
        self.assertEqual(out, "open ei ai usa sequel")

    def test_apply_delivery_tuning_clamps_values(self):
        rate, pause = tts.apply_delivery_tuning(400, -999, "comercial", "energetico")
        self.assertGreaterEqual(rate, 130)
        self.assertLessEqual(rate, 230)
        self.assertGreaterEqual(pause, 40)
        self.assertLessEqual(pause, 900)

    def test_normalize_output_path_forces_mp3(self):
        path, fmt = tts.normalize_output_path("edge", Path("salida.wav"), "wav")
        self.assertEqual(fmt, "mp3")
        self.assertEqual(path.suffix, ".mp3")

    def test_build_mastering_chain(self):
        chain = tts.build_mastering_chain("anti-sibilancia")
        self.assertIn("equalizer", chain)

    def test_default_pronunciation_dictionary_is_packaged(self):
        pronunciation_path = Path(tts.DEFAULT_PRONUNCIATION_FILE)
        self.assertTrue(pronunciation_path.is_file())
        self.assertEqual(tts.load_pronunciation_map(str(pronunciation_path))["OpenAI"], "open ei ai")

    def test_invalid_pronunciation_dictionary_is_ignored(self):
        dictionary_path = FIXTURES_DIRECTORY / f"test-{uuid4().hex}-invalid-pronunciation.json"
        self.addCleanup(dictionary_path.unlink, missing_ok=True)
        dictionary_path.write_text("[1, 2, 3]", encoding="utf-8")
        self.assertEqual(tts.load_pronunciation_map(str(dictionary_path)), {})

    def test_requested_edge_voice_has_priority_over_gender_preference(self):
        self.assertEqual(
            tts.pick_edge_voice("es-CO-GonzaloNeural", prefer_male=False),
            "es-CO-GonzaloNeural",
        )
        self.assertEqual(
            tts.pick_edge_voice("es-MX-DaliaNeural", prefer_male=True),
            "es-MX-DaliaNeural",
        )

    def test_additional_valid_edge_voice_is_preserved(self):
        self.assertEqual(
            tts.pick_edge_voice("es-EC-LuisNeural", prefer_male=False),
            "es-EC-LuisNeural",
        )

    def test_pauses_do_not_duplicate_sentence_punctuation(self):
        self.assertEqual(core._with_pauses("Hola.\nMundo.", 200), "Hola. Mundo.")

    def test_longer_pause_changes_generated_punctuation(self):
        short_pause = core._with_pauses("Hola.\nMundo.", 200)
        long_pause = core._with_pauses("Hola.\nMundo.", 900)
        self.assertNotEqual(short_pause, long_pause)

    def test_style_changes_actual_voice_parameters(self):
        documentary = tts.apply_style_tuning(180, 300, "documentary-narration", "neutro")
        casual = tts.apply_style_tuning(180, 300, "newscast-casual", "neutro")
        self.assertNotEqual(documentary, casual)
        self.assertLess(documentary[0], casual[0])
        self.assertGreater(documentary[1], casual[1])

    def test_female_local_voice_is_not_detected_as_male(self):
        female_voice = SimpleNamespace(
            gender="female",
            name="Female Spanish Voice",
            id="spanish-female",
        )
        self.assertFalse(core._is_male_voice(female_voice))

    def test_local_voice_supports_language_values_in_bytes(self):
        voice = SimpleNamespace(
            gender="female",
            name="Spanish Voice",
            id="voice-es",
            languages=[b"es-MX"],
        )
        engine = SimpleNamespace(getProperty=lambda _name: [voice])
        self.assertEqual(tts.pick_voice(engine, hint="es-mx"), "voice-es")

    def test_requested_local_voice_has_priority_over_gender_preference(self):
        male_voice = SimpleNamespace(
            gender="male",
            name="Male Spanish Voice",
            id="voice-male",
            languages=["es-MX"],
        )
        female_voice = SimpleNamespace(
            gender="female",
            name="Female Spanish Voice",
            id="voice-dalia",
            languages=["es-MX"],
        )
        engine = SimpleNamespace(getProperty=lambda _name: [male_voice, female_voice])
        self.assertEqual(tts.pick_voice(engine, hint="dalia", prefer_male=True), "voice-dalia")

    def test_apply_profile_uses_profile_defaults_when_missing(self):
        rate, volume, voice_hint, prefer_male, style, pause_ms = tts.apply_profile(
            "documental",
            rate=None,
            volume=None,
            voice_hint=None,
            prefer_male=None,
            style=None,
            pause_ms=None,
        )
        self.assertEqual(rate, 164)
        self.assertAlmostEqual(volume, 1.0)
        self.assertEqual(voice_hint, "es-CO-GonzaloNeural")
        self.assertTrue(prefer_male)
        self.assertEqual(style, "documentary-narration")
        self.assertEqual(pause_ms, 380)

    def test_apply_profile_keeps_explicit_user_values(self):
        rate, volume, voice_hint, prefer_male, style, pause_ms = tts.apply_profile(
            "locutor-latino",
            rate=230,
            volume=0.75,
            voice_hint="es-US-PalomaNeural",
            prefer_male=False,
            style="newscast-casual",
            pause_ms=40,
        )
        self.assertEqual(rate, 230)
        self.assertAlmostEqual(volume, 0.75)
        self.assertEqual(voice_hint, "es-US-PalomaNeural")
        self.assertFalse(prefer_male)
        self.assertEqual(style, "newscast-casual")
        self.assertEqual(pause_ms, 40)

    def test_engine_rejects_invalid_values_before_starting_synthesis(self):
        invalid_options = (
            ({"rate": 120}, "velocidad"),
            ({"volume": 1.1}, "volumen"),
            ({"pause_ms": 901}, "pausa"),
            ({"delivery_mode": "improvisado"}, "Modo de entrega"),
            ({"mastering_preset": "desconocido"}, "Preset de mastering"),
        )
        for overrides, error_text in invalid_options:
            with self.subTest(overrides=overrides):
                options = {
                    "rate": 180,
                    "volume": 1.0,
                    "voice_hint": None,
                    "provider": "edge",
                    "enable_mastering": False,
                }
                options.update(overrides)
                with self.assertRaisesRegex(ValueError, error_text):
                    core.synthesize("Hola", Path("salida.mp3"), **options)


if __name__ == "__main__":
    unittest.main()
