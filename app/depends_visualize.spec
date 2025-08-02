# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os
from pathlib import Path

project_dir = os.path.abspath(".")

# Collect all files in dep-visualizer/dist (React app)
dist_assets = []
dist_dir = os.path.join(project_dir, "dep-visualizer", "dist")
for root, _, files in os.walk(dist_dir):
    for f in files:
        full_path = os.path.join(root, f)
        relative_path_in_dist = os.path.relpath(full_path, dist_dir)
        dist_assets.append(
            (full_path, os.path.join("dep-visualizer", "dist", relative_path_in_dist))
        )

a = Analysis(
    ['depends_visualize.py'],
    pathex=[],
    binaries=[
        (os.path.join(project_dir, "graphviz", "bin", "dot.exe"), "graphviz/bin"),
        *[(os.path.join(project_dir, "graphviz", "bin", dll), "graphviz/bin") for dll in os.listdir(os.path.join(project_dir, "graphviz", "bin")) if dll.endswith(".dll")],
    ],
    datas=[
        # ✅ Include Depends JAR
        (os.path.join(project_dir, "depends.jar"), "."),

        # ✅ Include Python script to run via runpy
        (os.path.join(project_dir, "convert_dot_ids.py"), "."),

        # ✅ Include all React assets
        *dist_assets
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
    console=True,  # show terminal window (good for CLI tools)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
