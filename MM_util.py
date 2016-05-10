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

import simplejson as json
import base64, hashlib, os, sys, time
import decimal, math, getpass, operator, random
from collections import namedtuple

# Enum: codes for p2p msg names.
IDENT, TAG, MARKET, OFFER, ORDER, CONF, PAY, REC, FINAL, FEEDBACK, CAST, SYNC, BURN, REG, CANCEL = range(15)
Msg = namedtuple('Msg', 'obj sig hash msgname')
MultiMsg = namedtuple('MultiMsg', 'msg hash msgnum total')

btcd = bm = None

# Returns a packed, signed and hashed MM msgstr given any
# dict, msgname, and BTC addr. Requires bitcoind to create BTC sig.
def MM_dumps(btc_addr, msgname, obj):
    b64 = base64.b64encode( json.dumps(obj, sort_keys=True) )
    sig = btcd.signmessage(btc_addr, b64)
    hash = hashlib.sha256(b64).hexdigest()
    msgobj = Msg( b64, sig, hash, msgname )
    return json.dumps(msgobj)

# Returns a verified Msg( dict, sig, hash, msgname ) given a MM objstr
# and BTC addr. Verifies sha256; requires bitcoind to verify BTC sig.
def MM_loads(btc_addr, str, checksig=True):
    msg = Msg(**json.loads(str))
    if msg.hash != hashlib.sha256(msg.obj).hexdigest():
        print "Hash failed to verify..."
        return None
    if checksig and not btcd.verifymessage(btc_addr, msg.sig, msg.obj):
        print "BTC Signature failed to verify..."
        return None
    r = json.loads( base64.b64decode(msg.obj) )
    return Msg( r, msg.sig, msg.hash, msg.msgname )

# Returns the value of a single element of the underlying
# dict, given the key string. VERIFIES NUSSING.
def MM_extract(name, str):
    msg = Msg(**json.loads(str))
    obj = json.loads( base64.b64decode(msg.obj) )
    return obj[name]

# Takes  a Msg string. Writes Msg to a file in msg dir,
# named hash.dat where hash is the Msg hash.
def MM_writefile(obj):
    hash = Msg( **json.loads(obj) ).hash
    
    dir = 'msg'
    if not os.path.isdir(dir):
        os.makedirs(dir)        
    path = os.path.join(dir, hash + '.dat')
    if not os.path.exists(path):
        ofile = open( path, 'w' )
        ofile.write(obj)
        ofile.close()
    
    return hash

# Takes an index name and Msg hash. 
# Renames the Msg file with a backup extension.
# Deletes hash from the named index.
def MM_backupfile(name, hash):
    fname = os.path.join('msg', hash + '.dat')
    os.rename( fname, fname + '.bak' )
    deletefromindex(name, hash)
    
    
# Takes an entity name eg. 'vendorid' and a Msg string,
# extracts the associated Ident, and returns the 
# BTC address associated with said Ident.
def btcfrommsg(entity, msgstr):
    idhash = MM_extract(entity, msgstr)
    ids = loadlist('ident')
    return searchlistbyhash( ids, idhash ).obj['btcaddr']

def offerfromordermsg( msg, offerlist, orderlist, conflist, paylist, reclist, getorder=False ):
    if msg.msgname == ORDER:
        return searchlistbyhash(offerlist, msg.obj['offerhash'])
    elif msg.msgname == CONF:
        order = searchlistbyhash(orderlist, msg.obj['orderhash'])
        return searchlistbyhash(offerlist, order.obj['offerhash'])
    elif msg.msgname == PAY:
        conf = searchlistbyhash(conflist, msg.obj['confhash'])
        order = searchlistbyhash(orderlist, conf.obj['orderhash'])
        return searchlistbyhash(offerlist, order.obj['offerhash'])
    elif msg.msgname == REC:
        pay = searchlistbyhash(paylist, msg.obj['payhash'])
        conf = searchlistbyhash(conflist, pay.obj['confhash'])
        order = searchlistbyhash(orderlist, conf.obj['orderhash'])
        return searchlistbyhash(offerlist, order.obj['offerhash'])
    elif msg.msgname == FINAL:
        rec = searchlistbyhash(reclist, msg.obj['rechash'])
        pay = searchlistbyhash(paylist, rec.obj['payhash'])
        conf = searchlistbyhash(conflist, pay.obj['confhash'])
        order = searchlistbyhash(orderlist, conf.obj['orderhash'])
        if getorder:
            return order
        return searchlistbyhash(offerlist, order.obj['offerhash'])

