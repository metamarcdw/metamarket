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

import MM_util
import bitcoin, bitcoin.rpc, bitcoin.core, pycoin.key.Key
import scrypt, simplecrypt
import simplejson as json
import argparse, ConfigParser
import sys, os, hashlib, getpass, time, decimal
import xmlrpclib, base64

def login( wp=None ):
    global username, passphrase, pkstr, wif, btcaddr, bmaddr, myid, mymarket, bannedtags
    
    print "WELCOME TO METAMARKET--"
    print "Please login--"
    username = raw_input("Name: ")
    passphrase = getpass.getpass("Passphrase: ")
    
    hash = hashlib.sha256(passphrase).hexdigest()
    pkbytes = scrypt.hash(hash, username, N=2**18, buflen=32)
    pkstr = bitcoin.core.b2x(pkbytes)
    se = long(pkstr, 16)
    pk = pycoin.key.Key(secret_exponent=se, netcode=netcode)
    
    wif = pk.wif()
    btcaddr = pk.address()
    bmaddr = MM_util.bm.getDeterministicAddress( base64.b64encode(pkstr), 4, 1 )
    
    print "BTC Address: %s\nBM Address: %s" % ( btcaddr, bmaddr )
    
    MM_util.unlockwallet(wp)
    if MM_util.bm.createDeterministicAddresses(base64.b64encode(pkstr)) == [] or \
        not MM_util.btcd.validateaddress(btcaddr)['ismine']:
        importkeys()
    
    identlist = MM_util.loadlist('ident')
    
    myidstr = MM_util.createidentmsgstr(btcaddr, bmaddr, username)
    myid = MM_util.MM_loads( btcaddr, myidstr )
    print "My ID: %s" % myid.hash
    
    if not MM_util.searchlistbyhash(identlist, myid.hash):
        register(myidstr)
    
    if entity == 'mod':
        marketlist = MM_util.loadlist('market')
        for i in marketlist:
            if i.obj['modid'] == myid.hash:
                mymarket = i
                print "My Market ID:", mymarket.hash
        bannedtags = MM_util.loadindex('bannedtags')
        
def importkeys( ):
    print "Bitcoin private key not found in wallet"
    print "or Bitmessage identity does not exist."
    print "Import your BTC private key and create your BM ID?"
    if MM_util.yorn():
        pass2 = getpass.getpass("Please re-enter your passphrase: ")
        if pass2 == passphrase:
            MM_util.btcd.importprivkey(wif, username, False)
            
            print "REMEMBER TO SECURELY BACKUP YOUR"
            print "wallet.dat AND keys.dat files!"
            print "--------------------------------"
        else:
            raise Exception("Passwords did not match.")
    else:
        MM_util.bm.deleteAddress(bmaddr)
        sys.exit()
    
def register( idstr ):
    print "We were not able to find your ID on file."
    print "Is this a new identity you would like to create?"
    if not MM_util.yorn():
        login()
    else:
        MM_util.MM_writefile(idstr)
        MM_util.appendindex('ident', myid.hash)
        
        
def synccast( ):
    identlist = MM_util.loadlist('ident')
    burnlist = MM_util.loadlist('burn')
    taglist = MM_util.loadlist('tags')
    offerlist = MM_util.loadlist('offer')
    feedbacklist = MM_util.loadlist('feedback')
    
    return MM_util.createcastmsgstr(btcaddr, myid.hash, \
                identlist, burnlist, taglist, offerlist, feedbacklist)
    
# creates a "CAST Msg" from current lists and broadcasts over BM
def modbroadcast( ):
    MM_util.bm.sendBroadcast(bmaddr, base64.b64encode('Msg'), base64.b64encode(synccast()))

# creates a "CAST Msg" from current lists and sends to new user
def modsync( bm_addr ):
    MM_util.sendmsgviabm(bm_addr, bmaddr, synccast(), False)

def modbanuser( ):
    userid = raw_input("Enter a User ID: ")
    print "Are you sure?:"
    if not MM_util.yorn():
        return
        
    identlist = MM_util.loadlist('ident')
    offerlist = MM_util.loadlist('offer')
    
    user = MM_util.searchlistbyhash(identlist, userid)
    if user:
        MM_util.bm.addAddressToBlackWhiteList( user.obj['bmaddr'], "Banned: %s" % user.obj['name'] )
        MM_util.MM_backupfile('ident', userid)
        
        for offer in offerlist:
            if offer.obj['vendorid'] == user.hash:
                MM_util.MM_backupfile('offer', offer.hash)
                    
def modbantag( ):
    taghash = raw_input("Enter a Tag ID: ")
    print "Are you sure?:"
    if not MM_util.yorn():
        return
        
    bannedtags.append(taghash)
    MM_util.appendindex('bannedtags', taghash)
    MM_util.MM_backupfile('tags', taghash)
    
    offerlist = MM_util.loadlist('offer')
    for offer in offerlist:
        for tag in offer.obj['tags']:
            if tag in bannedtags:
                MM_util.MM_backupfile('offer', offer.hash)
                
def modremoveoffer( ):
    offerhash = raw_input("Enter an Offer ID: ")
    print "Are you sure?:"
    if not MM_util.yorn():
        return
    MM_util.MM_backupfile('offer', offerhash)
    
    
def getrep( identhash, burn_mult ):
    numrep = 0
    downvote_mult = 10
    feedbacklist = MM_util.loadlist('feedback')
    burnlist = MM_util.loadlist('burn')
    
    for fb in feedbacklist:
        if fb.obj['toid'] == identhash:
            if fb.obj['upvote']:
                numrep += 1
            else:
                numrep -= downvote_mult
                
    for burn in burnlist:
        if burn.obj['userid'] == identhash:
            try:
                burntx_hex = MM_util.btcd.getrawtransaction(burn.obj['txid'])
            except bitcoin.rpc.JSONRPCException as jre:
                if jre.error['code'] == -5:
                    continue
            burntx = MM_util.btcd.decoderawtransaction( burntx_hex )
            amount = burntx['vout'][0]['value']
            numrep += amount * burn_mult
            
    return numrep

# Takes a list of Verified Msgs and prints info to stdout.
def showanylist( list, mktid ):
    for i in list:
        title = "Name"
        if i.msgname == MM_util.REG:
            title = "User ID"
            str = i.obj['userid']
        elif i.msgname == MM_util.BURN:
            title = "TXID"
            str = i.obj['txid']
        elif i.msgname == MM_util.IDENT:
            marketlist = MM_util.loadlist('market')
            market = MM_util.searchlistbyhash(marketlist, mktid)
            mult = decimal.Decimal( market.obj['multiplier'] )
            rep = getrep(i.hash, mult)
            str = "%s:\tRep: %d" % ( i.obj['name'], rep )
        elif i.msgname == MM_util.TAG:
            str = i.obj['tagname']
        elif i.msgname == MM_util.MARKET:
            str = i.obj['marketname']
        elif i.msgname == MM_util.OFFER:
            str = "%s;\t%s:\t%s BTC" % ( i.obj['name'], i.obj['amount'], i.obj['price'] )
        elif i.msgname == MM_util.FEEDBACK:
            title = "Message"
            str = i.obj['message']
        else:
            offer = MM_util.offerfromordermsg(i)
            str = "%s;\t%s:\t%s BTC" % ( offer.obj['name'], offer.obj['amount'], offer.obj['price'] )
        print "%s: %s\nID: %s\n" % ( title, str, i.hash )

    

