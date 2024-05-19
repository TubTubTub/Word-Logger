# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['word-logger.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('CustomTitleBar.py', '.'), ('Dict.py', '.'), ('dark-mode.css', '.'), ('light-mode.css', '.'), ('data.json', '.'), ('settings.json', '.')],
    hiddenimports=[],
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
    name='Word Logger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/enter.png",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='word-logger',
)
