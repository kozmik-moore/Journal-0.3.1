# -*- mode: python -*-

from os import getcwd

root = getcwd()
resources = root + "\\Resources\\"

block_cipher = None

options =[('v', None, 'OPTIONS')]

added_files =[
			(resources + 'Messages', 'Resources'),
			(resources + 'Template.jeif', 'Resources'),
			(resources + 'Trash_Can-512.png', 'Resources'),
			(resources + 'web.ico', 'Resources')
			]
a = Analysis(['Journal.py'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'icudt57.dll', 'icuin57.dll', 'icuuc57.dll', 'PyQt5', 'tk'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='kunnekted-jurnl',
          debug=True,
          strip=False,
          upx=True,
          console=True,
		  icon=resources + 'web.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='kunnekted-jurnl')
