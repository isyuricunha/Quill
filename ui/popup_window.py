"""Main popup window shown near the cursor."""

import logging
from pathlib import Path
from typing import Dict, List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QTextEdit,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QEvent, QSize, QTimer
from PySide6.QtGui import QKeyEvent, QScreen, QIcon, QFontMetrics

from ui.styles import apply_dark_theme


logger = logging.getLogger(__name__)


class PopupWindow(QWidget):
    """Compact action popup for the currently selected text."""

    action_requested = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_text = ""
        self.action_buttons: Dict[str, QPushButton] = {}

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Popup
        )

        self._setup_ui()
        apply_dark_theme(self)
        logger.debug("PopupWindow initialized")

    def _setup_ui(self):
        self.setFixedWidth(300)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.icon_container = QLabel()
        self.icon_container.setObjectName("iconContainer")
        self.icon_container.setFixedSize(40, 40)
        self.icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_icon()
        header_layout.addWidget(self.icon_container)

        text_info_layout = QVBoxLayout()
        text_info_layout.setSpacing(2)

        self.preview_label = QLabel("Select text to process")
        self.preview_label.setObjectName("previewLabel")
        text_info_layout.addWidget(self.preview_label)

        self.char_count_label = QLabel("0 characters")
        self.char_count_label.setObjectName("subtitleLabel")
        text_info_layout.addWidget(self.char_count_label)

        header_layout.addLayout(text_info_layout, 1)
        layout.addLayout(header_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        self.actions_scroll = QScrollArea()
        self.actions_scroll.setWidgetResizable(True)
        self.actions_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.actions_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.actions_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.actions_widget = QWidget()
        self.actions_layout = QGridLayout()
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setHorizontalSpacing(8)
        self.actions_layout.setVerticalSpacing(8)
        self.actions_widget.setLayout(self.actions_layout)
        self.actions_scroll.setWidget(self.actions_widget)
        layout.addWidget(self.actions_scroll)

        self.set_actions([])

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator2)

        prompt_label = QLabel("Custom Instruction:")
        prompt_label.setObjectName("subtitleLabel")
        layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Enter custom instruction here...\n"
            "(Press Enter to send, Shift+Enter for newline)"
        )
        self.prompt_input.setFixedHeight(80)
        self.prompt_input.installEventFilter(self)
        layout.addWidget(self.prompt_input)

        self.btn_send = QPushButton("Send")
        self.btn_send.setObjectName("sendButton")
        self.btn_send.setFixedHeight(36)
        self.btn_send.clicked.connect(lambda: self._emit_action("custom"))
        layout.addWidget(self.btn_send)

        help_label = QLabel("Press ESC to close")
        help_label.setObjectName("subtitleLabel")
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(help_label)

        self.setLayout(layout)

    def set_actions(self, actions: List[Dict[str, str]]) -> None:
        """Replace the action button grid with the supplied popup actions."""
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.action_buttons = {}

        if not actions:
            empty_label = QLabel("No actions are enabled for the popup.")
            empty_label.setObjectName("subtitleLabel")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.actions_layout.addWidget(empty_label, 0, 0, 1, 2)
            self.actions_scroll.setFixedHeight(40)
            return

        for index, action in enumerate(actions):
            prompt_key = str(action.get("key", "")).strip()
            name = str(action.get("name", prompt_key)).strip() or prompt_key
            if not prompt_key:
                continue

            button = QPushButton(name)
            button.setObjectName("quickActionButton")
            button.setToolTip(name)
            button.clicked.connect(
                lambda checked=False, key=prompt_key: self._emit_action(key)
            )

            row, column = divmod(index, 2)
            self.actions_layout.addWidget(button, row, column)
            self.action_buttons[prompt_key] = button

        rows = max(1, (len(self.action_buttons) + 1) // 2)
        self.actions_scroll.setFixedHeight(min(184, 36 + (rows - 1) * 44))

    def eventFilter(self, obj, event):
        if obj == self.prompt_input and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    return False
                self._emit_action("custom")
                return True

        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def _load_icon(self):
        project_root = Path(__file__).parent.parent
        icon_paths = [
            project_root / "resources" / "icon_alpha.ico",
            project_root / "resources" / "icon.ico",
            project_root / "_internal" / "resources" / "icon_alpha.ico",
            project_root / "_internal" / "resources" / "icon.ico",
        ]

        target_size = 36

        for icon_path in icon_paths:
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                if not icon.isNull():
                    pixmap = icon.pixmap(QSize(64, 64))
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            target_size,
                            target_size,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                        self.icon_container.setPixmap(scaled_pixmap)
                        logger.debug("Loaded icon from: %s", icon_path)
                        return

        logger.warning("Could not load icon for popup header")

    def _update_preview(self, text: str):
        if not text:
            self.preview_label.setText("Select text to process")
            self.char_count_label.setText("0 characters")
            return

        char_count = len(text)
        self.char_count_label.setText(
            "1 character" if char_count == 1 else f"{char_count} characters"
        )

        preview_source = text[:50]
        clean_text = preview_source.replace("\n", " ").replace("\r", "")

        fm = QFontMetrics(self.preview_label.font())
        max_width = 205
        ellipsis = "..."
        ellipsis_width = fm.horizontalAdvance(ellipsis)
        quote_width = fm.horizontalAdvance('""')

        truncated = clean_text
        while (
            fm.horizontalAdvance(truncated) + quote_width > max_width
            and truncated
        ):
            truncated = truncated[:-1]

        if len(text) > len(truncated):
            while (
                fm.horizontalAdvance(truncated)
                + quote_width
                + ellipsis_width
                > max_width
                and truncated
            ):
                truncated = truncated[:-1]
            preview_text = f'"{truncated}..."'
        else:
            preview_text = f'"{truncated}"'

        self.preview_label.setText(preview_text)

    def show_at_position(self, x: int, y: int, text: str):
        self.selected_text = text
        self.prompt_input.clear()
        self._update_preview(text)
        self.adjustSize()

        screen = self._get_screen_at(x, y)
        if screen:
            screen_geometry = screen.geometry()
            popup_width = self.width()
            popup_height = self.height()

            new_x = x
            new_y = y + 20

            if new_x + popup_width > screen_geometry.right():
                new_x = screen_geometry.right() - popup_width

            if new_y + popup_height > screen_geometry.bottom():
                new_y = y - popup_height - 10

            if new_x < screen_geometry.left():
                new_x = screen_geometry.left()

            if new_y < screen_geometry.top():
                new_y = screen_geometry.top()

            self.move(new_x, new_y)
        else:
            self.move(x, y + 20)

        self.show()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(50, lambda: self.prompt_input.setFocus())

        logger.debug(
            "Popup shown at (%s, %s), text length: %s",
            x,
            y,
            len(text),
        )

    def _get_screen_at(self, x: int, y: int) -> QScreen:
        from PySide6.QtGui import QGuiApplication

        for screen in QGuiApplication.screens():
            if screen.geometry().contains(x, y):
                return screen

        return QGuiApplication.primaryScreen()

    def _emit_action(self, prompt_key: str):
        instruction = self.prompt_input.toPlainText().strip()

        logger.info(
            "Action requested: %s, instruction length: %s",
            prompt_key,
            len(instruction),
        )

        self.action_requested.emit(prompt_key, self.selected_text, instruction)
        self.prompt_input.clear()
        self.hide()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QCursor

    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = PopupWindow()
    window.set_actions(
        [
            {"key": "grammar_check", "name": "Grammar Check"},
            {"key": "rewrite", "name": "Rewrite"},
            {"key": "translate", "name": "Translate"},
        ]
    )

    cursor_pos = QCursor.pos()
    window.show_at_position(
        cursor_pos.x(),
        cursor_pos.y(),
        "This is a test text that user selected.",
    )

    sys.exit(app.exec())
