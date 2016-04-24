#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
import view_market_dialog

class ViewMarketDlg(QDialog,
        view_market_dialog.Ui_view_market_dialog):
    
    def __init__(self, marketname, regfee, burnmult, downvotemult, desc, json, parent=None):
        super(ViewMarketDlg, self).__init__(parent)
        self.setupUi(self)
        self.viewMarketGroupBox.setTitle("View Market: %s" % marketname)
        self.regFeeLabel.setText("Registration Fee: %s" % regfee)
        self.burnMultLabel.setText("BURN Multiplier: %s" % burnmult)
        self.downvoteMultLabel.setText("Downvote Multiplier: %s" % downvotemult)
        self.descPlainTextEdit.document().setPlainText(desc)
        self.jsonPlainTextEdit.document().setPlainText(json)
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    marketname = sys.argv[1]
    regfee = sys.argv[2]
    burnmult = sys.argv[3]
    downvotemult = sys.argv[4]
    desc = sys.argv[5]
    json = sys.argv[6]
    
    form = ViewMarketDlg(marketname, regfee, burnmult, downvotemult, desc, json)
    form.show()
    app.exec_()

