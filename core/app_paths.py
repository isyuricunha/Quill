"""Application path helpers for installed and portable Bragi builds."""

import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List

from core.brand import APP_NAME, LEGACY_APP_NAME, UNINSTALL_KEYS


logger = logging.getLogger(__name__)

USER_DATA_FILES = ("config.json", "user_prompts.json")


def get_app_dir() -> Path:
    """Return the directory containing Bragi.exe, or the project root in development."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_runtime_root() -> Path:
    """Return the root containing bundled runtime resources."""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass).resolve()
    return Path(__file__).resolve().parent.parent


def get_resource_dir() -> Path:
    """Return the directory containing bundled Bragi resources."""
    return get_runtime_root() / "resources"


def is_installed_build() -> bool:
    """Return True when Bragi is running from a per-user Inno Setup installation."""
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return False

    executable_dir = get_app_dir()

    try:
        import winreg

        for uninstall_key in UNINSTALL_KEYS:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, uninstall_key) as key:
                    install_location, _ = winreg.QueryValueEx(key, "InstallLocation")

                if install_location:
                    installed_dir = Path(install_location).resolve()
                    if executable_dir == installed_dir:
                        return True
            except FileNotFoundError:
                continue
    except (ImportError, OSError):
        pass

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        programs_dir = Path(local_app_data) / "Programs"
        expected_dirs = (
            (programs_dir / APP_NAME).resolve(),
            (programs_dir / LEGACY_APP_NAME).resolve(),
        )
        if executable_dir in expected_dirs:
            return True

    return False


def _legacy_data_dirs() -> List[Path]:
    """Return known locations used by Bragi and its Quill predecessor."""
    candidates = [
        get_app_dir() / "data",
        get_runtime_root() / "data",
        Path(__file__).resolve().parent.parent / "data",
    ]

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / LEGACY_APP_NAME)
    else:
        candidates.append(Path.home() / "AppData" / "Local" / LEGACY_APP_NAME)

    unique: List[Path] = []
    seen = set()
    for candidate in candidates:
        normalized = str(candidate.resolve())
        if normalized not in seen:
            seen.add(normalized)
            unique.append(candidate)

    return unique


def migrate_legacy_user_data(target_dir: Path) -> None:
    """Copy legacy config and prompt files into Bragi's current data directory.

    Existing destination files always win. Legacy files are intentionally left in
    place so downgrades or manual recovery remain possible.
    """
    target_dir = Path(target_dir)

    for filename in USER_DATA_FILES:
        destination = target_dir / filename
        if destination.exists():
            continue

        for legacy_dir in _legacy_data_dirs():
            source = legacy_dir / filename

            try:
                if source.resolve() == destination.resolve():
                    continue
            except OSError:
                pass

            if not source.is_file():
                continue

            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                logger.info(
                    "Migrated legacy user data: %s -> %s",
                    source,
                    destination,
                )
            except OSError as exc:
                logger.warning(
                    "Failed to migrate legacy user data %s: %s",
                    source,
                    exc,
                )
            break


def get_user_data_dir() -> Path:
    """Return Bragi's writable user-data directory for the current build mode.

    Installed builds use %LOCALAPPDATA%/Bragi. Portable and development builds
    keep their data beside the executable/project in ./data. Existing Quill data
    is copied automatically on first use when the Bragi destination is empty.
    """
    if is_installed_build():
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            target_dir = Path(local_app_data) / APP_NAME
        else:
            target_dir = Path.home() / "AppData" / "Local" / APP_NAME
    else:
        target_dir = get_app_dir() / "data"

    migrate_legacy_user_data(target_dir)
    return target_dir