# Takes an unverified msg string of any type,
# Uses btcfrommsg() to extract the associated btc address,
# Returns a verifed version of the Msg.
def readmsg( msgstr ):
    msgname = Msg(**json.loads(msgstr)).msgname
    if msgname == IDENT:
        btc = MM_extract('btcaddr', msgstr)
    elif msgname == TAG or msgname == OFFER or msgname == CONF or msgname == REC:
        btc = btcfrommsg('vendorid', msgstr)
    elif msgname == ORDER or msgname == PAY or msgname == FINAL:
        btc = btcfrommsg('buyerid', msgstr)
    elif msgname == MARKET or msgname == CAST:
        btc = btcfrommsg('modid', msgstr)
    elif msgname == FEEDBACK or msgname == CANCEL:
        btc = btcfrommsg('fromid', msgstr)
    elif msgname == SYNC or msgname == BURN:
        btc = btcfrommsg('userid', msgstr)
    elif msgname == REG:
        return MM_loads(None, msgstr, False)
    return MM_loads(btc, msgstr)
    
    
# Takes a list, an index filename, and an entity name.
# Loads the index from file. Loads all associated Msgs
# from their files into the given list. Verifies everything.
def loadlist( fname ):
    list = []
    for i in loadindex(fname):
        msgstr = open( os.path.join('msg', i + '.dat') ).read()
        list.append( readmsg(msgstr) )
    return list

# Returns a list entry by it's hash.
def searchlistbyhash(list, hash):
    for entry in list:
        if entry.hash == hash:
            return entry
    else:
        return None
        

# Packs a list of Msgs into a b64 string for CASTing.
def packlistforcast( name, list ):
    newlist = []
    for msg in list:
        b64 = base64.b64encode( json.dumps(msg.obj, sort_keys=True) )
        msgobj = Msg(b64, msg.sig, msg.hash, msg.msgname)
        msgstr = json.dumps(msgobj)
        newlist.append(msgstr)
#        MM_backupfile(name, msg.hash)
    return base64.b64encode( json.dumps(newlist) )

# Unpacks a list of msgs from a CAST, 
# writes/indexes msgs to files without verification.
def unpackcastlist( caststr, index ):
    if not caststr:
        return
    list = json.loads( base64.b64decode(caststr) )
    for msg in list:
        hash = MM_writefile(msg)
        appendindex(index, hash)


# Breaks up a list/string into chunks of a given size.    
def chunks(seq, n):
    return (seq[i:i+n] for i in xrange(0, len(seq), n))
    
# Breaks a b64 string down into b64 encoded MultiMsgs.
def breakdownbmmsg( b64msg ):
    newlist = []
    CHUNKSIZE = 5000 #250 * 1024
    chunk_list = list( chunks(b64msg, CHUNKSIZE) )
    hash = hashlib.sha256(b64msg).hexdigest()
    total = len(chunk_list)
    
    for i in range(total):
        msgobj = MultiMsg( chunk_list[i], hash, i, total )
        newlist.append( base64.b64encode(json.dumps(msgobj, sort_keys=True)) )
    return newlist
    
# Reconstructs a b64 string from a list of MultiMsgs.
def reconstructmsg(mmsg_list):
    mmsg_list = sorted(mmsg_list, key=operator.attrgetter('msgnum'))
    b64msg = ''
    for mmsg in mmsg_list:
        b64msg += mmsg.msg
    return base64.b64decode(b64msg)
    
    
