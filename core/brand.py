"""Central branding and compatibility constants for Bragi."""

APP_NAME = "Bragi"
APP_DESCRIPTION = "AI Writing Assistant"
PUBLISHER = "isyuricunha"

# The repository is still reachable through the historical fork URL. GitHub
# redirects renamed repositories, so keeping this endpoint also protects older
# clients during the repository rename transition.
CURRENT_REPOSITORY = "isyuricunha/Quill"
RENAMED_REPOSITORY = "isyuricunha/Bragi"

LEGACY_APP_NAME = "Quill"
LEGACY_INSTALLER_APP_ID = "isyuricunha.Quill"

UNINSTALL_KEYS = (
    rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{LEGACY_INSTALLER_APP_ID}_is1",
    r"Software\Microsoft\Windows\CurrentVersion\Uninstall\isyuricunha.Bragi_is1",
)
