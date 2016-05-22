import sys
import os.path
sys.path.append(    # Make sure we can access MM_util in the parent directory
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import MM_util
import bitcoin, bitcoin.rpc, bitcoin.core, pycoin.key.Key
import scrypt, simplecrypt
import simplejson as json
import ConfigParser
import hashlib, time, decimal, socket, httplib
import xmlrpclib, base64

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import metamarket_qt
from LoginDlg import LoginDlg
from ViewIdentDlg import ViewIdentDlg
from ViewOfferDlg import ViewOfferDlg
from ViewMarketDlg import ViewMarketDlg
from ViewChanmsgDlg import ViewChanmsgDlg
from ImportMarketDlg import ImportMarketDlg
from SendChanmsgDlg import SendChanmsgDlg
from AboutDlg import AboutDlg

class MyForm(QtGui.QMainWindow,
        metamarket_qt.Ui_MainWindow):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        
        #INIT ALL DATA STRUCTURES
        
        section = 'metamarket'
        defaults = {    'chain':        'mainnet',
                        'channame':     'METAMARKET',
                        'fee':          '0.0001',
                        'minconf':      '6',
                        'bmuser':       'username',
                        'bmpswd':       'password',
                        'bmhost':       'localhost',
                        'bmport':       '8442',
                        'btcport':      '8332'    }
        config = ConfigParser.RawConfigParser(defaults)
        config.read('mm.cfg')
        
        self.chain = config.get(section, 'chain')
        self.channame = config.get(section, 'channame')
        
        self.default_fee = MM_util.truncate( decimal.Decimal( config.get(section, 'fee') ) )
        self.minconf = config.getint(section, 'minconf')
        
        self.bm_url = "http://%s:%s@%s:%d" % ( config.get(section, 'bmuser'),
                                            config.get(section, 'bmpswd'),
                                            config.get(section, 'bmhost'),
                                            config.getint(section, 'bmport') )                                
        self.btc_port = config.getint(section, 'btcport')
        
        if self.chain == 'testnet':
            self.netcode = 'XTN'
            self.pob_address = "msj42CCGruhRsFrGATiUuh25dtxYtnpbTx"
        elif self.chain == 'mainnet':
            self.netcode = 'BTC'
            self.pob_address = "1METAMARKETxxxxxxxxxxxxxxxxx4TPjws"
        else:
            raise Exception("Config: chain must be either testnet or mainnet.")
        
        bitcoin.SelectParams(self.chain)
        MM_util.btcd = bitcoin.rpc.RawProxy(service_port=self.btc_port)
        MM_util.bm = xmlrpclib.ServerProxy(self.bm_url)
        MM_util.minconf = self.minconf
        
        try:
            self.chan_v3 = MM_util.bm.getDeterministicAddress( base64.b64encode(self.channame), 3,1 )
            self.chan_v4 = MM_util.bm.getDeterministicAddress( base64.b64encode(self.channame), 4,1 )
        except socket.error:
            self.sockErr()
        
        self.loggedIn = False
        self.username = None
        self.passphrase = None
        self.pkstr = None
        self.wif = None
        self.btcaddr = None
        self.bmaddr = None
        self.myid = None
        self.inbox = None
        self.currentMarket = None
        self.currentTag = None
        
        self.searchText = ''
        self.indexNames = ('market', 'ident', 'offer', 'order', 'conf', \
                                'pay', 'rec', 'final', 'feedback', 'tags')
        self.listDict = {}
        self.listLastLoaded = {}
        for index in self.indexNames:
            self.listLastLoaded[index] = 0
        
        self.setWindowIcon( QIcon("mm_logo.jpg") )
    
    
    def loadListIfModified(self, index):
        MM_util.loadindex(index)
        mtime = os.path.getmtime("%s.dat" % index)
        lastTime = self.listLastLoaded[index]
        
        if mtime > lastTime:
            self.listLastLoaded[index] = time.time()
            list = MM_util.loadlist(index)
            
            if index == "ident":
                MM_util.idList = list
            return list
    
    def loadLists(self):
        for index in self.indexNames:
            list = self.loadListIfModified(index)
            if list is not None:
                self.listDict[index] = list
    
    
    def populateMktBox(self, mktBox, search):
        index = mktBox.currentIndex()
        mktBox.clear()
        for mkt in self.listDict['market']:
            mktname = mkt.obj['marketname']
            if search not in mktname:
                continue
            mktBox.addItem(mktname)
        if not search:
            mktBox.setCurrentIndex(index)
    
    def updateUi(self):
        #UPDATE MAINWINDOW UI WITH DATA FROM ALL DATA STRUCTURES
        if not self.loggedIn:
            return
        
        self.tabWidget.setEnabled(True)
        self.inbox = json.loads( MM_util.bm.getAllInboxMessages() )['inboxMessages']
        
        chanMsgs = []
        for msg in self.inbox:
            subject = base64.b64decode( msg['subject'] )
            if subject not in ('Msg', 'MultiMsg') and \
                    msg['toAddress'] in ( self.chan_v3, self.chan_v4 ):
                chanMsgs.append(msg)
        
        self.do_processinbox()
        self.loadLists()
        
        # Update 'Channel' Tab:
        self.chanGroupBox.setTitle("Channel: %s" % self.channame)
        numChanMsgs = len(chanMsgs)
        self.chanTableWidget.setRowCount(numChanMsgs)
        
        for i in range(numChanMsgs):
            subject = base64.b64decode( chanMsgs[i]['subject'] )
            msgid = chanMsgs[i]['msgid']
            self.chanTableWidget.setItem( i, 0, QTableWidgetItem(subject) )
            self.chanTableWidget.setItem( i, 1, QTableWidgetItem(msgid) )
        
        # Update 'Markets' Tab:
        marketlist = self.listDict['market']
        numMarkets = len(marketlist)
        self.marketTableWidget.setRowCount(numMarkets)
        
        for i in range(numMarkets):
            self.marketTableWidget.setItem( i, 0, QTableWidgetItem(marketlist[i].obj['marketname']) )
            self.marketTableWidget.setItem( i, 1, QTableWidgetItem(marketlist[i].obj['description']) )
            self.marketTableWidget.setItem( i, 2, QTableWidgetItem(marketlist[i].hash) )
        
        # Update 'Offers' Tab:
        if self.currentTag:
            self.offerGroupBox.setTitle( \
                    "Available Offers: Filtered for '%s'" % self.currentTag.obj['tagname'])
        else:
            self.offerGroupBox.setTitle("Available Offers:")
        self.populateMktBox(self.offerMktComboBox, self.searchText)
        
        if self.offerMktComboBox.count() <= 0:
            self.currentMarket = None
        
        if self.currentMarket:
            offerlist = self.listDict['offer']
            currentOffers = []
            
            for offer in offerlist:
                if offer.obj['markethash'] == self.currentMarket.hash:
                    if not self.currentTag or self.currentTag.hash in offer.obj['tags']:
                        currentOffers.append(offer)
            
            numOffers = len(currentOffers)
            self.offerTableWidget.setRowCount(numOffers)
            
            for i in range(numOffers):
                self.offerTableWidget.setItem( i, 0, QTableWidgetItem(currentOffers[i].obj['name']) )
                self.offerTableWidget.setItem( i, 1, QTableWidgetItem(currentOffers[i].obj['locale']) )
                self.offerTableWidget.setItem( i, 2, QTableWidgetItem(currentOffers[i].obj['amount']) )
                self.offerTableWidget.setItem( i, 3, QTableWidgetItem(currentOffers[i].obj['price']) )
                self.offerTableWidget.setItem( i, 4, QTableWidgetItem(currentOffers[i].hash) )
        else:
            self.offerTableWidget.clearContents()
            self.offerTableWidget.setRowCount(0)
        
        # Update 'Orders' Tab:
        # TODO
        
        # Update 'Identities' Tab:
        self.setWindowTitle("METAmarket-Qt [%s]" % self.username)
        self.identMyidLabel.setText("ID Hash: %s" % self.myid.hash)
        self.identBtcaddrLabel.setText("BTC Address: %s" % self.btcaddr)
        self.identBmaddrLabel.setText("BM Address: %s" % self.bmaddr)
        
        search = str( self.identSearchLineEdit.text() )
        self.populateMktBox(self.identMktComboBox, self.searchText)
        # TODO
    
    @pyqtSignature("int")
    def on_tabWidget_currentChanged(self):
        self.updateUi()
    
    
    def showLoginDlg(self):
        loginDlg = LoginDlg(self)
        if loginDlg.exec_():
            return loginDlg.result()
        
    def login(self):
        credentials = self.showLoginDlg()
        if not credentials:
            return
        
        self.username, self.passphrase = credentials
        
        hash = hashlib.sha256(self.passphrase).hexdigest()
        pkbytes = scrypt.hash(hash, self.username, N=2**18, buflen=32)
        self.pkstr = bitcoin.core.b2x(pkbytes)
        se = long(self.pkstr, 16)
        pk = pycoin.key.Key(secret_exponent=se, netcode=self.netcode)
        
        self.wif = pk.wif()
        self.btcaddr = pk.address()
        try:
            self.bmaddr = MM_util.bm.getDeterministicAddress( base64.b64encode(self.pkstr), 4, 1 )
            
            wp = self.input("Please enter your Bitcoin Core wallet encryption passphrase:", password=True)
            MM_util.unlockwallet(wp)
        except bitcoin.rpc.JSONRPCException as jre:
            if jre.error['code'] == -14:
                self.info("The passphrase was not correct. Please try logging in again.")
                return
        except socket.error:
            self.sockErr()
        
        if MM_util.bm.createDeterministicAddresses(base64.b64encode(self.pkstr)) == [] or \
            not MM_util.btcd.validateaddress(self.btcaddr)['ismine']:
            if not self.importkeys():
                return
                    
        myidstr = MM_util.createidentmsgstr(self.btcaddr, self.bmaddr, self.username)
        self.myid = MM_util.MM_loads( self.btcaddr, myidstr )
        
        identlist = self.listDict['ident'] = MM_util.loadlist('ident')
        if not MM_util.searchlistbyhash(identlist, self.myid.hash):
            if not self.register(myidstr):
                return
        
        self.info("You are now logged in as: %s" % self.username)
        self.loggedIn = True
        self.updateUi()
    
    def importkeys(self):
        if self.yorn("Bitcoin private key not found in wallet or "+\
                "Bitmessage identity does not exist. Import your "+\
                "BTC private key and create your BM ID?"):
            pass2 = self.input("Please re-enter your passphrase:", password=True)
            if pass2 == self.passphrase:
                MM_util.btcd.importprivkey(self.wif, self.username, False)
                
                self.info("REMEMBER TO SECURELY BACKUP YOUR wallet.dat AND keys.dat files!")
                return True
            else:
                self.info("Passphrase did not match.")
                return False
        else:
            MM_util.bm.deleteAddress(self.bmaddr)
            return False
        
    def register(self, idstr):
        if self.yorn("We were not able to find your ID on file. "+\
                "Is this a new identity you would like to create?"):
            MM_util.MM_writefile(idstr)
            MM_util.appendindex('ident', self.myid.hash)
            return True
        else:
            return False
    
    @pyqtSignature("")
    def on_actionLogin_triggered(self):
        if self.loggedIn:
            self.info("You are already logged in!")
        else:
            self.login()
    
    
    def showAboutDlg(self):
        aboutDlg = AboutDlg(self)
        aboutDlg.show()
    
    @pyqtSignature("")
    def on_actionAbout_triggered(self):
        self.showAboutDlg()
    
    
    def do_sendmsgviabm(self, to_addr, msgstr, prompt=False, subject='Msg'):
        if not prompt or self.yorn("Are you sure you want to send this Message?"):
            MM_util.sendmsgviabm(to_addr, self.bmaddr, msgstr, subject)
            self.info("Message sent!")

    ##### BEGIN CHAN SLOTS #####
    def showSendChanmsgDlg(self):
        sendChanmsgDlg = SendChanmsgDlg(self)
        if sendChanmsgDlg.exec_():
            return sendChanmsgDlg.result()
    
    @pyqtSignature("")
    def on_chanSendButton_clicked(self):
        result = self.showSendChanmsgDlg()
        if not result:
            return
        
        subject, message = result
        self.do_sendmsgviabm(self.chan_v4, message, prompt=True, subject=subject)
    
    
    def showViewChanmsgDlg(self, subject, message):
        viewChanmsgDlg = ViewChanmsgDlg(subject, message, self)
        viewChanmsgDlg.show()
    
    @pyqtSignature("")
    def on_chanViewButton_clicked(self):
        selection = self.chanTableWidget.selectedItems()
        if not selection:
            return
        
        msgid = str( selection[1].text() )
        bmmsg = json.loads( MM_util.bm.getInboxMessageByID(msgid) )['inboxMessage'][0]
        subject = base64.b64decode( bmmsg['subject'] )
        message = base64.b64decode( bmmsg['message'] )
        self.showViewChanmsgDlg(subject, message)
    
    
    @pyqtSignature("")
    def on_chanDeleteButton_clicked(self):
        selection = self.chanTableWidget.selectedItems()
        if not selection:
            return
        
        if not self.yorn("Are you sure?"):
            return
        
        msgid = str( selection[1].text() )
        MM_util.bm.trashMessage(msgid)
        self.updateUi()
    ##### END CHAN SLOTS #####
    
    
    ##### BEGIN MARKET SLOTS #####
    def showImportMarketDlg(self):
        importMarketDlg = ImportMarketDlg(self)
        if importMarketDlg.exec_():
            return importMarketDlg.result()
    
    @pyqtSignature("")
    def on_marketImportButton_clicked(self):
        result = self.showImportMarketDlg()
        if not result:
            return
        
        try:
            MM_util.importMarket(result)
        except json.scanner.JSONDecodeError:
            self.info("Input was not a JSON encoded string")
        
        self.info("Congratulations, you may now Register with a new Metamarket!")
        self.updateUi()
    
    
    def showViewMarketDlg(self, marketname, regfee, burnmult, downvotemult, desc, mktjson):
        viewMarketDlg = ViewMarketDlg(marketname, regfee, burnmult, downvotemult, desc, mktjson, self)
        viewMarketDlg.show()
    
    @pyqtSignature("")
    def on_marketViewButton_clicked(self):
        selection = self.marketTableWidget.selectedItems()
        if not selection:
            return
        
        mktHash = str( selection[2].text() )
        market = MM_util.searchlistbyhash(self.listDict["market"], mktHash)
        
        mktName = market.obj['marketname']
        regfee = market.obj['fee']
        burnmult = market.obj['multiplier']
        downvotemult = 0
        desc = market.obj['description']
        
        modident = MM_util.searchlistbyhash(self.listDict["ident"], market.obj['modid'])
        info = {    "market": market,
                    "modid": modident }
        mktjson = json.dumps(info, indent=4, sort_keys=True)
        
        self.showViewMarketDlg(mktName, regfee, burnmult, downvotemult, desc, mktjson)
    
    @pyqtSignature("")
    def on_marketDeleteButton_clicked(self):
        selection = self.marketTableWidget.selectedItems()
        if not selection:
            return
        
        if not self.yorn("Are you sure?"):
            return
        
        mktHash = str( selection[2].text() )
        market = self.searchlistbyhash(listDict["market"], mktHash)
        
        MM_util.MM_backupfile("market", market.hash)
        self.updateUi()
    ##### END MARKET SLOTS #####
    
    
    ##### BEGIN OFFER SLOTS #####
    @pyqtSignature("int")
    def on_offerMktComboBox_activated(self, index):
        self.identMktComboBox.setCurrentIndex( index )
        mktName = str( self.offerMktComboBox.currentText() )
        self.currentMarket = self.searchlistbyname(self.listDict["market"], "marketname", mktName)
        self.updateUi()
    
    @pyqtSignature("")
    def on_offerSearchLineEdit_editingFinished(self):
        self.searchText = str( self.offerSearchLineEdit.text() )
        self.offerSearchLineEdit.setText('')
        self.updateUi()
    
    @pyqtSignature("")
    def on_offerOrderButton_clicked(self):
        selection = self.offerTableWidget.selectedItems()
        if not selection:
            return
        
        if not self.yorn("Are you sure?"):
            return
        
        offerlist = self.listDict["offer"]
        identlist = self.listDict["ident"]
        offer = MM_util.searchlistbyhash( offerlist, str(selection[4].text()) )
        vendor = MM_util.searchlistbyhash(identlist, offer.obj['vendorid'])
        
        msgstr = MM_util.createorder( \
                    self.myid.hash, self.btcaddr, offer, self.pkstr, self.default_fee)
        hash = MM_util.MM_writefile(msgstr)
        MM_util.appendindex('order', hash)
        
        self.do_sendmsgviabm(vendor.obj['bmaddr'], msgstr)
        self.info("Order placed!")
    
    def showViewOfferDlg(self, offername, vendor, ratio, locktime, minrep, desc, tags):
        viewOfferDlg = ViewOfferDlg(offername, vendor, ratio, locktime, minrep, desc, tags, self)
        viewOfferDlg.show()
    
    @pyqtSignature("")
    def on_offerViewButton_clicked(self):
        selection = self.offerTableWidget.selectedItems()
        if not selection:
            return
        
        offerlist = self.listDict["offer"]
        identlist = self.listDict["ident"]
        taglist = self.listDict["tags"]
        offer = MM_util.searchlistbyhash( offerlist, str(selection[4].text()) )
        vendor = MM_util.searchlistbyhash(identlist, offer.obj['vendorid'])
        
        offername = offer.obj['name']
        ratio = offer.obj['ratio']
        locktime = time.asctime( time.localtime(offer.obj['locktime']) )
        minrep = offer.obj['minrep']
        desc = offer.obj['description']
        tags = []
        for tag in offer.obj['tags']:
            tags.append( MM_util.searchlistbyhash(taglist, tag) )
        
        self.showViewOfferDlg(offername, vendor, ratio, locktime, minrep, desc, tags)
    
    @pyqtSignature("")
    def on_offerFilterButton_clicked(self):
        taglist = self.listDict["tags"]
        key = "tagname"
        
        tagnames = [""]
        for tag in taglist:
            tagnames.append(tag.obj[key])
            
        tagName = self.select("Known tags:", tagnames)
        self.currentTag = self.searchlistbyname(taglist, key, tagName)
        self.updateUi()
    ##### END OFFER SLOTS #####
    
    
    ##### BEGIN ORDER SLOTS #####
    
    ##### END ORDER SLOTS #####
    
    
    ##### BEGIN IDENT SLOTS #####
    @pyqtSignature("int")
    def on_identMktComboBox_activated(self, index):
        self.offerMktComboBox.setCurrentIndex( index )
        mktName = str( self.offerMktComboBox.currentText() )
        self.currentMarket = self.searchlistbyname(self.listDict["market"], "marketname", mktName)
        self.updateUi()
    
    @pyqtSignature("")
    def on_identSearchLineEdit_editingFinished(self):
        self.searchText = str( self.identSearchLineEdit.text() )
        self.identSearchLineEdit.setText('')
        self.updateUi()
    
    ##### END IDENT SLOTS #####
    
    def searchlistbyname(self, list, key, name):
        for obj in list:
            if obj.obj[key] == name:
                return obj
    
    def processMsg(self, msg):
        ver = MM_util.readmsg(msg) # Verifies sig/hash
        
        if ver.msgname == MM_util.IDENT:
            MM_util.processident(msg, ver)
        elif ver.msgname == MM_util.TAG:
            MM_util.processtag(msg, ver)
        elif ver.msgname == MM_util.OFFER:
            MM_util.processoffer(msg, ver)
        elif ver.msgname == MM_util.CONF:
            MM_util.processconf(msg, ver)
        elif ver.msgname == MM_util.REC:
            MM_util.processrec(msg, ver)
        elif ver.msgname == MM_util.FEEDBACK:
            MM_util.processfeedback(msg, ver)
        elif ver.msgname == MM_util.CAST:
            MM_util.processcast(msg, ver)
        else:
            raise Exception("Someone sent us the wrong type of Msg.")
            
        return ver
    
    def do_processinbox(self):
        return MM_util.processinbox(self.bmaddr, self.processMsg)
    
    
    def select(self, groupname, selections):
        text, ok = QInputDialog.getItem(self, "Select", groupname, selections)
        if ok:
            return str(text)
    
    def input(self, prompt, password=False):
        if password:
            mode = QLineEdit.Password
        else:
            mode = QLineEdit.Normal
        text, ok = QInputDialog.getText(self, "Input", prompt, mode)
        if ok:
            return str(text)
    
    def yorn(self, prompt):
        reply = QMessageBox.question(self, "Question", prompt, QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        elif reply == QMessageBox.No:
            return False
    
    def info(self, message):
        QMessageBox.information(self, "Information", message, QMessageBox.Ok)
    
    def sockErr(self):
        self.info("Please make sure Bitcoin Core and Bitmessage "+\
                "are up and running before launching METAmarket.")
        self.quit()
    
    
    def quit(self):
        self.close()
        sys.exit(0) # <-- Not sure if needed
    
    @pyqtSignature("")
    def on_actionClose_triggered(self):
        self.quit()
    

def run():
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    myapp.login()
    sys.exit(app.exec_())
    
    
