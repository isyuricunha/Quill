import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core import app_paths


class AppPathsTests(unittest.TestCase):
    def test_portable_data_lives_beside_executable_and_migrates_legacy_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            app_dir = root / "portable"
            runtime_root = app_dir / "_internal"
            legacy_data = runtime_root / "data"
            legacy_data.mkdir(parents=True)
            (legacy_data / "config.json").write_text('{"portable": true}', encoding="utf-8")
            (legacy_data / "user_prompts.json").write_text('{"rewrite": {}}', encoding="utf-8")

            with (
                patch.object(app_paths, "is_installed_build", return_value=False),
                patch.object(app_paths, "get_app_dir", return_value=app_dir),
                patch.object(app_paths, "get_runtime_root", return_value=runtime_root),
            ):
                data_dir = app_paths.get_user_data_dir()

            self.assertEqual(data_dir, app_dir / "data")
            self.assertEqual(
                (data_dir / "config.json").read_text(encoding="utf-8"),
                '{"portable": true}',
            )
            self.assertTrue((data_dir / "user_prompts.json").exists())

    def test_installed_data_lives_in_bragi_localappdata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            install_dir = root / "Programs" / "Bragi"
            runtime_root = install_dir / "_internal"
            local_app_data = root / "LocalAppData"

            with (
                patch.object(app_paths, "is_installed_build", return_value=True),
                patch.object(app_paths, "get_app_dir", return_value=install_dir),
                patch.object(app_paths, "get_runtime_root", return_value=runtime_root),
                patch.dict(os.environ, {"LOCALAPPDATA": str(local_app_data)}),
            ):
                data_dir = app_paths.get_user_data_dir()

            self.assertEqual(data_dir, local_app_data / "Bragi")

    def test_installed_bragi_migrates_quill_localappdata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            install_dir = root / "Programs" / "Bragi"
            runtime_root = install_dir / "_internal"
            local_app_data = root / "LocalAppData"
            legacy_data = local_app_data / "Quill"
            legacy_data.mkdir(parents=True)
            (legacy_data / "config.json").write_text('{"from": "quill"}', encoding="utf-8")
            (legacy_data / "user_prompts.json").write_text('{"rewrite": {}}', encoding="utf-8")

            with (
                patch.object(app_paths, "is_installed_build", return_value=True),
                patch.object(app_paths, "get_app_dir", return_value=install_dir),
                patch.object(app_paths, "get_runtime_root", return_value=runtime_root),
                patch.dict(os.environ, {"LOCALAPPDATA": str(local_app_data)}),
            ):
                data_dir = app_paths.get_user_data_dir()

            self.assertEqual(data_dir, local_app_data / "Bragi")
            self.assertEqual(
                (data_dir / "config.json").read_text(encoding="utf-8"),
                '{"from": "quill"}',
            )
            self.assertTrue((data_dir / "user_prompts.json").exists())
            self.assertTrue((legacy_data / "config.json").exists())

    def test_existing_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            install_dir = root / "Programs" / "Bragi"
            runtime_root = install_dir / "_internal"
            local_app_data = root / "LocalAppData"
            legacy_data = local_app_data / "Quill"
            target_data = local_app_data / "Bragi"
            legacy_data.mkdir(parents=True)
            target_data.mkdir(parents=True)

            (legacy_data / "config.json").write_text("legacy", encoding="utf-8")
            (target_data / "config.json").write_text("current", encoding="utf-8")

            with (
                patch.object(app_paths, "is_installed_build", return_value=True),
                patch.object(app_paths, "get_app_dir", return_value=install_dir),
                patch.object(app_paths, "get_runtime_root", return_value=runtime_root),
                patch.dict(os.environ, {"LOCALAPPDATA": str(local_app_data)}),
            ):
                app_paths.get_user_data_dir()

            self.assertEqual(
                (target_data / "config.json").read_text(encoding="utf-8"),
                "current",
            )


if __name__ == "__main__":
    unittest.main()