def backupordermsgs(finalhash):
    finallist = MM_util.loadlist('final')
    reclist = MM_util.loadlist('rec')
    paylist = MM_util.loadlist('pay')
    conflist = MM_util.loadlist('conf')
    
    final = MM_util.searchlistbyhash(finallist, finalhash)
    rec = MM_util.searchlistbyhash(reclist, final.obj['rechash'])
    pay = MM_util.searchlistbyhash(paylist, rec.obj['payhash'])
    conf = MM_util.searchlistbyhash(conflist, pay.obj['confhash'])
    
    MM_util.MM_backupfile('final', finalhash)
    MM_util.MM_backupfile('rec', final.obj['rechash'])
    MM_util.MM_backupfile('pay', rec.obj['payhash'])
    MM_util.MM_backupfile('conf', pay.obj['confhash'])
    MM_util.MM_backupfile('order', conf.obj['orderhash'])


def pretty_json( obj ):
    return json.dumps(obj, indent=4, sort_keys=True)
    
def intput( prompt ):
    try:
        return int( raw_input(prompt) )
    except ValueError as err:
        print "Oops:", err
        time.sleep(SLEEP)
        sys.exit()
        
def decput( prompt ):
    try:
        return decimal.Decimal( raw_input(prompt) )
    except ValueError as err:
        print "Oops:", err
        time.sleep(SLEEP)
        sys.exit()
        
def multiline():
    print "Enter multiple lines of input. Use '~' to end."
    input = ''
    while True:
        str = raw_input()
        if str == '~':
            break
        else:
            input += str + '\n'
    return input
        
def sendtx(tx):
    try:
        return MM_util.btcd.sendrawtransaction(tx)
    except bitcoin.rpc.JSONRPCException as jre:
        print "TX NOT SENT.", jre
        time.sleep(SLEEP)
        sys.exit()
        
def gettx(txid):
    while True:
        tx = None
        try:
            tx = MM_util.btcd.getrawtransaction(txid, 1)
        except bitcoin.rpc.JSONRPCException as jre:
            pass
        if tx:
            return tx
        else:
            print "Waiting for broadcast of TX..."
            time.sleep(5)
            
def waitforconf(txid):
    while True:
        confirms = 0
        tx = MM_util.btcd.getrawtransaction(txid, 1)
        if 'confirmations' in tx:
            confirms = tx['confirmations']
        if confirms >= minconf:
            break
        else:
            print "Waiting for confirmation. %d/%d so far..." % ( confirms, minconf )
            time.sleep(5)

def searchtxops(tx, address, amount=None):
    for op in tx['vout']:
        if not amount or op['value'] == amount:
            if address in op['scriptPubKey']['addresses']:
                return op['n']
    else:
        raise Exception("No vout found matching address/amount.")


def createreg():
    markethash = raw_input("Enter a Market ID: ")
    marketlist = MM_util.loadlist('market')
    identlist = MM_util.loadlist('ident')
    market = MM_util.searchlistbyhash(marketlist, markethash)
    mod = MM_util.searchlistbyhash(identlist, market.obj['modid'])
    modbtc = mod.obj['btcaddr']
    
    amount = decimal.Decimal(market.obj['fee'])
    print "Are you sure you want to register at %s;" % market.obj['marketname']
    print "by sending %f BTC to %s?:" % ( amount, modbtc )
    if not MM_util.yorn():
        sys.exit()
        
    change_addr = MM_util.btcd.getrawchangeaddress()
    
    def create_regtx(fee):
        regtx_hex = MM_util.mktx(amount, modbtc, change_addr, default_fee, minconf)
        return MM_util.btcd.signrawtransaction(regtx_hex)['hex']
        
    regtx_hex_signed = create_regtx(default_fee)
    regtx_fee = MM_util.calc_fee(regtx_hex_signed)
    if regtx_fee != default_fee:
        regtx_hex_signed = create_regtx(regtx_fee)
        
    reg_txid = sendtx(regtx_hex_signed)
    print "REGISTER TXID:", reg_txid
    
    msgstr = MM_util.createregmsgstr(btcaddr, mod.hash, myid.hash, reg_txid)
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('reg', hash)
    
    print "Registration ID:", hash

def createburn():
    amount = MM_util.truncate( decput("Enter an amount of BTC to burn: ") )
    print "Are you sure you want to BURN %f coin(s)" % amount
    print "by sending to %s?:" % pob_address
    if not MM_util.yorn():
        sys.exit()
        
    change_addr = MM_util.btcd.getrawchangeaddress()
    
    # Aggregate to main address. Includes 2 fees.
    def create_ag(fee):
        raw_agtx_hex = MM_util.mktx(amount+default_fee, btcaddr, change_addr, fee, minconf)
        return MM_util.btcd.signrawtransaction(raw_agtx_hex)['hex']
        
    sig_agtx_hex = create_ag(default_fee)
    ag_fee = MM_util.calc_fee(sig_agtx_hex)
    if ag_fee != default_fee:
        sig_agtx_hex = create_ag(ag_fee)
    
    ag_txid = sendtx(sig_agtx_hex)
    print "AGGREGATE TXID:", ag_txid
    waitforconf(ag_txid)

    # Create raw burn TX.
    sig_agtx = MM_util.btcd.decoderawtransaction(sig_agtx_hex)
    vout = searchtxops(sig_agtx, btcaddr, amount+default_fee)
    
    txs = [{    "txid": ag_txid,
                "vout": vout }]
    addrs = {   pob_address: amount }
    
    burntx_hex = MM_util.btcd.createrawtransaction(txs, addrs)
    burntx_hex_signed = MM_util.btcd.signrawtransaction(burntx_hex)['hex']
    burn_txid = sendtx(burntx_hex_signed)
    
    print "BURN TXID:", burn_txid
    
    msgstr = MM_util.createburnmsgstr(btcaddr, myid.hash, burn_txid)
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('burn', hash)
    
    print "Burn ID:", hash
    
def createtag():
    tagname = raw_input("Enter a name for this TAG: ")
    desc = raw_input("Enter a description: ")
    
    msgstr = MM_util.createtagmsgstr(btcaddr, myid.hash, tagname, desc)
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('tags', hash)
    
    print "Tag ID:", hash

