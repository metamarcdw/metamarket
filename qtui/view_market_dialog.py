#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_market_dialog.ui'
#
# Created: Mon May 25 00:30:43 2015
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
        self.view_market_groupbox = QtGui.QGroupBox(Dialog)
        self.view_market_groupbox.setObjectName(_fromUtf8("view_market_groupbox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.view_market_groupbox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.desc_plaintextedit = QtGui.QPlainTextEdit(self.view_market_groupbox)
        self.desc_plaintextedit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.desc_plaintextedit.setReadOnly(True)
        self.desc_plaintextedit.setObjectName(_fromUtf8("desc_plaintextedit"))
        self.verticalLayout.addWidget(self.desc_plaintextedit)
        self.regfee_label = QtGui.QLabel(self.view_market_groupbox)
        self.regfee_label.setObjectName(_fromUtf8("regfee_label"))
        self.verticalLayout.addWidget(self.regfee_label)
        self.burn_mult_label = QtGui.QLabel(self.view_market_groupbox)
        self.burn_mult_label.setObjectName(_fromUtf8("burn_mult_label"))
        self.verticalLayout.addWidget(self.burn_mult_label)
        self.downvote_mult_label = QtGui.QLabel(self.view_market_groupbox)
        self.downvote_mult_label.setObjectName(_fromUtf8("downvote_mult_label"))
        self.verticalLayout.addWidget(self.downvote_mult_label)
        self.gridLayout_2.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.desc_label = QtGui.QLabel(self.view_market_groupbox)
        self.desc_label.setObjectName(_fromUtf8("desc_label"))
        self.gridLayout_2.addWidget(self.desc_label, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.view_market_groupbox)
        self.json_groupbox = QtGui.QGroupBox(Dialog)
        self.json_groupbox.setObjectName(_fromUtf8("json_groupbox"))
        self.gridLayout = QtGui.QGridLayout(self.json_groupbox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.json_plaintextedit = QtGui.QPlainTextEdit(self.json_groupbox)
        self.json_plaintextedit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.json_plaintextedit.setReadOnly(True)
        self.json_plaintextedit.setObjectName(_fromUtf8("json_plaintextedit"))
        self.gridLayout.addWidget(self.json_plaintextedit, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.json_groupbox)
        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "View Market", None))
        self.view_market_groupbox.setTitle(_translate("Dialog", "View Market: Marketname", None))
        self.regfee_label.setText(_translate("Dialog", "Registration Fee: ", None))
        self.burn_mult_label.setText(_translate("Dialog", "BURN Multiplier: ", None))
        self.downvote_mult_label.setText(_translate("Dialog", "Downvote Multiplier: ", None))
        self.desc_label.setText(_translate("Dialog", "Description:", None))
        self.json_groupbox.setTitle(_translate("Dialog", "Market JSON:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

