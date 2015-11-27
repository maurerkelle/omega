#
#    Copyright (C) 2015  Sven Kromminga
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'Sven Kromminga'

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from .rectconcretedesign import RectConcreteDesign

from .ui import mainwindow_ui
from .ui import aboutdialog_ui

class MainWindow(QtGui.QMainWindow):
        def __init__(self):
                super(MainWindow,self).__init__()
                self.rectConcreteDesign = RectConcreteDesign()
                self.locale = QtCore.QLocale()

                self.ui = mainwindow_ui.Ui_MainWindow()
                self.ui.setupUi(self)
                self.setup_signals()
                self.on_concrete_combo_activated()  # call to init fields
                self.on_value_changed()  # call to init fields

        def setup_signals(self):
                for box in (self.ui.medSpinBox, self.ui.nedSpinBox, self.ui.fcdSpinBox,
                            self.ui.widthSpinBox, self.ui.heightSpinBox, self.ui.d1SpinBox):
                        box.valueChanged.connect(self.on_value_changed)
                        self.ui.concreteCombo.activated.connect(self.on_concrete_combo_activated)
                        self.ui.actionAbout.triggered.connect(self.on_action_about)

        def on_concrete_combo_activated(self):
                value = self.ui.concreteCombo.currentText().split('/')[0].replace('C','')
                self.ui.fcdSpinBox.setValue(float(value)*0.85/1.5)

        def on_value_changed(self):
                p = {}
                p['MEd'] = self.ui.medSpinBox.value()
                p['NEd'] = self.ui.nedSpinBox.value()
                p['fcd'] = self.ui.fcdSpinBox.value()
                p['w'] = self.ui.widthSpinBox.value()
                p['h'] = self.ui.heightSpinBox.value()
                p['d1'] = self.ui.d1SpinBox.value()/100.0
                p['d2'] = 0.1  # TODO

                self.rectConcreteDesign.set_params(p)

                self.ui.outZs.setText(self.locale.toString(self.rectConcreteDesign._zs))
                self.ui.outD.setText(self.locale.toString(self.rectConcreteDesign._d))
                self.ui.outMuS1Ed.setText(self.locale.toString(self.rectConcreteDesign._mus1ed))
                self.ui.outOmega1.setText(self.locale.toString(self.rectConcreteDesign._omega.omega_1))
                self.ui.outEpsS1.setText(self.locale.toString(self.rectConcreteDesign._omega.epss1))
                self.ui.outEpsC2.setText(self.locale.toString(self.rectConcreteDesign._omega.epsc2))
                self.ui.outXi.setText(self.locale.toString(self.rectConcreteDesign._omega.xi))
                self.ui.outZeta.setText(self.locale.toString(self.rectConcreteDesign._omega.zeta))
                self.ui.outVSigma.setText(self.locale.toString(self.rectConcreteDesign._omega.vsigma))
                self.ui.outAs1.setText(self.locale.toString(self.rectConcreteDesign._As1))
                self.ui.outAs2.setText(self.locale.toString(self.rectConcreteDesign._As2))


        def on_action_about(self):
                abdlg = QtGui.QDialog()
                uid = aboutdialog_ui.Ui_AboutDialog()
                uid.setupUi(abdlg)
                abdlg.exec_()




def run():
        app = QtGui.QApplication(sys.argv)
        m = MainWindow()
        m.show()
        sys.exit(app.exec_())