def createmarket():
    global mymarket
    
    if entity != 'mod':
        print "Enter a Market Offer:"
        infostr = multiline()
        info = json.loads(infostr)
        mod = info['modid']
        market = info['market']
        
        idb64 = base64.b64encode( json.dumps(mod['obj'], sort_keys=True) )
        idmsg = MM_util.Msg( idb64, mod['sig'], mod['hash'], mod['msgname'] )
        idmsgstr = json.dumps(idmsg)
        
        if not MM_util.readmsg(idmsgstr): # Verifies sig/hash
            raise Exception("New Market creation failed..")
        MM_util.MM_writefile(idmsgstr)
        MM_util.appendindex('ident', idmsg.hash)
        
        mktb64 = base64.b64encode( json.dumps(market['obj'], sort_keys=True) )
        mktmsg = MM_util.Msg( mktb64, market['sig'], market['hash'], market['msgname'] )
        mktmsgstr = json.dumps(mktmsg)
        
        if not MM_util.readmsg(mktmsgstr): # Verifies sig/hash
            raise Exception("New Market creation failed..")
        MM_util.MM_writefile(mktmsgstr)
        MM_util.appendindex('market', mktmsg.hash)
        
        MM_util.bm.addSubscription(mod['obj']['bmaddr'])
        print "Congratulations, you may now Register with a new Metamarket!"
        print "Market ID:", mktmsg.hash
        
    else:
        if not mymarket:
            marketname = raw_input("Enter a name for this MARKET: ")
            print "Enter a description:"
            desc = multiline()
            reg_fee = str( MM_util.truncate( decput("Enter a registration fee: ") ) )
            burn_mult = str( decput("Enter a Burn Multiplier: ") )
            
            msgstr = MM_util.createmarketmsgstr(btcaddr, myid.hash, marketname, desc, reg_fee, burn_mult)
            mymarket = MM_util.MM_loads(btcaddr, msgstr)
            MM_util.MM_writefile(msgstr)
            MM_util.appendindex('market', mymarket.hash)
            print "Congratulations, you are the proud new Owner of a new Metamarket!"
            print "Market ID:", mymarket.hash
        else:
            raise Exception("You are already running a Market!")
    
def createsync():
    markethash = raw_input("Enter a Market ID: ")
    marketlist = MM_util.loadlist('market')
    market = MM_util.searchlistbyhash(marketlist, markethash)
    
    msgstr = MM_util.createsyncmsgstr(btcaddr, market.obj['modid'], myid.hash)
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('sync', hash)
    
    print "Sync ID:", hash
    
def createoffer():
    markethash = raw_input("Enter a Market ID: ")
    name = raw_input("Enter a name for this OFFER: ")
    locale = raw_input("Enter a locale: ")
    print "Enter a description:"
    desc = multiline()
    amount = raw_input("Enter an amount: ")
    price = str( MM_util.truncate( decput("Enter a price: ") ) )
    ratio = str( decput("Enter a refund ratio: ") )
    locktime = intput("Enter a locktime: ")
    minrep = intput("Enter a minimum Reputation Score: ")
    numtags = intput("How many tags?: ")
    
    taglist = []
    for i in range(numtags):
        tagid = raw_input("Enter a Tag ID (%d/%d): " % (i+1, numtags))
        taglist.append(tagid)
    
    pubkey = MM_util.btcd.validateaddress(btcaddr)['pubkey']
    msgstr = MM_util.createoffermsgstr( btcaddr, markethash, myid.hash, pubkey, \
                                        name, locale, desc, amount, price, ratio, \
                                        locktime, minrep, taglist )
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('offer', hash)
    
    print "Offer ID:", hash
    
def createorder():
    offerhash = raw_input("Enter an Offer ID: ")
    offerlist = MM_util.loadlist('offer')
    marketlist = MM_util.loadlist('market')
    offer = MM_util.searchlistbyhash(offerlist, offerhash)
    market = MM_util.searchlistbyhash(marketlist, offer.obj['markethash'])
    
    price = decimal.Decimal(offer.obj['price'])
    mult = decimal.Decimal(market.obj['multiplier'])
    minrep = offer.obj['minrep']
    myrep = getrep(myid.hash, mult)
    
    if myrep < minrep:
        raise Exception("Insufficient Reputation Score.")
        
    pubkey = MM_util.btcd.validateaddress(btcaddr)['pubkey']
    multisig = MM_util.btcd.createmultisig( 2, sorted([offer.obj['pubkey'], pubkey]) )
    change_addr = MM_util.btcd.getrawchangeaddress()
    
    def create_funding(fee):
        rawtx_hex = MM_util.mktx(price, multisig['address'], change_addr, fee)
        return MM_util.btcd.signrawtransaction(rawtx_hex)['hex']
    
    signedtx_hex = create_funding(default_fee)
    funding_fee = MM_util.calc_fee(signedtx_hex)
    if funding_fee != default_fee:
        signedtx_hex = create_funding(funding_fee)
    
    crypttx = base64.b64encode( simplecrypt.encrypt(pkstr, signedtx_hex) )
    
    signedtx = MM_util.btcd.decoderawtransaction(signedtx_hex)
    vout = searchtxops(signedtx, multisig['address'], price)
    
    msgstr = MM_util.createordermsgstr(btcaddr, offer.hash, offer.obj['vendorid'], myid.hash, \
                                        pubkey, multisig, crypttx, signedtx['txid'], \
                                        vout, signedtx['vout'][vout]['scriptPubKey']['hex'] )
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('order', hash)
    
    print "Order ID:", hash
    
def createconf( orderhash=None ):
    if not orderhash:
        orderhash = raw_input("Enter an Order ID: ")
        
    orderlist = MM_util.loadlist('order')
    identlist = MM_util.loadlist('ident')
    order = MM_util.searchlistbyhash(orderlist, orderhash)
    buyer = MM_util.searchlistbyhash(identlist, order.obj['buyerid'])
    
    offer = MM_util.offerfromordermsg(order)
    price = decimal.Decimal(offer.obj['price'])
    ratio = decimal.Decimal(offer.obj['ratio'])
    
    pubkey = offer.obj['pubkey']
    ms_verify = MM_util.btcd.createmultisig( 2, sorted([order.obj['pubkey'], pubkey]) )
    if ms_verify['address'] != order.obj['multisig']['address']:
        raise Exception("Multisig did not verify!")
    
    b_portion, v_portion = MM_util.getamounts(ratio, price)
    
    refund_op = prev_tx = [ dict((key, order.obj[key]) for key in ("txid", "vout")) ]
    def create_refund(fee):
        refund_addr_obj = { buyer.obj['btcaddr']: b_portion - fee/2, 
                            btcaddr: v_portion - fee/2 }
        return MM_util.btcd.createrawtransaction(refund_op, refund_addr_obj)
        
    refund_tx_hex = create_refund(default_fee)
    refund_fee = MM_util.calc_fee(refund_tx_hex)
    if refund_fee != default_fee:
        refund_tx_hex = create_refund(refund_fee)
    
    #sets sequence to 0 (hacky as balls)
    refund_tx_hex = refund_tx_hex[:84] + "00000000" + refund_tx_hex[92:]
    #do nlocktime edit
    locktime = offer.obj['locktime']
    locktime_hex = bitcoin.core.b2lx( bytearray.fromhex(hex(locktime)[2:].rjust(8,'0')) )
    refund_tx_hex = refund_tx_hex[:-8] + locktime_hex
    
    prev_tx[0]["scriptPubKey"] = order.obj['spk']
    prev_tx[0]["redeemScript"] = order.obj['multisig']['redeemScript']
    
    sig_refund_hex = MM_util.btcd.signrawtransaction(refund_tx_hex, prev_tx, [wif])['hex']
    
    msgstr = MM_util.createconfmsgstr(btcaddr, order.hash, myid.hash, order.obj['buyerid'], \
                                        sig_refund_hex, prev_tx )
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('conf', hash)
    
    print "Confirmation ID:", hash
    return hash
    
