# -*- mode: python -*-

import sys
sys.path.append(".")
import easydst

block_cipher = None


added_files = [('easydst.json','.')]

a = Analysis(['easydst_gui.py'],
             pathex=['C:\\Users\\Nobody\\Desktop\\easydst'],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='easydst_gui '+easydst.str_ver,
          debug=False,
          strip=False,
          upx=True,
          console=False )
