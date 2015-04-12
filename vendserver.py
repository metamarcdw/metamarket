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
import time, getpass, decimal

if mmcli.entity != 'vendor':
    raise Exception("Vendserver must be run as vendor. Modify your mm.cfg file.")
wp = getpass.getpass("Enter wallet passphrase: ")
mmcli.login(wp)
mmcli.MM_util.btcd.walletlock()

while True:
    if mmcli.checkinbox():
        mmcli.MM_util.unlockwallet(wp)
        
        for msginfo in mmcli.processinbox():            
            if msginfo.msgname == mmcli.MM_util.ORDER:
                print "Sending CONF.."
                confhash = mmcli.createconf(msginfo.hash)
                mmcli.sendmsg(confhash, prompt=False)
                
            elif msginfo.msgname == mmcli.MM_util.PAY:
                print "Sending REC.."
                rechash = mmcli.createrec(msginfo.hash)
                mmcli.sendmsg(rechash, prompt=False)
                
        mmcli.MM_util.btcd.walletlock()
        
    print '.'
    time.sleep(60)
    
    