def createpay():
    confhash = raw_input("Enter a Confirmation ID: ")
    address = raw_input("Enter an Address: ")
    
    conflist = MM_util.loadlist('conf')
    orderlist = MM_util.loadlist('order')

    conf = MM_util.searchlistbyhash(conflist, confhash)
    order = MM_util.searchlistbyhash(orderlist, conf.obj['orderhash'])
    offer = MM_util.offerfromordermsg(conf)
    
    price = decimal.Decimal(offer.obj['price'])
    ratio = decimal.Decimal(offer.obj['ratio'])
    b_portion, v_portion = MM_util.getamounts(ratio, price)
    refund_fee = MM_util.calc_fee( conf.obj['refundtx'] )
    
    refund_verify = MM_util.btcd.decoderawtransaction(conf.obj['refundtx'])
    searchtxops(refund_verify, btcaddr, b_portion - refund_fee/2)
    complete_refund = MM_util.btcd.signrawtransaction( conf.obj['refundtx'], conf.obj['prevtx'], [wif])['hex']
    
    print "Broadcast funding TX?:"
    if not MM_util.yorn():
        sys.exit(0)
    
    fund_tx = simplecrypt.decrypt( pkstr, base64.b64decode(order.obj['crypt_fundingtx']) )
    sendtx(fund_tx)
    
    msgstr = MM_util.createpaymsgstr(btcaddr, conf.hash, conf.obj['vendorid'], myid.hash, \
                                        complete_refund, address )
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('pay', hash)
    
    print "Payment ID:", hash
    
def createrec( payhash=None ):
    if not payhash:
        payhash = raw_input("Enter a Payment ID: ")
    
    paylist = MM_util.loadlist('pay')
    conflist = MM_util.loadlist('conf')
    orderlist = MM_util.loadlist('order')
    
    pay = MM_util.searchlistbyhash(paylist, payhash)
    conf = MM_util.searchlistbyhash(conflist, pay.obj['confhash'])
    order = MM_util.searchlistbyhash(orderlist, conf.obj['orderhash'])
    offer = MM_util.offerfromordermsg(pay)
    price = decimal.Decimal(offer.obj['price'])
    
    # Accept payment.
    fund_tx = gettx(order.obj['txid'])
    searchtxops(fund_tx, order.obj['multisig']['address'], price)
    waitforconf(order.obj['txid'])
    print "FUNDS SUCCESSFULLY ESCROWED. SHIP PRODUCT NOW."
    
    final_op = prev_tx = [ dict((key, order.obj[key]) for key in ("txid", "vout")) ]
    def create_final(fee):
        final_addr_obj = { btcaddr: price - fee }
        return MM_util.btcd.createrawtransaction(final_op, final_addr_obj)
        
    final_tx_hex = create_final(default_fee)
    final_fee = MM_util.calc_fee(final_tx_hex)
    if final_fee != default_fee:
        final_tx_hex = create_final(final_fee)

    prev_tx[0]["scriptPubKey"] = order.obj['spk']
    prev_tx[0]["redeemScript"] = order.obj['multisig']['redeemScript']
    
    sig_final_hex = MM_util.btcd.signrawtransaction(final_tx_hex, prev_tx, [wif])['hex']
    
    msgstr = MM_util.createrecmsgstr(btcaddr, pay.hash, myid.hash, pay.obj['buyerid'], \
                                        sig_final_hex, prev_tx )
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('rec', hash)
    
    print "Reciept ID:", hash
    return hash
    
def createfinal():
    rechash = raw_input("Enter a Reciept ID: ")
    
    reclist = MM_util.loadlist('rec')
    paylist = MM_util.loadlist('pay')
    identlist = MM_util.loadlist('ident')
    
    rec = MM_util.searchlistbyhash(reclist, rechash)
    pay = MM_util.searchlistbyhash(paylist, rec.obj['payhash'])
    vendor = MM_util.searchlistbyhash(identlist, rec.obj['vendorid'])
    
    offer = MM_util.offerfromordermsg(rec)
    price = decimal.Decimal(offer.obj['price'])
    time_for_refund = time.asctime( time.localtime(offer.obj['locktime']) )
    
    final_verify = MM_util.btcd.decoderawtransaction(rec.obj['finaltx'])
    searchtxops(final_verify, vendor.obj['btcaddr'], price - default_fee)
    complete_final = MM_util.btcd.signrawtransaction(rec.obj['finaltx'], rec.obj['prevtx'], [wif])['hex']
    
    print "Would you like to finalize or refund escrowed funds?:"
    finorref = raw_input("Enter the word [final or refund]: ")
    print "Are you sure?"
    if not MM_util.yorn():
        sys.exit()
        
    if finorref == 'final':
        final_tx = complete_final
    elif finorref == 'refund':
        print "Your refund tx will be sent to Bitcoin Core,"
        print "but cannot be confirmed until after", time_for_refund
        final_tx = pay.obj['refundhex']
    else:
        raise Exception("Must enter 'final' or 'refund'")
        
    final_txid = sendtx(final_tx)
    
    msgstr = MM_util.createfinalmsgstr(btcaddr, rec.hash, rec.obj['vendorid'], myid.hash, final_txid )
    hash = MM_util.MM_writefile(msgstr)
    MM_util.appendindex('final', hash)
    
    print "Finalize ID:", hash
    
