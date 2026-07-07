# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Mobile Communication System Simulator
Build: pyinstaller mobile_comm_sim.spec
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('core', 'core'),
        ('gui', 'gui'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends.backend_qt5agg',
        'scipy.special',
        'scipy.stats',
        'sklearn.linear_model',
        'sklearn.preprocessing',
        'sklearn.metrics',
        'reportlab',
        'reportlab.platypus',
        'reportlab.lib',
        'numpy',
    ],
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
    name='CommSim',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CommSim',
)
