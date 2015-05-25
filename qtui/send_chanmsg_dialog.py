#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'send_chanmsg_dialog.ui'
#
# Created: Mon May 25 16:41:49 2015
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

class Ui_send_chanmsg_dialog(object):
    def setupUi(self, send_chanmsg_dialog):
        send_chanmsg_dialog.setObjectName(_fromUtf8("send_chanmsg_dialog"))
        send_chanmsg_dialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(send_chanmsg_dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(send_chanmsg_dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.plainTextEdit = QtGui.QPlainTextEdit(self.groupBox)
        self.plainTextEdit.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.gridLayout_2.addWidget(self.plainTextEdit, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(send_chanmsg_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(send_chanmsg_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), send_chanmsg_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), send_chanmsg_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(send_chanmsg_dialog)

    def retranslateUi(self, send_chanmsg_dialog):
        send_chanmsg_dialog.setWindowTitle(_translate("send_chanmsg_dialog", "Send Channel Message", None))
        self.groupBox.setTitle(_translate("send_chanmsg_dialog", "Enter Message:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    send_chanmsg_dialog = QtGui.QDialog()
    ui = Ui_send_chanmsg_dialog()
    ui.setupUi(send_chanmsg_dialog)
    send_chanmsg_dialog.show()
    sys.exit(app.exec_())