def createfeedback():
    finalhash = raw_input("Enter a Finalize ID: ")
    print "Were you satisfied with this sale?:"
    upvote = MM_util.yorn()
    message = raw_input("Enter a Message: ")
    
    finallist = MM_util.loadlist('final')
    final = MM_util.searchlistbyhash(finallist, finalhash)
    offer = MM_util.offerfromordermsg(final)
    order = MM_util.offerfromordermsg(final, getorder=True)
    
    if entity == 'buyer':
        fromid = final.obj['buyerid']
        toid = final.obj['vendorid']
    elif entity == 'vendor':
        fromid = final.obj['vendorid']
        toid = final.obj['buyerid']
        
    msgstr = MM_util.createfeedbackmsgstr(btcaddr, offer.obj['markethash'], finalhash, fromid, toid, \
                                            final.obj['finaltxid'], order.obj['multisig']['redeemscript'], upvote, message)
    ver = MM_util.MM_loads(btcaddr, msgstr)
    MM_util.MM_writefile(msgstr)
    MM_util.appendindex('feedback', ver.hash)
    backupordermsgs(final.hash)
    
    print "Feedback ID: %s" % ver.hash
    
def createcancel():
    orderhash = raw_input("Enter an Order ID: ")
    orderlist = MM_util.loadlist('order')
    conflist = MM_util.loadlist('conf')
    order = MM_util.searchlistbyhash(orderlist, orderhash)
    
    MM_util.MM_backupfile('order', orderhash)
    
    toid = None
    if entity == 'buyer':
        toid = order.obj['vendorid']
        for conf in conflist:
            if conf.obj['orderhash'] == orderhash:
                MM_util.MM_backupfile('conf', conf.hash)
    else:
        toid = order.obj['buyerid']
    
    msgstr = MM_util.createcancelmsgstr(btcaddr, myid.hash, toid, orderhash)
    ver = MM_util.MM_loads(btcaddr, msgstr)
    MM_util.MM_writefile(msgstr)
    MM_util.appendindex('cancel', ver.hash)
    
    print "Cancel ID: %s" % ver.hash
    
    
    
def checkinbox( ):
    print "Checking Inbox."
    num = 0
    mkts = 0
    
    inbox = json.loads( MM_util.bm.getAllInboxMessages() )['inboxMessages']
    for i in inbox:
        subject = base64.b64decode( i['subject'] )
        if subject in ('Msg', 'MultiMsg'):
            num += 1
        elif subject == 'Mkt':
            mkts += 1
            
    if mkts > 0:
        print "You have %d Market Offer(s) waiting to be viewed!" % mkts
    if num > 0:
        print "You have %d Metamarket Message(s) waiting to be processed!" % num
    return num > 0
    
    
def processreg(msg, ver):
    if not allownewregs:
        return
        
    reg_tx = gettx(ver.obj['txid'])
    waitforconf(ver.obj['txid'])
    fee = decimal.Decimal(mymarket.obj['fee'])
    searchtxops(reg_tx, btcaddr, fee)
    
    MM_util.MM_writefile(msg)
    MM_util.appendindex('reg', ver.hash)
    print "REG Msg accepted:\n%s" % pretty_json(ver)
    
def processident(msg, ver):
    reglist = MM_util.loadlist('reg')
    
    for reg in reglist:
        if reg.obj['userid'] == ver.hash:
            MM_util.MM_writefile(msg)
            MM_util.appendindex('ident', ver.hash)
            print "IDENT Msg accepted:\n%s" % pretty_json(ver)
            return
    else:
        print("IDENT Msg rejected.")
        
def processburn(msg, ver):
    identlist = MM_util.loadlist("ident")
    user = MM_util.searchlistbyhash(identlist, ver.obj['userid'])
    burntxid = ver.obj['txid']
    burn_tx = gettx(burntxid)
    ag_tx = gettx( burn_tx['vin'][0]['txid'] )
    
    searchtxops(ag_tx, user.obj['btcaddr'])
    searchtxops(burn_tx, pob_address)
    
    if user:
        waitforconf(burntxid)
        
        MM_util.MM_writefile(msg)
        MM_util.appendindex('burn', ver.hash)
        print "BURN Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("BURN Msg rejected.")
        
def processtag(msg, ver):
    identlist = MM_util.loadlist("ident")
    
    if allownewtags and \
       ver.hash not in bannedtags and \
       MM_util.searchlistbyhash(identlist, ver.obj['vendorid']):
        MM_util.MM_writefile(msg)
        MM_util.appendindex('tags', ver.hash)
        print "TAG Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("TAG Msg rejected.")
        
def processoffer(msg, ver):
    identlist = MM_util.loadlist("ident")
    
    if allownewoffers and \
      MM_util.searchlistbyhash(identlist, ver.obj['vendorid']):
        for tag in ver.obj['tags']:
            if tag in bannedtags:
                return
        MM_util.MM_writefile(msg)
        MM_util.appendindex('offer', ver.hash)
        print "OFFER Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("OFFER Msg rejected.")
          
def processorder(msg, ver):
    identlist = MM_util.loadlist("ident")
    marketlist = MM_util.loadlist('market')
    offer = MM_util.offerfromordermsg(ver)
    buyer = MM_util.searchlistbyhash(identlist, ver.obj['buyerid'])
    market = MM_util.searchlistbyhash(marketlist, offer.obj['markethash'])
    
    mult = decimal.Decimal(market.obj['multiplier'])
    minrep = offer.obj['minrep']
    buyer_rep = getrep(buyer.hash, mult)
    
    if buyer and offer and buyer_rep >= minrep:
        MM_util.MM_writefile(msg)
        MM_util.appendindex('order', ver.hash)
        print "ORDER Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("ORDER Msg rejected.")
          
def processconf(msg, ver):
    identlist = MM_util.loadlist("ident")
    orderlist = MM_util.loadlist("order")
    
    if MM_util.searchlistbyhash(identlist, ver.obj['vendorid']) and \
       MM_util.searchlistbyhash(orderlist, ver.obj['orderhash']):
        MM_util.MM_writefile(msg)
        MM_util.appendindex('conf', ver.hash)
        print "CONF Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("CONF Msg rejected.")
          
def processpay(msg, ver):
    identlist = MM_util.loadlist("ident")
    conflist = MM_util.loadlist("conf")
    
    if MM_util.searchlistbyhash(identlist, ver.obj['buyerid']) and \
       MM_util.searchlistbyhash(conflist, ver.obj['confhash']):
        MM_util.MM_writefile(msg)
        MM_util.appendindex('pay', ver.hash)
        print "PAY Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("PAY Msg rejected.")
        
def processrec(msg, ver):
    identlist = MM_util.loadlist("ident")
    paylist = MM_util.loadlist("pay")
    
    if MM_util.searchlistbyhash(identlist, ver.obj['vendorid']) and \
       MM_util.searchlistbyhash(paylist, ver.obj['payhash']):
        MM_util.MM_writefile(msg)
        MM_util.appendindex('rec', ver.hash)
        print "REC Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("REC Msg rejected.")
        
