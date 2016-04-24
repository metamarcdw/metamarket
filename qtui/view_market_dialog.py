#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_market_dialog.ui'
#
# Created: Sat Apr 23 20:10:44 2016
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

class Ui_view_market_dialog(object):
    def setupUi(self, view_market_dialog):
        view_market_dialog.setObjectName(_fromUtf8("view_market_dialog"))
        view_market_dialog.resize(485, 509)
        self.gridLayout_3 = QtGui.QGridLayout(view_market_dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.viewMarketGroupBox = QtGui.QGroupBox(view_market_dialog)
        self.viewMarketGroupBox.setObjectName(_fromUtf8("viewMarketGroupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.viewMarketGroupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.descPlainTextEdit = QtGui.QPlainTextEdit(self.viewMarketGroupBox)
        self.descPlainTextEdit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.descPlainTextEdit.setReadOnly(True)
        self.descPlainTextEdit.setObjectName(_fromUtf8("descPlainTextEdit"))
        self.verticalLayout.addWidget(self.descPlainTextEdit)
        self.regFeeLabel = QtGui.QLabel(self.viewMarketGroupBox)
        self.regFeeLabel.setObjectName(_fromUtf8("regFeeLabel"))
        self.verticalLayout.addWidget(self.regFeeLabel)
        self.burnMultLabel = QtGui.QLabel(self.viewMarketGroupBox)
        self.burnMultLabel.setObjectName(_fromUtf8("burnMultLabel"))
        self.verticalLayout.addWidget(self.burnMultLabel)
        self.downvoteMultLabel = QtGui.QLabel(self.viewMarketGroupBox)
        self.downvoteMultLabel.setObjectName(_fromUtf8("downvoteMultLabel"))
        self.verticalLayout.addWidget(self.downvoteMultLabel)
        self.gridLayout_2.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.descLabel = QtGui.QLabel(self.viewMarketGroupBox)
        self.descLabel.setObjectName(_fromUtf8("descLabel"))
        self.gridLayout_2.addWidget(self.descLabel, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.viewMarketGroupBox)
        self.jsonGroupBox = QtGui.QGroupBox(view_market_dialog)
        self.jsonGroupBox.setObjectName(_fromUtf8("jsonGroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.jsonGroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.jsonPlainTextEdit = QtGui.QPlainTextEdit(self.jsonGroupBox)
        self.jsonPlainTextEdit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.jsonPlainTextEdit.setReadOnly(True)
        self.jsonPlainTextEdit.setObjectName(_fromUtf8("jsonPlainTextEdit"))
        self.gridLayout.addWidget(self.jsonPlainTextEdit, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.jsonGroupBox)
        self.gridLayout_3.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(view_market_dialog)
        QtCore.QMetaObject.connectSlotsByName(view_market_dialog)

    def retranslateUi(self, view_market_dialog):
        view_market_dialog.setWindowTitle(_translate("view_market_dialog", "View Market", None))
        self.viewMarketGroupBox.setTitle(_translate("view_market_dialog", "View Market: Marketname", None))
        self.regFeeLabel.setText(_translate("view_market_dialog", "Registration Fee: ", None))
        self.burnMultLabel.setText(_translate("view_market_dialog", "BURN Multiplier: ", None))
        self.downvoteMultLabel.setText(_translate("view_market_dialog", "Downvote Multiplier: ", None))
        self.descLabel.setText(_translate("view_market_dialog", "Description:", None))
        self.jsonGroupBox.setTitle(_translate("view_market_dialog", "Market JSON:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    view_market_dialog = QtGui.QDialog()
    ui = Ui_view_market_dialog()
    ui.setupUi(view_market_dialog)
    view_market_dialog.show()
    sys.exit(app.exec_())

