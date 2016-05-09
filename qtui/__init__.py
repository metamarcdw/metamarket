import sys
import os.path
sys.path.append(    # Make sure we can access MM_util in the parent directory
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import MM_util
import bitcoin, bitcoin.rpc, bitcoin.core, pycoin.key.Key
import scrypt, simplecrypt
import simplejson as json
import ConfigParser
import hashlib, time, decimal, socket
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
        
        self.netcode = 'XTN'
        self.chain = "testnet"
        self.btc_port = 18332
        self.bm_url = "http://username:password@localhost:8442"
        
        bitcoin.SelectParams(self.chain)
        MM_util.btcd = bitcoin.rpc.RawProxy(service_port=self.btc_port)
        MM_util.bm = xmlrpclib.ServerProxy(self.bm_url)
        
        self.loggedIn = False
        self.username = None
        self.passphrase = None
        self.pkstr = None
        self.wif = None
        self.btcaddr = None
        self.bmaddr = None
        self.myid = None
        self.mymarket = None
        self.inbox = None
        
        try:
            self.marketlist = MM_util.loadlist('market')
            self.identlist = MM_util.loadlist('ident')
            self.offerlist = MM_util.loadlist('offer')
            self.orderlist = MM_util.loadlist('order')
            self.conflist = MM_util.loadlist('conf')
            self.paylist = MM_util.loadlist('pay')
            self.reclist = MM_util.loadlist('rec')
            self.finallist = MM_util.loadlist('final')
            self.feedbacklist = MM_util.loadlist('feedback')
        except socket.error:
            self.sockErr()

        self.bannedtags = MM_util.loadindex('bannedtags')
        
        self.updateUi()
    
    def updateUi(self):
        #UPDATE MAINWINDOW UI WITH DATA FROM ALL DATA STRUCTURES
        
        # Update 'Channel' Tab:
        try:
            self.inbox = json.loads( MM_util.bm.getAllInboxMessages() )['inboxMessages']
        except socket.error:
            self.sockErr()
        
        if self.inbox:
            chanMsgs = []
            for msg in self.inbox:
                subject = base64.b64decode( msg['subject'] )
                if subject not in ('Mkt', 'Msg', 'MultiMsg'):
                    chanMsgs.append(msg)
            
            numChanMsgs = len(chanMsgs)
            self.chanTableWidget.setRowCount(numChanMsgs)
            for i in range(numChanMsgs):
                subject = base64.b64decode( chanMsgs[i]['subject'] )
                msgid = chanMsgs[i]['msgid']
                self.chanTableWidget.setItem( i, 0, QTableWidgetItem(subject) )
                self.chanTableWidget.setItem( i, 1, QTableWidgetItem(msgid) )
        
        # Update 'Identities' Tab:
        if self.loggedIn:
            self.setWindowTitle("METAmarket-Qt [%s]" % self.username)
            self.identMyidLabel.setText("ID Hash: %s" % self.myid.hash)
            self.identBtcaddrLabel.setText("BTC Address: %s" % self.btcaddr)
            self.identBmaddrLabel.setText("BM Address: %s" % self.bmaddr)
    
    
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
        except socket.error:
            self.sockErr()
        
        if MM_util.bm.createDeterministicAddresses(base64.b64encode(self.pkstr)) == [] or \
            not MM_util.btcd.validateaddress(self.btcaddr)['ismine']:
            if not self.importkeys():
                return
                    
        myidstr = MM_util.createidentmsgstr(self.btcaddr, self.bmaddr, self.username)
        self.myid = MM_util.MM_loads( self.btcaddr, myidstr )
        
        if not MM_util.searchlistbyhash(self.identlist, self.myid.hash):
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
                self.info("Passwords did not match.")
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
        #TODO: Save all data to flat files
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
    
    
