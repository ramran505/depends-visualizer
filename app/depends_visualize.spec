# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['depends_visualize.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(project_dir, 'graphviz'), 'graphviz'),
        (os.path.join(project_dir, 'openjdk'), 'openjdk'),
        (os.path.join(project_dir, 'convert_dot_ids.py'), '.'),
        (os.path.join(project_dir, 'depends.jar'), '.'),
        (os.path.join(project_dir, 'dep-visualizer', 'dist'), os.path.join('dep-visualizer', 'dist'))
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
