"""Build the Windows installer after PyInstaller has created the application."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess


APP_NAME = "TNH Optima"
APP_VERSION = "1.1.0"
INSTALLER_FILE_NAME = f"TNH_Optima_Setup_{APP_VERSION}.exe"


def _inno_setup_candidates() -> list[Path]:
    """Return common locations for the Inno Setup command-line compiler."""
    candidates: list[Path] = []

    configured_path = os.environ.get("ISCC_PATH")
    if configured_path:
        candidates.append(Path(configured_path).expanduser())

    path_command = shutil.which("ISCC.exe") or shutil.which("ISCC")
    if path_command:
        candidates.append(Path(path_command))

    for environment_name in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
        base_dir = os.environ.get(environment_name)
        if not base_dir:
            continue
        base_path = Path(base_dir)
        if environment_name == "LOCALAPPDATA":
            candidates.append(base_path / "Programs" / "Inno Setup 6" / "ISCC.exe")
        else:
            candidates.append(base_path / "Inno Setup 6" / "ISCC.exe")

    return candidates


def find_inno_setup_compiler() -> Path:
    """Find ISCC.exe or raise an actionable build error."""
    checked_paths: list[str] = []
    for candidate in _inno_setup_candidates():
        resolved_candidate = candidate.resolve()
        checked_paths.append(str(resolved_candidate))
        if resolved_candidate.is_file():
            return resolved_candidate

    checked = "\n  - ".join(checked_paths) if checked_paths else "(no candidate paths)"
    raise RuntimeError(
        "PyInstaller created the application, but the installer cannot be built "
        "because Inno Setup 6 (ISCC.exe) is not installed.\n"
        "Install Inno Setup 6, or set ISCC_PATH to the full path of ISCC.exe.\n"
        f"Checked:\n  - {checked}"
    )


def compile_installer(project_dir: str | Path) -> Path:
    """Compile installer.iss and return the generated setup executable."""
    project_path = Path(project_dir).resolve()
    application_executable = (
        project_path / "dist" / APP_NAME / f"{APP_NAME}.exe"
    )
    if not application_executable.is_file():
        raise FileNotFoundError(
            "PyInstaller application executable was not found at "
            f"{application_executable}"
        )

    installer_script = project_path / "installer.iss"
    if not installer_script.is_file():
        raise FileNotFoundError(f"Installer script was not found at {installer_script}")

    output_dir = project_path / "Folder Download Software"
    output_dir.mkdir(parents=True, exist_ok=True)

    compiler = find_inno_setup_compiler()
    print(f"Compiling Windows installer with: {compiler}")
    subprocess.run(
        [str(compiler), str(installer_script)],
        cwd=project_path,
        check=True,
    )

    installer_executable = output_dir / INSTALLER_FILE_NAME
    if not installer_executable.is_file():
        raise FileNotFoundError(
            "Inno Setup completed without creating the expected installer at "
            f"{installer_executable}"
        )

    print(f"Installer created successfully: {installer_executable}")
    return installer_executable


if __name__ == "__main__":
    compile_installer(Path(__file__).resolve().parent)
