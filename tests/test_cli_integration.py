import subprocess
import sys
import unittest
from pathlib import Path


class TestCLIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[1]
        cls.python = sys.executable

    def test_cli_requires_input(self):
        result = subprocess.run(
            [self.python, "tts.py"],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        combined = (result.stdout or "") + (result.stderr or "")
        self.assertIn("Debe proporcionar --text o --file", combined)

    def test_cli_help_runs(self):
        result = subprocess.run(
            [self.python, "tts.py", "--help"],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--mastering-preset", result.stdout)

    def test_missing_input_file_has_a_clean_error(self):
        result = subprocess.run(
            [self.python, "tts.py", "--file", "archivo_inexistente.txt"],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No existe el archivo de texto", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_volume_is_rejected_before_generating_audio(self):
        result = subprocess.run(
            [self.python, "tts.py", "--text", "Hola", "--volume", "5"],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--volume debe estar entre 0.0 y 1.0", result.stderr)

    def test_package_can_be_executed_as_a_module(self):
        result = subprocess.run(
            [self.python, "-m", "studio_tts_latino", "--version"],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Studio TTS Latino 0.2.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
