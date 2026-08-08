"""Settings extensions for Bragi direct hotkeys, translation, updates and Custom Actions."""

import copy
import logging
import re

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.hotkey_defaults import DIRECT_ACTION_HOTKEYS, DIRECT_ACTION_LABELS
from ui.settings_window import HotkeyEdit, SettingsWindow as BaseSettingsWindow


logger = logging.getLogger(__name__)


class SettingsWindow(BaseSettingsWindow):
    """Add maintained Bragi features to the standard settings window."""

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

    CRITICAL_HOTKEYS = {
        "<alt>+<f4>",
        "<ctrl>+<alt>+<delete>",
        "<ctrl>+<shift>+<esc>",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Bragi - Settings")

        if self.prompt_manager:
            self._add_custom_actions_tab()

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

        self.checkbox_check_updates = QCheckBox(
            "Check for updates when Bragi starts"
        )
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
            "Run a built-in action immediately on the selected text without opening the popup.\n"
            "Custom Action hotkeys are configured in the Custom Actions tab."
        )
        help_label.setObjectName("subtitleLabel")
        help_label.setWordWrap(True)
        direct_layout.addRow("", help_label)

        direct_group.setLayout(direct_layout)
        layout.insertWidget(max(0, layout.count() - 1), direct_group)
        return tab

    def _load_prompts(self):
        """Keep user-created Custom Actions out of the built-in Prompts editor."""
        if not self.prompt_manager:
            return

        try:
            self.prompt_combo.clear()
            for key, prompt in self.prompt_manager.prompts.items():
                if self.prompt_manager.is_custom_action(key):
                    continue
                name = prompt.get("name", key)
                self.prompt_combo.addItem(name, key)
        except Exception as exc:
            logger.error("Error loading prompts: %s", exc)

    def _create_prompts_tab(self):
        tab = super()._create_prompts_tab()

        prompts_group = tab.layout().itemAt(0).widget()
        prompts_layout = prompts_group.layout()

        self.prompt_model_edit = QLineEdit()
        self.prompt_model_edit.setPlaceholderText(
            "Leave empty to use the global model"
        )
        self.prompt_model_edit.setToolTip(
            "Optional. When empty, this prompt uses the model configured in the API tab."
        )
        prompts_layout.insertRow(
            3,
            "Model override (optional):",
            self.prompt_model_edit,
        )

        current_index = self.prompt_combo.currentIndex()
        if current_index >= 0:
            self._on_prompt_selected(current_index)

        return tab

    def _on_prompt_selected(self, index):
        super()._on_prompt_selected(index)

        if (
            index < 0
            or not self.prompt_manager
            or not hasattr(self, "prompt_model_edit")
        ):
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

    def _add_custom_actions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)

        selector_group = QGroupBox("Custom Actions")
        selector_layout = QVBoxLayout()
        selector_layout.setSpacing(10)

        selector_row = QHBoxLayout()
        self.custom_action_combo = QComboBox()
        self.custom_action_combo.currentIndexChanged.connect(
            self._on_custom_action_selected
        )
        selector_row.addWidget(self.custom_action_combo, 1)

        self.btn_new_custom_action = QPushButton("New")
        self.btn_new_custom_action.clicked.connect(self._on_new_custom_action)
        selector_row.addWidget(self.btn_new_custom_action)

        self.btn_delete_custom_action = QPushButton("Delete")
        self.btn_delete_custom_action.clicked.connect(
            self._on_delete_custom_action
        )
        selector_row.addWidget(self.btn_delete_custom_action)

        selector_layout.addLayout(selector_row)
        selector_group.setLayout(selector_layout)
        layout.addWidget(selector_group)

        editor_group = QGroupBox("Action Settings")
        editor_layout = QFormLayout()
        editor_layout.setSpacing(12)

        self.custom_action_name = QLineEdit()
        self.custom_action_name.setPlaceholderText("e.g., Make it casual")
        editor_layout.addRow("Name:", self.custom_action_name)

        self.custom_action_temperature = QLineEdit()
        self.custom_action_temperature.setPlaceholderText("0.7")
        editor_layout.addRow("Temperature:", self.custom_action_temperature)

        self.custom_action_model = QLineEdit()
        self.custom_action_model.setPlaceholderText(
            "Leave empty to use the global model"
        )
        editor_layout.addRow(
            "Model override (optional):",
            self.custom_action_model,
        )

        self.custom_action_hotkey = HotkeyEdit()
        self.custom_action_hotkey.setPlaceholderText("Leave empty to disable")
        editor_layout.addRow(
            "Direct hotkey (optional):",
            self.custom_action_hotkey,
        )

        self.custom_action_show_popup = QCheckBox("Show this action in the popup")
        editor_layout.addRow("", self.custom_action_show_popup)

        self.custom_action_template = QTextEdit()
        self.custom_action_template.setMinimumHeight(180)
        self.custom_action_template.setPlaceholderText(
            "ChatML prompt template. Include {{text}} where the selected text should be inserted."
        )
        editor_layout.addRow("Prompt:", self.custom_action_template)

        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)

        help_label = QLabel(
            "Custom Actions behave like built-in actions: they can appear in the popup, use an optional global hotkey, "
            "override the model, participate in Quick Repeat, and process the currently selected text. "
            "The prompt must contain {{text}}."
        )
        help_label.setObjectName("subtitleLabel")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        action_buttons = QHBoxLayout()
        action_buttons.addStretch()

        self.btn_apply_custom_action = QPushButton("Apply Changes")
        self.btn_apply_custom_action.clicked.connect(
            lambda: self._save_custom_action(persist=True, show_message=True)
        )
        action_buttons.addWidget(self.btn_apply_custom_action)
        layout.addLayout(action_buttons)

        layout.addStretch()
        tab.setLayout(layout)

        prompt_tab_index = -1
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == "Prompts":
                prompt_tab_index = index
                break

        if prompt_tab_index >= 0:
            self.tabs.insertTab(prompt_tab_index, tab, "Custom Actions")
        else:
            self.tabs.addTab(tab, "Custom Actions")

        self._load_custom_actions()

    def _set_custom_action_editor_enabled(self, enabled: bool):
        for widget in (
            self.custom_action_name,
            self.custom_action_temperature,
            self.custom_action_model,
            self.custom_action_hotkey,
            self.custom_action_show_popup,
            self.custom_action_template,
            self.btn_delete_custom_action,
            self.btn_apply_custom_action,
        ):
            widget.setEnabled(enabled)

    def _load_custom_actions(self, select_key=None):
        if not self.prompt_manager:
            return

        actions = self.prompt_manager.get_custom_actions()

        self.custom_action_combo.blockSignals(True)
        self.custom_action_combo.clear()

        selected_index = -1
        for index, action in enumerate(actions):
            action_key = action["key"]
            self.custom_action_combo.addItem(
                str(action.get("name", action_key)),
                action_key,
            )
            if action_key == select_key:
                selected_index = index

        self.custom_action_combo.blockSignals(False)

        if not actions:
            self._set_custom_action_editor_enabled(False)
            self.custom_action_name.clear()
            self.custom_action_temperature.clear()
            self.custom_action_model.clear()
            self.custom_action_hotkey.clear()
            self.custom_action_show_popup.setChecked(False)
            self.custom_action_template.clear()
            return

        self._set_custom_action_editor_enabled(True)
        self.custom_action_combo.setCurrentIndex(
            selected_index if selected_index >= 0 else 0
        )
        self._on_custom_action_selected(self.custom_action_combo.currentIndex())

    def _on_custom_action_selected(self, index):
        if index < 0 or not self.prompt_manager:
            self._set_custom_action_editor_enabled(False)
            return

        prompt_key = self.custom_action_combo.itemData(index)
        action = self.prompt_manager.get_prompt_info(prompt_key)
        if not action or not self.prompt_manager.is_custom_action(prompt_key):
            self._set_custom_action_editor_enabled(False)
            return

        self._set_custom_action_editor_enabled(True)
        self.custom_action_name.setText(str(action.get("name", "")))
        self.custom_action_temperature.setText(
            str(action.get("temperature", 0.7))
        )
        self.custom_action_model.setText(str(action.get("model", "")))
        self.custom_action_hotkey.set_key_sequence(
            str(action.get("hotkey", ""))
        )
        self.custom_action_show_popup.setChecked(
            bool(action.get("show_in_popup", True))
        )
        self.custom_action_template.setPlainText(
            str(action.get("template", ""))
        )

    def _on_new_custom_action(self):
        if not self.prompt_manager:
            return

        name, accepted = QInputDialog.getText(
            self,
            "New Custom Action",
            "Action name:",
        )
        if not accepted:
            return

        name = name.strip()
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Custom Action name cannot be empty.",
            )
            return

        try:
            prompt_key = self.prompt_manager.add_custom_action(name)
            self.prompt_manager.save()
            self._load_custom_actions(select_key=prompt_key)
            self.custom_action_template.setFocus()
        except Exception as exc:
            logger.error("Failed to create Custom Action: %s", exc)
            QMessageBox.warning(
                self,
                "Custom Action",
                str(exc),
            )

    def _on_delete_custom_action(self):
        if not self.prompt_manager:
            return

        index = self.custom_action_combo.currentIndex()
        if index < 0:
            return

        prompt_key = self.custom_action_combo.itemData(index)
        action_name = self.custom_action_combo.currentText()

        reply = QMessageBox.question(
            self,
            "Delete Custom Action",
            f"Delete '{action_name}'?\n\nThis cannot be reset because Custom Actions do not have a built-in default.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.prompt_manager.delete_custom_action(prompt_key)
            self.prompt_manager.save()
            self._load_custom_actions()
        except Exception as exc:
            logger.error("Failed to delete Custom Action: %s", exc)
            QMessageBox.critical(
                self,
                "Custom Action",
                f"Failed to delete action:\n\n{exc}",
            )

    def _build_hotkey_entries(
        self,
        proposed_custom_key=None,
        proposed_custom_name=None,
        proposed_custom_hotkey=None,
    ):
        entries = [
            ("Main Hotkey", self.input_hotkey.get_key_sequence()),
            ("Quick Repeat", self.input_quick_hotkey.get_key_sequence()),
        ]

        entries.extend(
            (
                DIRECT_ACTION_LABELS[prompt_key],
                edit.get_key_sequence(),
            )
            for prompt_key, edit in self.input_action_hotkeys.items()
        )

        if self.prompt_manager:
            for action in self.prompt_manager.get_custom_actions():
                action_key = action["key"]
                if action_key == proposed_custom_key:
                    continue
                entries.append(
                    (
                        str(action.get("name", action_key)),
                        str(action.get("hotkey", "")),
                    )
                )

        if proposed_custom_key is not None:
            entries.append(
                (
                    proposed_custom_name or "Custom Action",
                    proposed_custom_hotkey or "",
                )
            )

        return entries

    def _validate_hotkey_entries(self, entries) -> bool:
        seen = {}

        for label, hotkey in entries:
            hotkey = str(hotkey or "").strip()
            if not hotkey:
                continue

            normalized = hotkey.lower()

            if not any(
                modifier in normalized
                for modifier in ("<ctrl>", "<shift>", "<alt>")
            ):
                QMessageBox.warning(
                    self,
                    "Invalid Hotkey",
                    f"{label} must include at least one modifier key (Ctrl, Shift, or Alt).",
                )
                return False

            if normalized in self.CRITICAL_HOTKEYS:
                QMessageBox.warning(
                    self,
                    "Reserved Hotkey",
                    f"'{hotkey}' is a critical system hotkey and cannot be used.",
                )
                return False

            if normalized in seen:
                QMessageBox.warning(
                    self,
                    "Hotkey Conflict",
                    f"{label} uses the same hotkey as {seen[normalized]}: {hotkey}",
                )
                return False

            seen[normalized] = label

        return True

    def _save_custom_action(
        self,
        *,
        persist: bool,
        show_message: bool = False,
    ) -> bool:
        if not self.prompt_manager or not hasattr(self, "custom_action_combo"):
            return True

        index = self.custom_action_combo.currentIndex()
        if index < 0:
            return True

        prompt_key = self.custom_action_combo.itemData(index)
        name = self.custom_action_name.text().strip()
        template = self.custom_action_template.toPlainText()
        model = self.custom_action_model.text().strip()
        hotkey = self.custom_action_hotkey.get_key_sequence()

        try:
            temperature = float(self.custom_action_temperature.text().strip())
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Temperature",
                "Custom Action temperature must be a number between 0.0 and 2.0.",
            )
            return False

        entries = self._build_hotkey_entries(
            proposed_custom_key=prompt_key,
            proposed_custom_name=name or "Custom Action",
            proposed_custom_hotkey=hotkey,
        )
        if not self._validate_hotkey_entries(entries):
            return False

        try:
            self.prompt_manager.update_custom_action(
                prompt_key,
                name=name,
                template=template,
                temperature=temperature,
                model=model,
                hotkey=hotkey,
                show_in_popup=self.custom_action_show_popup.isChecked(),
            )
            if persist:
                self.prompt_manager.save()

            self.custom_action_combo.setItemText(index, name)

            if show_message:
                QMessageBox.information(
                    self,
                    "Applied",
                    "Custom Action changes applied.",
                )
            return True
        except Exception as exc:
            logger.error("Failed to save Custom Action: %s", exc)
            QMessageBox.warning(
                self,
                "Custom Action",
                str(exc),
            )
            return False

    def _load_current_settings(self):
        super()._load_current_settings()

        target_language = self.config_manager.get(
            "translation.target_language",
            "English",
        )
        self.input_target_language.setCurrentText(target_language)
        self.checkbox_check_updates.setChecked(
            bool(self.config_manager.get("updates.check_on_startup", True))
        )

        for prompt_key, default_hotkey in DIRECT_ACTION_HOTKEYS.items():
            hotkey = self.config_manager.get(
                f"hotkey.actions.{prompt_key}",
                default_hotkey,
            )
            self.input_action_hotkeys[prompt_key].set_key_sequence(hotkey)

    def _validate_direct_hotkeys(self):
        entries = self._build_hotkey_entries()
        if not self._validate_hotkey_entries(entries):
            return None

        return {
            prompt_key: edit.get_key_sequence()
            for prompt_key, edit in self.input_action_hotkeys.items()
        }

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
                template = template.replace(
                    marker,
                    f"{marker}\n\n{target_line}",
                    1,
                )
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

        if (
            hasattr(self, "prompt_combo")
            and self.prompt_combo.currentIndex() >= 0
            and self.prompt_combo.currentData() == "translate"
        ):
            self.prompt_template_edit.setPlainText(template)

    def _on_save(self):
        previous_values = {
            prompt_key: self.config_manager.get(
                f"hotkey.actions.{prompt_key}",
                default_hotkey,
            )
            for prompt_key, default_hotkey in DIRECT_ACTION_HOTKEYS.items()
        }
        previous_target_language = self.config_manager.get(
            "translation.target_language",
            "English",
        )
        previous_check_updates = bool(
            self.config_manager.get("updates.check_on_startup", True)
        )

        previous_user_prompts = None
        previous_prompts = None
        if self.prompt_manager:
            previous_user_prompts = copy.deepcopy(
                self.prompt_manager.user_prompts
            )
            previous_prompts = copy.deepcopy(self.prompt_manager.prompts)

        if not self._save_custom_action(persist=False):
            return

        action_hotkeys = self._validate_direct_hotkeys()
        if action_hotkeys is None:
            if self.prompt_manager and previous_user_prompts is not None:
                self.prompt_manager.user_prompts = previous_user_prompts
                self.prompt_manager.prompts = previous_prompts
            return

        target_language = self.input_target_language.currentText().strip()
        if not target_language:
            if self.prompt_manager and previous_user_prompts is not None:
                self.prompt_manager.user_prompts = previous_user_prompts
                self.prompt_manager.prompts = previous_prompts
            QMessageBox.warning(
                self,
                "Invalid Target Language",
                "Target language cannot be empty.",
            )
            return

        try:
            for prompt_key, hotkey in action_hotkeys.items():
                self.config_manager.set(
                    f"hotkey.actions.{prompt_key}",
                    hotkey,
                )

            self.config_manager.set(
                "translation.target_language",
                target_language,
            )
            self.config_manager.set(
                "updates.check_on_startup",
                self.checkbox_check_updates.isChecked(),
            )
            self._apply_translation_language(target_language)

            super()._on_save()
        except Exception as exc:
            logger.error(
                "Failed to apply extended settings: %s",
                exc,
                exc_info=True,
            )
            QMessageBox.critical(
                self,
                "Settings Error",
                f"Failed to apply settings:\n\n{exc}",
            )

        if self.result() != QDialog.DialogCode.Accepted:
            for prompt_key, hotkey in previous_values.items():
                self.config_manager.set(
                    f"hotkey.actions.{prompt_key}",
                    hotkey,
                )
            self.config_manager.set(
                "translation.target_language",
                previous_target_language,
            )
            self.config_manager.set(
                "updates.check_on_startup",
                previous_check_updates,
            )

            if self.prompt_manager and previous_user_prompts is not None:
                self.prompt_manager.user_prompts = previous_user_prompts
                self.prompt_manager.prompts = previous_prompts
                try:
                    self.prompt_manager.save()
                except Exception:
                    logger.exception(
                        "Failed to restore prompt storage after settings save failure"
                    )

            logger.debug(
                "Restored extended settings after save was cancelled or failed"
            )
