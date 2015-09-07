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

from MM_util import *
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
    
    unlockwallet(wp)
    if not MM_util.btcd.validateaddress(btcaddr)['ismine'] or \
        MM_util.bm.createDeterministicAddresses(base64.b64encode(pkstr)) != []:
        importkeys()
    
    identlist = loadlist('ident')
    
    myidstr = createidentmsgstr(btcaddr, bmaddr, username)
    myid = MM_loads( btcaddr, myidstr )
    print "My ID: %s" % myid.hash
    
    if not searchlistbyhash(identlist, myid.hash):
        register(myidstr)
    
    if entity == 'mod':
        marketlist = loadlist('market')
        for i in marketlist:
            if i.obj['modid'] == myid.hash:
                mymarket = i
                print "My Market ID:", mymarket.hash
        bannedtags = loadindex('bannedtags')
        
def importkeys( ):
    print "Bitcoin private key not found in wallet"
    print "or Bitmessage identity does not exist."
    print "Import your BTC private key and create your BM ID?"
    if yorn():
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
    if not yorn():
        login()
    else:
        MM_writefile(idstr)
        appendindex('ident', myid.hash)
        
        
def synccast( ):
    identlist = loadlist('ident')
    burnlist = loadlist('burn')
    taglist = loadlist('tags')
    offerlist = loadlist('offer')
    feedbacklist = loadlist('feedback')
    
    return createcastmsgstr(btcaddr, myid.hash, \
                identlist, burnlist, taglist, offerlist, feedbacklist)
    
# creates a "CAST Msg" from current lists and broadcasts over BM
def modbroadcast( ):
    MM_util.bm.sendBroadcast(bmaddr, base64.b64encode('Msg'), base64.b64encode(synccast()))

# creates a "CAST Msg" from current lists and sends to new user
def modsync( bm_addr ):
    do_sendmsgviabm(bm_addr, bmaddr, synccast(), False)

def do_modbanuser( ):
    userid = raw_input("Enter a User ID: ")
    print "Are you sure?:"
    if not yorn():
        return
        
    identlist = loadlist('ident')
    offerlist = loadlist('offer')
    
    modbanuser(userid, identlist, offerlist)
    
def do_modbantag( ):
    taghash = raw_input("Enter a Tag ID: ")
    print "Are you sure?:"
    if not yorn():
        return
        
    offerlist = loadlist('offer')
    bannedtags.append(taghash)
    modbantag(taghash, offerlist, bannedtags)

def do_modremoveoffer( ):
    offerhash = raw_input("Enter an Offer ID: ")
    print "Are you sure?:"
    if not yorn():
        return
    modremoveoffer(offerhash)
        
    
def do_getrep( identhash, burn_mult ):
    return getrep( identhash, burn_mult, loadlist('feedback'), loadlist('burn') )

# Takes a verified "OrderMsg" and returns the associated Offer.
def do_offerfromordermsg( msg, getorder=False ):
    return offerfromordermsg( msg, loadlist('offer'), \
                                   loadlist('order'), \
                                   loadlist('conf'), \
                                   loadlist('pay'), \
                                   loadlist('rec'), getorder )
    
    
# Takes a list of Verified Msgs and prints info to stdout.
def showanylist( list, mktid=None, marketlist=None ):
    for i in list:
        title = "Name"
        if i.msgname == REG:
            title = "User ID"
            str = i.obj['userid']
        elif i.msgname == BURN:
            title = "TXID"
            str = i.obj['txid']
        elif i.msgname == IDENT:
            market = searchlistbyhash(marketlist, mktid)
            mult = decimal.Decimal( market.obj['multiplier'] )
            rep = do_getrep(i.hash, mult)
            str = "%s:\tRep: %d" % ( i.obj['name'], rep )
        elif i.msgname == TAG:
            str = i.obj['tagname']
        elif i.msgname == MARKET:
            str = i.obj['marketname']
        elif i.msgname == OFFER:
            str = "%s;\t%s:\t%s BTC" % ( i.obj['name'], i.obj['amount'], i.obj['price'] )
        elif i.msgname == FEEDBACK:
            title = "Message"
            str = i.obj['message']
        else:
            offer = do_offerfromordermsg(i)
            str = "%s;\t%s:\t%s BTC" % ( offer.obj['name'], offer.obj['amount'], offer.obj['price'] )
        print "%s: %s\nID: %s\n" % ( title, str, i.hash )

    
