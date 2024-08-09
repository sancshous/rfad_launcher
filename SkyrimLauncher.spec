# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/background.jpg', 'assets'),
        ('style.qss', '.'),  
    ],
    hiddenimports=[
        'googleapiclient.discovery',
        'google.oauth2.service_account',
        'PyQt5.QtWidgets',
        'py7zr',
        'zipfile',
        'shutil',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='SkyrimLauncher.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',  # Укажите путь к иконке, если она есть
)

# Используем формат "onefile", чтобы получить единый exe
app = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SkyrimLauncher.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/icon.ico',  # Укажите путь к иконке
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    argv_emulation=False,
    resources=[],
    codesign_identity=None,
    entitlements_file=None,
    runtime_tmpdir=None,
)

