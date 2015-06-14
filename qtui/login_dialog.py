#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_dialog.ui'
#
# Created: Sun Jun 14 13:04:14 2015
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

class Ui_login_dialog(object):
    def setupUi(self, login_dialog):
        login_dialog.setObjectName(_fromUtf8("login_dialog"))
        login_dialog.resize(400, 180)
        self.gridLayout = QtGui.QGridLayout(login_dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(login_dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.pswd_lineedit = QtGui.QLineEdit(self.groupBox)
        self.pswd_lineedit.setEchoMode(QtGui.QLineEdit.Password)
        self.pswd_lineedit.setObjectName(_fromUtf8("pswd_lineedit"))
        self.gridLayout_2.addWidget(self.pswd_lineedit, 3, 0, 1, 1)
        self.pswd_label = QtGui.QLabel(self.groupBox)
        self.pswd_label.setObjectName(_fromUtf8("pswd_label"))
        self.gridLayout_2.addWidget(self.pswd_label, 2, 0, 1, 1)
        self.name_lineedit = QtGui.QLineEdit(self.groupBox)
        self.name_lineedit.setObjectName(_fromUtf8("name_lineedit"))
        self.gridLayout_2.addWidget(self.name_lineedit, 1, 0, 1, 1)
        self.name_label = QtGui.QLabel(self.groupBox)
        self.name_label.setObjectName(_fromUtf8("name_label"))
        self.gridLayout_2.addWidget(self.name_label, 0, 0, 1, 1)
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
        login_dialog.setTabOrder(self.name_lineedit, self.pswd_lineedit)
        login_dialog.setTabOrder(self.pswd_lineedit, self.buttonBox)

    def retranslateUi(self, login_dialog):
        login_dialog.setWindowTitle(_translate("login_dialog", "Welcome to METAmarket", None))
        self.groupBox.setTitle(_translate("login_dialog", "Please login:", None))
        self.pswd_label.setText(_translate("login_dialog", "Password", None))
        self.name_label.setText(_translate("login_dialog", "Username", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    login_dialog = QtGui.QDialog()
    ui = Ui_login_dialog()
    ui.setupUi(login_dialog)
    login_dialog.show()
    sys.exit(app.exec_())

