"""Windows system tray manager for Quill."""

import logging
import threading
import webbrowser
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from core.config_manager import ConfigManager
from core.update_manager import UpdateManager


logger = logging.getLogger(__name__)


class TrayManager(QObject):
    """Manage the Windows tray icon, menu and lightweight update flow."""

    settings_requested = Signal()
    pause_toggled = Signal(bool)
    quit_requested = Signal()

    update_check_finished = Signal(object, bool, str)
    update_download_finished = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tray_icon: Optional[QSystemTrayIcon] = None
        self.tray_menu: Optional[QMenu] = None
        self.is_paused: bool = False

        self.action_settings: Optional[QAction] = None
        self.action_check_updates: Optional[QAction] = None
        self.action_pause: Optional[QAction] = None
        self.action_quit: Optional[QAction] = None

        self.update_manager = UpdateManager()
        self._startup_update_check_scheduled = False
        self._update_operation_in_progress = False

        self.update_check_finished.connect(self._on_update_check_finished)
        self.update_download_finished.connect(self._on_update_download_finished)

        logger.debug("TrayManager initialized")

    def _create_default_icon(self) -> QIcon:
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#007ACC"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)

        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Q")
        painter.end()

        return QIcon(pixmap)

    def create_tray_icon(self, icon_path: Optional[str] = None):
        if self.tray_icon is not None:
            self.tray_icon.hide()
            self.tray_icon.setContextMenu(None)
            self.tray_icon.deleteLater()
            self.tray_icon = None

        if self.tray_menu is not None:
            self.tray_menu.deleteLater()
            self.tray_menu = None

        self.action_settings = None
        self.action_check_updates = None
        self.action_pause = None
        self.action_quit = None

        if icon_path is None:
            project_root = Path(__file__).parent.parent
            icon_path = project_root / "resources" / "icon.ico"

        if not Path(icon_path).exists():
            logger.warning("Icon file not found: %s, creating default icon", icon_path)
            icon = self._create_default_icon()
        else:
            icon = QIcon(str(icon_path))

        self.tray_icon = QSystemTrayIcon(icon)
        self.tray_icon.setToolTip(
            f"Quill {self.update_manager.current_version} - AI Writing Assistant"
        )

        self._create_menu()
        self.tray_icon.show()
        logger.info("Tray icon created and shown")

        if (
            not self._startup_update_check_scheduled
            and self._should_check_updates_on_startup()
        ):
            self._startup_update_check_scheduled = True
            QTimer.singleShot(1500, lambda: self.check_for_updates(manual=False))

    def _create_menu(self):
        self.tray_menu = QMenu()

        self.action_settings = QAction("Settings", self.tray_menu)
        self.action_settings.triggered.connect(self._on_settings_clicked)
        self.tray_menu.addAction(self.action_settings)

        self.action_check_updates = QAction("Check for Updates", self.tray_menu)
        self.action_check_updates.triggered.connect(self._on_check_updates_clicked)
        self.tray_menu.addAction(self.action_check_updates)

        self.tray_menu.addSeparator()

        self.action_pause = QAction("Pause", self.tray_menu)
        self.action_pause.triggered.connect(self._on_pause_clicked)
        self.tray_menu.addAction(self.action_pause)

        self.tray_menu.addSeparator()

        self.action_quit = QAction("Quit", self.tray_menu)
        self.action_quit.triggered.connect(self._on_quit_clicked)
        self.tray_menu.addAction(self.action_quit)

        self.tray_icon.setContextMenu(self.tray_menu)
        logger.debug("Tray menu created with actions")

    def _should_check_updates_on_startup(self) -> bool:
        try:
            config = ConfigManager()
            config.load()
            return bool(config.get("updates.check_on_startup", True))
        except Exception as exc:
            logger.debug("Could not read startup update preference: %s", exc)
            return False

    def _on_settings_clicked(self):
        logger.debug("Settings menu clicked")
        self.settings_requested.emit()

    def _on_check_updates_clicked(self):
        self.check_for_updates(manual=True)

    def check_for_updates(self, manual: bool = True):
        """Check GitHub Releases without blocking the UI thread."""
        if self._update_operation_in_progress:
            if manual:
                self.show_message("Quill Update", "An update operation is already running.")
            return

        self._update_operation_in_progress = True
        if self.action_check_updates:
            self.action_check_updates.setEnabled(False)

        def worker():
            try:
                info = self.update_manager.check_for_update()
                self.update_check_finished.emit(info, manual, "")
            except Exception as exc:
                logger.error("Update check failed: %s", exc, exc_info=True)
                self.update_check_finished.emit(None, manual, str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _on_update_check_finished(self, info, manual: bool, error: str):
        self._update_operation_in_progress = False
        if self.action_check_updates:
            self.action_check_updates.setEnabled(True)

        if error:
            if manual:
                QMessageBox.warning(
                    None,
                    "Update Check Failed",
                    f"Could not check for updates:\n\n{error}",
                )
            return

        if not info:
            return

        if not info.get("available"):
            if manual:
                QMessageBox.information(
                    None,
                    "Quill is Up to Date",
                    f"Quill v{info['current_version']} is the latest version.",
                )
            return

        latest = info["latest_version"]

        if not manual:
            self.show_message(
                f"Quill v{latest} available",
                "Right-click Quill and choose Check for Updates to update.",
            )
            return

        if info.get("installed_build") and info.get("installer_url"):
            reply = QMessageBox.question(
                None,
                "Update Available",
                f"Quill v{latest} is available.\n\n"
                f"Current version: v{info['current_version']}\n\n"
                "Download and start the installer now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._download_and_install(info)
            return

        reply = QMessageBox.question(
            None,
            "Update Available",
            f"Quill v{latest} is available.\n\n"
            f"Current version: v{info['current_version']}\n\n"
            "This appears to be a portable build. Open the release page?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            webbrowser.open(info.get("release_url") or UpdateManager.RELEASES_URL)

    def _download_and_install(self, info):
        self._update_operation_in_progress = True
        if self.action_check_updates:
            self.action_check_updates.setEnabled(False)

        self.show_message(
            "Quill Update",
            f"Downloading Quill v{info['latest_version']}...",
        )

        def worker():
            try:
                installer_path = self.update_manager.download_installer(info)
                self.update_download_finished.emit(str(installer_path), "")
            except Exception as exc:
                logger.error("Update download failed: %s", exc, exc_info=True)
                self.update_download_finished.emit("", str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _on_update_download_finished(self, installer_path: str, error: str):
        self._update_operation_in_progress = False
        if self.action_check_updates:
            self.action_check_updates.setEnabled(True)

        if error:
            QMessageBox.warning(
                None,
                "Update Download Failed",
                f"Could not download the update:\n\n{error}",
            )
            return

        try:
            self.update_manager.launch_installer(Path(installer_path))
            self.hide()
            app = QApplication.instance()
            if app is not None:
                app.quit()
        except Exception as exc:
            logger.error("Could not launch installer: %s", exc, exc_info=True)
            QMessageBox.critical(
                None,
                "Update Failed",
                f"The installer was downloaded but could not be started:\n\n{exc}",
            )

    def _on_pause_clicked(self):
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.action_pause.setText("Resume")
            logger.info("Application paused")
        else:
            self.action_pause.setText("Pause")
            logger.info("Application resumed")

        self.pause_toggled.emit(self.is_paused)

    def _on_quit_clicked(self):
        logger.info("Quit requested")
        self.quit_requested.emit()

    def show_message(
        self,
        title: str,
        message: str,
        icon=QSystemTrayIcon.MessageIcon.Information,
    ):
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, 3000)

    def set_paused(self, paused: bool):
        self.is_paused = paused
        if self.action_pause:
            self.action_pause.setText("Resume" if paused else "Pause")

    def hide(self):
        if self.tray_icon:
            self.tray_icon.hide()

    def show(self):
        if self.tray_icon:
            self.tray_icon.show()
