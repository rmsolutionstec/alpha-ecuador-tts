import unittest
from unittest.mock import patch

from studio_tts_latino import PROJECT_WEBSITE
from studio_tts_latino.gui import TTSApp


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


if __name__ == "__main__":
    unittest.main()
