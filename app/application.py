"""
Bragi main application.

Integrates all components and coordinates the selected-text workflow.
"""

import logging
import sys
import threading
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QIcon

from core.config_manager import ConfigManager
from core.crypto_manager import CryptoManager
from core.ai_provider import OAICompatibleProvider
from core.hotkey_defaults import DIRECT_ACTION_HOTKEYS
from core.prompt_manager import PromptManager

from app.hotkey_manager import HotkeyManager
from app.text_processor import TextProcessor
from app.tray_manager import TrayManager

from ui.onboarding_window import OnboardingWindow
from ui.direct_hotkey_settings import SettingsWindow
from ui.popup_window import PopupWindow


logger = logging.getLogger(__name__)


class BragiApp(QApplication):
    """Main Bragi application class."""

    POPUP_ACTION_ORDER = (
        "grammar_check",
        "rewrite",
        "professional",
        "summarize",
        "translate",
    )

    error_occurred = Signal(str, str)
    _replace_text_signal = Signal(str)

    def __init__(self, argv):
        super().__init__(argv)

        self.setQuitOnLastWindowClosed(False)
        self._set_app_icon()

        logger.info("Bragi application starting...")

        self.config_manager = ConfigManager()
        self.crypto_manager = CryptoManager()
        self.ai_provider = OAICompatibleProvider()
        self.prompt_manager = PromptManager()

        self.hotkey_manager = HotkeyManager()
        self.text_processor = TextProcessor()
        self.tray_manager = TrayManager()

        self.onboarding_window = None
        self.settings_window = None
        self.popup_window = None

        self.current_text = ""

        self._last_prompt_key: str = ""
        self._last_instruction: str = ""
        self._quick_mode: bool = False
        self._direct_prompt_key: str = ""
        self._extraction_in_progress: bool = False

        self._ai_request_lock = threading.Lock()
        self._ai_request_in_progress = False

        self._connect_signals()

        if not self.config_manager.is_configured():
            logger.info("First run detected, showing onboarding")
            self._show_onboarding()
        else:
            logger.info("Configuration found, starting application")
            self._start_app()

    def _set_app_icon(self):
        project_root = Path(__file__).parent.parent
        icon_path = project_root / "resources" / "icon.ico"

        if not icon_path.exists():
            icon_path = project_root / "_internal" / "resources" / "icon.ico"

        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            logger.debug("Application icon set: %s", icon_path)
        else:
            logger.warning("Icon file not found: %s", icon_path)

    def _connect_signals(self):
        self.hotkey_manager.hotkey_pressed.connect(self._on_hotkey_pressed)
        self.hotkey_manager.quick_hotkey_pressed.connect(self._on_quick_hotkey_pressed)
        self.hotkey_manager.action_hotkey_pressed.connect(
            self._on_action_hotkey_pressed
        )

        self.text_processor.text_extracted.connect(self._on_text_extracted)
        self.text_processor.text_replaced.connect(self._on_text_replaced)

        self.tray_manager.settings_requested.connect(self._show_settings)
        self.tray_manager.pause_toggled.connect(self._on_pause_toggled)
        self.tray_manager.quit_requested.connect(self._on_quit_requested)

        self.error_occurred.connect(self._show_error_dialog)
        self._replace_text_signal.connect(self._do_replace_text)

        logger.debug("All signals connected")

    def _show_onboarding(self):
        self.onboarding_window = OnboardingWindow()
        self.onboarding_window.setup_completed.connect(self._on_onboarding_completed)
        self.onboarding_window.rejected.connect(self._on_onboarding_cancelled)
        self.onboarding_window.show()

    @Slot()
    def _on_onboarding_cancelled(self):
        logger.info("Onboarding cancelled, quitting application")
        self.quit()

    @Slot(str, str, str)
    def _on_onboarding_completed(self, base_url: str, api_key: str, model: str):
        try:
            self.config_manager.create_default_config()
            self.config_manager.set("api.base_url", base_url)
            self.config_manager.set("api.model", model)
            if api_key:
                self.config_manager.set_api_key(api_key)
            self.config_manager.save()

            logger.info("Onboarding completed, configuration saved")
            self._start_app()

        except Exception as e:
            logger.error("Error completing onboarding: %s", e)
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to save configuration: {e}",
            )
            self.quit()

    def _get_direct_action_hotkeys(self):
        action_hotkeys = {
            prompt_key: self.config_manager.get(
                f"hotkey.actions.{prompt_key}", default_hotkey
            )
            for prompt_key, default_hotkey in DIRECT_ACTION_HOTKEYS.items()
        }
        action_hotkeys.update(self.prompt_manager.get_custom_action_hotkeys())
        return action_hotkeys

    def _get_popup_actions(self):
        actions = []

        for prompt_key in self.POPUP_ACTION_ORDER:
            prompt = self.prompt_manager.get_prompt_info(prompt_key)
            if not prompt:
                continue
            actions.append(
                {
                    "key": prompt_key,
                    "name": str(prompt.get("name", prompt_key)),
                }
            )

        for action in self.prompt_manager.get_custom_actions(visible_only=True):
            actions.append(
                {
                    "key": action["key"],
                    "name": str(action.get("name", action["key"])),
                }
            )

        return actions

    def _refresh_popup_actions(self):
        if self.popup_window is not None:
            self.popup_window.set_actions(self._get_popup_actions())

    def _start_app(self):
        try:
            self.config_manager.load()

            base_url = self.config_manager.get("api.base_url")
            api_key = self.config_manager.get_api_key()
            model = self.config_manager.get("api.model")

            self.ai_provider.configure(base_url, api_key, model)
            logger.info("AI provider configured")

            hotkey = self.config_manager.get("hotkey.key", "<ctrl>+<space>")
            quick_hotkey = self.config_manager.get("hotkey.quick_key", "")
            action_hotkeys = self._get_direct_action_hotkeys()
            self.hotkey_manager.start(hotkey, quick_hotkey, action_hotkeys)
            logger.info(
                "Hotkeys started: main=%s, quick=%s, actions=%s",
                hotkey,
                quick_hotkey or "disabled",
                action_hotkeys,
            )

            self.tray_manager.create_tray_icon()
            self._create_popup_window()

            logger.info("Bragi application started successfully")

        except Exception as e:
            logger.error("Error starting application: %s", e)
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to start application: {e}\n\nPlease check your configuration.",
            )
            self.quit()

    @Slot(int, int)
    def _on_hotkey_pressed(self, x: int, y: int):
        if self._ai_request_in_progress:
            logger.debug("AI request in progress, ignoring hotkey")
            return
        if self._extraction_in_progress:
            logger.debug("Extraction in progress, ignoring main hotkey")
            return

        logger.debug("Main hotkey pressed at (%s, %s)", x, y)

        self._quick_mode = False
        self._direct_prompt_key = ""
        self._extraction_in_progress = True
        self.text_processor.extract_selected_text()

    @Slot(int, int)
    def _on_quick_hotkey_pressed(self, x: int, y: int):
        if self._ai_request_in_progress:
            logger.debug("AI request in progress, ignoring quick hotkey")
            return

        self._direct_prompt_key = ""

        if not self._last_prompt_key:
            logger.debug("No previous action, falling back to normal popup")
            self._quick_mode = False
            self._extraction_in_progress = True
            self.text_processor.extract_selected_text()
            return

        if not self.prompt_manager.get_prompt_info(self._last_prompt_key):
            logger.warning(
                "Previous prompt '%s' no longer exists", self._last_prompt_key
            )
            self.tray_manager.show_message(
                "Quick Repeat",
                f"Previous prompt '{self._last_prompt_key}' no longer exists.",
            )
            self._last_prompt_key = ""
            return

        logger.debug(
            "Quick hotkey pressed at (%s, %s), repeating: %s",
            x,
            y,
            self._last_prompt_key,
        )
        self._quick_mode = True

        if self._extraction_in_progress:
            logger.debug(
                "Extraction already in progress, will use its result in quick mode"
            )
            return

        self._extraction_in_progress = True
        self.text_processor.extract_selected_text()

    @Slot(str, int, int)
    def _on_action_hotkey_pressed(self, prompt_key: str, x: int, y: int):
        if self._ai_request_in_progress:
            logger.debug("AI request in progress, ignoring direct action hotkey")
            return
        if self._extraction_in_progress:
            logger.debug("Extraction in progress, ignoring direct action hotkey")
            return

        if not self.prompt_manager.get_prompt_info(prompt_key):
            logger.warning("Direct action prompt does not exist: %s", prompt_key)
            self.tray_manager.show_message(
                "Direct Action",
                f"Prompt '{prompt_key}' is not available.",
            )
            return

        logger.debug(
            "Direct action hotkey pressed: %s at (%s, %s)",
            prompt_key,
            x,
            y,
        )

        self._quick_mode = False
        self._direct_prompt_key = prompt_key
        self._extraction_in_progress = True
        self.text_processor.extract_selected_text()

    def _create_popup_window(self):
        if self.popup_window is not None:
            return

        self.popup_window = PopupWindow()
        self.popup_window.action_requested.connect(self._on_action_requested)
        self._refresh_popup_actions()

        self.popup_window.setWindowOpacity(0)
        self.popup_window.show()
        self.processEvents()
        self.popup_window.hide()
        self.popup_window.setWindowOpacity(1)

        logger.debug("Popup window pre-created")

    @Slot(str)
    def _on_text_extracted(self, text: str):
        self._extraction_in_progress = False

        if not text:
            logger.debug("No text selected, ignoring hotkey")
            self._quick_mode = False
            self._direct_prompt_key = ""
            return

        logger.debug(
            "Text extracted (length: %s), quick_mode=%s, direct=%s",
            len(text),
            self._quick_mode,
            self._direct_prompt_key or "none",
        )
        self.current_text = text

        if self._direct_prompt_key:
            prompt_key = self._direct_prompt_key
            self._direct_prompt_key = ""
            self._quick_mode = False
            logger.debug("Direct action mode: executing %s", prompt_key)
            self._on_action_requested(prompt_key, text, "")
            return

        if self._quick_mode:
            self._quick_mode = False
            logger.debug("Quick mode: executing %s", self._last_prompt_key)
            self._on_action_requested(
                self._last_prompt_key,
                text,
                self._last_instruction,
            )
            return

        if self.popup_window is None:
            self._create_popup_window()

        self._refresh_popup_actions()

        from PySide6.QtGui import QCursor

        cursor_pos = QCursor.pos()
        self.popup_window.show_at_position(cursor_pos.x(), cursor_pos.y(), text)

    @Slot(str, str, str)
    def _on_action_requested(self, prompt_key: str, text: str, instruction: str):
        with self._ai_request_lock:
            if self._ai_request_in_progress:
                logger.warning("AI request already in progress, ignoring")
                return
            self._ai_request_in_progress = True

        self._last_prompt_key = prompt_key
        self._last_instruction = instruction

        logger.info("Action requested: %s", prompt_key)

        threading.Thread(
            target=self._process_ai_request,
            args=(prompt_key, text, instruction),
            daemon=True,
        ).start()

    def _process_ai_request(self, prompt_key: str, text: str, instruction: str):
        try:
            messages = self.prompt_manager.get_messages(
                prompt_key,
                text,
                instruction,
            )
            temperature = self.prompt_manager.get_temperature(prompt_key)
            model_override = self.prompt_manager.get_model(prompt_key)

            additional_params = self.config_manager.get(
                "api.additional_params", {}
            )

            logger.debug(
                "Calling AI: %s messages, temp=%s, model=%s",
                len(messages),
                temperature,
                model_override or self.ai_provider.model,
            )

            response = self.ai_provider.complete(
                messages,
                temperature,
                None,
                additional_params,
                model=model_override,
            )

            logger.info("AI response received (length: %s)", len(response))
            self._replace_text_signal.emit(response)

        except Exception as e:
            logger.error("Error processing AI request: %s", e, exc_info=True)
            self.error_occurred.emit(
                "AI Request Failed",
                "Failed to process AI request:\n\n"
                f"{type(e).__name__}: {e}\n\n"
                "Please check your API configuration.",
            )
        finally:
            with self._ai_request_lock:
                self._ai_request_in_progress = False

    @Slot(str)
    def _do_replace_text(self, response: str):
        self.text_processor.replace_text(response)

    @Slot()
    def _on_text_replaced(self):
        logger.info("Text replacement completed")

    def _show_settings(self):
        logger.debug("Showing settings window")

        if self.settings_window is not None:
            try:
                self.settings_window.settings_saved.disconnect(
                    self._on_settings_saved
                )
            except RuntimeError:
                pass
            self.settings_window.close()
            self.settings_window.deleteLater()
            self.settings_window = None

        self.settings_window = SettingsWindow(
            self.config_manager,
            self.crypto_manager,
            self.prompt_manager,
        )
        self.settings_window.settings_saved.connect(self._on_settings_saved)
        self.settings_window.show()

    @Slot(dict)
    def _on_settings_saved(self, settings: dict):
        logger.info("Settings saved, reloading configuration")

        try:
            base_url = self.config_manager.get("api.base_url")
            api_key = self.config_manager.get_api_key()
            model = self.config_manager.get("api.model")

            self.ai_provider.configure(base_url, api_key, model)

            hotkey = self.config_manager.get("hotkey.key", "<ctrl>+<space>")
            quick_hotkey = self.config_manager.get("hotkey.quick_key", "")
            action_hotkeys = self._get_direct_action_hotkeys()
            self.hotkey_manager.set_hotkeys(
                hotkey,
                quick_hotkey,
                action_hotkeys,
            )
            self._refresh_popup_actions()

            logger.info("Configuration reloaded successfully")

        except Exception as e:
            logger.error("Error reloading configuration: %s", e)
            QMessageBox.warning(
                None,
                "Warning",
                f"Settings saved but failed to reload:\n{e}\n\nPlease restart Bragi.",
            )

    @Slot(bool)
    def _on_pause_toggled(self, paused: bool):
        if paused:
            self.hotkey_manager.pause()
            logger.info("Application paused")
        else:
            self.hotkey_manager.resume()
            logger.info("Application resumed")

    def _on_quit_requested(self):
        logger.info("Quit requested")

        reply = QMessageBox.question(
            None,
            "Quit Bragi",
            "Are you sure you want to quit Bragi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Quitting application, performing cleanup")

            self.hotkey_manager.stop()
            self.ai_provider.close()
            self.tray_manager.hide()

            if self.popup_window is not None:
                try:
                    self.popup_window.action_requested.disconnect(
                        self._on_action_requested
                    )
                except RuntimeError:
                    pass
                self.popup_window.close()
                self.popup_window.deleteLater()
                self.popup_window = None

            if self.settings_window is not None:
                try:
                    self.settings_window.settings_saved.disconnect(
                        self._on_settings_saved
                    )
                except RuntimeError:
                    pass
                self.settings_window.close()
                self.settings_window.deleteLater()
                self.settings_window = None

            if self.onboarding_window is not None:
                self.onboarding_window.close()
                self.onboarding_window.deleteLater()
                self.onboarding_window = None

            self.text_processor.cleanup()

            logger.info("Cleanup complete, exiting")
            self.quit()

    @Slot(str, str)
    def _show_error_dialog(self, title: str, message: str):
        QMessageBox.critical(None, title, message)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = BragiApp(sys.argv)
    sys.exit(app.exec())
