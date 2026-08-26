import unittest
from pathlib import Path

from studio_tts_latino.subtitles import split_subtitle_chunks, write_srt


class TestSubtitles(unittest.TestCase):
    def test_chunks_split_sentences_and_long_lines(self):
        chunks = split_subtitle_chunks("Primera frase. " + "palabra " * 30)
        self.assertEqual(chunks[0], "Primera frase.")
        self.assertTrue(all(len(chunk) <= 90 for chunk in chunks))

    def test_write_srt_uses_fallback_duration_without_ffprobe(self):
        output = Path(__file__).resolve().parent / "fixtures" / "subtitles-test.srt"
        self.addCleanup(output.unlink, missing_ok=True)
        audio = output.with_suffix(".mp3")
        write_srt("Hola mundo. Esta es otra frase.", audio, output)
        content = output.read_text(encoding="utf-8")
        self.assertIn("1\n00:00:00,000 -->", content)
        self.assertIn("Hola mundo.", content)
        self.assertIn("Esta es otra frase.", content)

    def test_write_srt_uses_edge_word_boundaries_when_available(self):
        output = Path(__file__).resolve().parent / "fixtures" / "subtitles-timed-test.srt"
        self.addCleanup(output.unlink, missing_ok=True)
        timings = [
            ("Hola", 0.0, 0.18),
            ("mundo,", 0.20, 0.48),
            ("esto", 0.50, 0.66),
            ("es", 0.68, 0.77),
            ("una", 0.79, 0.93),
            ("prueba.", 0.95, 1.25),
        ]
        write_srt("Texto original", output.with_suffix(".mp3"), output, word_timings=timings)
        content = output.read_text(encoding="utf-8")
        self.assertIn("00:00:00,000 --> 00:00:01,250", content)
        self.assertIn("Hola mundo, esto es una prueba.", content)


if __name__ == "__main__":
    unittest.main()