def do_backupordermsgs(finalhash):
    backupordermsgs( finalhash, loadlist('final'), loadlist('rec'), loadlist('pay'), loadlist('conf') )
    
def do_sendmsgviabm(to_addr, from_addr, msgstr, prompt, subject='Msg'):
    if prompt:
        print "Are you sure you want to send this Message?"
    if not prompt or yorn():
        sendmsgviabm(to_addr, from_addr, msgstr, subject)
        print "Message sent!"

# Asks user yes or no, returns boolean
def yorn( ):
    yorn = raw_input("[Y or N]: ")
    return yorn in ('Y', 'y', 'yes', 'YES', 'Yes')

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
        

def do_createreg():
    markethash = raw_input("Enter a Market ID: ")
    
    marketlist = loadlist('market')
    identlist = loadlist('ident')
    market = searchlistbyhash(marketlist, markethash)
    mod = searchlistbyhash(identlist, market.obj['modid'])
    modbtc = mod.obj['btcaddr']
    amount = decimal.Decimal(market.obj['fee'])
    
    print "Are you sure you want to register at %s;" % market.obj['marketname']
    print "by sending %f BTC to %s?:" % ( amount, modbtc )
    if not yorn():
        sys.exit()
        
    msgstr = createreg(myid.hash, btcaddr, amount, mod, default_fee)
    hash = MM_writefile(msgstr)
    appendindex('reg', hash)
    
    print "Registration ID:", hash
    
    
def do_createburn():
    amount = truncate( decput("Enter an amount of BTC to burn: ") )
    print "Are you sure you want to BURN %f coin(s)" % amount
    print "by sending to %s?:" % pob_address
    if not yorn():
        sys.exit()

    msgstr = createburn(myid.hash, btcddr, amount, default_fee)
    hash = MM_writefile(msgstr)
    appendindex('burn', hash)
    
    print "Burn ID:", hash

        
def createtag():
    tagname = raw_input("Enter a name for this TAG: ")
    desc = raw_input("Enter a description: ")
    
    msgstr = createtagmsgstr(btcaddr, myid.hash, tagname, desc)
    hash = MM_writefile(msgstr)
    appendindex('tags', hash)
    
    print "Tag ID:", hash

################################# createmarket STILL REQUIRES REFACTORING ##############

def createmarket():
    global mymarket
    
    if entity != 'mod':
        print "Enter a Market Offer:"
        infostr = multiline()
        info = json.loads(infostr)
        mod = info['modid']
        market = info['market']
        
        idb64 = base64.b64encode( json.dumps(mod['obj'], sort_keys=True) )
        idmsg = Msg( idb64, mod['sig'], mod['hash'], mod['msgname'] )
        idmsgstr = json.dumps(idmsg)
        
        if not readmsg(idmsgstr): # Verifies sig/hash
            raise Exception("New Market creation failed..")
        MM_writefile(idmsgstr)
        appendindex('ident', idmsg.hash)
        
        mktb64 = base64.b64encode( json.dumps(market['obj'], sort_keys=True) )
        mktmsg = Msg( mktb64, market['sig'], market['hash'], market['msgname'] )
        mktmsgstr = json.dumps(mktmsg)
        
        if not readmsg(mktmsgstr): # Verifies sig/hash
            raise Exception("New Market creation failed..")
        MM_writefile(mktmsgstr)
        appendindex('market', mktmsg.hash)
        
        MM_util.bm.addSubscription(mod['obj']['bmaddr'])
        print "Congratulations, you may now Register with a new Metamarket!"
        print "Market ID:", mktmsg.hash
        
    else:
        if not mymarket:
            marketname = raw_input("Enter a name for this MARKET: ")
            print "Enter a description:"
            desc = multiline()
            reg_fee = str( truncate( decput("Enter a registration fee: ") ) )
            burn_mult = str( decput("Enter a Burn Multiplier: ") )
            
            msgstr = createmarketmsgstr(btcaddr, myid.hash, marketname, desc, reg_fee, burn_mult)
            mymarket = MM_loads(btcaddr, msgstr)
            MM_writefile(msgstr)
            appendindex('market', mymarket.hash)
            print "Congratulations, you are the proud new Owner of a new Metamarket!"
            print "Market ID:", mymarket.hash
        else:
            raise Exception("You are already running a Market!")
    
    
