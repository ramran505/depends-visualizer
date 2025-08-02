# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

project_dir = os.path.abspath(".")

# === 📦 Include React build ===
dist_assets = []
dist_dir = os.path.join(project_dir, "dep-visualizer", "dist")
for root, _, files in os.walk(dist_dir):
    for f in files:
        full_path = os.path.join(root, f)
        rel_path_in_dist = os.path.relpath(full_path, dist_dir)
        dist_assets.append(
            (full_path, os.path.join("dep-visualizer", "dist", rel_path_in_dist))
        )

# === 📦 Include Graphviz binaries, DLLs, plugins, config8 ===
graphviz_bin = os.path.join(project_dir, "graphviz", "bin")
graphviz_plugin = os.path.join(graphviz_bin, "plugin")

graphviz_binaries = [
    # dot.exe
    (os.path.join(graphviz_bin, "dot.exe"), "graphviz/bin"),

    # config6/config8
    *[
        (os.path.join(graphviz_bin, f), "graphviz/bin")
        for f in os.listdir(graphviz_bin)
        if f.startswith("config") and os.path.isfile(os.path.join(graphviz_bin, f))
    ],

    # main DLLs
    *[
        (os.path.join(graphviz_bin, f), "graphviz/bin")
        for f in os.listdir(graphviz_bin)
        if f.endswith(".dll")
    ],

    # plugin DLLs
    *[
        (os.path.join(graphviz_plugin, f), "graphviz/bin/plugin")
        for f in os.listdir(graphviz_plugin)
        if f.endswith(".dll")
    ],
]

# === 🔧 Full PyInstaller build config ===
a = Analysis(
    ['depends_visualize.py'],
    pathex=[],
    binaries=graphviz_binaries,
    datas=[
        # Depends CLI JAR
        (os.path.join(project_dir, "depends.jar"), "."),

        # Embedded script to run via runpy
        (os.path.join(project_dir, "convert_dot_ids.py"), "."),

        # React visualizer build
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
