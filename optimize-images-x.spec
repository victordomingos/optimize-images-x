# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller build recipe for Optimize Images X.
#
# Build (run on the target OS — PyInstaller does not cross-compile):
#   pip install pyinstaller
#   pyinstaller optimize-images-x.spec
#
# Output:
#   macOS   -> dist/Optimize Images X.app
#   Windows -> dist/Optimize Images X/Optimize Images X.exe
#   Linux   -> dist/Optimize Images X/Optimize Images X
#
import sys

APP_NAME = "Optimize Images X"
ENTRY = "optimize_images_x/__main__.py"

# Bundle the package's data files. The destination path MUST match what
# resource_path() expects at runtime: <bundle>/optimize_images_x/images/...
datas = [
    ("optimize_images_x/images", "optimize_images_x/images"),
    ("optimize_images_x/locale", "optimize_images_x/locale"),
]
binaries = []
hiddenimports = []

# Optional drag-and-drop support. tkinterdnd2 ships native tkDnD binaries that
# PyInstaller must bundle; collect them only if the package is installed in the
# build environment, so the build still works without it (DnD simply absent).
try:
    from PyInstaller.utils.hooks import collect_all
    dnd_datas, dnd_binaries, dnd_hiddenimports = collect_all('tkinterdnd2')
    datas += dnd_datas
    binaries += dnd_binaries
    hiddenimports += dnd_hiddenimports
except Exception:
    pass

# Platform-specific app icon. Leave None to ship with the default icon for now;
# drop a file in and point to it later (.icns on macOS, .ico on Windows).
if sys.platform == "darwin":
    icon = None  # e.g. "packaging/app.icns"
elif sys.platform == "win32":
    icon = None  # e.g. "packaging/app.ico"
else:
    icon = None  # Linux: no icon needed here

a = Analysis(
    [ENTRY],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,        # GUI app: no terminal window
    icon=icon,
)

# One-folder layout (recommended for a .app): faster launch than one-file,
# which would re-extract to a temp dir on every run.
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=APP_NAME,
)

# macOS: wrap the collected output as a proper .app bundle.
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=icon,
        bundle_identifier="com.victordomingos.optimize-images-x",
        info_plist={
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleShortVersionString": "2.2.0",
            "CFBundleVersion": "2.2.0",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "10.13.0",
        },
    )