def createsync():
    markethash = raw_input("Enter a Market ID: ")
    marketlist = loadlist('market')
    market = searchlistbyhash(marketlist, markethash)
    
    msgstr = createsyncmsgstr(btcaddr, market.obj['modid'], myid.hash)
    hash = MM_writefile(msgstr)
    appendindex('sync', hash)
    
    print "Sync ID:", hash
    
    
def createoffer():
    markethash = raw_input("Enter a Market ID: ")
    name = raw_input("Enter a name for this OFFER: ")
    locale = raw_input("Enter a locale: ")
    print "Enter a description:"
    desc = multiline()
    amount = raw_input("Enter an amount: ")
    price = str( truncate( decput("Enter a price: ") ) )
    ratio = str( decput("Enter a refund ratio: ") )
    locktime = intput("Enter a locktime: ")
    minrep = intput("Enter a minimum Reputation Score: ")
    numtags = intput("How many tags?: ")
    
    taglist = []
    for i in range(numtags):
        tagid = raw_input("Enter a Tag ID (%d/%d): " % (i+1, numtags))
        taglist.append(tagid)
    
    pubkey = MM_util.btcd.validateaddress(btcaddr)['pubkey']
    msgstr = createoffermsgstr( btcaddr, markethash, myid.hash, pubkey, \
                                        name, locale, desc, amount, price, ratio, \
                                        locktime, minrep, taglist )
    hash = MM_writefile(msgstr)
    appendindex('offer', hash)
    
    print "Offer ID:", hash
    
def do_createorder():
    offerhash = raw_input("Enter an Offer ID: ")
    offerlist = loadlist('offer')
    marketlist = loadlist('market')
    offer = searchlistbyhash(offerlist, offerhash)
    market = searchlistbyhash(marketlist, offer.obj['markethash'])
    
    mult = decimal.Decimal(market.obj['multiplier'])
    minrep = offer.obj['minrep']
    myrep = do_getrep(myid.hash, mult)
    
    if myrep < minrep:
        raise Exception("Insufficient Reputation Score.")
    
    msgstr = createorder(myid.hash, btcaddr, offer, pkstr, default_fee)
    hash = MM_writefile(msgstr)
    appendindex('order', hash)
    
    print "Order ID:", hash
        

def do_createconf( orderhash=None ):
    if not orderhash:
        orderhash = raw_input("Enter an Order ID: ")
        
    orderlist = loadlist('order')
    identlist = loadlist('ident')
    order = searchlistbyhash(orderlist, orderhash)
    offer = do_offerfromordermsg(order)
    buyer = searchlistbyhash(identlist, order.obj['buyerid'])
    
    msgstr = createconf( myid.hash, btcaddr, order, offer, buyer, default_fee )
    hash = MM_writefile(msgstr)
    appendindex('conf', hash)
    
    print "Confirmation ID:", hash
    return hash
    
    
def do_createpay():
    confhash = raw_input("Enter a Confirmation ID: ")
    address = raw_input("Enter an Address: ")
    
    print "Broadcast funding TX?:"
    if not yorn():
        sys.exit(0)
    
    conflist = loadlist('conf')
    orderlist = loadlist('order')

    conf = searchlistbyhash(conflist, confhash)
    order = searchlistbyhash(orderlist, conf.obj['orderhash'])
    offer = do_offerfromordermsg(conf)
    
    msgstr = createpay(myid.hash, btcaddr, conf, order, offer)
    hash = MM_writefile(msgstr)
    appendindex('pay', hash)
    
    print "Payment ID:", hash
    
    
