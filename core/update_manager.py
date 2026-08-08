"""GitHub Releases based update support for Bragi."""

import json
import logging
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from core.app_paths import get_resource_dir, is_installed_build
from core.brand import APP_NAME, CURRENT_REPOSITORY, LEGACY_REPOSITORIES


logger = logging.getLogger(__name__)


class UpdateManager:
    """Check, download and launch Bragi updates from GitHub Releases."""

    API_URL = f"https://api.github.com/repos/{CURRENT_REPOSITORY}/releases/latest"
    RELEASES_URL = f"https://github.com/{CURRENT_REPOSITORY}/releases"
    USER_AGENT = "Bragi-Updater"
    INSTALLER_SUFFIX = "-setup-windows-x64.exe"
    ALLOWED_DOWNLOAD_PREFIXES = tuple(
        f"https://github.com/{repository}/releases/download/"
        for repository in (CURRENT_REPOSITORY, *LEGACY_REPOSITORIES)
    )

    def __init__(self):
        self.current_version = self._read_current_version()

    @staticmethod
    def _version_tuple(version: str) -> Tuple[int, int, int]:
        match = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", version.strip())
        if not match:
            raise ValueError(f"Invalid semantic version: {version}")
        return tuple(int(part) for part in match.groups())

    @classmethod
    def _is_allowed_installer_url(cls, url: str) -> bool:
        """Return whether an installer URL belongs to a known Bragi release path."""
        normalized_url = str(url).casefold()
        return any(
            normalized_url.startswith(prefix.casefold())
            for prefix in cls.ALLOWED_DOWNLOAD_PREFIXES
        )

    def _read_current_version(self) -> str:
        version_file = get_resource_dir() / "version.txt"

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

    @staticmethod
    def is_installed_build() -> bool:
        """Return whether Bragi is running from the installed build."""
        return is_installed_build()

    def download_installer(self, update_info: Dict[str, Any]) -> Path:
        """Download the installer for a release into the user's temp directory."""
        url = update_info.get("installer_url")
        name = update_info.get("installer_name")

        if not url or not name:
            raise RuntimeError("This release does not contain a Windows installer.")

        if not self._is_allowed_installer_url(str(url)):
            raise RuntimeError("Refusing to download an installer from an unexpected URL.")

        safe_name = Path(str(name)).name
        updates_dir = Path(tempfile.gettempdir()) / APP_NAME / "updates"
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
