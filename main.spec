# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['main.py'],  # main.py замените на реальное имя вашего скрипта
    pathex=[],
    binaries=[],
    datas=[
        ('assets/Body.svg', 'assets'),
        ('assets/Header.svg', 'assets'),
        ("assets/buttons/Patreon.svg", "assets/buttons"),
        ("assets/buttons/MO2.svg", "assets/buttons"),
        ("assets/buttons/GameFolder.svg", "assets/buttons"),
        ("assets/buttons/Discord.svg", "assets/buttons"),
        ("assets/buttons/DataBase.svg", "assets/buttons"),
        ("assets/buttons/Boosty.svg", "assets/buttons"),
        ("assets/options/Play.svg", "assets/options"),
        ("assets/options/Update.svg", "assets/options"),
        ("assets/options/Exit.svg", "assets/options"),
        ("assets/ProgressBar.svg", "assets"),
        ("assets/MagicCardsCyrillic/MagicCardsCyrillic.ttf", "assets/MagicCardsCyrillic"),
    ],
    hiddenimports=[
        'googleapiclient.discovery',
        'google.oauth2.service_account',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        'PyQt5.QtCore',
        'zipfile',
        'shutil',
        'io',
        'os',
        'sys',
        'logging',
        'webbrowser',
        'time',
        'functools',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RFADGameLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    noarchive=False,
    optimize=2,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # Укажите путь к иконке
)