def do_createrec( payhash=None ):
    if not payhash:
        payhash = raw_input("Enter a Payment ID: ")
    
    paylist = loadlist('pay')
    conflist = loadlist('conf')
    orderlist = loadlist('order')
    
    pay = searchlistbyhash(paylist, payhash)
    conf = searchlistbyhash(conflist, pay.obj['confhash'])
    order = searchlistbyhash(orderlist, conf.obj['orderhash'])
    offer = do_offerfromordermsg(pay)
    price = decimal.Decimal(offer.obj['price'])
    
    msgstr = createrec(myid.hash, btcaddr, pay, order, price)
    print "FUNDS SUCCESSFULLY ESCROWED. SHIP PRODUCT NOW."
    hash = MM_writefile(msgstr)
    appendindex('rec', hash)
    
    print "Reciept ID:", hash
    return hash
    
########################### LEFT OFF REFACTORING HERE ##############################

def createfinal():
    rechash = raw_input("Enter a Reciept ID: ")
    
    reclist = loadlist('rec')
    paylist = loadlist('pay')
    identlist = loadlist('ident')
    
    rec = searchlistbyhash(reclist, rechash)
    pay = searchlistbyhash(paylist, rec.obj['payhash'])
    vendor = searchlistbyhash(identlist, rec.obj['vendorid'])
    
    offer = do_offerfromordermsg(rec)
    price = decimal.Decimal(offer.obj['price'])
    time_for_refund = time.asctime( time.localtime(offer.obj['locktime']) )
    
    final_verify = MM_util.btcd.decoderawtransaction(rec.obj['finaltx'])
    searchtxops(final_verify, vendor.obj['btcaddr'], price - default_fee)
    complete_final = MM_util.btcd.signrawtransaction(rec.obj['finaltx'], rec.obj['prevtx'], [wif])['hex']
    
    print "Would you like to finalize or refund escrowed funds?:"
    finorref = raw_input("Enter the word [final or refund]: ")
    print "Are you sure?"
    if not yorn():
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
    
    msgstr = createfinalmsgstr(btcaddr, rec.hash, rec.obj['vendorid'], myid.hash, final_txid )
    hash = MM_writefile(msgstr)
    appendindex('final', hash)
    
    print "Finalize ID:", hash
    
def createfeedback():
    finalhash = raw_input("Enter a Finalize ID: ")
    print "Were you satisfied with this sale?:"
    upvote = yorn()
    message = raw_input("Enter a Message: ")
    
    finallist = loadlist('final')
    final = searchlistbyhash(finallist, finalhash)
    offer = do_offerfromordermsg(final)
    order = do_offerfromordermsg(final, getorder=True)
    
    if entity == 'buyer':
        fromid = final.obj['buyerid']
        toid = final.obj['vendorid']
    elif entity == 'vendor':
        fromid = final.obj['vendorid']
        toid = final.obj['buyerid']
        
    msgstr = createfeedbackmsgstr(btcaddr, offer.obj['markethash'], finalhash, fromid, toid, \
                                            final.obj['finaltxid'], order.obj['multisig']['redeemscript'], upvote, message)
    ver = MM_loads(btcaddr, msgstr)
    MM_writefile(msgstr)
    appendindex('feedback', ver.hash)
    do_backupordermsgs(final.hash)
    
    print "Feedback ID: %s" % ver.hash
    
def createcancel():
    orderhash = raw_input("Enter an Order ID: ")
    orderlist = loadlist('order')
    conflist = loadlist('conf')
    order = searchlistbyhash(orderlist, orderhash)
    
    MM_backupfile('order', orderhash)
    
    toid = None
    if entity == 'buyer':
        toid = order.obj['vendorid']
        for conf in conflist:
            if conf.obj['orderhash'] == orderhash:
                MM_backupfile('conf', conf.hash)
    else:
        toid = order.obj['buyerid']
    
    msgstr = createcancelmsgstr(btcaddr, myid.hash, toid, orderhash)
    ver = MM_loads(btcaddr, msgstr)
    MM_writefile(msgstr)
    appendindex('cancel', ver.hash)
    
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
    
    MM_writefile(msg)
    appendindex('reg', ver.hash)
    print "REG Msg accepted:\n%s" % pretty_json(ver)
    
