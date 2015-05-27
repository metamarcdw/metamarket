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
import pycoin.key.Key
import bitcoin, bitcoin.rpc, bitcoin.core
import xmlrpclib, base64, hashlib, decimal, time
import scrypt, simplecrypt

CHAIN = "testnet"
NETCODE = "XTN"
BMURL = "http://username:password@localhost:8442"
HOUR = 60 * 60
DAY = HOUR * 24

decimal.getcontext().prec = 8
bitcoin.SelectParams(CHAIN)
MM_util.btcd = bitcoin.rpc.RawProxy()
MM_util.btcd.walletpassphrase('test', 300)
bm = xmlrpclib.ServerProxy(BMURL)

def pkstr( username, pswd ):
    hash = hashlib.sha256(pswd).hexdigest()
    pkbytes = scrypt.hash(hash, username, N=2**18, buflen=32)
    return bitcoin.core.b2x(pkbytes)

def btcaddr( pkstr ):
    se = long(pkstr, 16)
    key = pycoin.key.Key(secret_exponent=se, netcode=NETCODE)
    return key.address()
    
def bmaddr( pkstr ):
    return bm.getDeterministicAddress(base64.b64encode(pkstr), 4,1)

def savemsg( btc, name, msgstr ):
    ver = MM_util.MM_loads(btc, msgstr)
    MM_util.MM_writefile(msgstr)
    MM_util.appendindex(name, ver.hash)
    return ver

mod_pkstr = pkstr("MM mod", """sr#hrAoe0S4]GCb8~J3>9"Hl$""")
vendor_pkstr = pkstr("MM vendor", """[OQ2zu%A|TFef5`!h|]BL""")
buyer_pkstr = pkstr("MM buyer", """W3}xa`XrHkoyZ9vHZ/'U{""")

mod_btc = btcaddr(mod_pkstr)
mod_bm = bmaddr(mod_pkstr)
vendor_btc = btcaddr(vendor_pkstr)
vendor_bm = bmaddr(vendor_pkstr)
buyer_btc = btcaddr(buyer_pkstr)
buyer_bm = bmaddr(buyer_pkstr)

# IDENT
msgstr = MM_util.createidentmsgstr( mod_btc, mod_bm, "MM mod" )
mod = savemsg(mod_btc, 'ident', msgstr)
print mod

msgstr = MM_util.createidentmsgstr( vendor_btc, vendor_bm, "MM vendor" )
vendor = savemsg(vendor_btc, 'ident', msgstr)
print vendor

msgstr = MM_util.createidentmsgstr( buyer_btc, buyer_bm, "MM buyer" )
buyer = savemsg(buyer_btc, 'ident', msgstr)
print buyer

# TAG
msgstr = MM_util.createtagmsgstr( vendor_btc, vendor.hash, "Anything", \
                "The most useless tag of all! Can be ascribed to anything." )
tag = savemsg(vendor_btc, 'tags', msgstr)
print tag

# MARKET
msgstr = MM_util.createmarketmsgstr( mod_btc, mod.hash, "MEGAMARKET", \
                "Where all the people can trade all the things!",
                "0.1",
                "10" )
market = savemsg(mod_btc, 'market', msgstr)
print market

# REG
vreg_txid = "721c2cfcb6a170eda89d667dd217e543f63a6b131499ed90ada1e28ee6c377c3"
msgstr = MM_util.createregmsgstr(vendor_btc, mod.hash, vendor.hash, vreg_txid)
vreg = savemsg(vendor_btc, 'reg', msgstr)
print vreg

breg_txid = "6c29ef88721ffc1e05fa0f4688c73d123cee816246cd5cdeb6a555f8a9731c64"
msgstr = MM_util.createregmsgstr(buyer_btc, mod.hash, buyer.hash, breg_txid)
breg = savemsg(buyer_btc, 'reg', msgstr)
print breg

