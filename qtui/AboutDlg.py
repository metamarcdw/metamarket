#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.QtGui
MAC = hasattr(PyQt4.QtGui, "qt_mac_set_native_menubar")
import about_dialog

class AboutDlg(QDialog,
        about_dialog.Ui_about_dialog):
    
    def __init__(self, parent=None):
        super(AboutDlg, self).__init__(parent)
        self.setupUi(self)
        if not MAC:
            self.buttonBox.setFocusPolicy(Qt.NoFocus)
    

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    form = AboutDlg()
    form.show()
    app.exec_()
    

