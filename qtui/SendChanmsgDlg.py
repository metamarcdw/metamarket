#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
MAC = hasattr(PyQt4.QtGui, "qt_mac_set_native_menubar")
import send_chanmsg_dialog

class SendChanmsgDlg(QDialog,
        send_chanmsg_dialog.Ui_send_chanmsg_dialog):
    
    def __init__(self, parent=None):
        super(SendChanmsgDlg, self).__init__(parent)
        self.setupUi(self)
        if not MAC:
            self.buttonBox.setFocusPolicy(Qt.NoFocus)
        self.updateUi()
    
    def updateUi(self):
        blank = self.plainTextEdit.toPlainText().isEmpty()
        if blank:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
    
    @pyqtSignature("")
    def on_plainTextEdit_textChanged(self):
        self.updateUi()
    
    def result(self):
        chanMsg = self.plainTextEdit.toPlainText()
        return chanMsg
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    form = SendChanmsgDlg()
    if form.exec_():
        print form.result()
    sys.exit(0)

