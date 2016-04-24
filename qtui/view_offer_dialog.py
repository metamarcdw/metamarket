#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_offer_dialog.ui'
#
# Created: Sat Apr 23 21:15:44 2016
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_view_offer_dialog(object):
    def setupUi(self, view_offer_dialog):
        view_offer_dialog.setObjectName(_fromUtf8("view_offer_dialog"))
        view_offer_dialog.resize(485, 509)
        self.gridLayout_3 = QtGui.QGridLayout(view_offer_dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.viewOfferGroupBox = QtGui.QGroupBox(view_offer_dialog)
        self.viewOfferGroupBox.setObjectName(_fromUtf8("viewOfferGroupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.viewOfferGroupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.descPlainTextEdit = QtGui.QPlainTextEdit(self.viewOfferGroupBox)
        self.descPlainTextEdit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.descPlainTextEdit.setReadOnly(True)
        self.descPlainTextEdit.setObjectName(_fromUtf8("descPlainTextEdit"))
        self.verticalLayout.addWidget(self.descPlainTextEdit)
        self.vendorNameLabel = QtGui.QLabel(self.viewOfferGroupBox)
        self.vendorNameLabel.setObjectName(_fromUtf8("vendorNameLabel"))
        self.verticalLayout.addWidget(self.vendorNameLabel)
        self.ratioLabel = QtGui.QLabel(self.viewOfferGroupBox)
        self.ratioLabel.setObjectName(_fromUtf8("ratioLabel"))
        self.verticalLayout.addWidget(self.ratioLabel)
        self.locktimeLabel = QtGui.QLabel(self.viewOfferGroupBox)
        self.locktimeLabel.setObjectName(_fromUtf8("locktimeLabel"))
        self.verticalLayout.addWidget(self.locktimeLabel)
        self.minRepLabel = QtGui.QLabel(self.viewOfferGroupBox)
        self.minRepLabel.setObjectName(_fromUtf8("minRepLabel"))
        self.verticalLayout.addWidget(self.minRepLabel)
        self.gridLayout_2.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.descLabel = QtGui.QLabel(self.viewOfferGroupBox)
        self.descLabel.setObjectName(_fromUtf8("descLabel"))
        self.gridLayout_2.addWidget(self.descLabel, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.viewOfferGroupBox)
        self.tagsGroupBox = QtGui.QGroupBox(view_offer_dialog)
        self.tagsGroupBox.setObjectName(_fromUtf8("tagsGroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.tagsGroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tagsTableWidget = QtGui.QTableWidget(self.tagsGroupBox)
        self.tagsTableWidget.setObjectName(_fromUtf8("tagsTableWidget"))
        self.tagsTableWidget.setColumnCount(2)
        self.tagsTableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tagsTableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tagsTableWidget.setHorizontalHeaderItem(1, item)
        self.tagsTableWidget.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tagsTableWidget, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.tagsGroupBox)
        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(view_offer_dialog)
        QtCore.QMetaObject.connectSlotsByName(view_offer_dialog)

    def retranslateUi(self, view_offer_dialog):
        view_offer_dialog.setWindowTitle(_translate("view_offer_dialog", "View Offer", None))
        self.viewOfferGroupBox.setTitle(_translate("view_offer_dialog", "View Offer: Offername", None))
        self.vendorNameLabel.setText(_translate("view_offer_dialog", "Vendor: ", None))
        self.ratioLabel.setText(_translate("view_offer_dialog", "Refund Ratio: ", None))
        self.locktimeLabel.setText(_translate("view_offer_dialog", "Locktime: ", None))
        self.minRepLabel.setText(_translate("view_offer_dialog", "Min. Reputation Score: ", None))
        self.descLabel.setText(_translate("view_offer_dialog", "Description:", None))
        self.tagsGroupBox.setTitle(_translate("view_offer_dialog", "Offer tags:", None))
        item = self.tagsTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("view_offer_dialog", "Name", None))
        item = self.tagsTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("view_offer_dialog", "Description", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    view_offer_dialog = QtGui.QDialog()
    ui = Ui_view_offer_dialog()
    ui.setupUi(view_offer_dialog)
    view_offer_dialog.show()
    sys.exit(app.exec_())

