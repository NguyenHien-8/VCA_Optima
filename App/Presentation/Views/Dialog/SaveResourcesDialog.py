# App/Presentation/Views/Dialog/SaveResourcesDialog.py
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, QFile

from App.Presentation.ViewModels.DialogViewModel.SaveResourcesViewModel import SaveResourcesViewModel

class SaveResourcesDialog(QDialog):
    def __init__(self, parent=None, item_name="Untitled"):
        super().__init__(parent)
        self.view_model = SaveResourcesViewModel(item_name)
        self.setWindowTitle("Save Resource")
        self.setFixedSize(400, 110)
        self.load_savedialog_style()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 20, 20)

        # Message Section
        msg_text = f"Save '{self.view_model.get_item_name()}'?"
        self.lbl_message = QLabel(msg_text)
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lbl_message.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.lbl_message)

        # Button Section
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_save = QPushButton("Save")
        self.btn_save.setObjectName("BtnSave")
        self.btn_save.setDefault(True)

        self.btn_dont_save = QPushButton("Don't Save")
        self.btn_cancel = QPushButton("Cancel")

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_dont_save)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def setup_connections(self):
        self.btn_save.clicked.connect(self.on_save)
        self.btn_dont_save.clicked.connect(self.on_dont_save)
        self.btn_cancel.clicked.connect(self.on_cancel)

    def load_savedialog_style(self):
        qss_path = "App/ReSource/Styles/DelSaveDialogStyles.qss"
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: Stylesheet not found at {qss_path}")
        
        qss_file = QFile(qss_path)
        if qss_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            style = qss_file.readAll().data().decode()
            self.setStyleSheet(style)
        qss_file.close()

    def on_save(self):
        self.view_model.set_action_save()
        self.accept()

    def on_dont_save(self):
        self.view_model.set_action_dont_save()
        self.accept()

    def on_cancel(self):
        self.view_model.set_action_cancel()
        self.reject()

    def get_action(self):
        return self.view_model.get_action()