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
import re, sys, os
from astropy.table import info
sys.path.append('../')
""" Get Package Version from _package_info.py """
#import importlib.metadata
#_APP_VERSION = importlib.metadata.version('PyJHora')
from jhora import _package_info
_APP_VERSION=_package_info.version
#----------
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QStyledItemDelegate, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, \
                            QListWidget, QTextEdit, QAbstractItemView, QAbstractScrollArea, QTableWidgetItem, \
                            QGridLayout, QLayout, QLabel, QSizePolicy, QLineEdit, QCompleter, QComboBox, \
                            QPushButton, QSpinBox, QCheckBox, QApplication, QDoubleSpinBox, QHeaderView, \
                            QListWidgetItem,QMessageBox, QFileDialog, QButtonGroup, QRadioButton, QStackedWidget, \
                            QTreeWidget
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtCore import Qt
from _datetime import datetime, timedelta, timezone
import img2pdf
from PIL import Image
import numpy as np
from jhora import const, utils
from jhora.panchanga import drik, pancha_paksha, vratha
from jhora.horoscope import main
from jhora.horoscope.prediction import general
from jhora.horoscope.match import compatibility
from jhora.horoscope.chart import ashtakavarga
from jhora.horoscope.chart import yoga, raja_yoga, dosha, charts, strength, arudhas
from jhora.horoscope.chart import house
from jhora.ui import varga_chart_dialog,options_dialog, mixed_chart_dialog, dhasa_bhukthi_options_dialog,vratha_finder, \
                     conjunction_dialog, pancha_pakshi_sastra_widget
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.ui.chart_styles import EastIndianChart, WesternChart, SouthIndianChart, NorthIndianChart, SudarsanaChakraChart
from jhora.ui.label_grid import LabelGrid
from jhora.horoscope.dhasa import sudharsana_chakra
from jhora.ui.chakra import KotaChakra, KaalaChakra, Sarvatobadra, Shoola, SuryaKalanala, Tripataki,ChandraKalanala, \
                            SapthaShalaka, PanchaShalaka, SapthaNaadi
_available_ayanamsa_modes = [k for k in list(const.available_ayanamsa_modes.keys()) if k not in ['SENTHIL','SIDM_USER','SUNDAR_SS']]
_KEY_COLOR = 'brown'; _VALUE_COLOR = 'blue'; _HEADER_COLOR='green'
_KEY_LENGTH=50; _VALUE_LENGTH=50; _HEADER_LENGTH=100
_HEADER_FORMAT_ = '<b><span style="color:'+_HEADER_COLOR+';">{:<'+str(_HEADER_LENGTH)+'}</span></b><br>'
_KEY_VALUE_FORMAT_ = '<span style="color:'+_KEY_COLOR+';">{:<'+str(_KEY_LENGTH)+'}</span><span style="color:'+\
        _VALUE_COLOR+';">{:<'+str(_VALUE_LENGTH)+'}</span><br>'
_images_path = const._IMAGES_PATH
_IMAGES_PER_PDF_PAGE = 2
_IMAGE_ICON_PATH=const._IMAGE_ICON_PATH
_INPUT_DATA_FILE = const._INPUT_DATA_FILE
_SHOW_GOURI_PANCHANG_OR_SHUBHA_HORA = 0 # 0=Gowri Panchang 1=Shubha Hora
_world_city_csv_file = const._world_city_csv_file
_planet_symbols=const._planet_symbols
_zodiac_symbols = const._zodiac_symbols
""" UI Constants """
_main_window_width = 1000#750 #725
_main_window_height = 725#630 #580 #
_main_ui_label_button_font_size = 10#8
#_main_ui_comp_label_font_size = 7
_info_label1_height = 200
_info_label1_width = 100
_info_label1_font_size = 7#8
_info_label2_height = _info_label1_height
_info_label2_width = 100
_info_label2_font_size = 6.8#8
_info_label3_font_size = 6#8
_row3_widget_width = 75
_chart_info_label_width = 230#350
_footer_label_font_height = 8
_footer_label_height = 30
_chart_size_factor = 1.35
_tab_names = ['panchangam_str']
_tab_count = len(_tab_names)
_tabcount_before_chart_tab = 1

available_languages = const.available_languages
class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignmentFlag.AlignHCenter
class GrowingTextEdit(QTextEdit):

    def __init__(self, *args, **kwargs):
        super(GrowingTextEdit, self).__init__(*args, **kwargs)  
        self.document().contentsChanged.connect(self.sizeChange)

        self.heightMin = 0
        self.heightMax = 65000

    def sizeChange(self):
        docHeight = int(self.document().size().height())
        if self.heightMin <= docHeight <= self.heightMax:
            self.setMinimumHeight(docHeight)
