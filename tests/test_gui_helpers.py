import unittest
from unittest.mock import patch

from studio_tts_latino import PROJECT_WEBSITE
from studio_tts_latino.gui import TTSApp, create_preview_path


class TestGuiHelpers(unittest.TestCase):
    @patch("studio_tts_latino.gui.webbrowser.open")
    @patch("studio_tts_latino.gui.messagebox.showwarning")
    @patch.dict("os.environ", {"STUDIO_TTS_DONATION_URL": "file:///C:/Windows/system.ini"})
    def test_support_page_rejects_non_web_urls(self, warning_mock, browser_mock):
        app = object.__new__(TTSApp)

        app.open_support_page()

        warning_mock.assert_called_once()
        browser_mock.assert_not_called()

    @patch("studio_tts_latino.gui.webbrowser.open")
    @patch.dict("os.environ", {"STUDIO_TTS_DONATION_URL": PROJECT_WEBSITE})
    def test_support_page_opens_valid_web_url(self, browser_mock):
        app = object.__new__(TTSApp)

        app.open_support_page()

        browser_mock.assert_called_once_with(PROJECT_WEBSITE)

    def test_preview_paths_are_unique_and_outside_the_project(self):
        quick_preview = create_preview_path(final_quality=False)
        final_preview = create_preview_path(final_quality=True)

        self.assertNotEqual(quick_preview, final_preview)
        self.assertEqual(quick_preview.suffix, ".mp3")
        self.assertIn("studio_tts_latino", quick_preview.parts)
        self.assertIn("rapida", quick_preview.name)
        self.assertIn("final", final_preview.name)


if __name__ == "__main__":
    unittest.main()
