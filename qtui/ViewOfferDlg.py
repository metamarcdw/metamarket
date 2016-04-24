#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
import view_offer_dialog

class ViewOfferDlg(QDialog,
        view_offer_dialog.Ui_view_offer_dialog):
    
    def __init__(self, offername, vendorname, ratio, locktime, minrep, desc, tags, parent=None):
        super(ViewOfferDlg, self).__init__(parent)
        self.setupUi(self)
        self.viewOfferGroupBox.setTitle("View Offer: %s" % offername)
        self.vendorNameLabel.setText("Vendor: %s" % vendorname)
        self.ratioLabel.setText("Refund Ratio: %s" % ratio)
        self.locktimeLabel.setText("Locktime: %s" % locktime)
        self.minRepLabel.setText("Min. Reputation Score: %s" % minrep)
        self.descPlainTextEdit.document().setPlainText(desc)
        # TODO: TAGS format
        numtags = len(tags)
        self.tagsTableWidget.setRowCount(numtags)
        for i in range(numtags):
            self.tagsTableWidget.setItem(i, 0, QTableWidgetItem(tags[i][0]) )
            self.tagsTableWidget.setItem(i, 1, QTableWidgetItem(tags[i][1]) )
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    offername = sys.argv[1]
    vendorname = sys.argv[2]
    ratio = sys.argv[3]
    locktime = sys.argv[4]
    minrep = sys.argv[5]
    desc = sys.argv[6]
    tagname = sys.argv[7]
    tagdesc = sys.argv[8]
    tags = [(tagname,tagdesc)]
    
    form = ViewOfferDlg(offername, vendorname, ratio, locktime, minrep, desc, tags)
    form.show()
    app.exec_()

