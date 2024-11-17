# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

a = Analysis(
    ['C:\\Users\\sebcr\\OneDrive\\Desktop\\inventory-tracker\\Desktop\\main.py'],
    pathex=[],
    binaries=[],
    datas=[("C:\\Users\\sebcr\\OneDrive\\Desktop\\inventory-tracker\\Desktop\\client_secret_dev.json", "."), ("C:\\Users\\sebcr\\OneDrive\\Desktop\\inventory-tracker\\Desktop\\client_key.json", "."), ("C:\\Users\\sebcr\\OneDrive\\Desktop\\inventory-tracker\\building\\desktop_compile\\dist\\libiconv.dll", "."), ("C:\\Users\\sebcr\\OneDrive\\Desktop\\inventory-tracker\\building\\desktop_compile\\dist\\libzbar-64.dll", ".")],
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
    Tree('C:\\Users\\sebcr\\OneDrive\\Desktop\\inventory-tracker\\Desktop', '.'),  # Add a Tree object for your folder
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    upx=True,
    name='FSAE-Scanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
