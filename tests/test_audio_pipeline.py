import unittest
from pathlib import Path
from unittest.mock import patch

from studio_tts_latino import core


FIXTURES_DIRECTORY = Path(__file__).resolve().parent / "fixtures"


class SuccessfulCommunication:
    def __init__(self, **_kwargs):
        pass

    async def stream(self):
        yield {"type": "WordBoundary", "data": b""}
        yield {"type": "audio", "data": b"audio-de-prueba"}


class FailingCommunication:
    def __init__(self, **_kwargs):
        pass

    async def stream(self):
        yield {"type": "audio", "data": b"audio-incompleto"}
        raise RuntimeError("conexion interrumpida")


class EmptyCommunication:
    def __init__(self, **_kwargs):
        pass

    async def stream(self):
        yield {"type": "WordBoundary", "data": b""}


class TestAudioPipeline(unittest.IsolatedAsyncioTestCase):
    async def _generate(self, output_path: Path) -> None:
        await core._synthesize_edge_async(
            "Hola mundo",
            output_path,
            voice="es-MX-JorgeNeural",
            rate="+0%",
            volume="+0%",
            pitch="+0Hz",
            style="newscast-formal",
            pause_ms=250,
        )

    async def test_audio_is_committed_only_after_successful_streaming(self):
        output_path = FIXTURES_DIRECTORY / "successful-audio.mp3"
        temporary_path = FIXTURES_DIRECTORY / ".successful-audio.mp3.part"
        self.addCleanup(output_path.unlink, missing_ok=True)
        self.addCleanup(temporary_path.unlink, missing_ok=True)

        with patch("studio_tts_latino.core.Communicate", SuccessfulCommunication):
            await self._generate(output_path)

        self.assertEqual(output_path.read_bytes(), b"audio-de-prueba")
        self.assertFalse(temporary_path.exists())

    async def test_partial_audio_is_removed_when_streaming_fails(self):
        output_path = FIXTURES_DIRECTORY / "failed-audio.mp3"
        temporary_path = FIXTURES_DIRECTORY / ".failed-audio.mp3.part"
        self.addCleanup(output_path.unlink, missing_ok=True)
        self.addCleanup(temporary_path.unlink, missing_ok=True)

        with patch("studio_tts_latino.core.Communicate", FailingCommunication):
            with self.assertRaisesRegex(RuntimeError, "conexion interrumpida"):
                await self._generate(output_path)

        self.assertFalse(output_path.exists())
        self.assertFalse(temporary_path.exists())

    async def test_empty_audio_stream_is_rejected(self):
        output_path = FIXTURES_DIRECTORY / "empty-audio.mp3"
        temporary_path = FIXTURES_DIRECTORY / ".empty-audio.mp3.part"
        self.addCleanup(output_path.unlink, missing_ok=True)
        self.addCleanup(temporary_path.unlink, missing_ok=True)

        with patch("studio_tts_latino.core.Communicate", EmptyCommunication):
            with self.assertRaisesRegex(RuntimeError, "no devolvio datos de audio"):
                await self._generate(output_path)

        self.assertFalse(output_path.exists())
        self.assertFalse(temporary_path.exists())


if __name__ == "__main__":
    unittest.main()
