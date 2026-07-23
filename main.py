# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from App.Presentation.ViewModels.MainViewModel import MainViewModel
from App.Presentation.Views.MainView import MainView

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for both the dev environment and PyInstaller. """
    try:
        # PyInstaller creates a temporary directory and saves the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)
    icon_path = resource_path(os.path.join("App", "ReSource", "Icon", "app_icon.ico"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    splash_path = resource_path(os.path.join("App", "ReSource", "Icon", "splash_screen.png"))
    
    if os.path.exists(splash_path):
        splash_pix = QPixmap(splash_path)
        splash_pix = splash_pix.scaled(500, 500,
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
    else:
        splash_pix = QPixmap(500, 500)
        splash_pix.fill(Qt.GlobalColor.darkGray)

    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()

    # Create a ViewModel and connect the splash update signal
    view_model = MainViewModel()
    view_model.progress_update.connect(splash.showMessage)

    # Create the main window (this process will trigger restore_session and other steps)
    main_view = MainView()

    # Hide splash screen and show main window
    splash.finish(main_view)
    main_view.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()