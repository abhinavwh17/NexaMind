# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import (
    collect_submodules,
)


keyring_hidden_imports = (
    collect_submodules(
        "keyring.backends"
    )
)


a = Analysis(
    ["launcher.py"],

    pathex=[],

    binaries=[],

    datas=[
        (
            "frontend/dist",
            "frontend/dist",
        ),
    ],

    hiddenimports=[
        *keyring_hidden_imports,
    ],

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[],

    noarchive=False,
)


pyz = PYZ(
    a.pure
)


exe = EXE(
    pyz,

    a.scripts,

    a.binaries,

    a.datas,

    [],

    name="NexaMind",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=True,

    console=True,
)