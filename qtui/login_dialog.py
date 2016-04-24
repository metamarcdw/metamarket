#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_dialog.ui'
#
# Created: Sat Apr 23 14:08:55 2016
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

class Ui_login_dialog(object):
    def setupUi(self, login_dialog):
        login_dialog.setObjectName(_fromUtf8("login_dialog"))
        login_dialog.resize(400, 195)
        self.gridLayout = QtGui.QGridLayout(login_dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(login_dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.pswdLineEdit = QtGui.QLineEdit(self.groupBox)
        self.pswdLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.pswdLineEdit.setObjectName(_fromUtf8("pswdLineEdit"))
        self.gridLayout_2.addWidget(self.pswdLineEdit, 3, 0, 1, 1)
        self.pswdLabel = QtGui.QLabel(self.groupBox)
        self.pswdLabel.setObjectName(_fromUtf8("pswdLabel"))
        self.gridLayout_2.addWidget(self.pswdLabel, 2, 0, 1, 1)
        self.nameLineEdit = QtGui.QLineEdit(self.groupBox)
        self.nameLineEdit.setObjectName(_fromUtf8("nameLineEdit"))
        self.gridLayout_2.addWidget(self.nameLineEdit, 1, 0, 1, 1)
        self.nameLabel = QtGui.QLabel(self.groupBox)
        self.nameLabel.setObjectName(_fromUtf8("nameLabel"))
        self.gridLayout_2.addWidget(self.nameLabel, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(login_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(login_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), login_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), login_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(login_dialog)
        login_dialog.setTabOrder(self.nameLineEdit, self.pswdLineEdit)
        login_dialog.setTabOrder(self.pswdLineEdit, self.buttonBox)

    def retranslateUi(self, login_dialog):
        login_dialog.setWindowTitle(_translate("login_dialog", "Welcome to METAmarket", None))
        self.groupBox.setTitle(_translate("login_dialog", "Please login:", None))
        self.pswdLabel.setText(_translate("login_dialog", "Password", None))
        self.nameLabel.setText(_translate("login_dialog", "Username", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    login_dialog = QtGui.QDialog()
    ui = Ui_login_dialog()
    ui.setupUi(login_dialog)
    login_dialog.show()
    sys.exit(app.exec_())

