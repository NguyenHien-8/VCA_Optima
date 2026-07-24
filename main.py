# main.py
import sys
from App.Infrastructure.CrashHandler import (
    install_exception_hooks,
    report_exception,
)

def main():
    install_exception_hooks()
    try:
        from App.Infrastructure.Helpers.WindowOwnershipHelper import (
            initialize_taskbar_identity,
        )
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QIcon, QPixmap
        from PyQt6.QtWidgets import QApplication, QSplashScreen
        from App.Infrastructure.Helpers.ResourceHelper import icon_path

        # Must run before the first native window is created so the main window
        # and all secondary windows share one stable Windows taskbar group.
        initialize_taskbar_identity()
        app = QApplication(sys.argv)
        app.setApplicationName("TNH Optima")
        app.setOrganizationName("TNH")
        app_icon = QIcon(icon_path("app_icon.ico"))
        if not app_icon.isNull():
            app.setWindowIcon(app_icon)

        splash_pix = QPixmap(icon_path("splash_screen.png"))
        if not splash_pix.isNull():
            splash_pix = splash_pix.scaled(
                500,
                500,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        else:
            splash_pix = QPixmap(500, 500)
            splash_pix.fill(Qt.GlobalColor.darkGray)

        splash = QSplashScreen(
            splash_pix, Qt.WindowType.WindowStaysOnTopHint
        )
        splash.show()
        app.processEvents()

        # Feature-heavy editors are imported lazily; only the application shell is
        # loaded while the splash screen is visible.
        from App.Presentation.ViewModels.MainViewModel import MainViewModel
        from App.Presentation.Views.MainView import MainView

        view_model = MainViewModel()
        view_model.progress_update.connect(splash.showMessage)
        main_view = MainView(view_model=view_model)

        main_view.show()
        splash.finish(main_view)
        return app.exec()
    except Exception:
        report_exception(*sys.exc_info())
        if "splash" in locals():
            splash.close()
        return 1

if __name__ == "__main__":
    sys.exit(main())