def processident(msg, ver):
    reglist = loadlist('reg')
    
    for reg in reglist:
        if reg.obj['userid'] == ver.hash:
            MM_writefile(msg)
            appendindex('ident', ver.hash)
            print "IDENT Msg accepted:\n%s" % pretty_json(ver)
            return
    else:
        print("IDENT Msg rejected.")
        
def processburn(msg, ver):
    identlist = loadlist("ident")
    user = searchlistbyhash(identlist, ver.obj['userid'])
    burntxid = ver.obj['txid']
    burn_tx = gettx(burntxid)
    ag_tx = gettx( burn_tx['vin'][0]['txid'] )
    
    searchtxops(ag_tx, user.obj['btcaddr'])
    searchtxops(burn_tx, pob_address)
    
    if user:
        waitforconf(burntxid)
        
        MM_writefile(msg)
        appendindex('burn', ver.hash)
        print "BURN Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("BURN Msg rejected.")
        
def processtag(msg, ver):
    identlist = loadlist("ident")
    
    if allownewtags and \
       ver.hash not in bannedtags and \
       searchlistbyhash(identlist, ver.obj['vendorid']):
        MM_writefile(msg)
        appendindex('tags', ver.hash)
        print "TAG Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("TAG Msg rejected.")
        
def processoffer(msg, ver):
    identlist = loadlist("ident")
    
    if allownewoffers and \
      searchlistbyhash(identlist, ver.obj['vendorid']):
        for tag in ver.obj['tags']:
            if tag in bannedtags:
                return
        MM_writefile(msg)
        appendindex('offer', ver.hash)
        print "OFFER Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("OFFER Msg rejected.")
          
def processorder(msg, ver):
    identlist = loadlist("ident")
    marketlist = loadlist('market')
    offer = do_offerfromordermsg(ver)
    buyer = searchlistbyhash(identlist, ver.obj['buyerid'])
    market = searchlistbyhash(marketlist, offer.obj['markethash'])
    
    mult = decimal.Decimal(market.obj['multiplier'])
    minrep = offer.obj['minrep']
    buyer_rep = do_getrep(buyer.hash, mult)
    
    if buyer and offer and buyer_rep >= minrep:
        MM_writefile(msg)
        appendindex('order', ver.hash)
        print "ORDER Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("ORDER Msg rejected.")
          
def processconf(msg, ver):
    identlist = loadlist("ident")
    orderlist = loadlist("order")
    
    if searchlistbyhash(identlist, ver.obj['vendorid']) and \
       searchlistbyhash(orderlist, ver.obj['orderhash']):
        MM_writefile(msg)
        appendindex('conf', ver.hash)
        print "CONF Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("CONF Msg rejected.")
          
def processpay(msg, ver):
    identlist = loadlist("ident")
    conflist = loadlist("conf")
    
    if searchlistbyhash(identlist, ver.obj['buyerid']) and \
       searchlistbyhash(conflist, ver.obj['confhash']):
        MM_writefile(msg)
        appendindex('pay', ver.hash)
        print "PAY Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("PAY Msg rejected.")
        
def processrec(msg, ver):
    identlist = loadlist("ident")
    paylist = loadlist("pay")
    
    if searchlistbyhash(identlist, ver.obj['vendorid']) and \
       searchlistbyhash(paylist, ver.obj['payhash']):
        MM_writefile(msg)
        appendindex('rec', ver.hash)
        print "REC Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("REC Msg rejected.")
        
def processfinal(msg, ver):
    identlist = loadlist("ident")
    reclist = loadlist("rec")
    
    if searchlistbyhash(identlist, ver.obj['buyerid']) and \
       searchlistbyhash(reclist, ver.obj['rechash']):
        MM_writefile(msg)
        appendindex('final', ver.hash)
        print "FINAL Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("FINAL Msg rejected.")
        