class ChartTabbed(QWidget):
    def __init__(self,calculation_type:str='drik',language = 'English',date_of_birth=None,time_of_birth=None,
                 place_of_birth=None):
        """
            @param date_of_birth: string in the format 'yyyy,m,d' e.g. '2024,1,1'  or '2024,01,01'
            @param place_of_birth: tuple in the format ('place_name',latitude_float,longitude_float,timezone_hrs_float)
                                    e.g. ('Chennai, India',13.0878,80.2785,5.5)
            @param language: One of 'English','Hindi','Tamil','Telugu','Kannada'; Default:English
        """
        super().__init__()
        self._horo = None
        self._language = language; utils.set_language(available_languages[language])
        self.resources = utils.resource_strings
        self._calculation_type = calculation_type
        ' read world cities'
        self._df = utils._world_city_db_df
        self._world_cities_db = utils.world_cities_db
        current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        self._init_main_window()
        self._v_layout = QVBoxLayout()
        self._create_row1_ui()
        self._create_row_2_ui()
        self._init_tab_widget_ui()
        if date_of_birth == None:
            self.date_of_birth(current_date_str)
        if time_of_birth == None:
            self.time_of_birth(current_time_str)
        if place_of_birth == None:
            loc = utils.get_place_from_user_ip_address()
            print('loc from IP address',loc)
            if len(loc)==4:
                print('setting values from loc')
                self.place(loc[0],loc[1],loc[2],loc[3])
        year,month,day = self._dob_text.text().split(",")
        dob = (int(year),int(month),int(day))
        tob = tuple([int(x) for x in self._tob_text.text().split(':')])
        self._birth_julian_day = utils.julian_day_number(dob, tob)
        """ Commented in V4.0.4 to force explicit calling """
        #self.compute_horoscope(calculation_type=self._calculation_type)    
    def _hide_2nd_row_widgets(self,show=True):
            self._dob_label.setVisible(show)
            self._dob_text.setVisible(show)
            self._tob_label.setVisible(show)
            self._tob_text.setVisible(show)
            self._ayanamsa_combo.setVisible(show)
    def _init_tab_widget_ui(self):
        self.tabNames = _tab_names
        self.tabWidget = QTabWidget()
        self.horo_tabs = []
        self._v_layout.addWidget(self.tabWidget)
        self.tabCount = len(self.tabNames)
        t = 0
        self._init_panchanga_tab_widgets(t)
        self.tabCount = self.tabWidget.count()
        self._add_footer_to_chart()
        self.setLayout(self._v_layout)        
    def _init_panchanga_tab_widgets(self,tab_index):
        self.horo_tabs.append(QWidget())
        self.tabWidget.addTab(self.horo_tabs[tab_index],self.tabNames[tab_index])
        h_layout = QHBoxLayout()
        h_layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self._info_label1 = QLabel("Information:")
        self._info_label1.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.MinimumExpanding)
        self._info_label1.setStyleSheet("border: 1px solid black;"+' font-size:'+str(_info_label1_font_size)+'pt')
        self._info_label1.setMinimumHeight(_info_label1_height)
        self._info_label1.setMinimumWidth(_info_label1_width)
        h_layout.addWidget(self._info_label1)
        self._info_label2 = QLabel("Information:")
        self._info_label2.setStyleSheet("border: 1px solid black;"+' font-size:'+str(_info_label2_font_size)+'pt')
        self._info_label2.setMinimumHeight(_info_label1_height)
        self._info_label2.setMinimumWidth(_info_label2_width)
        h_layout.addWidget(self._info_label2)
        self._info_label3 = QLabel("Information:")
        self._info_label3.setStyleSheet("border: 1px solid black;"+' font-size:'+str(_info_label3_font_size)+'pt')
        self._info_label3.setMinimumHeight(_info_label1_height)
        self._info_label3.setMinimumWidth(_info_label2_width)
        h_layout.addWidget(self._info_label3)
        self.horo_tabs[tab_index].setLayout(h_layout)
    def _init_main_window(self):
        self._footer_title = ''
        self.setWindowIcon(QtGui.QIcon(_IMAGE_ICON_PATH))
        self._language = list(available_languages.keys())[0]#list(available_languages.keys())[0]
        self.setFixedSize(_main_window_width,_main_window_height)
        self.showMaximized()
        #self.setMinimumSize(_main_window_width,_main_window_height)        
    def _create_row1_ui(self):
        self._row1_h_layout = QHBoxLayout()
        self._dob_label = QLabel("Date of Birth:")
        self._row1_h_layout.addWidget(self._dob_label)
        self._date_of_birth = ''
        self._dob_text = QLineEdit(self._date_of_birth)
        self._dob_text.setToolTip('Date of birth in the format YYYY,MM,DD\nFor BC enter negative years.\nAllowed Year Range: -13000 (BC) to 16800 (AD)')
        self._dob_label.setMaximumWidth(_row3_widget_width)
        self._dob_text.setMaximumWidth(_row3_widget_width)
        self._row1_h_layout.addWidget(self._dob_text)
        self._tob_label = QLabel("Time of Birth:")
        self._row1_h_layout.addWidget(self._tob_label)
        self._time_of_birth = ''
        self._tob_text = QLineEdit(self._time_of_birth)
        self._tob_text.setToolTip('Enter time of birth in the format HH:MM:SS if afternoon use 12+ hours')
        self._tob_label.setMaximumWidth(_row3_widget_width)
        self._tob_text.setMaximumWidth(_row3_widget_width)
        current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
        self.date_of_birth(current_date_str)
        self.time_of_birth(current_time_str)
        self._row1_h_layout.addWidget(self._tob_text)
        self._place_label = QLabel("Place:")
        self._row1_h_layout.addWidget(self._place_label)
        self._place_name = ''
        self._place_text = QLineEdit(self._place_name)
        self._world_cities_list = utils.world_cities_list
        completer = QCompleter(self._world_cities_list)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self._place_text.setCompleter(completer)
        self._place_text.textChanged.connect(self._resize_place_text_size)
        self._place_text.editingFinished.connect(lambda : self._get_location(self._place_text.text()))
        self._place_text.setToolTip('Enter place of birth, country name')
        self._row1_h_layout.addWidget(self._place_text)
        self._lat_label = QLabel("Latidude:")
        self._row1_h_layout.addWidget(self._lat_label)
        self._lat_text = QLineEdit('')
        self._latitude = 0.0
        self._lat_text.setToolTip('Enter Latitude preferably exact at place of birth: Format: +/- xx.xxx')
        self._row1_h_layout.addWidget(self._lat_text)
        self._long_label = QLabel("Longitude:")
        self._row1_h_layout.addWidget(self._long_label)
        self._long_text = QLineEdit('')
        self._longitude = 0.0
        self._long_text.setToolTip('Enter Longitude preferably exact at place of birth. Format +/- xx.xxx')
        self._row1_h_layout.addWidget(self._long_text)
        self._tz_label = QLabel("Time Zone:")
        self._row1_h_layout.addWidget(self._tz_label)
        self._tz_text = QLineEdit('')
        self._time_zone = 0.0
        self._tz_text.setToolTip('Enter Time offset from GMT e.g. -5.5 or 4.5')
        self._row1_h_layout.addWidget(self._tz_text)
        " Initialize with default place based on IP"
        loc = utils.get_place_from_user_ip_address()
        if len(loc)==4:
            self.place(loc[0],loc[1],loc[2],loc[3])
        self._v_layout.addLayout(self._row1_h_layout)
    def _create_row_2_ui(self):
        self._row2_h_layout = QHBoxLayout()
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(available_languages.keys())
        self._lang_combo.setCurrentText(self._language)
        self._lang_combo.setToolTip('Choose language for display')
        self._lang_combo.activated.connect(self._update_main_window_label_and_tooltips)
        self._row2_h_layout.addWidget(self._lang_combo)
        self._ayanamsa_combo = QComboBox()
        self._ayanamsa_combo.addItems(_available_ayanamsa_modes)
        self._ayanamsa_mode = const._DEFAULT_AYANAMSA_MODE
        self._ayanamsa_combo.setCurrentText(self._ayanamsa_mode)
        self._ayanamsa_combo.activated.connect(self._ayanamsa_selection_changed)
        self._ayanamsa_combo.setToolTip('Choose Ayanamsa mode from the list')
        self._ayanamsa_value = None
        self._row2_h_layout.addWidget(self._ayanamsa_combo)
        self._compute_button = QPushButton("Show Chart")
        self._compute_button.setFont(QtGui.QFont("Arial Bold",9))
        self._compute_button.clicked.connect(lambda: self.compute_horoscope(calculation_type=self._calculation_type))
        self._compute_button.setToolTip('Click to update the chart information based on selections made')
        self._row2_h_layout.addWidget(self._compute_button)
        self._save_image_button = QPushButton("Save as PDF")
        self._save_image_button.setFont(QtGui.QFont("Arial Bold",8))
        self._save_image_button.clicked.connect(lambda : self.save_as_pdf(pdf_file_name=None))
        self._save_image_button.setToolTip('Click to save horoscope as a PDF')
        self._row2_h_layout.addWidget(self._save_image_button)
        self._save_city_button = QPushButton("Save City")
        self._save_city_button.clicked.connect(self._save_city_to_database)
        self._save_city_button.setToolTip('Click to save the city information in csv database')
        self._row2_h_layout.addWidget(self._save_city_button)
        self._v_layout.addLayout(self._row2_h_layout)
    def _add_footer_to_chart(self):
        self._footer_label = QLabel('')
        self._footer_label.setTextFormat(Qt.TextFormat.RichText)
        self._footer_label.setText(self._footer_title)
        self._footer_label.setStyleSheet("border: 1px solid black;")
        self._footer_label.setFont(QtGui.QFont("Arial Bold",_footer_label_font_height))
        self._footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer_label.setFixedHeight(_footer_label_height)
        self._footer_label.setFixedWidth(self.width())
        self._footer_label.setWordWrap(True)
        self._footer_label.setOpenExternalLinks(True)
        self._v_layout.addWidget(self._footer_label)
    def _on_application_exit(self):
        def except_hook(cls, exception, traceback):
            sys.__excepthook__(cls, exception, traceback)
        sys.excepthook = except_hook
        QApplication.quit()
    def _ayanamsa_selection_changed(self):
        self._ayanamsa_mode = self._ayanamsa_combo.currentText().upper()
        drik.set_ayanamsa_mode(self._ayanamsa_mode)
        const._DEFAULT_AYANAMSA_MODE = self._ayanamsa_mode
    def ayanamsa_mode(self, ayanamsa_mode, ayanamsa=None):
        """
            Set Ayanamsa mode
            @param ayanamsa_mode - Default - Lahiri
            See 'drik.available_ayanamsa_modes' for the list of available models
        """
        if ayanamsa_mode.upper() in const.available_ayanamsa_modes.keys():
            self._ayanamsa_mode = ayanamsa_mode
            self._ayanamsa_value = ayanamsa
            self._ayanamsa_combo.setCurrentText(ayanamsa_mode)
            const._DEFAULT_AYANAMSA_MODE = self._ayanamsa_mode
    def place(self,place_name,latitude,longitude,timezone_hrs):
        """
            Set the place of birth
            @param - place_name - Specify with country code. e.g. Chennai, IN
            NOTE: Uses Nominatim to get the latitude and longitude
            An error message displayed if lat/long could not be found in which case enter lat/long manually.
            Also NOTE: calling latitude() or longitude() will replace the lat/long values added already
        """
        self._place_name = place_name
        self._latitude = latitude; self._longitude = longitude
        self._time_zone = timezone_hrs
        self._place_text.setText(self._place_name)
        self._lat_text.setText(str(self._latitude))
        self._long_text.setText(str(self._longitude))
        self._tz_text.setText(str(self._time_zone))
        """
        if self._latitude==0.0 or self._longitude==0.0 or self._time_zone==0.0:
            print('place missing lat/long/tz trying to get from location')
            result = utils.get_location(place_name)
            if result == None or len(result)==0:
                return
            [self._place_name,self._latitude,self._longitude,self._time_zone] = result
            self._lat_text.setText(str(self._latitude))
            self._long_text.setText(str(self._longitude))
            self._tz_text.setText(str(self._time_zone))
        """
    def latitude(self,latitude):
        """
            Sets the latitude manually
            @param - latitude
        """
        self._latitude = float(latitude)
        self._lat_text.setText(str(latitude))
    def longitude(self,longitude):
        """
            Sets the longitude manually
            @param - longitude
        """
        self._longitude = float(longitude)
        self._long_text.setText(str(longitude))
    def time_zone(self,time_zone):
        """
            Sets the time zone offset manually
            @param - time_zone - time zone offset
        """
        self._time_zone = float(time_zone)
        self._tz_text.setText(str(time_zone))
    def date_of_birth(self, date_of_birth):
        """
            Sets the Date of birth (Format:YYYY,MM,DD)
            @param - date_of_birth
        """
        self._date_of_birth = date_of_birth
        self._dob_text.setText(self._date_of_birth)
    def time_of_birth(self, time_of_birth):
        """
            Sets the time of birth (Format:HH:MM:SS)
            @param - time_of_birth
        """
        self._time_of_birth = time_of_birth
        self._tob_text.setText(self._time_of_birth)
    def language(self,language):
        """
            Sets the language for display
            @param - language
        """
        if language in available_languages.keys():
            self._language = language
            self._lang_combo.setCurrentText(language)
    def _validate_ui(self):
        all_data_ok = self._place_text.text().strip() != '' and \
                         re.match(r"[\+|\-]?\d+\.\d+\s?", self._lat_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"[\+|\-]?\d+\.\d+\s?", self._long_text.text().strip(),re.IGNORECASE) and \
                         re.match(r"[\+|\-]?\d{1,5}\,\d{1,2}\,\d{1,2}", self._dob_text.text().strip(),re.IGNORECASE)
        return all_data_ok
    def _update_main_window_label_and_tooltips(self):
        try:
            if self.resources:
                msgs = self.resources
                self._place_label.setText(msgs['place_str'])
                self._place_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._place_label.setToolTip(msgs['place_tooltip_str'])
                self._lat_label.setText(msgs['latitude_str'])
                self._lat_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._lat_label.setToolTip(msgs['latitude_tooltip_str'])
                self._long_label.setText(msgs['longitude_str'])
                self._long_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._long_label.setToolTip(msgs['longitude_tooltip_str'])
                self._tz_label.setText(msgs['timezone_offset_str'])
                self._tz_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._tz_label.setToolTip(msgs['timezone_tooltip_str'])
                self._dob_label.setText(msgs['date_of_birth_str'])
                self._dob_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._dob_label.setToolTip(msgs['dob_tooltip_str'])
                self._tob_label.setText(msgs['time_of_birth_str'])
                self._tob_label.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._tob_label.setToolTip(msgs['tob_tooltip_str'])
                _language_index = self._lang_combo.currentIndex()
                self._lang_combo.clear()
                self._lang_combo.addItems([msgs[l.lower()+'_str'] for l in const.available_languages.keys()])
                self._lang_combo.setCurrentIndex(_language_index)
                self._ayanamsa_combo.setToolTip(msgs['ayanamsa_tooltip_str'])
                self._ayanamsa_combo.setMaximumWidth(300)
                self._lang_combo.setToolTip(msgs['language_tooltip_str'])
                self._compute_button.setText(msgs['show_chart_str'])
                self._compute_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._compute_button.setToolTip(msgs['compute_tooltip_str'])
                self._save_image_button.setText(msgs['save_pdf_str'])
                self._save_image_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._save_image_button.setToolTip(msgs['savepdf_tooltip_str'])
                self._save_city_button.setText(msgs['save_city_str'])
                self._save_city_button.setStyleSheet('font-size:'+str(_main_ui_label_button_font_size)+'pt')
                self._save_city_button.setToolTip(msgs['savecity_tooltip_str'])
                self._footer_label.setText(msgs['window_footer_title'])
                self.setWindowTitle(msgs['window_title']+'-'+_APP_VERSION)
                self._update_combos()
                self.update()
                print('UI Language change to',self._language,'completed')
        except:
            print('Some error happened during changing to',self._language,' language and displaying UI in that language.\n'+\
            'Please Check resources file:',const._DEFAULT_LANGUAGE_MSG_STR+available_languages[self._language]+'.txt')
            print(sys.exc_info())
    def _update_combos(self):
        pass
    def compute_horoscope(self, calculation_type='drik'):
        """
            Compute the horoscope based on details entered
            if details missing - error is displayed            
        """
        if not self._validate_ui():
            print('values are not filled properly')
            return
        self._place_name = self._place_text.text()
        self._latitude = float(self._lat_text.text())
        self._longitude = float(self._long_text.text())
        self._time_zone = float(self._tz_text.text())
        self._language = list(const.available_languages.keys())[self._lang_combo.currentIndex()]
        year,month,day = self._date_of_birth.split(",")
        birth_date = drik.Date(int(year),int(month),int(day))
        self._time_of_birth = self._tob_text.text()
        self._ayanamsa_mode =  self._ayanamsa_combo.currentText()
        ' set the chart type and reset widgets'
        #self._recreate_chart_tab_widgets()
        if self._place_name.strip() != '' and abs(self._latitude) > 0.0 and abs(self._longitude) > 0.0 and abs(self._time_zone) > 0.0:
            self._horo= main.Horoscope(place_with_country_code=self._place_name,latitude=self._latitude,longitude=self._longitude,timezone_offset=self._time_zone,
                                       date_in=birth_date,birth_time=self._time_of_birth,ayanamsa_mode=self._ayanamsa_mode,
                                       ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                       language=available_languages[self._language])
        else:
            self._horo= main.Horoscope(place_with_country_code=self._place_name,date_in=birth_date,birth_time=self._time_of_birth,
                                       ayanamsa_mode=self._ayanamsa_mode,ayanamsa_value=self._ayanamsa_value,calculation_type=calculation_type,
                                       language=available_languages[self._language])
        self._calendar_info = self._horo.calendar_info
        self.resources = self._horo.cal_key_list
        info_str = ''
        format_str = _KEY_VALUE_FORMAT_
        self._fill_panchangam_info(info_str, format_str)
        self.tabWidget.setCurrentIndex(0) # Switch First / Panchanga Tab
        self._update_main_window_label_and_tooltips()
        self._update_chart_ui_with_info()
        self.resize(self.minimumSizeHint())
        self.tabWidget.setFocus()
    def _recreate_chart_tab_widgets(self):
        self._v_layout.removeWidget(self.tabWidget)
        current_tab = self.tabWidget.currentIndex()
        self.tabWidget.deleteLater()
        self._footer_label.deleteLater()
        self.tabWidget = None
        self._init_tab_widget_ui()
        self.tabWidget.setCurrentIndex(current_tab)
    def _fill_panchangam_info(self, info_str,format_str):
        self._info_label1.setText( self._fill_information_label1(info_str, format_str))
        self._info_label2.setText( self._fill_information_label2(info_str, format_str))
        self._info_label3.setText( self._fill_information_label3(info_str, format_str))
        return
        info_str = self._fill_information_label1(info_str, format_str)
        info_str += self._fill_information_label2(info_str, format_str)
        # divide equally to three labels
        info_list = info_str.split('\n'); info_len = len(info_list); each_len = int(info_len/3)
        self._info_label1.setText('\n'.join(info_list[:each_len]))
        self._info_label2.setText('\n'.join(info_list[each_len:2*each_len]))
        self._info_label3.setText('\n'.join(info_list[2*each_len:]))
    def _fill_information_label1(self,info_str,format_str):
        jd = self._horo.julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        bt=self._horo.birth_time
        tob = bt[0]+bt[1]/60.0+bt[2]/3600.0
        jd_years = drik.next_solar_date(jd, place)
        yb, mb, db, hfb = utils.jd_to_gregorian(jd)
        yy, my, dy, hfy = utils.jd_to_gregorian(jd_years)
        self._date_text_dob =  '%04d-%02d-%02d' %(yb,mb,db)
        self._time_text_dob = utils.to_dms(hfb,as_string=True)
        self._date_text_years =  '%04d-%02d-%02d' %(yy,my,dy)
        self._time_text_years = utils.to_dms(hfy,as_string=True)
        self._lat_chart_text = utils.to_dms(self._latitude,is_lat_long='lat')
        self._long_chart_text = utils.to_dms(self._longitude,is_lat_long='long')
        self._timezone_text = '(GMT '+str(self._tz_text.text())+')'
        key = self.resources['vaaram_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = 'date_of_birth_str'
        info_str += format_str.format(self.resources[key],self._date_text_dob)
        key = 'time_of_birth_str'
        info_str += format_str.format(self.resources[key],self._time_text_dob)
        info_str += format_str.format(self.resources['udhayathi_str'], utils.udhayadhi_nazhikai(jd,place)[0])
        key = self.resources['tamil_month_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = self.resources['lunar_year_month_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = 'sunrise_str'
        sunrise_time = self._calendar_info[self.resources[key]]
        info_str += format_str.format(self.resources[key],sunrise_time)
        key = 'sunset_str'
        info_str += format_str.format(self.resources[key],self._calendar_info[self.resources[key]])
        key = 'nakshatra_str'
        info_str += format_str.format(self.resources[key],self._calendar_info[self.resources[key]])
        key = 'raasi_str'
        info_str += format_str.format(self.resources[key],self._calendar_info[self.resources[key]])
        key = 'tithi_str'
        info_str += format_str.format(self.resources[key],self._calendar_info[self.resources[key]])
        key = 'yogam_str'
        info_str += format_str.format(self.resources[key],self._calendar_info[self.resources[key]])
        key = 'karanam_str'
        info_str += format_str.format(self.resources[key],self._calendar_info[self.resources[key]])
        jd = self._horo.julian_day#V3.2.0
        key = self.resources['bhava_lagna_str']
        value = drik.bhava_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['hora_lagna_str']
        value = drik.hora_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['ghati_lagna_str']
        value = drik.ghati_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['vighati_lagna_str']
        value = drik.vighati_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['pranapada_lagna_str']
        value = drik.pranapada_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['indu_lagna_str']
        value = drik.indu_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['bhrigu_bindhu_lagna_str']
        value = drik.bhrigu_bindhu_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['kunda_lagna_str']
        value = drik.kunda_lagna(jd,place,divisional_chart_factor=1)
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        key = self.resources['sree_lagna_str']
        value = drik.sree_lagna(jd,place,divisional_chart_factor=1)
        jd = self._horo.julian_day # V3.1.9
        info_str += format_str.format(key, utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong')) #V2.3.1
        #key = self.resources['raasi_str']+'-'+self.resources['ascendant_str']
        #value = self._horoscope_info[key]
        value = drik.ascendant(jd, place)
        info_str += format_str.format(self.resources['ascendant_str'],utils.RAASI_LIST[value[0]] +' ' + utils.to_dms(value[1],is_lat_long='plong'))
        key = self.resources['raahu_kaalam_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = self.resources['kuligai_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = self.resources['yamagandam_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = self.resources['dhurmuhurtham_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = self.resources['abhijit_str']
        value = self._calendar_info[key]
        info_str += format_str.format(self.resources['vijaya_muhurtha_str'],value)
        nm = drik.nishita_muhurtha(jd, place)
        key = self.resources['nishitha_muhurtha_str']+' : '
        value = utils.to_dms(nm[0]) +' '+self.resources['starts_at_str']+ ' '+ utils.to_dms(nm[1]) + ' '+ self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        key = self.resources['moonrise_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = self.resources['moonset_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)        
        y,m,d,fh = utils.jd_to_gregorian(jd); dob = drik.Date(y,m,d); tob=utils.to_dms(fh,as_string=False)
        scd = drik.sahasra_chandrodayam(dob, tob, self._horo.Place)
        if scd is not None:
            key = self.resources['sahasra_chandrodhayam_str']+' '+self.resources['day_str']
            value = str(scd[0])+'-'+'{:02d}'.format(scd[1])+'-'+'{:02d}'.format(scd[2])\
                    #+' '+'{:02d}'.format(scd[3])+':'+'{:02d}'.format(scd[4])+':'+'{:02d}'.format(scd[5])
            info_str += format_str.format(key,value) #'%-40s%-40s\n' % (key,value)        
        ag = drik.amrita_gadiya(jd, place)
        key = self.resources['amritha_gadiya_str']
        value = utils.to_dms(ag[0])+' '+self.resources['starts_at_str']+' '+utils.to_dms(ag[1])+' '+self.resources['ends_at_str']
        info_str += format_str.format(key,value)        
        ag = drik.varjyam(jd, place)
        key = self.resources['varjyam_str']
        value = utils.to_dms(ag[0])+' '+self.resources['starts_at_str']+' '+utils.to_dms(ag[1])+' '+self.resources['ends_at_str']
        info_str += format_str.format(key,value)        
        if len(ag)>2:
            value += '&nbsp;&nbsp;'+utils.to_dms(ag[2])+' '+self.resources['starts_at_str']+' '+utils.to_dms(ag[3])+' '+self.resources['ends_at_str']
        ay = drik.anandhaadhi_yoga(jd, place)
        key = self.resources['anandhaadhi_yoga_str']
        value = self.resources['ay_'+const.anandhaadhi_yoga_names[ay[0]]+'_str']+' '+utils.to_dms(ay[1])+' '+self.resources['starts_at_str']
        info_str += format_str.format(key,value)
        key = self.resources['day_length_str']
        value = utils.to_dms(drik.day_length(jd, place)).replace(' AM','').replace(' PM','')+' '+self.resources['hours_str']
        info_str += format_str.format(key,value)
        key = self.resources['night_length_str']
        value = utils.to_dms(drik.night_length(jd, place)).replace(' AM','').replace(' PM','')+' '+self.resources['hours_str']
        info_str += format_str.format(key,value)
        key = self.resources['present_str']+' '+self.resources['triguna_str']
        tg = drik.triguna(jd, place)
        value = self.resources[const.triguna_names[tg[0]]+'_str']
        value += '&nbsp;&nbsp;'+utils.to_dms(tg[1])+' '+self.resources['starts_at_str']+' '+utils.to_dms(tg[2])+' '+self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        key = self.resources['present_str']+' '+self.resources['vivaha_chakra_palan']+' :'
        value = drik.vivaha_chakra_palan(jd, place)
        value = self.resources['vivaha_chakra_palan_'+str(value)]
        info_str += format_str.format(key,value)
        self._info_label1.setText(info_str)
        key = self.resources['tamil_yogam_str']+' : '
        tg = drik.tamil_yogam(jd, place)
        value = self.resources[const.tamil_yoga_names[tg[0]]+'_yogam_str']
        value += ' ('+self.resources[const.tamil_yoga_names[tg[3]]+'_yogam_str']+')' if tg[0] != tg[3] else '' 
        value += '&nbsp;&nbsp;'+utils.to_dms(tg[1])+' '+self.resources['starts_at_str']+' '+utils.to_dms(tg[2])+' '+self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        #self._info_label1.setText(info_str)
        return info_str
    def _fill_information_label2(self,info_str,format_str):
        header = _HEADER_FORMAT_
        jd = self._horo.julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        info_str = ''
        #if _SHOW_GOURI_PANCHANG_OR_SHUBHA_HORA==0:
        info_str += header.format(self.resources['daytime_str']+' '+self.resources['gauri_choghadiya_str']+':')
        gc = drik.gauri_choghadiya(self._horo.julian_day, self._horo.Place)
        _gc_types = ['gc_udvega_str','gc_chara_str','gc_laabha_str','gc_amrit_str','gc_kaala_str','gc_shubha_str','gc_roga_str']
        for g,(gt,st,et) in enumerate(gc):
            if g==9:info_str += header.format(self.resources['nighttime_str']+' '+self.resources['gauri_choghadiya_str']+':')
            key = '&nbsp;&nbsp;'+self.resources[_gc_types[gt]]
            value = st +' '+self.resources['starts_at_str']+ ' '+ et + ' '+ self.resources['ends_at_str']
            info_str += format_str.format(key,value)
        #else:
        info_str += header.format(self.resources['daytime_str']+' '+self.resources['shubha_hora_str']+':')
        gc = drik.shubha_hora(self._horo.julian_day, self._horo.Place)
        for g,(gt,st,et) in enumerate(gc):
            #if g == 12: break
            if g==12: info_str += header.format(self.resources['nighttime_str']+' '+self.resources['shubha_hora_str']+':')
            key = '&nbsp;&nbsp;'+utils.PLANET_NAMES[gt]+' '+self.resources['shubha_hora_'+str(gt)]
            value = st +' '+self.resources['starts_at_str']+ ' '+ et + ' '+ self.resources['ends_at_str']
            info_str += format_str.format(key,value)
        bad_panchakas = {1:'mrithyu',2:'agni',4:'raja',6:'chora',8:'roga'}
        self.panchaka_rahitha = drik.panchaka_rahitha(jd, place)
        info_str += header.format(self.resources['panchaka_rahitha_str']+' :')
        for prc,pr_beg,pr_end in self.panchaka_rahitha[:1]:
            key=self.resources['muhurtha_str']+' ('+self.resources['good_str']+') ' if prc==0 \
                    else self.resources[bad_panchakas[prc]+'_panchaka_str']
            value1 = utils.to_dms(pr_beg)+' '+utils.resource_strings['starts_at_str']
            value2 = utils.to_dms(pr_end)+' '+utils.resource_strings['ends_at_str']
            info_str += format_str.format(key,value1+' '+value2)
        self._info_label2.setStyleSheet("border: 1px solid black;"+' font-size:6pt')
        return info_str
    def _fill_information_label3(self,info_str,format_str):
        header = _HEADER_FORMAT_
        jd = self._horo.julian_day
        place = drik.Place(self._place_name,float(self._latitude),float(self._longitude),float(self._time_zone))
        info_str = ''
        bad_panchakas = {1:'mrithyu',2:'agni',4:'raja',6:'chora',8:'roga'}
        #info_str += header.format(self.resources['panchaka_rahitha_str']+' :')
        for prc,pr_beg,pr_end in self.panchaka_rahitha[1:]:
            key=self.resources['muhurtha_str']+' ('+self.resources['good_str']+') ' if prc==0 \
                    else self.resources[bad_panchakas[prc]+'_panchaka_str']
            value1 = utils.to_dms(pr_beg)+' '+utils.resource_strings['starts_at_str']
            value2 = utils.to_dms(pr_end)+' '+utils.resource_strings['ends_at_str']
            info_str += format_str.format(key,value1+' '+value2)
        tb = drik.thaaraabalam(jd, place, return_only_good_stars=True)
        info_str += header.format(self.resources['thaaraabalam_str']+' :')
        star_list = [utils.NAKSHATRA_LIST[t-1] for t in tb]; knt=6
        star_list = [' '.join(map(str, star_list[i:i + knt])) for i in range(0, len(star_list), knt)]
        for sl in star_list:
            info_str += format_str.format('',sl)
        cb = drik.chandrabalam(jd, place)
        info_str += header.format(self.resources['chandrabalam_str']+' :')
        star_list = [utils.RAASI_LIST[t-1] for t in cb]; knt=5
        star_list = [' '.join(map(str, star_list[i:i + knt])) for i in range(0, len(star_list), knt)]
        for sl in star_list:
            info_str += format_str.format('',sl)
        bm = drik.brahma_muhurtha(jd, place)
        key = self.resources['brahma_str']+' '+self.resources['muhurtha_str']+' : '
        value = utils.to_dms(bm[0]) +' '+self.resources['starts_at_str']+ ' '+ utils.to_dms(bm[1]) + ' '+ self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        bm = drik.godhuli_muhurtha(jd, place)
        key = self.resources['godhuli_muhurtha_str']+' : '
        value = utils.to_dms(bm[0]) +' '+self.resources['starts_at_str']+ ' '+ utils.to_dms(bm[1]) + ' '+ self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        ps,ms,ss = drik.sandhya_periods(jd, place)
        key = self.resources['pratah_sandhya_kaalam_str']+' : '
        value = utils.to_dms(ps[0]) +' '+self.resources['starts_at_str']+ ' '+ utils.to_dms(ps[1]) + ' '+ self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        key = self.resources['madhyaahna_sandhya_kaalam_str']+' : '
        value = utils.to_dms(ms[0]) +' '+self.resources['starts_at_str']+ ' '+ utils.to_dms(ms[1]) + ' '+ self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        key = self.resources['saayam_sandhya_kaalam_str']+' : '
        value = utils.to_dms(ss[0]) +' '+self.resources['starts_at_str']+ ' '+ utils.to_dms(ss[1]) + ' '+ self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        nm = drik.nishita_kaala(jd, place)
        key = self.resources['nishitha_kaala_str']+' : '
        value = utils.to_dms(nm[0]) +' '+self.resources['starts_at_str']+ ' '+ utils.to_dms(nm[1]) + ' '+ self.resources['ends_at_str']
        info_str += format_str.format(key,value)
        ulm = drik.udhaya_lagna_muhurtha(jd, place)
        info_str += header.format(self.resources['udhaya_lagna_str']+':')
        for ulr,ulb,ule in ulm:
            key = '&nbsp;&nbsp;'+utils.RAASI_LIST[ulr]+' : '
            ulb_str = utils.to_dms(ulb); ule_str=utils.to_dms(ule)
            value = ulb_str +' '+self.resources['starts_at_str']+ ' '+ ule_str + ' '+ self.resources['ends_at_str']
            info_str += format_str.format(key,value)
            
        jd = self._horo.julian_day
        dob = self._horo.Date
        tob = self._horo.birth_time
        place = self._horo.Place
        info_str += header.format(self.resources['vimsottari_str']+' '+self.resources['dhasa_str']+':')
        _vimsottari_dhasa_bhukti_info = self._horo._get_vimsottari_dhasa_bhukthi(dob, tob, place)
        _vim_balance = ':'.join(map(str,self._horo._vimsottari_balance))
        dhasa = [k for k,_ in _vimsottari_dhasa_bhukti_info][8].split('-')[0]
        value = _vim_balance; db_list = []
        key = '&nbsp;&nbsp;'+dhasa + ' '+self.resources['balance_str']
        db_list.append(key+' '+value)
        #info_str += format_str.format(key,value)
        dhasa = ''
        dhasa_end_date = ''
        di = 9
        for p,(k,v) in enumerate(_vimsottari_dhasa_bhukti_info):
            # get dhasa
            if (p+1) == di:
                dhasa = '&nbsp;&nbsp;'+k.split("-")[0]
            # Get dhasa end Date
            elif (p+1) == di+1:
                """ to account for BC Dates negative sign is introduced"""
                if len(v.split('-')) == 4:
                    _,year,month,day = v.split('-')
                    year = '-'+year
                else:
                    year,month,day = v.split('-')
                dd = day.split(' ')[0] # REMOVE TIME STRING FROM VIMSOTTARI DATES
                dhasa_end_date = year+'-'+month+'-'+str(int(dd)-1)+ ' '+self.resources['ends_at_str']
                db_list.append(dhasa+' '+dhasa_end_date)
                #info_str += format_str.format(dhasa, dhasa_end_date)
                di += 9
        db_list = [' '.join(map(str, db_list[i:i + 2])) for i in range(0, len(db_list), 2)]
        for sl in db_list:
            info_str += format_str.format('',sl)
        bs = pancha_paksha._get_birth_nakshathra(jd, place)
        paksha_index = pancha_paksha._get_paksha(jd, place)
        bird_index = pancha_paksha._get_birth_bird_from_nakshathra(bs,paksha_index)
        key = self.resources['pancha_pakshi_sastra_str']+' '+self.resources['main_bird_str'].replace('\\n',' ')+' : '
        value = utils.resource_strings[pancha_paksha.pancha_pakshi_birds[bird_index-1]+'_str']
        info_str += format_str.format(key,value)
        key = self.resources['ayanamsam_str']+' ('+self._ayanamsa_mode+') '
        """ Need to call set_ayanamsa_mode before getting ayanamsa value V3.5.6 """
        drik.set_ayanamsa_mode(self._ayanamsa_mode)
        value = drik.get_ayanamsa_value(self._horo.julian_day)
        self._ayanamsa_value = value
        value = utils.to_dms(value,as_string=True,is_lat_long='lat').replace('N','').replace('S','')
        #print("horo_chart: Ayanamsa mode",key,'set to value',value)
        info_str += format_str.format(key,value)
        key = self.resources['kali_year_str']
        key_str = '<span style="color:'+_KEY_COLOR+';">'+key+'</span>'+' '
        value = '<span style="color:'+_VALUE_COLOR+';">'+str(self._calendar_info[key])+'</span>'+ ' '
        info_str += key_str+value
        key = self.resources['vikrama_year_str']
        key_str = '<span style="color:'+_KEY_COLOR+';">'+key+'</span>'+' '
        value = '<span style="color:'+_VALUE_COLOR+';">'+str(self._calendar_info[key])+'</span>'+ ' '
        info_str += key_str+value
        key = self.resources['saka_year_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        key = self.resources['calculation_type_str']
        value = self._calendar_info[key]
        info_str += format_str.format(key,value)
        #self._info_label2.setText(info_str)
        return info_str
    def _update_chart_ui_with_info(self):
        # Update Panchanga and Bhava tab names here
        for t in range(_tabcount_before_chart_tab):
            self.tabWidget.setTabText(t,self.resources[_tab_names[t]])
        self.update()
    def _reset_place_text_size(self):
        pt = 'Chennai'#self._place_text.text().split(',')[0]
        f = QFont("",0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._place_text.setFixedSize(pw,ph)
        self._place_text.adjustSize()
        self._place_text.selectionStart()
        self._place_text.setCursorPosition(0)
    def _resize_place_text_size(self):
        pt = self._place_text.text()
        f = QFont("",0)
        fm = QFontMetrics(f)
        pw = fm.boundingRect(pt).width()
        ph = fm.height()
        self._place_text.setFixedSize(pw,ph)
        self._place_text.adjustSize()       
    def _get_location(self,place_name):
        result = utils.get_location(place_name)
        print('RESULT',result)
        if result:
            self._place_name,self._latitude,self._longitude,self._time_zone = result
            self._place_text.setText(self._place_name)
            self._lat_text.setText(str(self._latitude))
            self._long_text.setText(str(self._longitude))
            self._tz_text.setText(str(self._time_zone))
            print(self._place_name,self._latitude,self._longitude,self._time_zone)
        else:
            msg = place_name+" could not be found in OpenStreetMap.\nTry entering latitude and longitude manually.\nOr try entering nearest big city"
            print(msg)
            QMessageBox.about(self,"City not found",msg)
            self._lat_text.setText('')
            self._long_text.setText('')
        self._reset_place_text_size()
            
    def _save_city_to_database(self):
        if self._validate_ui():
            " add this data to csv file "
            tmp_arr = self._place_name.split(',')
            country = 'N/A'
            city = tmp_arr[0]
            if len(tmp_arr) > 1:
                country = tmp_arr[1:]
            location_data = [country,city,self._latitude,self._longitude,country,self._time_zone]
            utils.save_location_to_database(location_data)
        return          
    def save_as_pdf(self,pdf_file_name=None):
        """
            Save the displayed chart as a pdf
            Choose a file from file save dialog displayed
        """
        image_prefix = 'pdf_grb_'
        image_ext = '.png'
        if pdf_file_name==None:
            path = QFileDialog.getSaveFileName(self, 'Choose folder and file to save as PDF file', './output', 'PDF files (*.pdf)')#)
            pdf_file_name = path[0]
        image_files = []
        combined_image_files = []
        image_id = 1
        def __save_scrollable_list_widget_as_image(widget:QWidget,image_id, image_files,_row_steps=1,widget_is_combo=False,row_count_size=None):
            """ TODO: Annual Dhasa count is not coming correct. Annual Dhasa is repeatedly printed by rasi/graha dhasa count times """
            _sleep_time = 0.01
            scroll_tab_count = 0
            import time; 
            row_count = widget.count() if row_count_size==None else row_count_size
            for row in range(0,row_count,_row_steps):
                self._hide_show_even_odd_pages(image_id)
                if widget_is_combo:
                    widget.setCurrentIndex(row)
                    if widget == self._dhasa_combo:
                        self._dhasa_type_selection_changed()                 
                else:
                    widget.setCurrentRow(row)
                image_file = _images_path+image_prefix+str(image_id)+image_ext
                time.sleep(_sleep_time)
                im = self.grab()
                im.save(image_file) 
                image_files.append(image_file)
                image_id +=1
                scroll_tab_count += 1
            return image_id
        if pdf_file_name:
            self._hide_show_layout_widgets(self._row2_h_layout, False)
            for t in range(self.tabCount):
                self._hide_show_even_odd_pages(image_id)
                self.tabWidget.setCurrentIndex(t)
                self._show_only_tab(t)
                image_file = _images_path+image_prefix+str(image_id)+image_ext
                image_files.append(image_file)
                im = self.grab()
                im.save(image_file) 
                image_id +=1
            self._reset_all_ui()
            ci = 1
            for i in range(0,len(image_files),_IMAGES_PER_PDF_PAGE):
                combined_image_file = _images_path+'combined_'+str(ci)+image_ext
                _combine_multiple_images(image_files[i:i+2],combined_image_file)
                combined_image_files.append(combined_image_file)
                ci += 1
            with open(pdf_file_name,"wb") as f:
                f.write(img2pdf.convert(combined_image_files))
            f.close()
        for image_file in image_files+combined_image_files:
            if os.path.exists(image_file):
                os.remove(image_file)
    def _reset_all_ui(self):
        self._hide_show_layout_widgets(self._row1_h_layout, True)
        self._hide_show_layout_widgets(self._row2_h_layout, True)
        self._footer_label.show()
        for t in range(self.tabCount): # reset all tabs to visible
            self.tabWidget.setTabVisible(t,True)
        
    def _hide_show_even_odd_pages(self,image_id):
        if image_id % 2 == 0: # Even Page
            self._hide_show_layout_widgets(self._row1_h_layout, False)
            self._hide_show_layout_widgets(self._row2_h_layout, False)
            self._footer_label.show()
        else:
            self._hide_show_layout_widgets(self._row1_h_layout, True)
            if image_id==1:
                self._hide_show_layout_widgets(self._row2_h_layout, True)
            self._footer_label.hide()        
    def _hide_show_layout_widgets(self,layout,show):
        for index in range(layout.count()):
            myWidget = layout.itemAt(index).widget()
            if show:
                myWidget.show()
            else:
                myWidget.hide()
            index -=1            
    def exit(self):
        self.close()
        QApplication.quit()
        print('Application Closed')
    def _show_only_tab(self,t): #set onlt tab t to be visible
        for ti in range(self.tabCount):
            self.tabWidget.setTabVisible(ti,False)
            if t==ti:
                self.tabWidget.setTabVisible(ti,True)
def show_horoscope(data):
    """
        Same as class method show() to display the horoscope
        @param data - last chance to pass the data to the class
    """
    app=QApplication(sys.argv)
    window=ChartTabbed(data)
    window.show()
    app.exec_()
def _index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
            return i
    return -1
def _combine_multiple_images(image_list,output_image,combine_mode='vertical',image_quality_in_pixels=100):
    total_width = 0
    total_height = 0
    max_width = 0
    max_height = 0
    ix =[]
    for img in image_list:
        im = Image.open(img)
        size = im.size
        w = size[0]
        h = size[1]
        total_width += w 
        total_height += h
        
        if h > max_height:
            max_height = h
        if w > max_width:
            max_width = w
        ix.append(im) 
    if combine_mode.lower()=='vertical':
        target = Image.new('RGB', (max_width, total_height))
    else:
        target = Image.new('RGB', (total_width, max_height))
    pre_w = 0
    pre_h = 0
    for img in ix:
        if combine_mode.lower()=='vertical':
            target.paste(img, (pre_w, pre_h, pre_w+max_width, pre_h + img.size[1]))
            pre_h += img.size[1]
        else:
            target.paste(img, (pre_w, pre_h, pre_w+img.size[0], pre_h + img.size[1]))
            pre_w += img.size[0]            
    target.save(output_image, quality=image_quality_in_pixels)
if __name__ == "__main__":
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    chart = ChartTabbed()
    chart.language('Tamil')
    """
    chart.name('XXX')#'('Rama')
    chart.gender(1) #(0)
    chart.date_of_birth('1996,12,7')#('-5114,1,9')
    chart.time_of_birth('10:34:00')#('12:10:00')
    chart.place('Chennai, India',13.0878,80.2785,5.5)
    """
    chart.compute_horoscope()
    chart.show()
    sys.exit(App.exec())
