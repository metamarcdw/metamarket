#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_offer_dialog.ui'
#
# Created: Mon May 25 15:54:44 2015
#      by: PyQt4 UI code generator 4.11.2
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(485, 509)
        self.gridLayout_3 = QtGui.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.view_offer_groupbox = QtGui.QGroupBox(Dialog)
        self.view_offer_groupbox.setObjectName(_fromUtf8("view_offer_groupbox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.view_offer_groupbox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.desc_plaintextedit = QtGui.QPlainTextEdit(self.view_offer_groupbox)
        self.desc_plaintextedit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.desc_plaintextedit.setReadOnly(True)
        self.desc_plaintextedit.setObjectName(_fromUtf8("desc_plaintextedit"))
        self.verticalLayout.addWidget(self.desc_plaintextedit)
        self.vendor_name_label = QtGui.QLabel(self.view_offer_groupbox)
        self.vendor_name_label.setObjectName(_fromUtf8("vendor_name_label"))
        self.verticalLayout.addWidget(self.vendor_name_label)
        self.ratio_label = QtGui.QLabel(self.view_offer_groupbox)
        self.ratio_label.setObjectName(_fromUtf8("ratio_label"))
        self.verticalLayout.addWidget(self.ratio_label)
        self.locktime_label = QtGui.QLabel(self.view_offer_groupbox)
        self.locktime_label.setObjectName(_fromUtf8("locktime_label"))
        self.verticalLayout.addWidget(self.locktime_label)
        self.minrep_label = QtGui.QLabel(self.view_offer_groupbox)
        self.minrep_label.setObjectName(_fromUtf8("minrep_label"))
        self.verticalLayout.addWidget(self.minrep_label)
        self.gridLayout_2.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.desc_label = QtGui.QLabel(self.view_offer_groupbox)
        self.desc_label.setObjectName(_fromUtf8("desc_label"))
        self.gridLayout_2.addWidget(self.desc_label, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.view_offer_groupbox)
        self.tags_groupbox = QtGui.QGroupBox(Dialog)
        self.tags_groupbox.setObjectName(_fromUtf8("tags_groupbox"))
        self.gridLayout = QtGui.QGridLayout(self.tags_groupbox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tags_tablewidget = QtGui.QTableWidget(self.tags_groupbox)
        self.tags_tablewidget.setObjectName(_fromUtf8("tags_tablewidget"))
        self.tags_tablewidget.setColumnCount(2)
        self.tags_tablewidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tags_tablewidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tags_tablewidget.setHorizontalHeaderItem(1, item)
        self.tags_tablewidget.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.tags_tablewidget, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.tags_groupbox)
        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "View Offer", None))
        self.view_offer_groupbox.setTitle(_translate("Dialog", "View Offer: Offername", None))
        self.vendor_name_label.setText(_translate("Dialog", "Vendor: ", None))
        self.ratio_label.setText(_translate("Dialog", "Refund Ratio: ", None))
        self.locktime_label.setText(_translate("Dialog", "Locktime: ", None))
        self.minrep_label.setText(_translate("Dialog", "Min. Reputation Score: ", None))
        self.desc_label.setText(_translate("Dialog", "Description:", None))
        self.tags_groupbox.setTitle(_translate("Dialog", "Offer tags:", None))
        item = self.tags_tablewidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Name", None))
        item = self.tags_tablewidget.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Description", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