# Accepts a BM address, Msg string and subject.
# Sends any raw Msg to any BM address.
def sendmsgviabm(to_addr, from_addr, msgstr, subject='Msg'):
    MAXBMOBJSIZE = 5000 #256*1024 - 20
    b64msg = base64.b64encode(msgstr)
    if sys.getsizeof(b64msg) > MAXBMOBJSIZE:
        multimsgs = breakdownbmmsg(b64msg)
        random.shuffle(multimsgs)
        for msg in multimsgs:
            bm.sendMessage(to_addr, from_addr, base64.b64encode('MultiMsg'), msg)
    else:
        bm.sendMessage(to_addr, from_addr, base64.b64encode(subject), b64msg)

        
# Writes and index to file.
def writeindex( index_set, name ):
    indfile = open( name + '.dat', 'w' )
    json.dump(list(index_set), indfile)
    indfile.close()

# Loads an index from file.
# Creates an empty index if none exists.
def loadindex( name ):
    fname = name + '.dat'
    if not os.path.exists(fname):
        writeindex([], name)
    indfile = open( fname, 'r' )
    index_set = set( json.load(indfile) )
    indfile.close()
    return index_set

# Loads an index from file, appends
# a new hash, and writes it back.
def appendindex( name, newhash ):
    index = loadindex(name)
    index.add(newhash)
    writeindex( index, name )

# Loads and index from file, deletes
# an existing hash, and writes it back.
def deletefromindex( name, hash ):
    index = loadindex(name)
    index.remove(hash)
    writeindex( index, name )


def modbanuser(userid, identlist, offerlist):
    user = searchlistbyhash(identlist, userid)
    if user:
        bm.addAddressToBlackWhiteList( user.obj['bmaddr'], "Banned: %s" % user.obj['name'] )
        MM_backupfile('ident', userid)
        
        for offer in offerlist:
            if offer.obj['vendorid'] == user.hash:
                MM_backupfile('offer', offer.hash)
                    
def modbantag(taghash, offerlist, bannedtags):
    appendindex('bannedtags', taghash)
    MM_backupfile('tags', taghash)
    
    for offer in offerlist:
        for tag in offer.obj['tags']:
            if tag in bannedtags:
                MM_backupfile('offer', offer.hash)
                
def modremoveoffer(offerhash):        
    MM_backupfile('offer', offerhash)
    

def getrep( identhash, burn_mult, feedbacklist, burnlist ):
    numrep = 0
    downvote_mult = 10      #TODO do not leave this hardcoded

    for fb in feedbacklist:
        if fb.obj['toid'] == identhash:
            if fb.obj['upvote']:
                numrep += 1
            else:
                numrep -= downvote_mult
                
    for burn in burnlist:
        if burn.obj['userid'] == identhash:
            try:
                burntx_hex = btcd.getrawtransaction(burn.obj['txid'])
            except bitcoin.rpc.JSONRPCException as jre:
                if jre.error['code'] == -5:
                    continue
            burntx = btcd.decoderawtransaction( burntx_hex )
            amount = burntx['vout'][0]['value']
            numrep += amount * burn_mult
            
    return numrep


def backupordermsgs(finalhash, finallist, reclist, paylist, conflist):
    final = searchlistbyhash(finallist, finalhash)
    rec = searchlistbyhash(reclist, final.obj['rechash'])
    pay = searchlistbyhash(paylist, rec.obj['payhash'])
    conf = searchlistbyhash(conflist, pay.obj['confhash'])
    
    MM_backupfile('final', finalhash)
    MM_backupfile('rec', final.obj['rechash'])
    MM_backupfile('pay', rec.obj['payhash'])
    MM_backupfile('conf', pay.obj['confhash'])
    MM_backupfile('order', conf.obj['orderhash'])


def sendtx(tx):
    try:
        return btcd.sendrawtransaction(tx)
    except bitcoin.rpc.JSONRPCException as jre:
        print "TX NOT SENT.", jre
        time.sleep(1)
        sys.exit()
        
def gettx(txid):
    while True:
        tx = None
        try:
            tx = btcd.getrawtransaction(txid, 1)
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
        tx = btcd.getrawtransaction(txid, 1)
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


def processreg(msg, ver):
    reg_tx = gettx(ver.obj['txid'])
    waitforconf(ver.obj['txid'])
    fee = decimal.Decimal(mymarket.obj['fee'])
    searchtxops(reg_tx, btcaddr, fee)
    
    MM_writefile(msg)
    appendindex('reg', ver.hash)