# BURN
vburn_txid = "721c2cfcb6a170eda89d667dd217e120f63a6b131499ed90ada1e28ee6c377c3"
msgstr = MM_util.createburnmsgstr(vendor_btc, vendor.hash, vburn_txid)
vburn = savemsg(vendor_btc, 'burn', msgstr)
print vburn

bburn_txid = "6c29ef88721ffc1e05fa0f4688c73d247cee816246cd5cdeb6a555f8a9731c64"
msgstr = MM_util.createburnmsgstr(buyer_btc, buyer.hash, bburn_txid)
bburn = savemsg(buyer_btc, 'burn', msgstr)
print bburn

# OFFER
vendor_pubkey = "02be3c8de123fbbba538b1fda2514a021342d30d1936670dc1d1094497018c2b72"
msgstr = MM_util.createoffermsgstr( vendor_btc, market.hash, vendor.hash,
                vendor_pubkey,
                "GOLD",
                "USA",
                "EXCELLENT QUALITY GOLD BULLION - 99.999% PURE.",
                "1 TROY OUNCE",
                '0.03',
                '5.0',
                int( time.time() + 1*HOUR ),
                '5',
                [tag.hash] )
offer = savemsg(vendor_btc, 'offer', msgstr)
print offer

# ORDER
buyer_pubkey = "023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a1"
multisig = {
        "address": "2MzciXEkpbSx9585hNrxSFXiBC5JLkV8k9A",
        "redeemScript": "5221023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a12102be3c8de123fbbba538b1fda2514a021342d30d1936670dc1d1094497018c2b7252ae"
    }
fundingtx = "01000000014762c15b1aa1e331020a9abc889e774d28a0037973a5b3a997e88a802a03c499000000006a47304402203c5fada60a8c6abda133e500e6db7dccab7c26783ed6731186e4e68742926194022071b0cc78931d7f18d55f4d2faea8b39399458220cb0aedb60e31e0dd7902a07e0121023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a1ffffffff0240420f000000000017a91450d96f356e7d5492164893af88f216d618330bc087b0a86a00000000001976a91406245119eb453eae3aba4ce557d458f70333fc6088ac00000000"
crypt_fundingtx = base64.b64encode( simplecrypt.encrypt(buyer_pkstr, fundingtx) )
funding_txid = "cc107206fade04670c3fbd989c8404efe7e38329bad55f8b0ae8fc6a3cec8857"
vout = 0
spk = "a91450d96f356e7d5492164893af88f216d618330bc087"

msgstr = MM_util.createordermsgstr( buyer_btc, offer.hash, vendor.hash, buyer.hash,
                buyer_pubkey, multisig, crypt_fundingtx, funding_txid, vout, spk )
order = savemsg(buyer_btc, 'order', msgstr)
print order

# CONF
refund_tx = "01000000015788ec3c6afce80a8b5fd5ba2983e3e7ef04849c98bd3f0c6704defa067210cc000000009200483045022100d1f46ad026df663585cd4499adf827875abcc52f32fc9b11112b7c5eee37703f022036444180a64515074b2fcdda47689092645904e2c7c7b92a8f8f1ad16cdc14ac01475221023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a12102be3c8de123fbbba538b1fda2514a021342d30d1936670dc1d1094497018c2b7252ae0000000001301b0f00000000001976a91406245119eb453eae3aba4ce557d458f70333fc6088ac43023354"
prev_tx = [
        {
            "redeemScript": "5221023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a12102be3c8de123fbbba538b1fda2514a021342d30d1936670dc1d1094497018c2b7252ae",
            "scriptPubKey": "a91450d96f356e7d5492164893af88f216d618330bc087",
            "txid": "cc107206fade04670c3fbd989c8404efe7e38329bad55f8b0ae8fc6a3cec8857",
            "vout": 0
        }
    ]
msgstr = MM_util.createconfmsgstr( vendor_btc, order.hash, vendor.hash, buyer.hash,
                refund_tx, prev_tx )
conf = savemsg(vendor_btc, 'conf', msgstr)
print conf