def processfeedback(msg, ver):
    identlist = loadlist("ident")
    finallist = loadlist("final")
    
    fromuser = searchlistbyhash(identlist, ver.obj['fromid'])
    touser = searchlistbyhash(identlist, ver.obj['toid'])
    
    finaltx = gettx(txid)
    prevtxid = finaltx['vin'][0]['txid']
    prevtx = gettx(prevtxid)
    msaddr = prevtx['vout'][0]['addresses'][0]
    
    redeemscript = MM_util.btcd.decodescript(ver.obj['redeemscript'])
    
    if fromuser and touser and \
       redeemscript['p2sh'] == msaddr and \
       fromuser.obj['btcaddr'] in redeemscript['addresses'] and \
       touser.obj['btcaddr'] in redeemscript['addresses']:
    
        MM_writefile(msg)
        appendindex('feedback', ver.hash)
        print "FEEDBACK Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("FEEDBACK Msg rejected.")

def processsync(msg, ver):
    identlist = loadlist("ident")
    user = searchlistbyhash(identlist, ver.obj['userid'])
    
    if user:
        modsync(user.obj['bmaddr'])
        MM_writefile(msg)
        appendindex('sync', ver.hash)
        print "SYNC Msg accepted:\n%s" % pretty_json(ver)
        print "SYNCing up with user:\n%s" % user.hash
    else:
        print("SYNC Msg rejected.")
        
def processcast(msg, ver):
    identlist = loadlist("ident")
    
    if searchlistbyhash(identlist, ver.obj['modid']):
        unpackcastlist(ver.obj['identlist'], 'ident')
        unpackcastlist(ver.obj['burnlist'], 'burn')
        unpackcastlist(ver.obj['taglist'], 'tags')
        unpackcastlist(ver.obj['offerlist'], 'offer')
        unpackcastlist(ver.obj['feedbacklist'], 'feedback')
        print "CAST Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("CAST Msg rejected.")
        
def processcancel(msg, ver):
    identlist = loadlist('ident')
    orderlist = loadlist('order')
    conflist = loadlist('conf')
    
    if searchlistbyhash(identlist, ver.obj['fromid']) and \
       searchlistbyhash(orderlist, ver.obj['orderhash']):
        MM_backupfile('order', ver.obj['orderhash'])
        
        if entity == 'vendor':
            for conf in conflist:
                if conf.obj['orderhash'] == ver.obj['orderhash']:
                    MM_backupfile('conf', conf.hash)
                    
        MM_writefile(msg)
        appendindex('sync', ver.hash)
        print "CANCEL Msg accepted:\n%s" % pretty_json(ver)
    else:
        print("CANCEL Msg rejected.")
        
        

def processmsg(msg):
    ver = readmsg(msg) # Verifies sig/hash
    
    if ver.msgname == IDENT and entity == 'mod':
        processident(msg, ver)
    elif ver.msgname == REG and entity == 'mod':
        processreg(msg, ver)
    elif ver.msgname == BURN and entity == 'mod':
        processburn(msg, ver)
    elif ver.msgname == TAG and entity == 'mod':
        processtag(msg, ver)
    elif ver.msgname == OFFER and entity != 'vendor':
        processoffer(msg, ver)
    elif ver.msgname == ORDER and entity == 'vendor':
        processorder(msg, ver)
    elif ver.msgname == CONF and entity == 'buyer':
        processconf(msg, ver)
    elif ver.msgname == PAY and entity == 'vendor':
        processpay(msg, ver)
    elif ver.msgname == REC and entity == 'buyer':
        processrec(msg, ver)
    elif ver.msgname == FINAL and entity == 'vendor':
        processfinal(msg, ver)
    elif ver.msgname == FEEDBACK and entity == 'mod':
        processfeedback(msg, ver)
    elif ver.msgname == SYNC and entity == 'mod':
        processsync(msg, ver)
    elif ver.msgname == CAST and entity != 'mod':
        processcast(msg, ver)
    elif ver.msgname == CANCEL and entity != 'mod':
        processcancel(msg, ver)
    else:
        print "Someone sent us the wrong type of Msg."
    return ver
    
