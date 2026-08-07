"""Settings window extension for direct action hotkeys and translation settings."""

import copy
import logging
import re

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
)

from core.hotkey_defaults import DIRECT_ACTION_HOTKEYS, DIRECT_ACTION_LABELS
from ui.settings_window import HotkeyEdit, SettingsWindow as BaseSettingsWindow


logger = logging.getLogger(__name__)


class SettingsWindow(BaseSettingsWindow):
    """Adds direct action hotkeys and translation settings."""

    TRANSLATION_LANGUAGES = [
        "Portuguese (Brazil)",
        "English",
        "Spanish",
        "French",
        "German",
        "Italian",
        "Japanese",
        "Korean",
        "Chinese (Simplified)",
        "Chinese (Traditional)",
        "Russian",
    ]

    def _create_general_tab(self):
        tab = super()._create_general_tab()
        layout = tab.layout()

        translation_group = QGroupBox("Translation")
        translation_layout = QFormLayout()
        translation_layout.setSpacing(12)

        self.input_target_language = QComboBox()
        self.input_target_language.setEditable(True)
        self.input_target_language.addItems(self.TRANSLATION_LANGUAGES)
        self.input_target_language.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        translation_layout.addRow("Target language:", self.input_target_language)

        help_label = QLabel(
            "Language used by the Translate action. Choose a common language or type any target language."
        )
        help_label.setObjectName("subtitleLabel")
        help_label.setWordWrap(True)
        translation_layout.addRow("", help_label)

        translation_group.setLayout(translation_layout)
        layout.insertWidget(max(0, layout.count() - 1), translation_group)
        return tab

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

        target_language = self.config_manager.get(
            "translation.target_language", "English"
        )
        self.input_target_language.setCurrentText(target_language)

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

    def _apply_translation_language(self, target_language: str):
        """Apply the configured target language to the Translate prompt."""
        if not self.prompt_manager:
            return

        prompt = self.prompt_manager.get_prompt_info("translate")
        if not prompt:
            raise RuntimeError("Translate prompt is not available.")

        template = prompt.get("template", "")
        if not template:
            raise RuntimeError("Translate prompt template is empty.")

        target_line = f"Target language: {target_language}"
        target_pattern = re.compile(r"(?m)^Target language:.*$")

        if target_pattern.search(template):
            template = target_pattern.sub(target_line, template, count=1)
        else:
            marker = "You are a professional translator."
            if marker in template:
                template = template.replace(
                    marker,
                    f"{marker}\n\n{target_line}",
                    1,
                )
            else:
                template = f"{target_line}\n\n{template}"

        # Migrate the original hardcoded target sentence when present.
        legacy_pattern = re.compile(
            r"Translate the text within <text> tags into [^.\n]+\."
        )
        if legacy_pattern.search(template):
            template = legacy_pattern.sub(
                "Translate the text within <text> tags into the target language specified above.",
                template,
                count=1,
            )

        self.prompt_manager.update_prompt("translate", template=template)

        # Keep the Prompts tab editor in sync if Translate is currently selected.
        if hasattr(self, "prompt_combo") and self.prompt_combo.currentIndex() >= 0:
            if self.prompt_combo.currentData() == "translate":
                self.prompt_template_edit.setPlainText(template)

    def _on_save(self):
        action_hotkeys = self._validate_direct_hotkeys()
        if action_hotkeys is None:
            return

        target_language = self.input_target_language.currentText().strip()
        if not target_language:
            QMessageBox.warning(
                self,
                "Invalid Target Language",
                "Target language cannot be empty.",
            )
            return

        previous_values = {
            prompt_key: self.config_manager.get(
                f"hotkey.actions.{prompt_key}", default_hotkey
            )
            for prompt_key, default_hotkey in DIRECT_ACTION_HOTKEYS.items()
        }
        previous_target_language = self.config_manager.get(
            "translation.target_language", "English"
        )

        previous_user_prompts = None
        previous_prompts = None
        if self.prompt_manager:
            previous_user_prompts = copy.deepcopy(self.prompt_manager.user_prompts)
            previous_prompts = copy.deepcopy(self.prompt_manager.prompts)

        try:
            for prompt_key, hotkey in action_hotkeys.items():
                self.config_manager.set(f"hotkey.actions.{prompt_key}", hotkey)

            self.config_manager.set(
                "translation.target_language", target_language
            )
            self._apply_translation_language(target_language)

            super()._on_save()
        except Exception as exc:
            logger.error("Failed to apply extended settings: %s", exc, exc_info=True)
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Failed to apply translation settings:\n\n{exc}",
            )

        # If base validation/save failed, restore the in-memory values as well.
        if self.result() != QDialog.DialogCode.Accepted:
            for prompt_key, hotkey in previous_values.items():
                self.config_manager.set(f"hotkey.actions.{prompt_key}", hotkey)
            self.config_manager.set(
                "translation.target_language", previous_target_language
            )

            if self.prompt_manager and previous_user_prompts is not None:
                self.prompt_manager.user_prompts = previous_user_prompts
                self.prompt_manager.prompts = previous_prompts

            logger.debug("Restored extended settings after save was cancelled or failed")
