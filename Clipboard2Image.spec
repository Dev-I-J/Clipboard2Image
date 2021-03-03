import importlib
import sys
import os

theme_dirs = ['fonts', 'resources', 'themes']
theme_files = ['material.css.template']

project_dirs = ['icons', 'style', 'html']

datas = []

qt_material_root = os.path.dirname(importlib.import_module('qt_material').__file__)
for dir in theme_dirs:
    if os.path.isdir(os.path.join(qt_material_root, dir)):
        datas.append((os.path.join(qt_material_root, dir), os.path.join("qt_material", dir),))
for file in theme_files:
    if os.path.isfile(os.path.join(qt_material_root, file)):
        datas.append((os.path.join(qt_material_root, file), "qt_material",))

for dir in project_dirs:
    datas.append((os.path.join("src", dir), dir,))


block_cipher = None


a = Analysis([r'src\main.py' if sys.platform == "win32" else "src/main.py"],
             pathex=[os.path.abspath(os.path.realpath("."))],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Clipboard2Image',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          icon=(r"src\icons\appicon.ico" if sys.platform == "win32" else "src/icons/appicon.icns" if sys.platform == "darwin" else "src/icons/appicon.png")
)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=(sys.platform == "win32"),
               upx_exclude=["qwindows.dll"],
               name='Clipboard2Image')