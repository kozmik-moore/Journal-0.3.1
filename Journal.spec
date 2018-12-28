# -*- mode: python -*-

block_cipher = None

options =[('v', None, 'OPTIONS')]

added_files =[
			('C:\\Users\\Kozmik\\Documents\\Programming Projects\\Journal 0.3.1\\Resources\\Messages', 'Resources'),
			('C:\\Users\\Kozmik\\Documents\\Programming Projects\\Journal 0.3.1\\Resources\\Template.jeif', 'Resources'),
			('C:\\Users\\Kozmik\\Documents\\Programming Projects\\Journal 0.3.1\\Resources\\Trash_Can-512.png', 'Resources'),
			('C:\\Users\\Kozmik\\Documents\\Programming Projects\\Journal 0.3.1\\Resources\\web.ico', 'Resources')
			]
a = Analysis(['Journal.py'],
             pathex=['C:\\Users\\Kozmik\\Documents\\Programming Projects\\Journal 0.3.1'],
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
		  icon='web.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='kunnekted-jurnl')
