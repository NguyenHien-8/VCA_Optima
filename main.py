# main.py
import sys
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

from App.Infrastructure.Helpers.ResourceHelper import icon_path
from App.Presentation.ViewModels.MainViewModel import MainViewModel
from App.Presentation.Views.MainView import MainView

def main():
    app = QApplication(sys.argv)
    app_icon = QIcon(icon_path("app_icon.ico"))
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
        
    splash_pix = QPixmap(icon_path("splash_screen.png"))
    if not splash_pix.isNull():
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
    main_view = MainView(view_model=view_model)

    # Hide splash screen and show main window
    splash.finish(main_view)
    main_view.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
