# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import (
    collect_submodules,
    collect_data_files,
    collect_dynamic_libs
)

block_cipher = None

hidden_imports = []
hidden_imports += collect_submodules('serial')
hidden_imports += collect_submodules('cv2')
hidden_imports += collect_submodules('PyQt6')
hidden_imports += collect_submodules('PyQt6.QtMultimedia')
hidden_imports += collect_submodules('PyQt6.QtMultimediaWidgets')

# Nếu code dùng thư viện lấy tên camera kiểu Windows friendly name,
# Hãy bỏ comment các dòng tương ứng:
# hidden_imports += collect_submodules('pygrabber')
# hidden_imports += collect_submodules('comtypes')
# hidden_imports += collect_submodules('wmi')
# hidden_imports += collect_submodules('pythoncom')
# hidden_imports += collect_submodules('win32com')

datas = [
    ('App', 'App'),
]

# Thu thập thêm data/plugin của Qt và cv2
datas += collect_data_files('PyQt6')
datas += collect_data_files('cv2')

binaries = []
binaries += collect_dynamic_libs('cv2')
binaries += collect_dynamic_libs('PyQt6')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports + [
        'cv2',
        'numpy',
        'scipy',
        'scipy.optimize',
        'scipy.signal',
        'scipy.spatial',
        'scipy.integrate',
        'scipy.stats',
        'scipy.spatial.transform._rotation_groups',
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'PIL',
        'PIL.Image',
        'PIL.ImageQt',
        'PIL.ImageDraw',
        'PIL.ImageFilter',
        'PIL.ImageFont',
        'matplotlib',
        'matplotlib.backends.backend_qt5agg',
        'App',
        'App.Presentation',
        'App.Models',
        'sqlite3',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TNH Optima',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='App/ReSource/Icon/app_icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TNH Optima',
)