import asyncio
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from studio_tts_latino import core


FIXTURES_DIRECTORY = Path(__file__).resolve().parent / "fixtures"


def temporary_output_path(name: str) -> Path:
    """Aisla cada archivo de prueba dentro de un directorio ya autorizado."""
    return FIXTURES_DIRECTORY / f"test-{uuid4().hex}-{name}"


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
        output_path = temporary_output_path("successful-audio.mp3")
        self.addCleanup(output_path.unlink, missing_ok=True)

        with patch("studio_tts_latino.core.Communicate", SuccessfulCommunication):
            await self._generate(output_path)

        self.assertEqual(output_path.read_bytes(), b"audio-de-prueba")
        self.assertEqual(list(output_path.parent.glob(f".{output_path.stem}-*.part")), [])

    async def test_partial_audio_is_removed_when_streaming_fails(self):
        output_path = temporary_output_path("failed-audio.mp3")
        self.addCleanup(output_path.unlink, missing_ok=True)

        with patch("studio_tts_latino.core.Communicate", FailingCommunication):
            with self.assertRaisesRegex(RuntimeError, "conexion interrumpida"):
                await self._generate(output_path)

        self.assertFalse(output_path.exists())
        self.assertEqual(list(output_path.parent.glob(f".{output_path.stem}-*.part")), [])

    async def test_empty_audio_stream_is_rejected(self):
        output_path = temporary_output_path("empty-audio.mp3")
        self.addCleanup(output_path.unlink, missing_ok=True)

        with patch("studio_tts_latino.core.Communicate", EmptyCommunication):
            with self.assertRaisesRegex(RuntimeError, "no devolvio datos de audio"):
                await self._generate(output_path)

        self.assertFalse(output_path.exists())
        self.assertEqual(list(output_path.parent.glob(f".{output_path.stem}-*.part")), [])

    async def test_simultaneous_streams_do_not_share_a_temporary_file(self):
        output_path = temporary_output_path("simultaneous-audio.mp3")
        self.addCleanup(output_path.unlink, missing_ok=True)

        with patch("studio_tts_latino.core.Communicate", SuccessfulCommunication):
            await asyncio.gather(self._generate(output_path), self._generate(output_path))

        self.assertEqual(output_path.read_bytes(), b"audio-de-prueba")
        self.assertEqual(list(output_path.parent.glob(f".{output_path.stem}-*.part")), [])


if __name__ == "__main__":
    unittest.main()
