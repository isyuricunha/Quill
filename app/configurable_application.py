"""Bragi application layer with configurable popup action layout."""

import logging

from app.application import BragiApp as BaseBragiApp
from core.action_layout import get_visible_popup_actions
from ui.action_layout_settings import SettingsWindow


logger = logging.getLogger(__name__)


class BragiApp(BaseBragiApp):
    """Bragi application with user-configurable popup actions."""

    def _get_popup_actions(self):
        return get_visible_popup_actions(
            self.config_manager,
            self.prompt_manager,
        )

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
