import unittest

from core.brand import (
    APP_NAME,
    CURRENT_REPOSITORY,
    LEGACY_APP_NAME,
    LEGACY_INSTALLER_APP_ID,
    LEGACY_REPOSITORIES,
    RENAMED_REPOSITORY,
)
from core.update_manager import UpdateManager


class BrandingTests(unittest.TestCase):
    def test_current_product_identity_is_bragi(self):
        self.assertEqual(APP_NAME, "Bragi")
        self.assertEqual(LEGACY_APP_NAME, "Quill")

    def test_legacy_installer_identity_is_preserved_for_upgrade_compatibility(self):
        self.assertEqual(LEGACY_INSTALLER_APP_ID, "isyuricunha.Quill")

    def test_repository_identity_uses_canonical_bragi_path(self):
        self.assertEqual(CURRENT_REPOSITORY, "isyuricunha/bragi")
        self.assertEqual(RENAMED_REPOSITORY, CURRENT_REPOSITORY)
        self.assertIn("isyuricunha/Quill", LEGACY_REPOSITORIES)

    def test_updater_uses_canonical_repository(self):
        self.assertEqual(
            UpdateManager.API_URL,
            "https://api.github.com/repos/isyuricunha/bragi/releases/latest",
        )
        self.assertEqual(
            UpdateManager.RELEASES_URL,
            "https://github.com/isyuricunha/bragi/releases",
        )

    def test_updater_accepts_canonical_and_legacy_release_urls_case_insensitively(self):
        canonical = (
            "https://github.com/isyuricunha/bragi/releases/download/v2.0.1/"
            "Bragi-v2.0.1-setup-windows-x64.exe"
        )
        historical = (
            "https://github.com/isyuricunha/Quill/releases/download/v2.0.1/"
            "Bragi-v2.0.1-setup-windows-x64.exe"
        )
        transition_case = (
            "https://github.com/isyuricunha/Bragi/releases/download/v2.0.1/"
            "Bragi-v2.0.1-setup-windows-x64.exe"
        )

        self.assertTrue(UpdateManager._is_allowed_installer_url(canonical))
        self.assertTrue(UpdateManager._is_allowed_installer_url(historical))
        self.assertTrue(UpdateManager._is_allowed_installer_url(transition_case))
        self.assertFalse(
            UpdateManager._is_allowed_installer_url(
                "https://github.com/example/bragi/releases/download/v2.0.1/evil.exe"
            )
        )


if __name__ == "__main__":
    unittest.main()