# PAY
refund_tx = "01000000015788ec3c6afce80a8b5fd5ba2983e3e7ef04849c98bd3f0c6704defa067210cc00000000db00483045022100c438f6b9bc90508d02d50a603620bbf8d88111c2e09559bc4b4dda444d621656022011b588c93d86944cc47c6cd819749ed4b2986132b45bf0b61dc36aea2c0c557b01483045022100d1f46ad026df663585cd4499adf827875abcc52f32fc9b11112b7c5eee37703f022036444180a64515074b2fcdda47689092645904e2c7c7b92a8f8f1ad16cdc14ac01475221023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a12102be3c8de123fbbba538b1fda2514a021342d30d1936670dc1d1094497018c2b7252ae0000000001301b0f00000000001976a91406245119eb453eae3aba4ce557d458f70333fc6088ac43023354"
address = "123 Fake St. Detroit MI 48233"
msgstr = MM_util.createpaymsgstr( buyer_btc, conf.hash, vendor.hash, buyer.hash,
                refund_tx, address )
pay = savemsg(buyer_btc, 'pay', msgstr)
print pay

# REC
final_tx = "01000000015788ec3c6afce80a8b5fd5ba2983e3e7ef04849c98bd3f0c6704defa067210cc0000000092004830450221009836d1484eb9a7d7545205cc2f6bd49a2ff1c53ee43bdbce60c1f7688ca971a202206cff23847a2347e4c1b8cc21b46a8e03780110cfb4c9f54dad8134348eb288d101475221023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a12102be3c8de123fbbba538b1fda2514a021342d30d1936670dc1d1094497018c2b7252aeffffffff01301b0f00000000001976a9141e8b47a1ae8bd264a66c249bbb5cb15b917f9a8188ac00000000"
prev_tx = [
        {
            "redeemScript": "5221023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a12102be3c8de123fbbba538b1fda2514a021342d30d1936670dc1d1094497018c2b7252ae",
            "scriptPubKey": "a91450d96f356e7d5492164893af88f216d618330bc087",
            "txid": "cc107206fade04670c3fbd989c8404efe7e38329bad55f8b0ae8fc6a3cec8857",
            "vout": 0
        }
    ]
msgstr = MM_util.createrecmsgstr( vendor_btc, pay.hash, vendor.hash, buyer.hash, \
                final_tx, prev_tx )
rec = savemsg(vendor_btc, 'rec', msgstr)
print rec

# FINAL
final_txid = "521df5e3f2ffa02eb3388f34ac20f0c87a6c3830092f227bc1c07133048903e0"
msgstr = MM_util.createfinalmsgstr( buyer_btc, rec.hash, vendor.hash, buyer.hash, final_txid )
final = savemsg(buyer_btc, 'final', msgstr)

# FEEDBACK
msgstr = MM_util.createfeedbackmsgstr( vendor_btc, market.hash, final.hash, vendor.hash, buyer.hash, \
                "1b18001c62dadaa7e1047cf336640a56c9b88a68eb6195add2d90d48379b11b3", \
                "5221023e5024192f82300470568fbd1d3fdd8ccf82f6b71a67afbe641eff7661e749a12102be3c8de123fbbba538b1fda2514a021342d30d1936670dc1d1094497018c2b7252ae", \
                True, \
                "Trade escrowed and finalized promptly." )
vfeedback = savemsg(vendor_btc, 'feedback', msgstr)
print vfeedback

msgstr = MM_util.createfeedbackmsgstr( buyer_btc, market.hash, final.hash, buyer.hash, vendor.hash, \
                "1b18001c62dadaa7e1047cf336640a56c9b88a68eb6195add2d90d48379b11b3", \
                "0.03", \
                True, \
                "Sale executed flawlessly, Many thanks." )
bfeedback = savemsg(buyer_btc, 'feedback', msgstr)
print bfeedback

MM_util.btcd.walletlock()
print "FINISH--"