def processident(msg, ver, reglist):
    for reg in reglist:
        if reg.obj['userid'] == ver.hash:
            MM_writefile(msg)
            appendindex('ident', ver.hash)
            return True
    else:
        return False

def processburn(msg, ver, identlist):
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
        return True
    else:
        return False

def processtag(msg, ver, identlist):
    if searchlistbyhash(identlist, ver.obj['vendorid']):
        MM_writefile(msg)
        appendindex('tags', ver.hash)
        return True
    else:
        return False

def processoffer(msg, ver, identlist):
    if searchlistbyhash(identlist, ver.obj['vendorid']):
        MM_writefile(msg)
        appendindex('offer', ver.hash)
        return True
    else:
        return False

def processorder(msg, ver, identlist, marketlist):
    offer = do_offerfromordermsg(ver)
    buyer = searchlistbyhash(identlist, ver.obj['buyerid'])
    market = searchlistbyhash(marketlist, offer.obj['markethash'])
    
    mult = decimal.Decimal(market.obj['multiplier'])
    minrep = offer.obj['minrep']
    buyer_rep = do_getrep(buyer.hash, mult)
    
    if buyer and offer and buyer_rep >= minrep:
        MM_writefile(msg)
        appendindex('order', ver.hash)
        return True
    else:
        return False

def processconf(msg, ver, identlist, orderlist):
    if searchlistbyhash(identlist, ver.obj['vendorid']) and \
       searchlistbyhash(orderlist, ver.obj['orderhash']):
        MM_writefile(msg)
        appendindex('conf', ver.hash)
        return True
    else:
        return False

def processpay(msg, ver, identlist, conflist):
    if searchlistbyhash(identlist, ver.obj['buyerid']) and \
       searchlistbyhash(conflist, ver.obj['confhash']):
        MM_writefile(msg)
        appendindex('pay', ver.hash)
        return True
    else:
        return False

def processrec(msg, ver, identlist, paylist):
    if searchlistbyhash(identlist, ver.obj['vendorid']) and \
       searchlistbyhash(paylist, ver.obj['payhash']):
        MM_writefile(msg)
        appendindex('rec', ver.hash)
        return True
    else:
        return False

def processfinal(msg, ver, identlist, reclist):
    if searchlistbyhash(identlist, ver.obj['buyerid']) and \
       searchlistbyhash(reclist, ver.obj['rechash']):
        MM_writefile(msg)
        appendindex('final', ver.hash)
        return True
    else:
        return False

def processfeedback(msg, ver, identlist):
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
        return True
    else:
        return False

def processsync(msg, ver, identlist):
    user = searchlistbyhash(identlist, ver.obj['userid'])
    if user:
        modsync(user.obj['bmaddr'])
        MM_writefile(msg)
        appendindex('sync', ver.hash)
        return True
    else:
        return False

def processcast(msg, ver, identlist):
    if searchlistbyhash(identlist, ver.obj['modid']):
        unpackcastlist(ver.obj['identlist'], 'ident')
        unpackcastlist(ver.obj['burnlist'], 'burn')
        unpackcastlist(ver.obj['taglist'], 'tags')
        unpackcastlist(ver.obj['offerlist'], 'offer')
        unpackcastlist(ver.obj['feedbacklist'], 'feedback')
        return True
    else:
        return False

def processcancel(msg, ver, identlist, orderlist, conflist):
    if searchlistbyhash(identlist, ver.obj['fromid']) and \
       searchlistbyhash(orderlist, ver.obj['orderhash']):
        MM_backupfile('order', ver.obj['orderhash'])
        
        if entity == 'vendor':
            for conf in conflist:
                if conf.obj['orderhash'] == ver.obj['orderhash']:
                    MM_backupfile('conf', conf.hash)
                    
        MM_writefile(msg)
        appendindex('sync', ver.hash)
        return True
    else:
        return False


