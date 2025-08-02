# depends_visualize.spec
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

# Handle missing __file__ in exec context
try:
    project_dir = os.path.abspath(os.path.dirname(__file__))
except NameError:
    # Fallback if __file__ is not defined (e.g., when running inside PyInstaller)
    project_dir = os.path.abspath(os.getcwd())

def collect_folder(folder, prefix):
    files = []
    for root, _, filenames in os.walk(os.path.join(project_dir, folder)):
        for f in filenames:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, project_dir)
            target_path = os.path.join(prefix, os.path.relpath(full_path, os.path.join(project_dir, folder)))
            files.append((full_path, target_path))
    return files

block_cipher = None

datas = [
    (os.path.join(project_dir, 'depends.jar'), '.'),
    (os.path.join(project_dir, 'convert_dot_ids.py'), '.'),
] + \
collect_folder('openjdk', 'openjdk') + \
collect_folder('graphviz', 'graphviz') + \
collect_folder(os.path.join('dep-visualizer', 'dist'), os.path.join('dep-visualizer', 'dist'))

a = Analysis(
    ['depends_visualize.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=collect_submodules('http'),
    runtime_hooks=[],
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='depends_visualize',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='depends_visualize',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    onefile=True,  # ✅ make sure this is here!
)