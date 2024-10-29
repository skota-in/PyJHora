#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from PyQt6.QtWidgets import QLineEdit, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QPushButton,\
                            QRadioButton, QDialog, QCheckBox
from PyQt6.QtCore import Qt
from jhora import utils, const
class OptionDialog(QDialog):
    """
        General Options Dialog
    """
    def __init__(self, title='',option_label='', options_list=[],multi_selection=False,default_options=[0]):
        super().__init__()
        self.res = utils.resource_strings
        self._title = 'Options' if title.strip()=='' else title
        self._option_label = 'Select one of the options:' if option_label.strip()=='' else option_label
        self._options_list = options_list
        self._multi_selection = multi_selection
        if not multi_selection and not isinstance(default_options,list): default_options = [default_options]
        self._default_options = default_options
        self.create_ui()
    def create_ui(self):
        v_layout = QVBoxLayout()
        _label = QLabel(self._option_label)
        v_layout.addWidget(_label)
        if len(self._options_list) == 0: return
        self._options = []
        if self._multi_selection:
            for mc in range(len(self._options_list)):
                _caption = self._options_list[mc]
                self._options.append(QCheckBox(_caption))
                if mc in self._default_options: self._options[mc].setChecked(True)
                v_layout.addWidget(self._options[mc])        
        else:
            for mc in range(len(self._options_list)):
                _caption = self._options_list[mc]
                self._options.append(QRadioButton(_caption))
                if mc in self._default_options: self._options[mc].setChecked(True)
                v_layout.addWidget(self._options[mc])        
        h_layout = QHBoxLayout()
        self._accept_button = QPushButton(self.res['accept_str'])
        self._accept_button.clicked.connect(self._accept_button_clicked)
        h_layout.addWidget(self._accept_button)
        self._cancel_button = QPushButton(self.res['cancel_str'])
        self._cancel_button.clicked.connect(self._cancel_button_clicked)
        h_layout.addWidget(self._cancel_button)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)
        self.setWindowTitle(self._title)
    def _accept_button_clicked(self):
        self._accept_clicked = True
        if self._multi_selection:
            self._option_string=[];self._option_index=[]
            for mc,rb in enumerate(self._options):
                if rb.isChecked():
                    self._option_string.append(rb.text())
                    self._option_index.append(mc+1)
        else:
            for mc,rb in enumerate(self._options):
                if rb.isChecked():
                    self._option_string = rb.text()
                    self._option_index = mc+1
        self.accept()
    def _cancel_button_clicked(self):
        self._accept_clicked = False
        self._option_string = [] if self._multi_selection else ''
        self._option_index = [] if self._multi_selection else ''
        self.reject()
    def closeEvent(self, *args, **kwargs):
        self._option_string = ''
        QApplication.restoreOverrideCursor()
        return QDialog.closeEvent(self, *args, **kwargs)

if __name__ == "__main__":
    import sys
    utils.set_language('ta')
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart = OptionDialog(title='Title',option_label='Select options from',options_list=['option1','option2'],
                         multi_selection=False,default_options=1)
    chart.show()
    sys.exit(App.exec())
