# -*- mode: python ; coding: utf-8 -*-
# このファイルはPyInstallerによって自動生成されたもので、それをカスタマイズして使用しています。
import os

datas = [
    ('CharSettingJson', 'api/CharSettingJson'),
    ('images', 'api/images'),
    ('comment_reciver', 'api/comment_reciver'),
    ('Extend', 'api/Extend'),
    ('gptAI', 'api/gptAI'),
    ('web', 'api/web'),
]

block_cipher = None

a = Analysis(
    ['web/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['openai','win32com','pyaudio','clr','psd_tools'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VoiroStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoiroStudio',
)

