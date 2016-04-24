#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
MAC = hasattr(PyQt4.QtGui, "qt_mac_set_native_menubar")
import login_dialog

class LoginDlg(QDialog,
        login_dialog.Ui_login_dialog):
    
    def __init__(self, parent=None):
        super(LoginDlg, self).__init__(parent)
        self.setupUi(self)
        if not MAC:
            self.buttonBox.setFocusPolicy(Qt.NoFocus)
        self.updateUi()
    
    def updateUi(self):
        name_blank = self.nameLineEdit.text().isEmpty()
        pswd_blank = self.pswdLineEdit.text().isEmpty()
        if name_blank or pswd_blank:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
    
    @pyqtSignature("QString")
    def on_nameLineEdit_textEdited(self):
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_pswdLineEdit_textEdited(self):
        self.updateUi()
    
    def result(self):
        name = str( self.nameLineEdit.text() )
        pswd = str( self.pswdLineEdit.text() )
        return ( name, pswd )
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    form = LoginDlg()
    if form.exec_():
        print form.result()
    sys.exit(0)

