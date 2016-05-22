#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config_dialog.ui'
#
# Created: Sun May 22 19:50:48 2016
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(384, 393)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.chainLabel = QtGui.QLabel(self.groupBox)
        self.chainLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.chainLabel.setObjectName(_fromUtf8("chainLabel"))
        self.verticalLayout.addWidget(self.chainLabel)
        self.channameLabel = QtGui.QLabel(self.groupBox)
        self.channameLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.channameLabel.setObjectName(_fromUtf8("channameLabel"))
        self.verticalLayout.addWidget(self.channameLabel)
        self.feeLabel = QtGui.QLabel(self.groupBox)
        self.feeLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.feeLabel.setObjectName(_fromUtf8("feeLabel"))
        self.verticalLayout.addWidget(self.feeLabel)
        self.minconfLabel = QtGui.QLabel(self.groupBox)
        self.minconfLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.minconfLabel.setObjectName(_fromUtf8("minconfLabel"))
        self.verticalLayout.addWidget(self.minconfLabel)
        self.bmuserLabel = QtGui.QLabel(self.groupBox)
        self.bmuserLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.bmuserLabel.setObjectName(_fromUtf8("bmuserLabel"))
        self.verticalLayout.addWidget(self.bmuserLabel)
        self.bmpswdLabel = QtGui.QLabel(self.groupBox)
        self.bmpswdLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.bmpswdLabel.setObjectName(_fromUtf8("bmpswdLabel"))
        self.verticalLayout.addWidget(self.bmpswdLabel)
        self.bmhostLabel = QtGui.QLabel(self.groupBox)
        self.bmhostLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.bmhostLabel.setObjectName(_fromUtf8("bmhostLabel"))
        self.verticalLayout.addWidget(self.bmhostLabel)
        self.bmportLabel = QtGui.QLabel(self.groupBox)
        self.bmportLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.bmportLabel.setObjectName(_fromUtf8("bmportLabel"))
        self.verticalLayout.addWidget(self.bmportLabel)
        self.btcportLabel = QtGui.QLabel(self.groupBox)
        self.btcportLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.btcportLabel.setObjectName(_fromUtf8("btcportLabel"))
        self.verticalLayout.addWidget(self.btcportLabel)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.chainComboBox = QtGui.QComboBox(self.groupBox)
        self.chainComboBox.setObjectName(_fromUtf8("chainComboBox"))
        self.chainComboBox.addItem(_fromUtf8(""))
        self.chainComboBox.addItem(_fromUtf8(""))
        self.verticalLayout_2.addWidget(self.chainComboBox)
        self.channameLineEdit = QtGui.QLineEdit(self.groupBox)
        self.channameLineEdit.setObjectName(_fromUtf8("channameLineEdit"))
        self.verticalLayout_2.addWidget(self.channameLineEdit)
        self.feeDoubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox)
        self.feeDoubleSpinBox.setDecimals(8)
        self.feeDoubleSpinBox.setSingleStep(1e-06)
        self.feeDoubleSpinBox.setObjectName(_fromUtf8("feeDoubleSpinBox"))
        self.verticalLayout_2.addWidget(self.feeDoubleSpinBox)
        self.minconfSpinBox = QtGui.QSpinBox(self.groupBox)
        self.minconfSpinBox.setObjectName(_fromUtf8("minconfSpinBox"))
        self.verticalLayout_2.addWidget(self.minconfSpinBox)
        self.bmuserLineEdit = QtGui.QLineEdit(self.groupBox)
        self.bmuserLineEdit.setObjectName(_fromUtf8("bmuserLineEdit"))
        self.verticalLayout_2.addWidget(self.bmuserLineEdit)
        self.bmpswdLineEdit = QtGui.QLineEdit(self.groupBox)
        self.bmpswdLineEdit.setObjectName(_fromUtf8("bmpswdLineEdit"))
        self.verticalLayout_2.addWidget(self.bmpswdLineEdit)
        self.bmhostLineEdit = QtGui.QLineEdit(self.groupBox)
        self.bmhostLineEdit.setObjectName(_fromUtf8("bmhostLineEdit"))
        self.verticalLayout_2.addWidget(self.bmhostLineEdit)
        self.bmportSpinBox = QtGui.QSpinBox(self.groupBox)
        self.bmportSpinBox.setMaximum(99999)
        self.bmportSpinBox.setObjectName(_fromUtf8("bmportSpinBox"))
        self.verticalLayout_2.addWidget(self.bmportSpinBox)
        self.btcportSpinBox = QtGui.QSpinBox(self.groupBox)
        self.btcportSpinBox.setMaximum(99999)
        self.btcportSpinBox.setObjectName(_fromUtf8("btcportSpinBox"))
        self.verticalLayout_2.addWidget(self.btcportSpinBox)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.verticalLayout_4.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_4.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.chainLabel.setBuddy(self.chainComboBox)
        self.channameLabel.setBuddy(self.channameLineEdit)
        self.feeLabel.setBuddy(self.feeDoubleSpinBox)
        self.minconfLabel.setBuddy(self.minconfSpinBox)
        self.bmuserLabel.setBuddy(self.bmuserLineEdit)
        self.bmpswdLabel.setBuddy(self.bmpswdLineEdit)
        self.bmhostLabel.setBuddy(self.bmhostLineEdit)
        self.bmportLabel.setBuddy(self.bmportSpinBox)
        self.btcportLabel.setBuddy(self.btcportSpinBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.chainComboBox, self.channameLineEdit)
        Dialog.setTabOrder(self.channameLineEdit, self.feeDoubleSpinBox)
        Dialog.setTabOrder(self.feeDoubleSpinBox, self.minconfSpinBox)
        Dialog.setTabOrder(self.minconfSpinBox, self.bmuserLineEdit)
        Dialog.setTabOrder(self.bmuserLineEdit, self.bmpswdLineEdit)
        Dialog.setTabOrder(self.bmpswdLineEdit, self.bmhostLineEdit)
        Dialog.setTabOrder(self.bmhostLineEdit, self.bmportSpinBox)
        Dialog.setTabOrder(self.bmportSpinBox, self.btcportSpinBox)
        Dialog.setTabOrder(self.btcportSpinBox, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.groupBox.setTitle(_translate("Dialog", "Configuration:", None))
        self.chainLabel.setText(_translate("Dialog", "Bitcoin Chain:", None))
        self.channameLabel.setText(_translate("Dialog", "Chan Name:", None))
        self.feeLabel.setText(_translate("Dialog", "Default Fee:", None))
        self.minconfLabel.setText(_translate("Dialog", "Minimum Confirms:", None))
        self.bmuserLabel.setText(_translate("Dialog", "Bitmessage RPC User:", None))
        self.bmpswdLabel.setText(_translate("Dialog", "Bitmessage RPC Password:", None))
        self.bmhostLabel.setText(_translate("Dialog", "Bitmessage RPC Host:", None))
        self.bmportLabel.setText(_translate("Dialog", "Bitmessage RPC Port:", None))
        self.btcportLabel.setText(_translate("Dialog", "Bitcoin Core RPC Port:", None))
        self.chainComboBox.setItemText(0, _translate("Dialog", "testnet", None))
        self.chainComboBox.setItemText(1, _translate("Dialog", "mainnet", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

