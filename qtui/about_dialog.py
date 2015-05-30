#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about_dialog.ui'
#
# Created: Fri May 29 23:27:52 2015
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

class Ui_about_dialog(object):
    def setupUi(self, about_dialog):
        about_dialog.setObjectName(_fromUtf8("about_dialog"))
        about_dialog.resize(360, 169)
        self.gridLayout = QtGui.QGridLayout(about_dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(about_dialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.labelVersion = QtGui.QLabel(about_dialog)
        self.labelVersion.setObjectName(_fromUtf8("labelVersion"))
        self.horizontalLayout.addWidget(self.labelVersion)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtGui.QLabel(about_dialog)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.label_5 = QtGui.QLabel(about_dialog)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.label_3 = QtGui.QLabel(about_dialog)
        self.label_3.setWordWrap(True)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.buttonBox = QtGui.QDialogButtonBox(about_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(about_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), about_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), about_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(about_dialog)

    def retranslateUi(self, about_dialog):
        about_dialog.setWindowTitle(_translate("about_dialog", "About", None))
        self.label.setText(_translate("about_dialog", "METAmarket-Qt", None))
        self.labelVersion.setText(_translate("about_dialog", "version v0.1.0", None))
        self.label_2.setText(_translate("about_dialog", "<html><head/><body><p>Copyright © 2015 METAmarket Developers</p></body></html>", None))
        self.label_5.setText(_translate("about_dialog", "This is Alpha software.", None))
        self.label_3.setText(_translate("about_dialog", "<html><head/><body><p>Distributed under the MIT software license; <a href=\"http://www.opensource.org/licenses/mit-license.php\"><span style=\" text-decoration: underline; color:#0000ff;\">http://www.opensource.org/licenses/mit-license.php</span></a></p></body></html>", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    about_dialog = QtGui.QDialog()
    ui = Ui_about_dialog()
    ui.setupUi(about_dialog)
    about_dialog.show()
    sys.exit(app.exec_())

