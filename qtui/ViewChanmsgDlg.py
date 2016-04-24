#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
import view_chanmsg_dialog

class ViewChanmsgDlg(QDialog,
        view_chanmsg_dialog.Ui_view_chanmsg_dialog):
    
    def __init__(self, message, parent=None):
        super(ViewChanmsgDlg, self).__init__(parent)
        self.setupUi(self)
        self.plainTextEdit.document().setPlainText(message)
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    message = sys.argv[1]
    
    form = ViewChanmsgDlg(message)
    form.show()
    app.exec_()