def processfinal(msg, ver):
    identlist = MM_util.loadlist("ident")
    reclist = MM_util.loadlist("rec")
    
    if MM_util.searchlistbyhash(identlist, ver.obj['buyerid']) and \
       MM_util.searchlistbyhash(reclist, ver.obj['rechash']):
        MM_util.MM_writefile(msg)
        MM_util.appendindex('final', ver.hash)
        print "FINAL Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("FINAL Msg rejected.")
        
def processfeedback(msg, ver):
    identlist = MM_util.loadlist("ident")
    finallist = MM_util.loadlist("final")
    
    fromuser = MM_util.searchlistbyhash(identlist, ver.obj['fromid'])
    touser = MM_util.searchlistbyhash(identlist, ver.obj['toid'])
    
    finaltx = gettx(txid)
    prevtxid = finaltx['vin'][0]['txid']
    prevtx = gettx(prevtxid)
    msaddr = prevtx['vout'][0]['addresses'][0]
    
    redeemscript = MM_util.btcd.decodescript(ver.obj['redeemscript'])
    
    if fromuser and touser and \
       redeemscript['p2sh'] == msaddr and \
       fromuser.obj['btcaddr'] in redeemscript['addresses'] and \
       touser.obj['btcaddr'] in redeemscript['addresses']:
    
        MM_util.MM_writefile(msg)
        MM_util.appendindex('feedback', ver.hash)
        print "FEEDBACK Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("FEEDBACK Msg rejected.")

def processsync(msg, ver):
    identlist = MM_util.loadlist("ident")
    user = MM_util.searchlistbyhash(identlist, ver.obj['userid'])
    
    if user:
        modsync(user.obj['bmaddr'])
        MM_util.MM_writefile(msg)
        MM_util.appendindex('sync', ver.hash)
        print "SYNC Msg accepted:\n%s" % pretty_json(ver)
        print "SYNCing up with user:\n%s" % user.hash
    else:
        print("SYNC Msg rejected.")
        
def processcast(msg, ver):
    identlist = MM_util.loadlist("ident")
    
    if MM_util.searchlistbyhash(identlist, ver.obj['modid']):
        MM_util.unpackcastlist(ver.obj['identlist'], 'ident')
        MM_util.unpackcastlist(ver.obj['burnlist'], 'burn')
        MM_util.unpackcastlist(ver.obj['taglist'], 'tags')
        MM_util.unpackcastlist(ver.obj['offerlist'], 'offer')
        MM_util.unpackcastlist(ver.obj['feedbacklist'], 'feedback')
        print "CAST Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("CAST Msg rejected.")
        
def processcancel(msg, ver):
    identlist = MM_util.loadlist('ident')
    orderlist = MM_util.loadlist('order')
    conflist = MM_util.loadlist('conf')
    
    if MM_util.searchlistbyhash(identlist, ver.obj['fromid']) and \
       MM_util.searchlistbyhash(orderlist, ver.obj['orderhash']):
        MM_util.MM_backupfile('order', ver.obj['orderhash'])
        
        if entity == 'vendor':
            for conf in conflist:
                if conf.obj['orderhash'] == ver.obj['orderhash']:
                    MM_util.MM_backupfile('conf', conf.hash)
                    
        MM_util.MM_writefile(msg)
        MM_util.appendindex('sync', ver.hash)
        print "CANCEL Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("CANCEL Msg rejected.")
        
        

def processmsg(msg):
    ver = MM_util.readmsg(msg) # Verifies sig/hash
    
    if ver.msgname == MM_util.IDENT and entity == 'mod':
        processident(msg, ver)
    elif ver.msgname == MM_util.REG and entity == 'mod':
        processreg(msg, ver)
    elif ver.msgname == MM_util.BURN and entity == 'mod':
        processburn(msg, ver)
    elif ver.msgname == MM_util.TAG and entity == 'mod':
        processtag(msg, ver)
    elif ver.msgname == MM_util.OFFER and entity != 'vendor':
        processoffer(msg, ver)
    elif ver.msgname == MM_util.ORDER and entity == 'vendor':
        processorder(msg, ver)
    elif ver.msgname == MM_util.CONF and entity == 'buyer':
        processconf(msg, ver)
    elif ver.msgname == MM_util.PAY and entity == 'vendor':
        processpay(msg, ver)
    elif ver.msgname == MM_util.REC and entity == 'buyer':
        processrec(msg, ver)
    elif ver.msgname == MM_util.FINAL and entity == 'vendor':
        processfinal(msg, ver)
    elif ver.msgname == MM_util.FEEDBACK and entity == 'mod':
        processfeedback(msg, ver)
    elif ver.msgname == MM_util.SYNC and entity == 'mod':
        processsync(msg, ver)
    elif ver.msgname == MM_util.CAST and entity != 'mod':
        processcast(msg, ver)
    elif ver.msgname == MM_util.CANCEL and entity != 'mod':
        processcancel(msg, ver)
    else:
        print "Someone sent us the wrong type of Msg."
    return ver
    
def processmultimsg(mmsg):
    mmsgobj = MM_util.MultiMsg(**json.loads(mmsg))
    fname = "multimsg.dat"
    mmsgfile = open(fname, 'r')
    mmsgdict = json.load(mmsgfile)
    mmsgfile.close()
    msginfo = None
    
    if mmsgobj.hash in mmsgdict:
        msglist = mmsgdict[mmsgobj.hash]
        for i in range( len(msglist) ):
            msglist[i] = MM_util.MultiMsg(**msglist[i])
        msglist.append(mmsgobj)
        
        if len(msglist) == mmsgobj.total:
            origmsg = MM_util.reconstructmsg(msglist)
            msginfo = processmsg(origmsg)
            del(mmsgdict[mmsgobj.hash])
    else:
        mmsgdict[mmsgobj.hash] = [mmsgobj]
        
    mmsgfile = open(fname, 'w')
    json.dump(mmsgdict, mmsgfile)
    mmsgfile.close()
    print "MultiMsg recieved."
    return msginfo
    
# Gets BM inbox from API, processes all new 'Msg's
def processinbox( ):
    print "Processing Inbox."
    msginfolist = []
    inbox = json.loads( MM_util.bm.getAllInboxMessages() )['inboxMessages']
    for i in inbox:
        subject = base64.b64decode( i['subject'] )
        bmmsg = base64.b64decode( i['message'] )
        if i['toAddress'] == bmaddr and subject == 'Msg':
            msginfo = processmsg(bmmsg)
            if msginfo:
                msginfolist.append(msginfo)
            MM_util.bm.trashMessage( i['msgid'] )
        elif i['toAddress'] == bmaddr and subject == 'MultiMsg':
            msginfo = processmultimsg(bmmsg)
            if msginfo:
                msginfolist.append(msginfo)
            MM_util.bm.trashMessage( i['msgid'] )
    return msginfolist
    
    
