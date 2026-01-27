from PyQt6.QtWidgets import QMenuBar

# --- IMPORT CSS ---
from App.Styles.MenuBarStyles import MENU_BAR_STYLE

# --- IMPORT MENU CON (MODULES) ---
# Đảm bảo đường dẫn import đúng theo cấu trúc thư mục
from App.Gui.Widgets.MenuBar.MenuFile import MenuFile
from App.Gui.Widgets.MenuBar.MenuSetup import MenuSetup
from App.Gui.Widgets.MenuBar.MenuControl import MenuControl
from App.Gui.Widgets.MenuBar.MenuTool import MenuTool
# from App.Gui.Widgets.MenuBar.MenuCalibration import MenuCalibration # (Tự tạo file này nếu cần)

class MenuBar(QMenuBar):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window # Lưu tham chiếu đến MainWindow

        # 1. Apply Style
        self.setup_style()
        
        # 2. Add các Menu con
        self.setup_structure()

    def setup_style(self):
        self.setStyleSheet(MENU_BAR_STYLE)

    def setup_structure(self):
        # --- MENU 1: FILE ---
        # Truyền self.main_window vào để các menu con có thể gọi hàm của cửa sổ chính (như close, show_error...)
        self.menu_file = MenuFile(self.main_window)
        self.addMenu(self.menu_file)

        # --- MENU 2: SETUP ---
        self.menu_setup = MenuSetup(self.main_window)
        self.addMenu(self.menu_setup)

        # --- MENU 3: CONTROL ---
        self.menu_control = MenuControl(self.main_window)
        self.addMenu(self.menu_control)

        # --- MENU 4: TOOLS ---
        self.menu_tool = MenuTool(self.main_window)
        self.addMenu(self.menu_tool)

        # --- MENU 5: HELP ---
        # Có thể tạo class riêng hoặc add nhanh tại đây nếu ít chức năng
        help_menu = self.addMenu("Help")
        help_menu.addAction("About", lambda: print("About TNH Optima"))