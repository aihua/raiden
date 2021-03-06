# -*- mode: python -*-
from __future__ import print_function
import sys
import pdb
import platform

from raiden.utils import get_system_spec

"""
PyInstaller spec file to build single file or dir distributions
"""

# Set to false to produce an exploded single-dir
ONEFILE = int(os.environ.get('ONEFILE', True))


def Entrypoint(dist, group, name, scripts=None, pathex=None, hiddenimports=None, hookspath=None,
               excludes=None, runtime_hooks=None, datas=None):
    import pkg_resources

    # get toplevel packages of distribution from metadata
    def get_toplevel(dist):
        distribution = pkg_resources.get_distribution(dist)
        if distribution.has_metadata('top_level.txt'):
            return list(distribution.get_metadata('top_level.txt').split())
        else:
            return []

    hiddenimports = hiddenimports or []
    packages = []
    for distribution in hiddenimports:
        try:
            packages += get_toplevel(distribution)
        except:
            pass

    scripts = scripts or []
    pathex = pathex or []
    # get the entry point
    ep = pkg_resources.get_entry_info(dist, group, name)
    # insert path of the egg at the verify front of the search path
    pathex = [ep.dist.location] + pathex
    # script name must not be a valid module name to avoid name clashes on import
    script_path = os.path.join(workpath, name + '-script.py')
    print("creating script for entry point", dist, group, name)
    with open(script_path, 'w') as fh:
        print("import", ep.module_name, file=fh)
        print("%s.%s()" % (ep.module_name, '.'.join(ep.attrs)), file=fh)
        for package in packages:
            print("import", package, file=fh)

    return Analysis(
        [script_path] + scripts,
        pathex=pathex,
        hiddenimports=hiddenimports,
        hookspath=hookspath,
        excludes=excludes,
        runtime_hooks=runtime_hooks,
        datas=datas
    )


if hasattr(pdb, 'pdb'):
    # pdbpp moves the stdlib pdb to the `pdb` attribute of it's own patched pdb module
    raise RuntimeError(
        'pdbpp is installed which causes broken PyInstaller builds. Please uninstall it.',
    )


# We don't need Tk and friends
sys.modules['FixTk'] = None

executable_name = 'raiden-{}-{}-{}'.format(
    os.environ.get('ARCHIVE_TAG', 'v' + get_system_spec()['raiden']),
    'macOS' if platform.system() == 'Darwin' else platform.system().lower(),
    platform.machine()
)

a = Entrypoint(
    'raiden',
    'console_scripts',
    'raiden',
    hookspath=['tools/pyinstaller_hooks'],
    runtime_hooks=[
        'tools/pyinstaller_hooks/runtime_gevent_monkey.py',
        'tools/pyinstaller_hooks/runtime_encoding.py',
        'tools/pyinstaller_hooks/runtime_raiden_contracts.py',
    ],
    hiddenimports=['scrypt', 'eth_tester'],
    datas=[
        ('raiden/smoketest_genesis.json', 'raiden'),
    ],
    excludes=['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter'],
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

if ONEFILE:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name=executable_name,
        debug=False,
        strip=True,
        upx=False,
        runtime_tmpdir=None,
        console=True
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        exclude_binaries=True,
        name=executable_name,
        debug=True,
        strip=False,
        upx=False,
        console=True
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=False,
        name='raiden'
    )
