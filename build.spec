# -*- mode: python ; coding: utf-8 -*-

import sys, os, sysconfig
from PyInstaller.utils.hooks import collect_data_files, collect_all, collect_submodules

def list_py_files(directory):
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

app_root = os.getcwd()
sys.setrecursionlimit(5000)
site_packages_path = sysconfig.get_paths()["purelib"]

print('##################### Build Info #####################')
print('app_root:', app_root)
print('site_packages_path:', site_packages_path)
print('######################################################')

##################### App Start #####################

sys.path.append('third_party/Matcha-TTS')

entries = ['webui.py'] + list_py_files('cosyvoice')

print('entries:', entries)

analysis_data = { 'datas': [], 'hiddenimports': [] }
libs = [
    'requests',
    'filelock',
    'numpy',
]
for lib in libs:
    data = collect_all(lib)
    analysis_data['datas'] += data[0]
    analysis_data['hiddenimports'] += data[2]

a = Analysis(
    entries,
    pathex = [ app_root ],
    binaries = [],
    datas=  collect_data_files('gradio_client')
          + collect_data_files('gradio')
          + collect_data_files('yapf_third_party')
          + collect_data_files('cosyvoice')
          + collect_data_files('matcha')
          + analysis_data['datas']
    ,
    hiddenimports = ['_pywrapfst',]
                  + analysis_data['hiddenimports']
    ,
    hookspath = [],
    hooksconfig = {},
    runtime_hooks = [],
    excludes = [],
    noarchive = False,
    optimize = 0,
    module_collection_mode = {
        'gradio': 'py',
        'cosyvoice': 'py',
        'inflect': 'py',
        'hyperpyyaml': 'py',
        'conformer': 'py',
        'diffusers': 'py',
    },
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries = True,
    name = 'main',
    debug = True,
    bootloader_ignore_signals = False,
    strip = False,
    upx = True,
    console = True,
    disable_windowed_traceback = False,
    argv_emulation = False,
    target_arch = None,
    codesign_identity = None,
    entitlements_file = None,
    contents_directory = '_dep',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas
        + Tree('pretrained_models', prefix = 'pretrained_models')
        + Tree('cosyvoice', prefix = 'cosyvoice')
        + Tree('third_party/Matcha-TTS/matcha', prefix = 'matcha')
        + Tree(f'{site_packages_path}/tn', prefix = 'tn')
        + Tree(f'{site_packages_path}/whisper', prefix = 'whisper')
    ,
    strip = False,
    upx = True,
    upx_exclude = [],
    name = 'server-cosyvoice',
    exclude = []
)

##################### App End #####################