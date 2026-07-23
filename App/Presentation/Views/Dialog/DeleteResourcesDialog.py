# App/Presentation/Views/Dialog/DeleteResourcesDialog.py
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel,
                             QCheckBox, QPushButton, QHBoxLayout, QWidget)
from PyQt6.QtCore import Qt, QFile

from App.Presentation.ViewModels.DialogViewModel.DeleteResourcesViewModel import DeleteResourcesViewModel

class DeleteResourcesDialog(QDialog):
    def __init__(self, parent, title, message, location_path, show_checkbox=True):
        super().__init__(parent)
        self.view_model = DeleteResourcesViewModel(title, message, location_path, show_checkbox)
        self.setWindowTitle(self.view_model.get_title())
        self.setFixedWidth(550)
        self.load_deldialog_style()

        # --- MAIN LAYOUT ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # --- CONTENT AREA (GRID) ---
        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setVerticalSpacing(10)
        content_layout.setHorizontalSpacing(10)
        content_layout.setColumnStretch(1, 1)

        # Icon
        icon_label = QLabel()
        icon = self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxQuestion)
        icon_label.setPixmap(icon.pixmap(25, 25))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(icon_label, 0, 0, Qt.AlignmentFlag.AlignTop)

        # Message 
        msg_label = QLabel(self.view_model.get_message())
        msg_label.setWordWrap(True)
        content_layout.addWidget(msg_label, 0, 1)

        # Checkbox
        self.chk_delete_disk = QCheckBox("Delete project contents on disk (cannot be undone)")
        if self.view_model.get_show_checkbox():
            self.chk_delete_disk.setChecked(False)
            content_layout.addWidget(self.chk_delete_disk, 1, 0, 1, 2)
        else:
            self.chk_delete_disk.setVisible(False)
            self.chk_delete_disk.setChecked(False)

        self.chk_delete_disk.stateChanged.connect(
            lambda state: self.view_model.set_delete_disk_checked(state == Qt.CheckState.Checked.value)
        )

        # Location info
        location_path = self.view_model.get_location_path()
        if location_path:
            loc_layout = QVBoxLayout()
            loc_layout.setSpacing(2)
            lbl_loc_title = QLabel("Location:")
            lbl_loc_path = QLabel(location_path)
            lbl_loc_path.setWordWrap(True)
            loc_layout.addWidget(lbl_loc_title)
            loc_layout.addWidget(lbl_loc_path)
            content_layout.addLayout(loc_layout, 2, 0, 1, 2)

        main_layout.addWidget(content_widget)
        main_layout.addStretch()

        # --- BUTTONS ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_ok = QPushButton("OK")
        self.btn_ok.setObjectName("BtnOk")
        self.btn_ok.setDefault(True)
        self.btn_ok.clicked.connect(self.accept)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(btn_layout)

    def load_deldialog_style(self):
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

    def is_delete_disk_checked(self):
        return self.view_model.get_delete_disk_checked()