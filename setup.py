# Copyright (C) 2015 Marc D. Wood
#
# This file is part of the METAMARKET project.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of METAMARKET, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

from distutils.core import setup
from glob import glob
import py2exe

data_files = [("Microsoft.VC90.CRT", glob(r'C:\WINDOWS\WinSxS\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.21022.8_x-ww_d08d0375\*.*'))]

setup(
    name='METAMARKET',
    data_files=data_files,
    console=['mmcli.py', 'modserver.py', 'vendserver.py'],
    options = {
        'py2exe': {
            'packages': ['bitcoin', 'pycoin'],
            'includes': ['simplejson', 'simplecrypt', '_scrypt'],
        } # Changed scrypt.py to import C module from current directory.
    }
)
