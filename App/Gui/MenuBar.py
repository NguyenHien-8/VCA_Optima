from PyQt6.QtWidgets import QMenuBar, QMenu, QStyle
from PyQt6.QtGui import QAction, QKeySequence

from App.Styles.MenuBarStyles import MENU_BAR_STYLE 

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # 1. Áp dụng Style ngay khi khởi tạo
        self.setup_style()
        
        # 2. Vẽ giao diện
        self.setup_ui()

    def setup_style(self):
        """Chỉ cần gọi biến đã import"""
        self.setStyleSheet(MENU_BAR_STYLE)

    def setup_ui(self):
        style = self.style()

        # --- 1. Menu FILE ---
        file_menu = self.addMenu("File")
        
        self.add_action(file_menu, "New Project...", self.new_project, 
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), shortcut="Ctrl+N")
        self.add_action(file_menu, "Open", self.open_project, 
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon), shortcut="Ctrl+O")
        
        file_menu.addSeparator()

        self.add_action(file_menu, "Import", self.import_project,
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight))
        self.add_action(file_menu, "Export", self.export_project,
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_ArrowLeft))

        file_menu.addSeparator()

        self.add_action(file_menu, "Save", self.save_project, 
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), shortcut="Ctrl+S")
        
        file_menu.addSeparator()

        self.add_action(file_menu, "Exit", self.exit, 
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))

        # --- 2. Menu SETUP ---
        setup_menu = self.addMenu("Setup")
        self.add_action(setup_menu, "Hardware Connection", self.hardware_connection, 
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.add_action(setup_menu, "Camera Connection", self.camera_connection,
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_DriveDVDIcon))

        # --- 3. Menu CONTROL ---
        control_menu = self.addMenu("Control")
        self.add_action(control_menu, "Pump Fluid", self.pump_fluid,
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.add_action(control_menu, "Stop Pump", self.stop_pump,
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.add_action(control_menu, "Move Stage", self.move_stage,
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))

        # --- 4. Menu TOOLS ---
        tools_menu = self.addMenu("Tools")
        self.add_action(tools_menu, "Settings", lambda: print("Tools clicked"),
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))

        # --- 5. Menu CALIBRATION ---
        calib_menu = self.addMenu("Calibration")
        self.add_action(calib_menu, "Calibrate Axis", lambda: print("Calib clicked"),
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload))

        # --- 6. Menu HELP ---
        help_menu = self.addMenu("Help")
        self.add_action(help_menu, "About", lambda: print("About clicked"),
                        icon=style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))

    def add_action(self, menu, text, slot_method, icon=None, shortcut=None):
        """Hàm helper tạo action"""
        if icon:
            action = QAction(icon, text, self)
        else:
            action = QAction(text, self)
            
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
            
        action.triggered.connect(slot_method)
        menu.addAction(action)

    # === ACTION HANDLERS ===
    def exit(self):
        if self.parent_window: self.parent_window.close()
    
    def new_project(self): print("[File] New Project")
    def open_project(self): print("[File] Open Project")
    def import_project(self): print("[File] Import Project")
    def export_project(self): print("[File] Export Project")
    def save_project(self): print("[File] Save Project")
    
    def hardware_connection(self): print("[Setup] Hardware Connection")
    def camera_connection(self): print("[Setup] Camera Connection")
    def pump_fluid(self): print("[Control] Pump Fluid")
    def stop_pump(self): print("[Control] Stop Pump")
    def move_stage(self): print("[Control] Move Stage")