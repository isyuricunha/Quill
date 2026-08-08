"""Settings layer for popup action ordering and visibility."""

import copy
import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.action_layout import (
    POPUP_ACTION_HIDDEN_KEY,
    POPUP_ACTION_ORDER_KEY,
    get_available_popup_actions,
    get_popup_action_layout,
    normalize_popup_layout,
    restore_builtin_defaults,
)
from ui.direct_hotkey_settings import SettingsWindow as BaseSettingsWindow


logger = logging.getLogger(__name__)


class SettingsWindow(BaseSettingsWindow):
    """Add a unified Popup Actions organizer on top of Bragi settings."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.prompt_manager:
            return

        self.popup_action_order, self.popup_hidden_actions = get_popup_action_layout(
            self.config_manager,
            self.prompt_manager,
        )
        self._add_popup_actions_tab()

        # v2.1 stored Custom Action visibility in the Custom Actions editor.
        # Keep that field for compatibility with persisted data, but make the
        # new Popup Actions tab the single user-facing source of truth.
        if hasattr(self, "custom_action_show_popup"):
            self.custom_action_show_popup.setVisible(False)

    def _add_popup_actions_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)

        group = QGroupBox("Popup Actions")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)

        help_label = QLabel(
            "Choose which actions appear in the popup and the order they use. "
            "Hidden actions are not deleted and direct hotkeys continue to work."
        )
        help_label.setObjectName("subtitleLabel")
        help_label.setWordWrap(True)
        group_layout.addWidget(help_label)

        self.popup_actions_list = QListWidget()
        self.popup_actions_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.popup_actions_list.itemChanged.connect(
            lambda _item: self._capture_popup_layout()
        )
        group_layout.addWidget(self.popup_actions_list)

        controls = QHBoxLayout()

        self.btn_popup_action_up = QPushButton("Move Up")
        self.btn_popup_action_up.clicked.connect(
            lambda: self._move_popup_action(-1)
        )
        controls.addWidget(self.btn_popup_action_up)

        self.btn_popup_action_down = QPushButton("Move Down")
        self.btn_popup_action_down.clicked.connect(
            lambda: self._move_popup_action(1)
        )
        controls.addWidget(self.btn_popup_action_down)

        controls.addStretch()

        self.btn_restore_popup_defaults = QPushButton("Restore Defaults")
        self.btn_restore_popup_defaults.clicked.connect(
            self._restore_popup_defaults
        )
        controls.addWidget(self.btn_restore_popup_defaults)

        group_layout.addLayout(controls)
        group.setLayout(group_layout)
        layout.addWidget(group)

        note = QLabel(
            "Restore Defaults makes every built-in action visible again and restores the original built-in order. "
            "Custom Actions are kept, including their current hidden state."
        )
        note.setObjectName("subtitleLabel")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        tab.setLayout(layout)

        insert_index = self.tabs.count()
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) in ("Custom Actions", "Prompts"):
                insert_index = index
                break
        self.tabs.insertTab(insert_index, tab, "Popup Actions")

        self._rebuild_popup_actions_list()

    def _capture_popup_layout(self):
        if not hasattr(self, "popup_actions_list"):
            return

        order = []
        hidden = []
        for row in range(self.popup_actions_list.count()):
            item = self.popup_actions_list.item(row)
            prompt_key = str(
                item.data(Qt.ItemDataRole.UserRole) or ""
            ).strip()
            if not prompt_key:
                continue
            order.append(prompt_key)
            if item.checkState() != Qt.CheckState.Checked:
                hidden.append(prompt_key)

        self.popup_action_order = order
        self.popup_hidden_actions = hidden

    def _rebuild_popup_actions_list(self, select_key=None):
        if not hasattr(self, "popup_actions_list"):
            return

        actions = get_available_popup_actions(self.prompt_manager)
        available_keys = [action["key"] for action in actions]
        self.popup_action_order, self.popup_hidden_actions = normalize_popup_layout(
            self.popup_action_order,
            self.popup_hidden_actions,
            available_keys,
        )

        action_by_key = {action["key"]: action for action in actions}
        hidden_set = set(self.popup_hidden_actions)

        self.popup_actions_list.blockSignals(True)
        self.popup_actions_list.clear()

        selected_row = -1
        for row, prompt_key in enumerate(self.popup_action_order):
            action = action_by_key.get(prompt_key)
            if not action:
                continue

            item = QListWidgetItem(str(action.get("name", prompt_key)))
            item.setData(Qt.ItemDataRole.UserRole, prompt_key)
            item.setFlags(
                item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
            )
            item.setCheckState(
                Qt.CheckState.Unchecked
                if prompt_key in hidden_set
                else Qt.CheckState.Checked
            )
            item.setToolTip(
                "Built-in action"
                if bool(action.get("builtin"))
                else "Custom Action"
            )
            self.popup_actions_list.addItem(item)

            if prompt_key == select_key:
                selected_row = row

        self.popup_actions_list.blockSignals(False)

        if self.popup_actions_list.count():
            if selected_row < 0:
                selected_row = min(
                    max(self.popup_actions_list.currentRow(), 0),
                    self.popup_actions_list.count() - 1,
                )
            self.popup_actions_list.setCurrentRow(selected_row)

    def _move_popup_action(self, delta: int):
        row = self.popup_actions_list.currentRow()
        if row < 0:
            return

        target = row + delta
        if target < 0 or target >= self.popup_actions_list.count():
            return

        item = self.popup_actions_list.takeItem(row)
        self.popup_actions_list.insertItem(target, item)
        self.popup_actions_list.setCurrentRow(target)
        self._capture_popup_layout()

    def _restore_popup_defaults(self):
        self._capture_popup_layout()
        self.popup_action_order, self.popup_hidden_actions = restore_builtin_defaults(
            self.popup_action_order,
            self.popup_hidden_actions,
            self.prompt_manager,
        )
        self._rebuild_popup_actions_list()

    def _on_new_custom_action(self):
        if hasattr(self, "popup_actions_list"):
            self._capture_popup_layout()

        super()._on_new_custom_action()

        if hasattr(self, "popup_actions_list"):
            select_key = self.custom_action_combo.currentData()
            self._rebuild_popup_actions_list(select_key=select_key)

    def _on_delete_custom_action(self):
        if hasattr(self, "popup_actions_list"):
            self._capture_popup_layout()

        super()._on_delete_custom_action()

        if hasattr(self, "popup_actions_list"):
            self._rebuild_popup_actions_list()

    def _save_custom_action(self, *, persist: bool, show_message: bool = False) -> bool:
        if hasattr(self, "popup_actions_list"):
            self._capture_popup_layout()

        prompt_key = None
        if hasattr(self, "custom_action_combo"):
            prompt_key = self.custom_action_combo.currentData()

        result = super()._save_custom_action(
            persist=persist,
            show_message=show_message,
        )

        if result and hasattr(self, "popup_actions_list"):
            self._rebuild_popup_actions_list(select_key=prompt_key)

        return result

    def _on_save(self):
        previous_order = copy.deepcopy(
            self.config_manager.get(POPUP_ACTION_ORDER_KEY, None)
        )
        previous_hidden = copy.deepcopy(
            self.config_manager.get(POPUP_ACTION_HIDDEN_KEY, None)
        )

        if hasattr(self, "popup_actions_list"):
            self._capture_popup_layout()
            self.config_manager.set(
                POPUP_ACTION_ORDER_KEY,
                list(self.popup_action_order),
            )
            self.config_manager.set(
                POPUP_ACTION_HIDDEN_KEY,
                list(self.popup_hidden_actions),
            )

        super()._on_save()

        if self.result() != self.DialogCode.Accepted:
            self.config_manager.set(POPUP_ACTION_ORDER_KEY, previous_order)
            self.config_manager.set(POPUP_ACTION_HIDDEN_KEY, previous_hidden)
            logger.debug("Restored popup action layout after settings save failure")
