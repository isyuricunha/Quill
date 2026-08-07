"""Windows startup registration helper for Quill."""

import logging
import subprocess
import sys
from pathlib import Path


logger = logging.getLogger(__name__)

try:
    import winreg
except ImportError:  # pragma: no cover - winreg only exists on Windows
    winreg = None


class StartupManager:
    """Manage Quill's per-user Windows startup registration."""

    RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    VALUE_NAME = "Quill"

    def is_supported(self) -> bool:
        """Return whether Windows startup registration is available."""
        return sys.platform == "win32" and winreg is not None

    def get_startup_command(self) -> str:
        """Build the command stored in the Windows Run registry key."""
        if getattr(sys, "frozen", False):
            args = [sys.executable]
        else:
            main_path = Path(__file__).resolve().parent.parent / "main.py"
            args = [sys.executable, str(main_path)]

        return subprocess.list2cmdline(args)

    def is_enabled(self) -> bool:
        """Return whether Quill currently has a Windows Run entry."""
        if not self.is_supported():
            return False

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.RUN_KEY,
                0,
                winreg.KEY_READ,
            ) as key:
                value, _ = winreg.QueryValueEx(key, self.VALUE_NAME)
                return bool(value)
        except FileNotFoundError:
            return False
        except OSError as exc:
            raise RuntimeError(f"Failed to read Windows startup settings: {exc}") from exc

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable Quill startup for the current Windows user."""
        if not self.is_supported():
            raise RuntimeError("Windows startup registration is only available on Windows.")

        try:
            if enabled:
                with winreg.CreateKeyEx(
                    winreg.HKEY_CURRENT_USER,
                    self.RUN_KEY,
                    0,
                    winreg.KEY_SET_VALUE,
                ) as key:
                    command = self.get_startup_command()
                    winreg.SetValueEx(key, self.VALUE_NAME, 0, winreg.REG_SZ, command)
                    logger.info("Windows startup enabled: %s", command)
            else:
                try:
                    with winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        self.RUN_KEY,
                        0,
                        winreg.KEY_SET_VALUE,
                    ) as key:
                        winreg.DeleteValue(key, self.VALUE_NAME)
                    logger.info("Windows startup disabled")
                except FileNotFoundError:
                    logger.debug("Windows startup entry was already absent")
        except OSError as exc:
            action = "enable" if enabled else "disable"
            raise RuntimeError(f"Failed to {action} Windows startup: {exc}") from exc
