"""GitHub Releases based update support for Quill."""

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


logger = logging.getLogger(__name__)


class UpdateManager:
    """Check, download and launch Quill updates from GitHub Releases."""

    API_URL = "https://api.github.com/repos/isyuricunha/Quill/releases/latest"
    RELEASES_URL = "https://github.com/isyuricunha/Quill/releases"
    USER_AGENT = "Quill-Updater"
    INSTALLER_SUFFIX = "-setup-windows-x64.exe"

    def __init__(self):
        self.current_version = self._read_current_version()

    @staticmethod
    def _version_tuple(version: str) -> Tuple[int, int, int]:
        match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", version.strip())
        if not match:
            raise ValueError(f"Invalid semantic version: {version}")
        return tuple(int(part) for part in match.groups())

    def _read_current_version(self) -> str:
        project_root = Path(__file__).resolve().parent.parent
        version_file = project_root / "resources" / "version.txt"

        try:
            version = version_file.read_text(encoding="utf-8").strip()
            if version:
                return version.lstrip("v")
        except OSError as exc:
            logger.warning("Could not read embedded version file: %s", exc)

        return "0.0.0"

    def check_for_update(self) -> Dict[str, Any]:
        """Return metadata for the latest public GitHub release."""
        request = urllib.request.Request(
            self.API_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": self.USER_AGENT,
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        tag_name = str(payload.get("tag_name", "")).strip()
        if not tag_name:
            raise RuntimeError("GitHub returned a release without a version tag.")

        latest_version = tag_name.lstrip("v")
        current_tuple = self._version_tuple(self.current_version)
        latest_tuple = self._version_tuple(latest_version)

        installer_url: Optional[str] = None
        installer_name: Optional[str] = None
        for asset in payload.get("assets", []):
            name = str(asset.get("name", ""))
            url = str(asset.get("browser_download_url", ""))
            if name.lower().endswith(self.INSTALLER_SUFFIX) and url:
                installer_name = name
                installer_url = url
                break

        return {
            "available": latest_tuple > current_tuple,
            "current_version": self.current_version,
            "latest_version": latest_version,
            "tag_name": tag_name,
            "release_url": str(payload.get("html_url") or self.RELEASES_URL),
            "installer_url": installer_url,
            "installer_name": installer_name,
            "installed_build": self.is_installed_build(),
        }

    def is_installed_build(self) -> bool:
        """Return True when the running executable belongs to the Inno Setup install."""
        if sys.platform != "win32" or not getattr(sys, "frozen", False):
            return False

        executable_dir = Path(sys.executable).resolve().parent

        try:
            import winreg

            uninstall_key = (
                r"Software\Microsoft\Windows\CurrentVersion\Uninstall\"
                r"isyuricunha.Quill_is1"
            )
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, uninstall_key) as key:
                install_location, _ = winreg.QueryValueEx(key, "InstallLocation")

            if install_location:
                installed_dir = Path(install_location).resolve()
                if executable_dir == installed_dir:
                    return True
        except (ImportError, FileNotFoundError, OSError):
            pass

        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            expected_dir = (Path(local_app_data) / "Programs" / "Quill").resolve()
            if executable_dir == expected_dir:
                return True

        return False

    def download_installer(self, update_info: Dict[str, Any]) -> Path:
        """Download the installer for a release into the user's temp directory."""
        url = update_info.get("installer_url")
        name = update_info.get("installer_name")

        if not url or not name:
            raise RuntimeError("This release does not contain a Windows installer.")

        if not str(url).startswith(
            "https://github.com/isyuricunha/Quill/releases/download/"
        ):
            raise RuntimeError("Refusing to download an installer from an unexpected URL.")

        safe_name = Path(str(name)).name
        updates_dir = Path(tempfile.gettempdir()) / "Quill" / "updates"
        updates_dir.mkdir(parents=True, exist_ok=True)
        destination = updates_dir / safe_name

        request = urllib.request.Request(
            str(url),
            headers={"User-Agent": self.USER_AGENT},
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            with destination.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)

        if not destination.exists() or destination.stat().st_size == 0:
            raise RuntimeError("The downloaded installer is empty.")

        return destination

    @staticmethod
    def launch_installer(installer_path: Path) -> None:
        """Launch an already downloaded installer."""
        if not installer_path.exists():
            raise FileNotFoundError(f"Installer not found: {installer_path}")

        subprocess.Popen([str(installer_path)], close_fds=True)
