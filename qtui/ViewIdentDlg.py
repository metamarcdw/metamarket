#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
import view_ident_dialog

class ViewIdentDlg(QDialog,
        view_ident_dialog.Ui_view_ident_dialog):
    
    def __init__(self, name, hash, btcaddr, bmaddr, parent=None):
        super(ViewIdentDlg, self).__init__(parent)
        self.setupUi(self)
        self.viewIdentGroupbox.setTitle("View Identity: %s" % name)
        self.hashLabel.setText("ID hash: %s" % hash)
        self.btcaddrLabel.setText("BTC address: %s" % btcaddr)
        self.bmaddrLabel.setText("BM address: %s" % bmaddr)
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    name = sys.argv[1]
    hash = sys.argv[2]
    btcaddr = sys.argv[3]
    bmaddr = sys.argv[4]
    
    form = ViewIdentDlg(name, hash, btcaddr, bmaddr)
    form.show()
    app.exec_()

