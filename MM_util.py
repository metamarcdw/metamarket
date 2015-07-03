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

# Takes a verified "OrderMsg" and returns the associated Offer.
def offerfromordermsg( msg, getorder=False ):
    offerlist = loadlist('offer')
    orderlist = loadlist('order')
    conflist = loadlist('conf')
    paylist = loadlist('pay')
    reclist = loadlist('rec')
    
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
        time.sleep(SLEEP)
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
    
    
    
    
    
