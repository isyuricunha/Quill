"""Central branding and compatibility constants for Bragi."""

APP_NAME = "Bragi"
APP_DESCRIPTION = "AI Writing Assistant"
PUBLISHER = "isyuricunha"

# Canonical repository after the completed Quill-to-Bragi rename.
CURRENT_REPOSITORY = "isyuricunha/bragi"

# Historical repository paths remain valid GitHub redirects and are accepted
# only where compatibility with older Bragi/Quill builds is useful.
LEGACY_REPOSITORIES = (
    "isyuricunha/Quill",
)

# Backwards-compatible internal alias kept for code that may still import the
# transition-era constant introduced during the rebrand.
RENAMED_REPOSITORY = CURRENT_REPOSITORY

LEGACY_APP_NAME = "Quill"
LEGACY_INSTALLER_APP_ID = "isyuricunha.Quill"

UNINSTALL_KEYS = (
    rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{LEGACY_INSTALLER_APP_ID}_is1",
    r"Software\Microsoft\Windows\CurrentVersion\Uninstall\isyuricunha.Bragi_is1",
)