def createreg(myidhash, mybtc, amount, mod, default_fee):
    modbtc = mod.obj['btcaddr']
    change_addr = MM_util.btcd.getrawchangeaddress()
    
    def create_regtx(fee):
        regtx_hex = mktx(amount, modbtc, change_addr, fee, minconf)
        return MM_util.btcd.signrawtransaction(regtx_hex)['hex']
        
    regtx_hex_signed = create_regtx(default_fee)
    regtx_fee = calc_fee(regtx_hex_signed)
    if regtx_fee != default_fee:
        regtx_hex_signed = create_regtx(regtx_fee)
        
    reg_txid = sendtx(regtx_hex_signed)
    # print "REGISTER TXID:", reg_txid
    return createregmsgstr(mybtc, mod.hash, myidhash, reg_txid)


def createburn(myidhash, mybtc, amount, default_fee):
    change_addr = MM_util.btcd.getrawchangeaddress()
    
    # Aggregate to main address. Includes 2 fees.
    def create_ag(fee):
        raw_agtx_hex = mktx(amount+default_fee, mybtc, change_addr, fee, minconf)
        return MM_util.btcd.signrawtransaction(raw_agtx_hex)['hex']
        
    sig_agtx_hex = create_ag(default_fee)
    ag_fee = calc_fee(sig_agtx_hex)
    if ag_fee != default_fee:
        sig_agtx_hex = create_ag(ag_fee)
    
    ag_txid = sendtx(sig_agtx_hex)
    # print "AGGREGATE TXID:", ag_txid
    waitforconf(ag_txid)

    # Create raw burn TX.
    sig_agtx = MM_util.btcd.decoderawtransaction(sig_agtx_hex)
    vout = searchtxops(sig_agtx, mybtc, amount+default_fee)
    
    txs = [{    "txid": ag_txid,
                "vout": vout }]
    addrs = {   pob_address: amount }
    
    burntx_hex = MM_util.btcd.createrawtransaction(txs, addrs)
    burntx_hex_signed = MM_util.btcd.signrawtransaction(burntx_hex)['hex']
    burn_txid = sendtx(burntx_hex_signed)
    
    # print "BURN TXID:", burn_txid
    return createburnmsgstr(mybtc, myidhash, burn_txid)
    
    
def createorder(myidhash, mybtc, offer, cryptkey, default_fee):
    price = decimal.Decimal(offer.obj['price'])
    pubkey = MM_util.btcd.validateaddress(mybtc)['pubkey']
    multisig = MM_util.btcd.createmultisig( 2, sorted([offer.obj['pubkey'], pubkey]) )
    change_addr = MM_util.btcd.getrawchangeaddress()
    
    def create_funding(fee):
        rawtx_hex = mktx(price, multisig['address'], change_addr, fee)
        return MM_util.btcd.signrawtransaction(rawtx_hex)['hex']
    
    signedtx_hex = create_funding(default_fee)
    funding_fee = calc_fee(signedtx_hex)
    if funding_fee != default_fee:
        signedtx_hex = create_funding(funding_fee)
    
    crypttx = base64.b64encode( simplecrypt.encrypt(cryptkey, signedtx_hex) )
    
    signedtx = MM_util.btcd.decoderawtransaction(signedtx_hex)
    vout = searchtxops(signedtx, multisig['address'], price)
    
    return createordermsgstr(mybtc, offer.hash, offer.obj['vendorid'], myidhash, \
                                        pubkey, multisig, crypttx, signedtx['txid'], \
                                        vout, signedtx['vout'][vout]['scriptPubKey']['hex'] )

    
def createconf( myidhash, mybtc, order, offer, buyer, default_fee ):
    price = decimal.Decimal(offer.obj['price'])
    ratio = decimal.Decimal(offer.obj['ratio'])
    pubkey = offer.obj['pubkey']

    ms_verify = MM_util.btcd.createmultisig( 2, sorted([order.obj['pubkey'], pubkey]) )
    if ms_verify['address'] != order.obj['multisig']['address']:
        raise Exception("Multisig did not verify!")
    
    b_portion, v_portion = getamounts(ratio, price)
    
    refund_op = prev_tx = [ dict((key, order.obj[key]) for key in ("txid", "vout")) ]
    def create_refund(fee):
        refund_addr_obj = { buyer.obj['btcaddr']: b_portion - fee/2, 
                            mybtc: v_portion - fee/2 }
        return MM_util.btcd.createrawtransaction(refund_op, refund_addr_obj)
        
    refund_tx_hex = create_refund(default_fee)
    refund_fee = calc_fee(refund_tx_hex)
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
    
    return createconfmsgstr(mybtc, order.hash, myidhash, order.obj['buyerid'], \
                                        sig_refund_hex, prev_tx )

    
