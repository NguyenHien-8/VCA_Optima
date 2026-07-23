# App/Presentation/Views/Widgets/MenuBar/MenuBar.py
import os
from PyQt6.QtWidgets import QMenuBar

from App.Presentation.Views.Widgets.MenuBar.MenuFile import MenuFile
from App.Presentation.Views.Widgets.MenuBar.MenuSetup import MenuSetup
from App.Presentation.Views.Widgets.MenuBar.MenuControl import MenuControl
# from App.Presentation.Views.Widgets.MenuBar.MenuTool import MenuTool
# from App.Presentation.Views.Widgets.MenuBar.MenuCalibration import MenuCalibration
# from App.Presentation.Views.Widgets.MenuBar.MenuWindow import MenuWindow
from App.Presentation.Views.Widgets.MenuBar.ToggleSideBar import ToggleAction

class MenuBar(QMenuBar):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window 
        self.load_menubar_style()
        self.setup_structure()

    def load_menubar_style(self):
        from App.Infrastructure.Helpers.ResourceHelper import resource_path
        qss_path = resource_path(os.path.join("App", "ReSource", "Styles", "MenuBarStyles.qss"))
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: Stylesheet not found at {qss_path}")

    def setup_structure(self):
        # --- TOGGLE SIDEBAR ACTION ---
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
        # self.menu_tool = MenuTool(self.main_window)
        # self.addMenu(self.menu_tool)

        # --- MENU 4: CALIBRATION ---
        # self.menu_calibration = MenuCalibration(self.main_window)
        # self.addMenu(self.menu_calibration)

        # --- MENU 5: WINDOW ---
        # self.menu_window = MenuWindow(self.main_window) 
        # self.addMenu(self.menu_window)
        
        # --- MENU 5: HELP ---
        # help_menu = self.addMenu("Help")
        # help_menu.addAction("About", lambda: print("About TNH Optima"))