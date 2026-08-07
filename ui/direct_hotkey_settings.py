"""Settings window extension for direct action hotkeys."""

import logging

from PySide6.QtWidgets import QDialog, QFormLayout, QGroupBox, QLabel, QMessageBox

from core.hotkey_defaults import DIRECT_ACTION_HOTKEYS, DIRECT_ACTION_LABELS
from ui.settings_window import HotkeyEdit, SettingsWindow as BaseSettingsWindow


logger = logging.getLogger(__name__)


class SettingsWindow(BaseSettingsWindow):
    """Adds configurable direct action hotkeys to the standard settings window."""

    def _create_hotkey_tab(self):
        tab = super()._create_hotkey_tab()
        layout = tab.layout()

        direct_group = QGroupBox("Direct Action Hotkeys")
        direct_layout = QFormLayout()
        direct_layout.setSpacing(12)

        self.input_action_hotkeys = {}
        for prompt_key, default_hotkey in DIRECT_ACTION_HOTKEYS.items():
            edit = HotkeyEdit()
            edit.setPlaceholderText("Leave empty to disable")
            self.input_action_hotkeys[prompt_key] = edit
            direct_layout.addRow(f"{DIRECT_ACTION_LABELS[prompt_key]}:", edit)

        help_label = QLabel(
            "Run an action immediately on the selected text without opening the popup.\n"
            "Leave any field empty to disable that direct hotkey."
        )
        help_label.setObjectName("subtitleLabel")
        help_label.setWordWrap(True)
        direct_layout.addRow("", help_label)

        direct_group.setLayout(direct_layout)

        # The base tab ends with a stretch. Insert the group immediately before it.
        layout.insertWidget(max(0, layout.count() - 1), direct_group)
        return tab

    def _load_current_settings(self):
        super()._load_current_settings()

        for prompt_key, default_hotkey in DIRECT_ACTION_HOTKEYS.items():
            hotkey = self.config_manager.get(
                f"hotkey.actions.{prompt_key}", default_hotkey
            )
            self.input_action_hotkeys[prompt_key].set_key_sequence(hotkey)

    def _validate_direct_hotkeys(self):
        """Validate modifiers, reserved combinations, and collisions."""
        main_hotkey = self.input_hotkey.get_key_sequence()
        quick_hotkey = self.input_quick_hotkey.get_key_sequence()
        action_hotkeys = {
            prompt_key: edit.get_key_sequence()
            for prompt_key, edit in self.input_action_hotkeys.items()
        }

        critical_hotkeys = {
            "<alt>+<f4>",
            "<ctrl>+<alt>+<delete>",
            "<ctrl>+<shift>+<esc>",
        }

        entries = [("Main Hotkey", main_hotkey), ("Quick Repeat", quick_hotkey)]
        entries.extend(
            (DIRECT_ACTION_LABELS[prompt_key], hotkey)
            for prompt_key, hotkey in action_hotkeys.items()
        )

        seen = {}
        for label, hotkey in entries:
            if not hotkey:
                continue

            normalized = hotkey.lower()

            if not any(mod in normalized for mod in ("<ctrl>", "<shift>", "<alt>")):
                QMessageBox.warning(
                    self,
                    "Invalid Hotkey",
                    f"{label} must include at least one modifier key (Ctrl, Shift, or Alt).",
                )
                return None

            if normalized in critical_hotkeys:
                QMessageBox.warning(
                    self,
                    "Reserved Hotkey",
                    f"'{hotkey}' is a critical system hotkey and cannot be used.",
                )
                return None

            if normalized in seen:
                QMessageBox.warning(
                    self,
                    "Hotkey Conflict",
                    f"{label} uses the same hotkey as {seen[normalized]}: {hotkey}",
                )
                return None

            seen[normalized] = label

        return action_hotkeys

    def _on_save(self):
        action_hotkeys = self._validate_direct_hotkeys()
        if action_hotkeys is None:
            return

        previous_values = {
            prompt_key: self.config_manager.get(
                f"hotkey.actions.{prompt_key}", default_hotkey
            )
            for prompt_key, default_hotkey in DIRECT_ACTION_HOTKEYS.items()
        }

        for prompt_key, hotkey in action_hotkeys.items():
            self.config_manager.set(f"hotkey.actions.{prompt_key}", hotkey)

        super()._on_save()

        # If base validation/save failed, restore the in-memory values as well.
        if self.result() != QDialog.DialogCode.Accepted:
            for prompt_key, hotkey in previous_values.items():
                self.config_manager.set(f"hotkey.actions.{prompt_key}", hotkey)
            logger.debug("Restored direct hotkeys after settings save was cancelled or failed")
