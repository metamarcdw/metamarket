#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_chanmsg_dialog.ui'
#
# Created: Wed May 11 02:04:51 2016
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_view_chanmsg_dialog(object):
    def setupUi(self, view_chanmsg_dialog):
        view_chanmsg_dialog.setObjectName(_fromUtf8("view_chanmsg_dialog"))
        view_chanmsg_dialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(view_chanmsg_dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(view_chanmsg_dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.plainTextEdit = QtGui.QPlainTextEdit(self.groupBox)
        self.plainTextEdit.setLineWrapMode(QtGui.QPlainTextEdit.WidgetWidth)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.gridLayout_2.addWidget(self.plainTextEdit, 1, 0, 1, 1)
        self.subjectLineEdit = QtGui.QLineEdit(self.groupBox)
        self.subjectLineEdit.setReadOnly(True)
        self.subjectLineEdit.setObjectName(_fromUtf8("subjectLineEdit"))
        self.gridLayout_2.addWidget(self.subjectLineEdit, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(view_chanmsg_dialog)
        QtCore.QMetaObject.connectSlotsByName(view_chanmsg_dialog)

    def retranslateUi(self, view_chanmsg_dialog):
        view_chanmsg_dialog.setWindowTitle(_translate("view_chanmsg_dialog", "View Channel Message", None))
        self.groupBox.setTitle(_translate("view_chanmsg_dialog", "Message:", None))
        self.subjectLineEdit.setPlaceholderText(_translate("view_chanmsg_dialog", "Subject", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    view_chanmsg_dialog = QtGui.QDialog()
    ui = Ui_view_chanmsg_dialog()
    ui.setupUi(view_chanmsg_dialog)
    view_chanmsg_dialog.show()
    sys.exit(app.exec_())

