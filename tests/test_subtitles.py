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


if __name__ == "__main__":
    unittest.main()
