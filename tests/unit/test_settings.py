import tempfile
import unittest
from pathlib import Path

from config.settings import AppSettings, SettingsRepository


class SettingsTests(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = SettingsRepository(directory)
            settings = AppSettings(theme_mode="dark", max_concurrent=3)
            repo.save(settings)

            loaded = repo.load()

            self.assertEqual("dark", loaded.theme_mode)
            self.assertEqual(3, loaded.max_concurrent)

    def test_load_validates_numeric_and_enum_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(
                '{"theme_mode":"neon","max_concurrent":99,"concurrent_fragments":0,"retry_count":99,"timeout_seconds":1}',
                encoding="utf-8",
            )
            loaded = SettingsRepository(directory).load()

            self.assertEqual("system", loaded.theme_mode)
            self.assertEqual(4, loaded.max_concurrent)
            self.assertEqual(1, loaded.concurrent_fragments)
            self.assertEqual(15, loaded.retry_count)
            self.assertEqual(5, loaded.timeout_seconds)


if __name__ == "__main__":
    unittest.main()
