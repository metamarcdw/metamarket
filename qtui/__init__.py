import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import MM_util

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from metamarket_qt import *
from LoginDlg import LoginDlg
from ViewIdentDlg import ViewIdentDlg
from ViewOfferDlg import ViewOfferDlg
from ViewMarketDlg import ViewMarketDlg
from ViewChanmsgDlg import ViewChanmsgDlg
from ImportMarketDlg import ImportMarketDlg
from SendChanmsgDlg import SendChanmsgDlg
from AboutDlg import AboutDlg

class MyForm(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        #INIT ALL DATA STRUCTURES
        
        self.loggedIn = False
        
        self.marketlist = MM_util.loadlist('market')
        self.identlist = MM_util.loadlist('ident')
        self.offerlist = MM_util.loadlist('offer')
        self.orderlist = MM_util.loadlist('order')
        self.conflist = MM_util.loadlist('conf')
        self.paylist = MM_util.loadlist('pay')
        self.reclist = MM_util.loadlist('rec')
        self.finallist = MM_util.loadlist('final')
        self.feedbacklist = MM_util.loadlist('feedback')
        
        bannedtags = MM_util.loadindex('bannedtags')
        
        self.updateUi()
    
    def updateUi(self):
        #INIT MAINWINDOW UI WITH DATA FROM ALL DATA STRUCTURES
        pass
    
    
    def showLoginDlg(self):
        self.loginDlg = LoginDlg(self)
        if self.loginDlg.exec_():
            return self.loginDlg.result()
        
    def login(self):
        credentials = self.showLoginDlg()
        if credentials:
            name, pswd = credentials
            # Stub for login method
            print "Name: %s" % name
            print "Pswd: %s" % pswd
            self.loggedIn = True
    
    
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
    
    