def createmsg(msgtype):
    print "Creating Msg of type: %s" % msgtype
    types = ('reg', 'burn', 'sync', 'tag', 'market', 'offer', 'order', \
                'cancel', 'conf', 'pay', 'rec', 'final', 'feedback')
    if msgtype not in types:
        raise Exception( "msgtype MUST be in %s" % str(types) )
        
    if msgtype == 'reg' and entity != 'mod':
        createreg()
    elif msgtype == 'burn' and entity != 'mod':
        createburn()
    elif msgtype == 'sync' and entity != 'mod':
        createsync()
    elif msgtype == 'tag' and entity != 'buyer':
        createtag()
    elif msgtype == 'market':
        createmarket()
    elif msgtype == 'offer' and entity == 'vendor':
        createoffer()
    elif msgtype == 'order' and entity == 'buyer':
        createorder()
    elif msgtype == 'conf' and entity == 'vendor':
        createconf()
    elif msgtype == 'pay' and entity == 'buyer':
        createpay()
    elif msgtype == 'rec' and entity == 'vendor':
        createrec()
    elif msgtype == 'final' and entity == 'buyer':
        createfinal()
    elif msgtype == 'feedback' and entity != 'mod':
        createfeedback()
    elif msgtype == 'cancel' and entity != 'mod':
        createcancel()
    else:
        raise Exception("Incorrect Entity or Msg type.")
        
def sendmsg(msgid, prompt=True):
    print "Sending Msg: %s" % msgid
    
    identlist = MM_util.loadlist('ident')
    marketlist = MM_util.loadlist('market')
    msgstr = open( os.path.join(msgdir, msgid + '.dat'), 'r' ).read()
    ver = MM_util.readmsg(msgstr)
    
    if ver.msgname == MM_util.IDENT:
        marketid = raw_input("Enter a Market ID to sync your Identity with: ")
        market = MM_util.searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    elif ver.msgname == MM_util.BURN:
        marketid = raw_input("Enter a Market ID to register your Proof-of-Burn at: ")
        market = MM_util.searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    elif ver.msgname == MM_util.REG:
        ident = ver.obj['modid']
    elif ver.msgname == MM_util.SYNC:
        ident = ver.obj['modid']
    elif ver.msgname == MM_util.CANCEL:
        ident = ver.obj['toid']
    elif ver.msgname == MM_util.TAG and entity == "vendor":
        marketid = raw_input("Enter a Market ID to register the Tag at: ")
        market = MM_util.searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    elif ver.msgname == MM_util.OFFER and entity == "vendor":
        marketid = MM_util.MM_extract('markethash', msgstr)        
        market = MM_util.searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    elif ver.msgname == MM_util.ORDER and entity == "buyer":
        ident = MM_util.MM_extract('vendorid', msgstr)        
    elif ver.msgname == MM_util.CONF and entity == "vendor":
        ident = MM_util.MM_extract('buyerid', msgstr)        
    elif ver.msgname == MM_util.PAY and entity == "buyer":
        ident = MM_util.MM_extract('vendorid', msgstr)        
    elif ver.msgname == MM_util.REC and entity == "vendor":
        ident = MM_util.MM_extract('buyerid', msgstr)        
    elif ver.msgname == MM_util.FINAL and entity == "buyer":
        ident = MM_util.MM_extract('vendorid', msgstr)        
    elif ver.msgname == MM_util.FEEDBACK and entity != "mod":
        marketid = MM_util.MM_extract('markethash', msgstr)        
        market = MM_util.searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    else:
        raise Exception("Bad Msg type.")
        
    tobm = MM_util.searchlistbyhash( identlist, ident ).obj['bmaddr']
    MM_util.sendmsgviabm(tobm, bmaddr, msgstr, prompt)
    
    
def showchan( channame ):
    print "Showing Chan: %s" % channame
    if channame == default_channame:
        chanv3 = default_chan_v3
        chanv4 = default_chan_v4
    else:
        chanv3 = MM_util.bm.getDeterministicAddress( base64.b64encode(channame), 3,1 )
        chanv4 = MM_util.bm.getDeterministicAddress( base64.b64encode(channame), 4,1 )
    
    inbox = json.loads( MM_util.bm.getAllInboxMessages() )['inboxMessages']
    for i in inbox:
        if  i['toAddress'] in (chanv3, chanv4):
            sbj = base64.b64decode(i['subject'])
            print "MSGID: %s\nSUBJECT: %s\n" % ( i['msgid'], sbj )
    
def showchanmsg(msgid):
    print "Showing Chan Msg: %s" % msgid
    bmmsg = json.loads( MM_util.bm.getInboxMessageById(msgid) )['inboxMessage'][0]
    subject = base64.b64decode(bmmsg['subject'])
    msg = base64.b64decode(bmmsg['message'])
    print "SUBJECT: %s\nMESSAGE:\n%s" % (subject, msg)
    
def showmsglist(msgtype):
    print "Showing Msg List: %s" % msgtype
    types = ('burn', 'ident', 'tags', 'market', 'offer', 'order', \
                'conf', 'pay', 'rec', 'final', 'feedback', 'cast')
    if msgtype not in types:
        raise Exception( "msgtype MUST be in %s" % str(types) )
    
    mkt = None
    if msgtype == 'ident':
        mkt = raw_input("Enter a Market ID : ")
    list = MM_util.loadlist(msgtype)
    showanylist(list, mkt)
    
def showmsg(hash):
    print "Showing Msg: %s" % hash
    msgstr = open( os.path.join(msgdir, hash + '.dat'), 'r' ).read()
    ver = MM_util.readmsg(msgstr)
    print pretty_json(ver)
    
def sendmarketoffer(channame):
    if not mymarket:
        raise Exception("There is no Market to offer!")
        
    print "Sending Market Offer to chan: %s" % channame
    if channame == default_channame:
        chan_addr = default_chan_v4
    else:
        chan_addr = MM_util.bm.getDeterministicAddress( base64.b64encode(channame), 4,1 )
    
    info = {    "market": mymarket,
                "modid": myid }
    mktoffer = pretty_json(info)
    MM_util.sendmsgviabm( chan_addr, bmaddr, mktoffer, False, 'Mkt' )
    

