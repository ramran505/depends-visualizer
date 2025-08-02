# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os
from pathlib import Path

project_dir = os.path.abspath(".")

# Collect all files in dep-visualizer/dist
dist_assets = []
for root, _, files in os.walk(os.path.join(project_dir, "dep-visualizer", "dist")):
    for f in files:
        full_path = os.path.join(root, f)
        rel_path = os.path.relpath(full_path, project_dir)
        dist_assets.append((full_path, os.path.join("dep-visualizer", "dist", os.path.relpath(full_path, os.path.join(project_dir, "dep-visualizer", "dist")))))

a = Analysis(
    ['depends_visualize.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(project_dir, "depends.jar"), "."),  # will be extracted into _MEIPASS root
        (os.path.join(project_dir, "convert_dot_ids.py"), "."),  # also in root
        *dist_assets  # React app
    ],
    hiddenimports=[],
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
    a.zipfiles,
    a.datas,
    [],
    name='depends_visualize',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