def createpay(myidhash, mybtc, conf, order, offer):
    price = decimal.Decimal(offer.obj['price'])
    ratio = decimal.Decimal(offer.obj['ratio'])
    b_portion, v_portion = getamounts(ratio, price)
    refund_fee = calc_fee( conf.obj['refundtx'] )
    
    refund_verify = MM_util.btcd.decoderawtransaction(conf.obj['refundtx'])
    searchtxops(refund_verify, btcaddr, b_portion - refund_fee/2)
    complete_refund = MM_util.btcd.signrawtransaction( conf.obj['refundtx'], conf.obj['prevtx'], [wif])['hex']
    
    fund_tx = simplecrypt.decrypt( pkstr, base64.b64decode(order.obj['crypt_fundingtx']) )
    sendtx(fund_tx)
    
    return createpaymsgstr(mybtc, conf.hash, conf.obj['vendorid'], myidhash, \
                                        complete_refund, address )


def createrec( myidhash, mybtc, pay, order, price ):
    fund_tx = gettx(order.obj['txid'])
    searchtxops(fund_tx, order.obj['multisig']['address'], price)
    waitforconf(order.obj['txid'])
    
    final_op = prev_tx = [ dict((key, order.obj[key]) for key in ("txid", "vout")) ]
    def create_final(fee):
        final_addr_obj = { btcaddr: price - fee }
        return MM_util.btcd.createrawtransaction(final_op, final_addr_obj)
        
    final_tx_hex = create_final(default_fee)
    final_fee = calc_fee(final_tx_hex)
    if final_fee != default_fee:
        final_tx_hex = create_final(final_fee)

    prev_tx[0]["scriptPubKey"] = order.obj['spk']
    prev_tx[0]["redeemScript"] = order.obj['multisig']['redeemScript']
    
    sig_final_hex = MM_util.btcd.signrawtransaction(final_tx_hex, prev_tx, [wif])['hex']
    
    return createrecmsgstr(mybtc, pay.hash, myidhash, pay.obj['buyerid'], \
                                        sig_final_hex, prev_tx )
    

def createfinal(myidhash, mybtc, finalflag, rec, vendor, offer, price):
    final_verify = MM_util.btcd.decoderawtransaction(rec.obj['finaltx'])
    searchtxops(final_verify, vendor.obj['btcaddr'], price - default_fee)
    complete_final = MM_util.btcd.signrawtransaction(rec.obj['finaltx'], rec.obj['prevtx'], [wif])['hex']
    
    if finalflag:
        final_tx = complete_final
    else:
        final_tx = pay.obj['refundhex']
    final_txid = sendtx(final_tx)
    
    return createfinalmsgstr(mybtc, rec.hash, rec.obj['vendorid'], myidhash, final_txid )


def createfeedback(mybtc, entity, upvote, message, final, offer, order):
    if entity == 'buyer':
        fromid = final.obj['buyerid']
        toid = final.obj['vendorid']
    elif entity == 'vendor':
        fromid = final.obj['vendorid']
        toid = final.obj['buyerid']
        
    return createfeedbackmsgstr(mybtc, offer.obj['markethash'], finalhash, fromid, toid, \
                                            final.obj['finaltxid'], order.obj['multisig']['redeemscript'], upvote, message)


def createcancel(myidhash, mybtc, entity, conflist, order):
    MM_backupfile('order', orderhash)
    
    toid = None
    if entity == 'buyer':
        toid = order.obj['vendorid']
        for conf in conflist:
            if conf.obj['orderhash'] == orderhash:
                MM_backupfile('conf', conf.hash)
    else:
        toid = order.obj['buyerid']
    
    return createcancelmsgstr(mybtc, myidhash, toid, orderhash)


