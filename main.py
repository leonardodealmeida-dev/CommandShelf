import json
import sys
import uuid
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QPlainTextEdit,
    QSplitter, QVBoxLayout, QWidget
)

APP_DIR = Path.home() / ".commandshelf"
CUSTOM_FILE = APP_DIR / "custom_commands.json"
FAVORITES_FILE = APP_DIR / "favorites.json"
BUILT_IN_FILE = Path(__file__).parent / "commands.json"


def read_json(path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class AddCommandDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add a command")
        self.setMinimumWidth(430)
        self.title = QLineEdit()
        self.command = QLineEdit()
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(["Linux", "Git", "Python", "JavaScript", "Java", "Networking", "Other"])
        self.description = QPlainTextEdit()
        self.description.setMaximumHeight(90)
        self.example = QLineEdit()

        form = QFormLayout()
        form.addRow("Title *", self.title)
        form.addRow("Command *", self.command)
        form.addRow("Category", self.category)
        form.addRow("Description *", self.description)
        form.addRow("Example / note", self.example)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def validate(self):
        if not all((self.title.text().strip(), self.command.text().strip(), self.description.toPlainText().strip())):
            QMessageBox.warning(self, "Missing information", "Title, command, and description are required.")
            return
        self.accept()

    def data(self):
        return {
            "id": "custom-" + uuid.uuid4().hex,
            "title": self.title.text().strip(),
            "command": self.command.text().strip(),
            "category": self.category.currentText().strip() or "Other",
            "description": self.description.toPlainText().strip(),
            "example": self.example.text().strip(),
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CommandShelf")
        self.resize(1000, 640)
        self.setMinimumSize(740, 460)
        self.builtins = read_json(BUILT_IN_FILE, [])
        self.custom = read_json(CUSTOM_FILE, [])
        self.favorites = set(read_json(FAVORITES_FILE, []))
        self.selected = None

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search commands, descriptions, examples…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.refresh)

        self.category = QComboBox()
        self.category.currentTextChanged.connect(self.refresh)
        self.favorites_only = QCheckBox("Favorites only")
        self.favorites_only.stateChanged.connect(self.refresh)

        filters = QHBoxLayout()
        filters.addWidget(self.search, 1)
        filters.addWidget(self.category)
        filters.addWidget(self.favorites_only)

        self.list = QListWidget()
        self.list.currentItemChanged.connect(self.show_command)
        self.name = QLabel("Choose a command")
        self.name.setObjectName("commandTitle")
        self.category_label = QLabel("")
        self.category_label.setObjectName("categoryLabel")
        self.description = QLabel("Select a command on the left to view its details.")
        self.description.setWordWrap(True)
        self.command = QPlainTextEdit()
        self.command.setReadOnly(True)
        self.command.setMaximumHeight(90)
        self.example = QLabel("")
        self.example.setWordWrap(True)
        self.copy_btn = QPushButton("Copy command")
        self.copy_btn.clicked.connect(self.copy_command)
        self.favorite_btn = QPushButton("☆ Add to favorites")
        self.favorite_btn.clicked.connect(self.toggle_favorite)

        details = QVBoxLayout()
        for widget in (self.name, self.category_label, QLabel("Description"), self.description,
                       QLabel("Command"), self.command, self.example):
            details.addWidget(widget)
        row = QHBoxLayout()
        row.addWidget(self.copy_btn)
        row.addWidget(self.favorite_btn)
        details.addLayout(row)
        details.addStretch()
        detail_widget = QWidget()
        detail_widget.setLayout(details)

        splitter = QSplitter()
        splitter.addWidget(self.list)
        splitter.addWidget(detail_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        add_btn = QPushButton("+ Add command")
        add_btn.clicked.connect(self.add_command)
        footer = QHBoxLayout()
        footer.addWidget(QLabel("Custom commands are saved on this computer."))
        footer.addStretch()
        footer.addWidget(add_btn)

        layout = QVBoxLayout()
        layout.addLayout(filters)
        layout.addWidget(splitter, 1)
        layout.addLayout(footer)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#171923; color:#e7eaf0; }
            QLineEdit, QComboBox, QPlainTextEdit, QListWidget {
                background:#222635; color:#f1f3f8; border:1px solid #3a4053;
                border-radius:7px; padding:7px; selection-background-color:#6d5dfc;
            }
            QPushButton { background:#6658e8; color:white; border:0; border-radius:7px;
                padding:9px 12px; font-weight:600; }
            QPushButton:hover { background:#7b70ff; }
            QLabel#commandTitle { font-size:22px; font-weight:700; }
            QLabel#categoryLabel { color:#a99fff; font-weight:600; }
            QListWidget::item { padding:9px; border-radius:5px; }
            QListWidget::item:selected { background:#37315f; }
        """)
        self.statusBar().showMessage("Ready")
        self.update_categories()
        self.refresh()
        QShortcut(QKeySequence.StandardKey.Find, self, activated=self.search.setFocus)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self, activated=self.copy_command)

    def commands(self):
        return self.builtins + self.custom

    def update_categories(self):
        old = self.category.currentText()
        categories = sorted({c.get("category", "Other") for c in self.commands()}, key=str.casefold)
        self.category.blockSignals(True)
        self.category.clear()
        self.category.addItem("All categories")
        self.category.addItems(categories)
        self.category.setCurrentText(old if old else "All categories")
        if self.category.currentIndex() < 0:
            self.category.setCurrentIndex(0)
        self.category.blockSignals(False)

    def refresh(self, *_):
        query = self.search.text().casefold().strip()
        category = self.category.currentText()
        previous_id = self.selected.get("id") if self.selected else None
        self.list.clear()
        for cmd in sorted(self.commands(), key=lambda c: c.get("title", "").casefold()):
            text = " ".join(str(cmd.get(k, "")) for k in ("title", "command", "description", "category", "example")).casefold()
            if query and query not in text:
                continue
            if category != "All categories" and cmd.get("category", "Other") != category:
                continue
            if self.favorites_only.isChecked() and cmd.get("id") not in self.favorites:
                continue
            star = "★ " if cmd.get("id") in self.favorites else ""
            item = QListWidgetItem(f"{star}{cmd.get('title', 'Untitled')}\n{cmd.get('command', '')}")
            item.setData(Qt.ItemDataRole.UserRole, cmd)
            self.list.addItem(item)
            if cmd.get("id") == previous_id:
                self.list.setCurrentItem(item)
        if self.list.count() and self.list.currentRow() < 0:
            self.list.setCurrentRow(0)
        elif not self.list.count():
            self.selected = None
            self.clear_details()

    def show_command(self, item, _previous=None):
        if item is None:
            self.selected = None
            self.clear_details()
            return
        self.selected = item.data(Qt.ItemDataRole.UserRole)
        c = self.selected
        self.name.setText(c.get("title", "Untitled"))
        self.category_label.setText(c.get("category", "Other"))
        self.description.setText(c.get("description", ""))
        self.command.setPlainText(c.get("command", ""))
        self.example.setText("Example / note: " + c["example"] if c.get("example") else "")
        self.favorite_btn.setText("★ Remove from favorites" if c["id"] in self.favorites else "☆ Add to favorites")
        self.copy_btn.setEnabled(bool(c.get("command")))

    def clear_details(self):
        self.name.setText("No commands found")
        self.category_label.setText("")
        self.description.setText("Try another search or add a command.")
        self.command.clear()
        self.example.clear()
        self.copy_btn.setEnabled(False)
        self.favorite_btn.setText("☆ Add to favorites")

    def copy_command(self):
        if self.selected:
            QApplication.clipboard().setText(self.selected.get("command", ""))
            self.statusBar().showMessage("Command copied to clipboard.", 2500)

    def toggle_favorite(self):
        if not self.selected:
            return
        cid = self.selected["id"]
        self.favorites.symmetric_difference_update({cid})
        write_json(FAVORITES_FILE, sorted(self.favorites))
        self.refresh()
        self.statusBar().showMessage("Favorites updated.", 2000)

    def add_command(self):
        dialog = AddCommandDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        command = dialog.data()
        self.custom.append(command)
        write_json(CUSTOM_FILE, self.custom)
        self.update_categories()
        self.search.clear()
        self.favorites_only.setChecked(False)
        self.category.setCurrentText("All categories")
        self.refresh()
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.data(Qt.ItemDataRole.UserRole)["id"] == command["id"]:
                self.list.setCurrentItem(item)
                break
        self.statusBar().showMessage("Command saved locally.", 2500)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CommandShelf")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
