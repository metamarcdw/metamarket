#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_ident_dialog.ui'
#
# Created: Wed May 27 22:08:10 2015
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
        Dialog.resize(400, 114)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.view_ident_groupbox = QtGui.QGroupBox(Dialog)
        self.view_ident_groupbox.setObjectName(_fromUtf8("view_ident_groupbox"))
        self.gridLayout = QtGui.QGridLayout(self.view_ident_groupbox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.hash_label = QtGui.QLabel(self.view_ident_groupbox)
        self.hash_label.setObjectName(_fromUtf8("hash_label"))
        self.verticalLayout.addWidget(self.hash_label)
        self.btcaddr_label = QtGui.QLabel(self.view_ident_groupbox)
        self.btcaddr_label.setObjectName(_fromUtf8("btcaddr_label"))
        self.verticalLayout.addWidget(self.btcaddr_label)
        self.bmaddr_label = QtGui.QLabel(self.view_ident_groupbox)
        self.bmaddr_label.setObjectName(_fromUtf8("bmaddr_label"))
        self.verticalLayout.addWidget(self.bmaddr_label)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.view_ident_groupbox, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.view_ident_groupbox.setTitle(_translate("Dialog", "View Identity: Identname", None))
        self.hash_label.setText(_translate("Dialog", "ID hash: ", None))
        self.btcaddr_label.setText(_translate("Dialog", "BTC address: ", None))
        self.bmaddr_label.setText(_translate("Dialog", "BM address: ", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

