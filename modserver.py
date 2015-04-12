#!/usr/bin/env python
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

import mmcli
import time, getpass

if mmcli.entity != 'mod':
    raise Exception("Modserver must be run as mod. Modify your mm.cfg file.")
wp = getpass.getpass("Enter wallet passphrase: ")
mmcli.login(wp)
mmcli.MM_util.btcd.walletlock()

intervals = 0
while True:
    mmcli.MM_util.unlockwallet(wp)
    if mmcli.checkinbox():
        mmcli.processinbox()
    
    if intervals % 10 == 0:
        print "Sending CAST..."
#        mmcli.modbroadcast()
    if intervals >= 30:
        print "Sending Market Offer..."
#        mmcli.sendmarketoffer(mmcli.default_channame)
        intervals = 0
    
    intervals += 1
    mmcli.MM_util.btcd.walletlock()
    
    print '.'
    time.sleep(60)
    
    
