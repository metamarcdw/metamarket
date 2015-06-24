import sys

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from metamarket_qt import *
from login_dialog import *
from view_ident_dialog import *
from view_offer_dialog import *
from view_market_dialog import *
from view_chanmsg_dialog import *
from import_market_dialog import *
from send_chanmsg_dialog import *
from about_dialog import *

class MyForm(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
    def showLoginDialog(self):
        self.loginDialogInstance = loginDialog(self)
        if self.loginDialogInstance.exec_():
            pass
        
    
class loginDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_login_dialog()
        self.ui.setupUi(self)
        self.parent = parent

class viewIdentDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_view_ident_dialog()
        self.ui.setupUi(self)
        self.parent = parent

class viewOfferDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_view_offer_dialog()
        self.ui.setupUi(self)
        self.parent = parent

class viewMarketDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_view_market_dialog()
        self.ui.setupUi(self)
        self.parent = parent

class viewChanmsgDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_view_chanmsg_dialog()
        self.ui.setupUi(self)
        self.parent = parent

class importMarketDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_import_market_dialog()
        self.ui.setupUi(self)
        self.parent = parent

class sendChanmsgDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_send_chanmsg_dialog()
        self.ui.setupUi(self)
        self.parent = parent

class aboutDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_about_dialog()
        self.ui.setupUi(self)
        self.parent = parent


def run():
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    myapp.showLoginDialog()
    sys.exit(app.exec_())
    
    
