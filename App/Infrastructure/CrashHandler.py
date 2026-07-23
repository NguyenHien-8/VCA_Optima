import faulthandler
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import threading
import traceback


_LOGGER = logging.getLogger("tnh_optima")
_NATIVE_CRASH_FILE = None
_HANDLING_EXCEPTION = False


def _log_directory():
    local_app_data = os.environ.get("LOCALAPPDATA")
    root = Path(local_app_data) if local_app_data else Path.home() / ".tnh_optima"
    return root / "TNH Optima" / "Logs"


def install_exception_hooks():
    """Install rotating logs and last-resort Python/native exception hooks."""
    global _NATIVE_CRASH_FILE

    log_dir = _log_directory()
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        if not _LOGGER.handlers:
            handler = RotatingFileHandler(
                log_dir / "application.log",
                maxBytes=2 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(threadName)s | %(message)s"
                )
            )
            _LOGGER.addHandler(handler)
            _LOGGER.setLevel(logging.INFO)

        if _NATIVE_CRASH_FILE is None:
            _NATIVE_CRASH_FILE = open(
                log_dir / "native-crash.log", "a", encoding="utf-8"
            )
            faulthandler.enable(_NATIVE_CRASH_FILE, all_threads=True)
    except OSError:
        # Logging must never prevent the application from starting.
        log_dir = None

    sys.excepthook = report_exception

    def thread_exception_hook(args):
        report_exception(
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
            show_dialog=False,
        )

    if hasattr(threading, "excepthook"):
        threading.excepthook = thread_exception_hook
    return str(log_dir) if log_dir is not None else None


def report_exception(exc_type, exc_value, exc_traceback, show_dialog=True):
    global _HANDLING_EXCEPTION

    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    if _HANDLING_EXCEPTION:
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        return

    _HANDLING_EXCEPTION = True
    try:
        formatted = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        if _LOGGER.handlers:
            _LOGGER.critical("Unhandled exception\n%s", formatted)
        traceback.print_exception(exc_type, exc_value, exc_traceback)

        if show_dialog and threading.current_thread() is threading.main_thread():
            try:
                from PyQt6.QtWidgets import QApplication, QMessageBox

                if QApplication.instance() is not None:
                    QMessageBox.critical(
                        None,
                        "Unexpected Error",
                        "TNH Optima encountered an unexpected error.\n\n"
                        f"{exc_type.__name__}: {exc_value}\n\n"
                        "Details were written to the application log.",
                    )
            except Exception:
                pass
    finally:
        _HANDLING_EXCEPTION = False


def log_exception(message):
    """Log the active exception from a defensive catch block."""
    if _LOGGER.handlers:
        _LOGGER.exception(message)
