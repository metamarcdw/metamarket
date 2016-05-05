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
        self.entity = None
        self.username = None
        self.passphrase = None
        self.pkstr = None
        self.wif = None
        self.btcaddr = None
        self.bmaddr = None
        self.myid = None
        self.mymarket = None
        
        self.marketlist = MM_util.loadlist('market')
        self.identlist = MM_util.loadlist('ident')
        self.offerlist = MM_util.loadlist('offer')
        self.orderlist = MM_util.loadlist('order')
        self.conflist = MM_util.loadlist('conf')
        self.paylist = MM_util.loadlist('pay')
        self.reclist = MM_util.loadlist('rec')
        self.finallist = MM_util.loadlist('final')
        self.feedbacklist = MM_util.loadlist('feedback')
        self.bannedtags = MM_util.loadindex('bannedtags')
        
        self.updateUi()
    
    def updateUi(self):
        #INIT MAINWINDOW UI WITH DATA FROM ALL DATA STRUCTURES
        pass
    
    
    def showLoginDlg(self):
        loginDlg = LoginDlg(self)
        if loginDlg.exec_():
            return loginDlg.result()
        
    def login(self):
        credentials = self.showLoginDlg()
        if credentials:
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
                
                wp = self.input("Please enter your Bitcoin Core wallet encryption passphrase:", True)
                MM_util.unlockwallet(wp)
            
            except socket.error:
                self.info("Please make sure Bitcoin Core and Bitmessage "+\
                        "are up and running before launching METAmarket.")
                sys.exit(0)
            
            if MM_util.bm.createDeterministicAddresses(base64.b64encode(self.pkstr)) == [] or \
                not MM_util.btcd.validateaddress(self.btcaddr)['ismine']:
                self.importkeys()
                        
            myidstr = MM_util.createidentmsgstr(self.btcaddr, self.bmaddr, self.username)
            self.myid = MM_util.MM_loads( self.btcaddr, myidstr )
            
            if not MM_util.searchlistbyhash(self.identlist, self.myid.hash):
                self.register(myidstr)
            
            if self.entity == 'mod':
                for i in self.marketlist:
                    if i.obj['modid'] == self.myid.hash:
                        self.mymarket = i
            
            self.loggedIn = True
    
    def importkeys(self):
        if self.yorn("Bitcoin private key not found in wallet or "+\
                "Bitmessage identity does not exist. Import your "+\
                "BTC private key and create your BM ID?"):
            pass2 = self.input("Please re-enter your passphrase:", True)
            if pass2 == self.passphrase:
                MM_util.btcd.importprivkey(wif, username, False)
                
                self.info("REMEMBER TO SECURELY BACKUP YOUR wallet.dat AND keys.dat files!")
            else:
                raise Exception("Passwords did not match.")
        else:
            MM_util.bm.deleteAddress(bmaddr)
        
    def register(self, idstr):
        print 
        if self.yorn("We were not able to find your ID on file. "+\
                "Is this a new identity you would like to create?"):
            MM_util.MM_writefile(idstr)
            MM_util.appendindex('ident', self.myid.hash)
    
    
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
    

def run():
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    myapp.login()
    sys.exit(app.exec_())
    
    
