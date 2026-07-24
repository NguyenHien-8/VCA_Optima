########################################################
# @file App/Infrastructure/Helpers/ResourceHelper.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
########################################################
from functools import lru_cache
from pathlib import Path
import sys


@lru_cache(maxsize=1)
def base_path() -> Path:
    """Return the project/bundle root without depending on the current directory."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and bundle_root:
        return Path(bundle_root).resolve()

    # ResourceHelper.py -> Helpers -> Infrastructure -> App -> project root.
    return Path(__file__).resolve().parents[3]


def resource_path(*relative_parts) -> str:
    """Resolve a project-relative resource path for source and PyInstaller runs."""
    if not relative_parts:
        raise ValueError("At least one resource path component is required.")

    candidate = Path(*relative_parts)
    if candidate.is_absolute():
        return str(candidate)
    return str((base_path() / candidate).resolve())


def app_resource_path(*relative_parts) -> str:
    """Resolve a path below App/ReSource."""
    return resource_path("App", "ReSource", *relative_parts)


def icon_path(*relative_parts) -> str:
    """Resolve an application icon path."""
    return app_resource_path("Icon", *relative_parts)


def stylesheet_path(file_name: str) -> str:
    """Resolve a stylesheet path."""
    return app_resource_path("Styles", file_name)


@lru_cache(maxsize=None)
def load_stylesheet(file_name: str) -> str:
    """Read and cache one UTF-8 QSS file for the lifetime of the process."""
    return Path(stylesheet_path(file_name)).read_text(encoding="utf-8")


def apply_stylesheet(widget, file_name: str) -> bool:
    """Load one UTF-8 QSS file and apply it to a Qt widget."""
    qss_path = Path(stylesheet_path(file_name))
    try:
        stylesheet = load_stylesheet(file_name)
    except (OSError, UnicodeError) as exc:
        print(f"Warning: Stylesheet not found or unreadable at {qss_path}: {exc}")
        return False

    widget.setStyleSheet(stylesheet)
    return True
