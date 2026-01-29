from PyQt6.QtWidgets import QMenuBar

# --- IMPORT CSS ---
from App.Styles.MenuBarStyles import MENU_BAR_STYLE

# --- IMPORT MENU CON (MODULES) ---
from App.Gui.Widgets.MenuBar.MenuFile import MenuFile
from App.Gui.Widgets.MenuBar.MenuSetup import MenuSetup
from App.Gui.Widgets.MenuBar.MenuControl import MenuControl
from App.Gui.Widgets.MenuBar.MenuTool import MenuTool
from App.Gui.Widgets.MenuBar.ToggleSideBar import ToggleAction

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
        # --- [NEW] TOGGLE SIDEBAR ACTION ---
        # Thêm Action icon vào vị trí đầu tiên
        self.toggle_action = ToggleAction(self)
        self.toggle_action.triggered.connect(self.main_window.toggle_sidebar)
        self.addAction(self.toggle_action)

        # --- MENU 1: FILE ---
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
        help_menu = self.addMenu("Help")
        help_menu.addAction("About", lambda: print("About TNH Optima"))