def processmultimsg(mmsg):
    mmsgobj = MultiMsg(**json.loads(mmsg))
    fname = "multimsg.dat"
    mmsgfile = open(fname, 'r')
    mmsgdict = json.load(mmsgfile)
    mmsgfile.close()
    msginfo = None
    
    if mmsgobj.hash in mmsgdict:
        msglist = mmsgdict[mmsgobj.hash]
        for i in range( len(msglist) ):
            msglist[i] = MultiMsg(**msglist[i])
        msglist.append(mmsgobj)
        
        if len(msglist) == mmsgobj.total:
            origmsg = reconstructmsg(msglist)
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
        do_createreg()
    elif msgtype == 'burn' and entity != 'mod':
        do_createburn()
    elif msgtype == 'sync' and entity != 'mod':
        createsync()
    elif msgtype == 'tag' and entity != 'buyer':
        createtag()
    elif msgtype == 'market':
        createmarket()
    elif msgtype == 'offer' and entity == 'vendor':
        createoffer()
    elif msgtype == 'order' and entity == 'buyer':
        do_createorder()
    elif msgtype == 'conf' and entity == 'vendor':
        do_createconf()
    elif msgtype == 'pay' and entity == 'buyer':
        do_createpay()
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
    
    identlist = loadlist('ident')
    marketlist = loadlist('market')
    msgstr = open( os.path.join(msgdir, msgid + '.dat'), 'r' ).read()
    ver = readmsg(msgstr)
    
    if ver.msgname == IDENT:
        marketid = raw_input("Enter a Market ID to sync your Identity with: ")
        market = searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    elif ver.msgname == BURN:
        marketid = raw_input("Enter a Market ID to register your Proof-of-Burn at: ")
        market = searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    elif ver.msgname == REG:
        ident = ver.obj['modid']
    elif ver.msgname == SYNC:
        ident = ver.obj['modid']
    elif ver.msgname == CANCEL:
        ident = ver.obj['toid']
    elif ver.msgname == TAG and entity == "vendor":
        marketid = raw_input("Enter a Market ID to register the Tag at: ")
        market = searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    elif ver.msgname == OFFER and entity == "vendor":
        marketid = MM_extract('markethash', msgstr)        
        market = searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    elif ver.msgname == ORDER and entity == "buyer":
        ident = MM_extract('vendorid', msgstr)        
    elif ver.msgname == CONF and entity == "vendor":
        ident = MM_extract('buyerid', msgstr)        
    elif ver.msgname == PAY and entity == "buyer":
        ident = MM_extract('vendorid', msgstr)        
    elif ver.msgname == REC and entity == "vendor":
        ident = MM_extract('buyerid', msgstr)        
    elif ver.msgname == FINAL and entity == "buyer":
        ident = MM_extract('vendorid', msgstr)        
    elif ver.msgname == FEEDBACK and entity != "mod":
        marketid = MM_extract('markethash', msgstr)        
        market = searchlistbyhash(marketlist, marketid)
        ident = market.obj['modid']
    else:
        raise Exception("Bad Msg type.")
        
    tobm = searchlistbyhash( identlist, ident ).obj['bmaddr']
    do_sendmsgviabm(tobm, bmaddr, msgstr, prompt)
    
    
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
    
    if msgtype == 'ident':
        mkt = raw_input("Enter a Market ID : ")
        mkts = loadlist('market')
    list = loadlist(msgtype)
    showanylist(list, mktid=mkt, marketlist=mkts)
    
def showmsg(hash):
    print "Showing Msg: %s" % hash
    msgstr = open( os.path.join(msgdir, hash + '.dat'), 'r' ).read()
    ver = readmsg(msgstr)
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
    do_sendmsgviabm( chan_addr, bmaddr, mktoffer, False, 'Mkt' )
    

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
                                        default=IDENT,
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
                        'sendmsg', help='Send any MM Message over MM_util.bm.')
    send_msg_parser.add_argument(   '-m',
                                    '--msgid',
                                    required=True,
                                    action='store',
                                    dest='msgid',
                                    help='Send a MM Message, given its ID; to its recipient via MM_util.bm.' )
                                    
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
        do_modbanuser()
    elif args.mode == "modbantag":
        do_modbantag()
    elif args.mode == "modremoveoffer":
        do_modremoveoffer()
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

default_fee = truncate( decimal.Decimal( config.get(section, 'fee') ) )
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
    
    
    
