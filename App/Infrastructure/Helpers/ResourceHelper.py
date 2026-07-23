# App/Infrastructure/Helpers/ResourceHelper.py
from pathlib import Path
import sys

def base_path() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]

def resource_path(relative_path: str) -> str:
    return str(base_path() / relative_path)