# Creates a new Ident Msg and returns its string representation.
def createidentmsgstr( btc_addr, bm_addr, user_name ):
    ident = { 'name': user_name,
                'btcaddr': btc_addr,
                'bmaddr': bm_addr }
    return MM_dumps(btc_addr, IDENT, ident)

# Creates a new Register Msg and returns its string representation.
def createregmsgstr( btc_addr, modid, userid, reg_fee_txid ):
    reg = { 'modid': modid,
                'userid': userid,
                'txid': reg_fee_txid }
    return MM_dumps(btc_addr, REG, reg)

def createburnmsgstr(btc_addr, userid, txid):
    burn = { 'userid': userid,
                'txid': txid }
    return MM_dumps(btc_addr, BURN, burn)
    
# Creates a new Tag Msg and returns its string representation.
def createtagmsgstr( btc_addr, vendorid, tagname, desc ):
    tag = { 'vendorid': vendorid,
            'tagname': tagname,
            'description': desc }
    return MM_dumps(btc_addr, TAG, tag)
    
# Creates a new Market Msg and returns its string representation.
def createmarketmsgstr( btc_addr, modid, marketname, desc, reg_fee, burn_mult ):
    market = { 'modid': modid,
                'marketname': marketname,
                'description': desc,
                'fee': reg_fee,
                'multiplier': burn_mult }
    return MM_dumps(btc_addr, MARKET, market)
    
# Creates a new Offer Msg and returns its string representation.
def createoffermsgstr( btc_addr, markethash, vendorid, vendor_pubkey, \
                        name, locale, desc, amount, price, refund_ratio, \
                        locktime, minrep, tags ):
    offer = { 'vendorid': vendorid,
                'markethash': markethash,
                'pubkey': vendor_pubkey,
                'name': name,
                'locale': locale,
                'description': desc,
                'amount': amount,
                'price': price,
                'ratio': refund_ratio,
                'locktime': locktime,
                'minrep': minrep,
                'tags': tags }
    return MM_dumps(btc_addr, OFFER, offer)

# Creates a new Order Msg and returns its string representation.
def createordermsgstr( btc_addr, offerhash, vendorid, buyerid, buyer_pubkey, \
                        multisig, crypt_fundingtx, funding_txid, vout, spk ):
    order = { 'offerhash': offerhash,
                'vendorid': vendorid,
                'buyerid': buyerid,
                'pubkey': buyer_pubkey,
                'multisig': multisig,
                'crypt_fundingtx': crypt_fundingtx,
                'txid': funding_txid,
                'vout': vout,
                'spk': spk }
    return MM_dumps(btc_addr, ORDER, order)
    
# Creates a new Confirmation Msg and returns its string representation.
def createconfmsgstr( btc_addr, orderhash, vendorid, buyerid, refundtx, prevtx ):
    conf = { 'orderhash': orderhash,
                'vendorid': vendorid,
                'buyerid': buyerid,
                'refundtx': refundtx,
                'prevtx': prevtx }
    return MM_dumps(btc_addr, CONF, conf)
    
# Creates a new Payment Msg and returns its string representation.
def createpaymsgstr( btc_addr, confhash, vendorid, buyerid, refundhex, address ):
    pay = { 'confhash': confhash,
            'vendorid': vendorid,
            'buyerid': buyerid,
            'refundhex': refundhex,
            'address': address }
    return MM_dumps(btc_addr, PAY, pay)
    
# Creates a new Reciept Msg and returns its string representation.
def createrecmsgstr( btc_addr, payhash, vendorid, buyerid, finaltx, prevtx ):
    rec = { 'payhash': payhash,
            'vendorid': vendorid,
            'buyerid': buyerid,
            'finaltx': finaltx,
            'prevtx': prevtx }
    return MM_dumps(btc_addr, REC, rec)
    
# Creates a new Finalize Msg and returns its string representation.
def createfinalmsgstr(btc_addr, rechash, vendorid, buyerid, finaltxid):
    final = { 'rechash': rechash,
                'vendorid': vendorid,
                'buyerid': buyerid,
                'finaltxid': finaltxid }
    return MM_dumps(btc_addr, FINAL, final)
    