def parseargs():
    global args
    
    parser = argparse.ArgumentParser(description="METAMARKET Command Line Interface")
    parser.add_argument('-e',
                        '--entity',
                        default=default_entity,
                        action='store',
                        dest='entity',
                        help='Choose which entity to act as: buyer, vendor, or mod.')
    parser.add_argument('-c',
                        '--chain',
                        default=default_chain,
                        action='store',
                        dest='chain',
                        help='Choose which blockchain to use: testnet or mainnet.')
    parser.add_argument('-p',
                        '--btcport',
                        default=default_btc_port,
                        action='store',
                        dest='btc_port',
                        help='Use a specific RPC port to connect to Bitcoin Core.') # Great for regtest mode
    
    subparsers = parser.add_subparsers(help='Program mode:', dest='mode')
    check_inbox_parser = subparsers.add_parser( \
                        'checkinbox', help='Check your BM inbox for new MM Messages.')

    process_inbox_parser = subparsers.add_parser( \
                        'processinbox', help='Parse your BM inbox for MM Messages.')

    modbanuser_parser = subparsers.add_parser( \
                        'modbanuser', help='Moderator: Ban a User.')

    modbantag_parser = subparsers.add_parser( \
                        'modbantag', help='Moderator: Ban a Tag. (and all Offers bearing said Tag)')

    modremoveoffer_parser = subparsers.add_parser( \
                        'modremoveoffer', help='Moderator: Remove an Offer.')

    show_chan_parser = subparsers.add_parser( \
                        'showchan', help='Show a list of available chan messages.')
    show_chan_parser.add_argument(  '-c',
                                    '--channame',
                                    default=default_channame,
                                    action='store',
                                    dest='channame',
                                    help='Show messages from a specific chan, given its passphrase.' )
                                    
    show_chanmsg_parser = subparsers.add_parser( \
                        'showchanmsg', help='Show a specific chan message.')
    show_chanmsg_parser.add_argument(   '-m',
                                        '--msgid',
                                        required=True,
                                        action='store',
                                        dest='msgid',
                                        help='Show a message, given a message ID.' )
                                        
    show_msglist_parser = subparsers.add_parser( \
                        'showmsglist', help='Show your current list of some type of MM Messages.')
    show_msglist_parser.add_argument(   '-t',
                                        '--msgtype',
                                        default=MM_util.IDENT,
                                        action='store',
                                        dest='msgtype',
                                        help='Show a list of MM Messages, given a specific type.' )
                                        
    show_msg_parser = subparsers.add_parser( \
                        'showmsg', help='Show a specific MM Message in detail.')
    show_msg_parser.add_argument(   '-m',
                                    '--msgid',
                                    required=True,
                                    action='store',
                                    dest='msgid',
                                    help='Show a MM Message, given its ID.' )
                                    
    create_msg_parser = subparsers.add_parser( \
                        'createmsg', help='Create any new MM Message.')
    create_msg_parser.add_argument( '-t',
                                    '--msgtype',
                                    required=True,
                                    action='store',
                                    dest='msgtype',
                                    help='Create a new MM Message of some type.' )
                                    
    send_msg_parser = subparsers.add_parser( \
                        'sendmsg', help='Send any MM Message over BM.')
    send_msg_parser.add_argument(   '-m',
                                    '--msgid',
                                    required=True,
                                    action='store',
                                    dest='msgid',
                                    help='Send a MM Message, given its ID; to its recipient via BM.' )
                                    
    send_market_parser = subparsers.add_parser( \
                        'sendmarketoffer', help='As a Moderator, send your Market offer to the chan.' )
    send_market_parser.add_argument('-c',
                                    '--channame',
                                    default=default_channame,
                                    action='store',
                                    dest='channame',
                                    help='Send Market offer to a specific chan, given its passphrase.' )

    args = parser.parse_args()

    
def main():
    if args.mode == "checkinbox":
        checkinbox()
    elif args.mode == "processinbox":
        login()
        processinbox()
        MM_util.btcd.walletlock()
    elif args.mode == "modbanuser":
        modbanuser()
    elif args.mode == "modbantag":
        modbantag()
    elif args.mode == "modremoveoffer":
        modremoveoffer()
    elif args.mode == "showchan":
        showchan(args.channame)
    elif args.mode == "showchanmsg":
        showchanmsg(args.msgid)
    elif args.mode == "showmsglist":
        showmsglist(args.msgtype)
    elif args.mode == "showmsg":
        showmsg(args.msgid)
    elif args.mode == "createmsg":
        login()
        createmsg(args.msgtype)
        MM_util.btcd.walletlock()
    elif args.mode == "sendmsg":
        login()
        sendmsg(args.msgid)
        MM_util.btcd.walletlock()
    elif args.mode == "sendmarketoffer" and entity == "mod":
        login()
        sendmarketoffer(args.channame)
        MM_util.btcd.walletlock()

msgdir = 'msg'
SLEEP = 1
username = passphrase = pkstr = btcaddr = wif = bmaddr = myid = mymarket = None
allownewregs = allownewtags = allownewoffers = bannedtags = None

section = 'metamarket'
defaults = {    'chain':        'mainnet',
                'entity':       'buyer',
                'channame':     'METAMARKET',
                'fee':          '0.0001',
                'minconf':      '6',
                'allownewtags': 'True',
                'bmuser':       'username',
                'bmpswd':       'password',
                'bmhost':       'localhost',
                'bmport':       '8442',
                'btcport':      '8332'    }
config = ConfigParser.RawConfigParser(defaults)
config.read('mm.cfg')

default_chain = config.get(section, 'chain')
default_entity = config.get(section, 'entity')
default_channame = config.get(section, 'channame')

default_fee = MM_util.truncate( decimal.Decimal( config.get(section, 'fee') ) )
minconf = config.getint(section, 'minconf')
if default_entity == 'mod':
    allownewregs = config.getboolean(section, 'allownewregs')
    allownewtags = config.getboolean(section, 'allownewtags')
    allownewoffers = config.getboolean(section, 'allownewoffers')

bm_url = "http://%s:%s@%s:%d" % ( config.get(section, 'bmuser'),
                                config.get(section, 'bmpswd'),
                                config.get(section, 'bmhost'),
                                config.getint(section, 'bmport') )                                
default_btc_port = config.getint(section, 'btcport')

args = None

if __name__ == "__main__":
    parseargs()
    entity = args.entity
    chain = args.chain
    btc_port = args.btc_port
else:
	entity = default_entity
	chain = default_chain
	btc_port = default_btc_port

if chain == 'testnet':
    netcode = 'XTN'
    pob_address = "msj42CCGruhRsFrGATiUuh25dtxYtnpbTx"
elif chain == 'mainnet':
    netcode = 'BTC'
    pob_address = "1METAMARKETxxxxxxxxxxxxxxxxx4TPjws"
else:
    raise Exception("Config: chain must be either testnet or mainnet.")

if entity not in ('buyer', 'vendor', 'mod'):
    raise Exception("Config: entity must be buyer, vendor or mod.")

bitcoin.SelectParams(chain)
MM_util.btcd = bitcoin.rpc.RawProxy(service_port=btc_port)
MM_util.bm = xmlrpclib.ServerProxy(bm_url)

default_chan_v3 = MM_util.bm.getDeterministicAddress( base64.b64encode(default_channame), 3,1 )
default_chan_v4 = MM_util.bm.getDeterministicAddress( base64.b64encode(default_channame), 4,1 )

if __name__ == "__main__":
    main()
    
    
    
