#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_market_dialog.ui'
#
# Created: Mon May 25 16:42:47 2015
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

class Ui_view_market_dialog(object):
    def setupUi(self, view_market_dialog):
        view_market_dialog.setObjectName(_fromUtf8("view_market_dialog"))
        view_market_dialog.resize(485, 509)
        self.gridLayout_3 = QtGui.QGridLayout(view_market_dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.view_market_groupbox = QtGui.QGroupBox(view_market_dialog)
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
        self.json_groupbox = QtGui.QGroupBox(view_market_dialog)
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

        self.retranslateUi(view_market_dialog)
        QtCore.QMetaObject.connectSlotsByName(view_market_dialog)

    def retranslateUi(self, view_market_dialog):
        view_market_dialog.setWindowTitle(_translate("view_market_dialog", "View Market", None))
        self.view_market_groupbox.setTitle(_translate("view_market_dialog", "View Market: Marketname", None))
        self.regfee_label.setText(_translate("view_market_dialog", "Registration Fee: ", None))
        self.burn_mult_label.setText(_translate("view_market_dialog", "BURN Multiplier: ", None))
        self.downvote_mult_label.setText(_translate("view_market_dialog", "Downvote Multiplier: ", None))
        self.desc_label.setText(_translate("view_market_dialog", "Description:", None))
        self.json_groupbox.setTitle(_translate("view_market_dialog", "Market JSON:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    view_market_dialog = QtGui.QDialog()
    ui = Ui_view_market_dialog()
    ui.setupUi(view_market_dialog)
    view_market_dialog.show()
    sys.exit(app.exec_())

