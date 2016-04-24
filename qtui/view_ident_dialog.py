#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_ident_dialog.ui'
#
# Created: Sat Apr 23 19:51:23 2016
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

class Ui_view_ident_dialog(object):
    def setupUi(self, view_ident_dialog):
        view_ident_dialog.setObjectName(_fromUtf8("view_ident_dialog"))
        view_ident_dialog.resize(400, 119)
        self.gridLayout_2 = QtGui.QGridLayout(view_ident_dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.viewIdentGroupbox = QtGui.QGroupBox(view_ident_dialog)
        self.viewIdentGroupbox.setObjectName(_fromUtf8("viewIdentGroupbox"))
        self.gridLayout = QtGui.QGridLayout(self.viewIdentGroupbox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.hashLabel = QtGui.QLabel(self.viewIdentGroupbox)
        self.hashLabel.setObjectName(_fromUtf8("hashLabel"))
        self.verticalLayout.addWidget(self.hashLabel)
        self.btcaddrLabel = QtGui.QLabel(self.viewIdentGroupbox)
        self.btcaddrLabel.setObjectName(_fromUtf8("btcaddrLabel"))
        self.verticalLayout.addWidget(self.btcaddrLabel)
        self.bmaddrLabel = QtGui.QLabel(self.viewIdentGroupbox)
        self.bmaddrLabel.setObjectName(_fromUtf8("bmaddrLabel"))
        self.verticalLayout.addWidget(self.bmaddrLabel)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.viewIdentGroupbox, 0, 0, 1, 1)

        self.retranslateUi(view_ident_dialog)
        QtCore.QMetaObject.connectSlotsByName(view_ident_dialog)

    def retranslateUi(self, view_ident_dialog):
        view_ident_dialog.setWindowTitle(_translate("view_ident_dialog", "Dialog", None))
        self.viewIdentGroupbox.setTitle(_translate("view_ident_dialog", "View Identity: Identname", None))
        self.hashLabel.setText(_translate("view_ident_dialog", "ID hash: ", None))
        self.btcaddrLabel.setText(_translate("view_ident_dialog", "BTC address: ", None))
        self.bmaddrLabel.setText(_translate("view_ident_dialog", "BM address: ", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    view_ident_dialog = QtGui.QDialog()
    ui = Ui_view_ident_dialog()
    ui.setupUi(view_ident_dialog)
    view_ident_dialog.show()
    sys.exit(app.exec_())