# Creates a new Feedback Msg and returns its string representation.
def createfeedbackmsgstr( btc_addr, markethash, finalhash, fromid, toid, finaltxid, redeemscript, upvote, message ):
    feedback = { 'markethash': markethash,
                    'finalhash': finalhash,
                    'fromid': fromid,
                    'toid': toid,
                    'finaltxid': finaltxid,
                    'redeemscript': redeemscript,
                    'upvote': upvote,
                    'message': message }
    return MM_dumps(btc_addr, FEEDBACK, feedback)
    
# Creates a new Broadcast Msg and returns its string representation.
def createcastmsgstr( btc_addr, modid, identlist, burnlist, taglist, offerlist, feedbacklist ):
    cast = { 'modid': modid,
                'identlist': packlistforcast('ident', identlist),
                'burnlist': packlistforcast('burn', burnlist),
                'taglist': packlistforcast('tags', taglist),
                'offerlist': packlistforcast('offer', offerlist),
                'feedbacklist': packlistforcast('feedback', feedbacklist) }
    return MM_dumps(btc_addr, CAST, cast)
    
# Creates a new Synchronize Msg and returns its string representation.
def createsyncmsgstr( btc_addr, modid, userid ):
    sync = { 'modid': modid,
                'userid': userid }
    return MM_dumps(btc_addr, SYNC, sync)
    
# Creates a new Cancel Order Msg and returns its string representation.
def createcancelmsgstr(btc_addr, fromid, toid, orderhash):
    cancel = { 'fromid': fromid,
                'toid': toid,
                'orderhash': orderhash }
    return MM_dumps(btc_addr, CANCEL, cancel)
   
    
# Takes an amount, destination address, change address,
# and optionally customizeable fee, and minimum confirms.
# Uses btcd createrawtransaction. To create a tx,
# payable by the user's btc core wallet.
def mktx(price, addr, chg_addr, fee, confs=1):
    
    dust_threshold = decimal.Decimal('0.00005430')
    collected = decimal.Decimal(0)
    utxos = btcd.listunspent(confs)
    ops = []
    
    #search for single utxo above price + fee
    single = None
    for op in utxos:
        amount = op['amount']
        if amount >= price + fee:
            single = op
            collected = amount
    
    #if not, accumulate sequentially up to price + fee
    if not single:
        for op in utxos:
            ops.append(op)
            amount = op['amount']
            collected += amount
            if collected >= price + fee:
                break
        else:
            raise Exception("Insufficient funds!")
    else:
        ops.append(single)
    
    #convert from tx format
    newops = []
    for op in ops:
        newops.append( dict((key, op[key]) for key in ("txid", "vout")) )
        
    change = collected - (price + fee)
    
    addresses = { addr: price }
    if change > dust_threshold:
        addresses[chg_addr] = change    
    
    return btcd.createrawtransaction( newops, addresses )
    
    
# Takes a tx hexstring and returns a more appropriate fee..
def calc_fee( hex_str ):
    size_bytes = len(hex_str) / 2
    size_rounded = int(math.ceil(size_bytes / 1000.0)) * 1000
    return size_rounded / decimal.Decimal('10000000.0')
    
# Takes a number and truncates it to 8 decimal places.
def truncate(num):
    strnum = str(num)
    if '.' in strnum:
        i = strnum.index('.')
        if len( strnum[i+1:] ) >= 8:
            return decimal.Decimal( strnum[:i+9] )
    return num
    
# Takes a ratio and amount, returns a tuple containing
# two portions of the amounts based on the given ratio.
def getamounts(ratio, amount):
    stratio = str(ratio)
    
    i = stratio.index('.')
    sp = len( stratio[i+1:] )
    
    denom = decimal.Decimal( '1'+'0'*sp )
    numer = ratio*denom
    total = numer+denom
    
    bper = numer/total
    vper = denom/total
    
    bbtc = truncate(amount*bper)
    vbtc = truncate(amount*vper)
    
    return ( bbtc, vbtc )
    
# Asks user for their wallet encryption passphrase.
# unlocks core wallet for 10min.
def unlockwallet( wp=None ):
    if not wp:
        wp = getpass.getpass("Please enter your wallet encryption passphrase: ")
    btcd.walletpassphrase(wp, 600)
    
    
    
    
    
