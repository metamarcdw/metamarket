#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
MAC = hasattr(PyQt4.QtGui, "qt_mac_set_native_menubar")
import config_dialog

import sys, os
sys.path.append(    # Make sure we can access MM_util in the parent directory
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from MM_util import truncate
from decimal import Decimal

class ConfigDlg(QDialog,
        config_dialog.Ui_config_dialog):
    
    def __init__(self, configTuple, parent=None):
        super(ConfigDlg, self).__init__(parent)
        self.setupUi(self)
        if not MAC:
            self.buttonBox.setFocusPolicy(Qt.NoFocus)
        
        chain, channame, fee, minconf, \
            bmuser, bmpswd, bmhost, bmport, \
            btcuser, btcpswd, btchost, btcport = configTuple
        
        if chain == "mainnet":
            self.chainComboBox.setCurrentIndex(0)
        else:
            self.chainComboBox.setCurrentIndex(1)
        self.channameLineEdit.setText(channame)
        self.feeDoubleSpinBox.setValue(fee)
        self.minconfSpinBox.setValue(minconf)
        
        self.bmuserLineEdit.setText(bmuser)
        self.bmpswdLineEdit.setText(bmpswd)
        self.bmhostLineEdit.setText(bmhost)
        self.bmportSpinBox.setValue(bmport)
        
        self.btcuserLineEdit.setText(btcuser)
        self.btcpswdLineEdit.setText(btcpswd)
        self.btchostLineEdit.setText(btchost)
        self.btcportSpinBox.setValue(btcport)
        
        self.updateUi()
    
    def updateUi(self):
        channame_blank = self.channameLineEdit.text().isEmpty()
        bmuser_blank = self.bmuserLineEdit.text().isEmpty()
        bmpswd_blank = self.bmpswdLineEdit.text().isEmpty()
        bmhost_blank = self.bmhostLineEdit.text().isEmpty()
        btcuser_blank = self.btcuserLineEdit.text().isEmpty()
        btcpswd_blank = self.btcpswdLineEdit.text().isEmpty()
        btchost_blank = self.btchostLineEdit.text().isEmpty()
        
        if channame_blank or \
                bmuser_blank or bmpswd_blank or bmhost_blank or \
                btcuser_blank or btcpswd_blank or btchost_blank:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
    
    
    @pyqtSignature("QString")
    def on_channameLineEdit_textEdited(self):
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_bmuserLineEdit_textEdited(self):
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_bmpswdLineEdit_textEdited(self):
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_bmhostLineEdit_textEdited(self):
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_btcuserLineEdit_textEdited(self):
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_btcpswdLineEdit_textEdited(self):
        self.updateUi()
    
    @pyqtSignature("QString")
    def on_btchostLineEdit_textEdited(self):
        self.updateUi()
    
    
    def result(self):
        chain = str( self.chainComboBox.currentText() )
        channame = str( self.channameLineEdit.text() )
        fee = truncate( Decimal(self.feeDoubleSpinBox.value()) )
        minconf = self.minconfSpinBox.value()
        
        bmuser = str( self.bmuserLineEdit.text() )
        bmpswd = str( self.bmpswdLineEdit.text() )
        bmhost = str( self.bmhostLineEdit.text() )
        bmport = self.bmportSpinBox.value()
        
        btcuser = str( self.btcuserLineEdit.text() )
        btcpswd = str( self.btcpswdLineEdit.text() )
        btchost = str( self.btchostLineEdit.text() )
        btcport = self.btcportSpinBox.value()
        
        return ( chain, channame, fee, minconf, \
                    bmuser, bmpswd, bmhost, bmport, \
                    btcuser, btcpswd, btchost, btcport )
    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    chain = sys.argv[1]
    channame = sys.argv[2]
    fee = Decimal( sys.argv[3] )
    minconf = int( sys.argv[4] )
    
    bmuser = sys.argv[5]
    bmpswd = sys.argv[6]
    bmhost = sys.argv[7]
    bmport = int( sys.argv[8] )
    
    btcuser = sys.argv[9]
    btcpswd = sys.argv[10]
    btchost = sys.argv[11]
    btcport = int( sys.argv[12] )
    
    configTuple = ( chain, channame, fee, minconf, \
                    bmuser, bmpswd, bmhost, bmport, \
                    btcuser, btcpswd, btchost, btcport )
    
    form = ConfigDlg(configTuple)
    if form.exec_():
        print form.result()
    sys.exit(0)

