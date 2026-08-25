import unittest

from studio_tts_latino import PROJECT_WEBSITE
from studio_tts_latino.gui import create_preview_path, is_safe_support_url


class TestGuiHelpers(unittest.TestCase):
    def test_support_page_rejects_non_web_urls(self):
        self.assertFalse(is_safe_support_url("file:///C:/Windows/system.ini"))

    def test_support_page_accepts_valid_web_url(self):
        self.assertTrue(is_safe_support_url(PROJECT_WEBSITE))

    def test_preview_paths_are_unique_and_outside_the_project(self):
        quick_preview = create_preview_path(final_quality=False)
        final_preview = create_preview_path(final_quality=True)

        self.assertNotEqual(quick_preview, final_preview)
        self.assertEqual(quick_preview.suffix, ".mp3")
        self.assertIn("alpha_studio_tts_latino", quick_preview.parts)
        self.assertIn("rapida", quick_preview.name)
        self.assertIn("final", final_preview.name)


if __name__ == "__main__":
    unittest.main()
