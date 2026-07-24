#######################################################
# @file App/Infrastructure/Repositories/StoragePath.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
#######################################################
import os
from pathlib import Path
import shutil


def persistent_database_path(file_name, legacy_path=None):
    """Return a per-user writable DB path and migrate legacy data once."""
    if not isinstance(file_name, str) or not file_name:
        raise ValueError("Database file name must be a non-empty string.")

    app_data = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    root = Path(app_data) if app_data else Path.home() / ".tnh_optima"
    storage_dir = root / "TNH Optima" / "Data"
    storage_dir.mkdir(parents=True, exist_ok=True)
    target = storage_dir / file_name

    if not target.exists() and legacy_path:
        legacy = Path(legacy_path)
        if legacy.is_file():
            try:
                shutil.copy2(legacy, target)
            except OSError:
                # A fresh DB is preferable to failing application startup.
                pass
    return str(target)
