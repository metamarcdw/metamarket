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
        

def run():
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    myapp.login()
    sys.exit(app.exec_())
    
    
