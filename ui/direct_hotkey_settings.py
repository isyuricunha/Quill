"""Settings extensions for Bragi direct hotkeys, translation and updates."""

import copy
import logging
import re

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
)

from core.hotkey_defaults import DIRECT_ACTION_HOTKEYS, DIRECT_ACTION_LABELS
from ui.settings_window import HotkeyEdit, SettingsWindow as BaseSettingsWindow


logger = logging.getLogger(__name__)


class SettingsWindow(BaseSettingsWindow):
    """Add Bragi-specific features to the standard settings window."""

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Bragi - Settings")

    def _create_general_tab(self):
        tab = super()._create_general_tab()
        layout = tab.layout()

        self.checkbox_startup.setText("Start Bragi with Windows")
        for label in tab.findChildren(QLabel):
            if "Launch Quill automatically" in label.text():
                label.setText(
                    "Launch Bragi automatically when you sign in to Windows."
                )

        translation_group = QGroupBox("Translation")
        translation_layout = QFormLayout()
        translation_layout.setSpacing(12)

        self.input_target_language = QComboBox()
        self.input_target_language.setEditable(True)
        self.input_target_language.addItems(self.TRANSLATION_LANGUAGES)
        self.input_target_language.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        translation_layout.addRow("Target language:", self.input_target_language)

        translation_help = QLabel(
            "Language used by the Translate action. Choose a common language or type any target language."
        )
        translation_help.setObjectName("subtitleLabel")
        translation_help.setWordWrap(True)
        translation_layout.addRow("", translation_help)

        translation_group.setLayout(translation_layout)
        layout.insertWidget(max(0, layout.count() - 1), translation_group)

        updates_group = QGroupBox("Updates")
        updates_layout = QFormLayout()
        updates_layout.setSpacing(12)

        self.checkbox_check_updates = QCheckBox("Check for updates when Bragi starts")
        updates_layout.addRow("", self.checkbox_check_updates)

        updates_help = QLabel(
            "Checks GitHub Releases once after startup. No notification is shown when Bragi is already up to date."
        )
        updates_help.setObjectName("subtitleLabel")
        updates_help.setWordWrap(True)
        updates_layout.addRow("", updates_help)

        updates_group.setLayout(updates_layout)
        layout.insertWidget(max(0, layout.count() - 1), updates_group)
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
        layout.insertWidget(max(0, layout.count() - 1), direct_group)
        return tab

    def _create_prompts_tab(self):
        tab = super()._create_prompts_tab()

        prompts_group = tab.layout().itemAt(0).widget()
        prompts_layout = prompts_group.layout()

        self.prompt_model_edit = QLineEdit()
        self.prompt_model_edit.setPlaceholderText("Leave empty to use the global model")
        self.prompt_model_edit.setToolTip(
            "Optional. When empty, this prompt uses the model configured in the API tab."
        )
        prompts_layout.insertRow(3, "Model override (optional):", self.prompt_model_edit)

        current_index = self.prompt_combo.currentIndex()
        if current_index >= 0:
            self._on_prompt_selected(current_index)

        return tab

    def _on_prompt_selected(self, index):
        super()._on_prompt_selected(index)

        if index < 0 or not self.prompt_manager or not hasattr(self, "prompt_model_edit"):
            return

        prompt_key = self.prompt_combo.itemData(index)
        prompt = self.prompt_manager.get_prompt_info(prompt_key) or {}
        self.prompt_model_edit.setText(prompt.get("model", ""))

    def _save_current_prompt(self) -> bool:
        if not super()._save_current_prompt():
            return False

        if not self.prompt_manager or not hasattr(self, "prompt_model_edit"):
            return True

        current_index = self.prompt_combo.currentIndex()
        if current_index < 0:
            return True

        prompt_key = self.prompt_combo.itemData(current_index)
        model_override = self.prompt_model_edit.text().strip()
        self.prompt_manager.update_prompt(prompt_key, model=model_override)
        self.prompt_manager.save()
        return True

    def _on_reset_prompt(self):
        super()._on_reset_prompt()

        if not self.prompt_manager or not hasattr(self, "prompt_model_edit"):
            return

        current_index = self.prompt_combo.currentIndex()
        if current_index < 0:
            return

        prompt_key = self.prompt_combo.itemData(current_index)
        prompt = self.prompt_manager.get_prompt_info(prompt_key) or {}
        self.prompt_model_edit.setText(prompt.get("model", ""))

    def _load_current_settings(self):
        super()._load_current_settings()

        target_language = self.config_manager.get(
            "translation.target_language", "English"
        )
        self.input_target_language.setCurrentText(target_language)
        self.checkbox_check_updates.setChecked(
            bool(self.config_manager.get("updates.check_on_startup", True))
        )

        for prompt_key, default_hotkey in DIRECT_ACTION_HOTKEYS.items():
            hotkey = self.config_manager.get(
                f"hotkey.actions.{prompt_key}", default_hotkey
            )
            self.input_action_hotkeys[prompt_key].set_key_sequence(hotkey)

    def _validate_direct_hotkeys(self):
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
                template = template.replace(marker, f"{marker}\n\n{target_line}", 1)
            else:
                template = f"{target_line}\n\n{template}"

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
        previous_check_updates = bool(
            self.config_manager.get("updates.check_on_startup", True)
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
            self.config_manager.set(
                "updates.check_on_startup", self.checkbox_check_updates.isChecked()
            )
            self._apply_translation_language(target_language)

            super()._on_save()
        except Exception as exc:
            logger.error("Failed to apply extended settings: %s", exc, exc_info=True)
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Failed to apply settings:\n\n{exc}",
            )

        if self.result() != QDialog.DialogCode.Accepted:
            for prompt_key, hotkey in previous_values.items():
                self.config_manager.set(f"hotkey.actions.{prompt_key}", hotkey)
            self.config_manager.set(
                "translation.target_language", previous_target_language
            )
            self.config_manager.set(
                "updates.check_on_startup", previous_check_updates
            )

            if self.prompt_manager and previous_user_prompts is not None:
                self.prompt_manager.user_prompts = previous_user_prompts
                self.prompt_manager.prompts = previous_prompts

            logger.debug("Restored extended settings after save was cancelled or failed")
