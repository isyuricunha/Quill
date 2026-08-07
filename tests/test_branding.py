import unittest

from core.brand import (
    APP_NAME,
    CURRENT_REPOSITORY,
    LEGACY_APP_NAME,
    LEGACY_INSTALLER_APP_ID,
    RENAMED_REPOSITORY,
)


class BrandingTests(unittest.TestCase):
    def test_current_product_identity_is_bragi(self):
        self.assertEqual(APP_NAME, "Bragi")
        self.assertEqual(LEGACY_APP_NAME, "Quill")

    def test_legacy_installer_identity_is_preserved_for_upgrade_compatibility(self):
        self.assertEqual(LEGACY_INSTALLER_APP_ID, "isyuricunha.Quill")

    def test_updater_knows_both_repository_names(self):
        self.assertEqual(CURRENT_REPOSITORY, "isyuricunha/Quill")
        self.assertEqual(RENAMED_REPOSITORY, "isyuricunha/Bragi")


if __name__ == "__main__":
    unittest.main()
