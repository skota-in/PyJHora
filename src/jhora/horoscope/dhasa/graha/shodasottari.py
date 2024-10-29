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
from jhora import const, utils
from jhora.panchanga import drik
year_duration = const.sidereal_year
""" Applicability: Lagna in Sun's hora in Sukla paksha or Lagna in Moon's hora in Krishna paksha """

#seed_star = 8 # Poosam
seed_lord = 0 # Sun
dhasa_adhipathi_list = {0:11,2:12,4:13,6:14,8:15,1:16,3:17,5:18} #  Total 116 years
#dhasa_adhipathi_dict = {0:[8,16,24,5],2:[9,17,25,6],4:[10,18,26,7],6:[11,19,27],8:[12,20,1],1:[13,21,2],3:[14,22,3],5:[15,23,4]} 
count_direction = 1 # 1> base star to birth star zodiac -1> base star to birth star antizodiac
def _next_adhipati(lord):
    """Returns next lord after `lord` in the adhipati_list"""
    current = list(dhasa_adhipathi_list.keys()).index(lord)
    next_lord = list(dhasa_adhipathi_list.keys())[((current + 1) % len(dhasa_adhipathi_list))]
    return next_lord
def _get_dhasa_dict(seed_star=8):
    dhasa_dict = {k:[] for k in dhasa_adhipathi_list.keys()}
    nak = seed_star-1
    lord = seed_lord
    lord_index = list(dhasa_adhipathi_list.keys()).index(lord)
    for _ in range(27):
        dhasa_dict[lord].append(nak+1)
        nak = (nak+1*count_direction)%27
        lord_index = (lord_index+1) % len(dhasa_adhipathi_list)
        lord = list(dhasa_adhipathi_list.keys())[lord_index]
    return dhasa_dict
#dhasa_adhipathi_dict = _get_dhasa_dict()

def _maha_dhasa(nak,seed_star=8):
    dhasa_adhipathi_dict = _get_dhasa_dict(seed_star)
    return [(_dhasa_lord, dhasa_adhipathi_list[_dhasa_lord]) for _dhasa_lord,_star_list in dhasa_adhipathi_dict.items() if nak in _star_list][0]
def _antardhasa(lord):
    _bhukthis = []
    for _ in range(len(dhasa_adhipathi_list)):
        _bhukthis.append(lord)
        lord = _next_adhipati(lord)
    return _bhukthis
def _dhasa_start(jd,place,star_position_from_moon=1,divisional_chart_factor=1,chart_method=1,seed_star=8,
                 dhasa_starting_planet=1):
    y,m,d,fh = utils.jd_to_gregorian(jd); dob=drik.Date(y,m,d); tob=(fh,0,0)
    one_star = (360 / 27.)        # 27 nakshatras span 360°
    from jhora.horoscope.chart import charts,sphuta
    _special_planets = ['M','G','T','I','B','I','P']
    planet_positions = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
    if dhasa_starting_planet in [*range(9)]:
        planet_long = planet_positions[dhasa_starting_planet+1][1][0]*30+planet_positions[dhasa_starting_planet+1][1][1]
    elif dhasa_starting_planet==const._ascendant_symbol:
        planet_long = planet_positions[0][1][0]*30+planet_positions[0][1][1]
    elif dhasa_starting_planet.upper()=='M':
        mn = drik.maandi_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = mn[0]*30+mn[1]
    elif dhasa_starting_planet.upper()=='G':
        gl = drik.gulika_longitude(dob,tob,place,divisional_chart_factor=divisional_chart_factor)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='B':
        gl = drik.bhrigu_bindhu(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='I':
        gl = drik.indu_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='P':
        gl = drik.pranapada_lagna(jd, place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = gl[0]*30+gl[1]
    elif dhasa_starting_planet.upper()=='T':
        sp = sphuta.tri_sphuta(dob,tob,place,divisional_chart_factor=divisional_chart_factor,chart_method=chart_method)
        planet_long = sp[0]*30+sp[1]
    else:
        planet_long = planet_positions[2][1][0]*30+planet_positions[2][1][1]
    if dhasa_starting_planet==1:
        planet_long += (star_position_from_moon-1)*one_star
    nak = int(planet_long / one_star); rem = (planet_long - nak * one_star)
    lord,res = _maha_dhasa(nak+1,seed_star)          # ruler of current nakshatra
    period = res
    period_elapsed = rem / one_star * period # years
    period_elapsed *= year_duration        # days
    start_date = jd - period_elapsed      # so many days before current day
    return [lord, start_date,res]
def get_dhasa_bhukthi(dob,tob,place,include_antardhasa=True,star_position_from_moon=1,use_tribhagi_variation=False,
                      divisional_chart_factor=1,chart_method=1,seed_star=8,dhasa_starting_planet=1):
    """
        returns a dictionary of all mahadashas and their start dates
        @param jd: Julian day for birthdate and birth time
        @param place: Place as tuple (place name, latitude, longitude, timezone) 
        @param include_antardhasa True/False. Default=True 
        @param divisional_chart_factor Default=1 
            1=Raasi, 9=Navamsa. See const.division_chart_factors for options
        @param chart_method: Default=1, various chart methods available for each div chart. See charts module
        @param star_position_from_moon: 
            1 => Default - moon
            4 => Kshema Star (4th constellation from moon)
            5 => Utpanna Star (5th constellation from moon)
            8 => Adhana Star (8th constellation from moon)
        @param use_tribhagi_variation: False (default), True means dhasa bhukthi duration in three phases
        @param seed_star 1..27. Default = 8
        @param antardhasa_option: (Not applicable if use_rasi_bhukthi_variation=True)
            1 => dhasa lord - forward (Default)
            2 => dhasa lord - backward
            3 => next dhasa lord - forward
            4 => next dhasa lord - backward
            5 => prev dhasa lord - forward
            6 => prev dhasa lord - backward
        @param dhasa_starting_planet 0=Sun 1=Moon(default)...8=Ketu, 'L'=Lagna
                                    M=Maandi, G=Gulika, T=Trisphuta, B=Bhindu, I=Indu, P=Pranapada
        @return: a list of [dhasa_lord,bhukthi_lord,bhukthi_start]
          Example: [ [7, 5, '1915-02-09'], [7, 0, '1917-06-10'], [7, 1, '1918-02-08'],...]
    """
    _tribhagi_factor = 1.
    _dhasa_cycles = 1
    if use_tribhagi_variation:
        _tribhagi_factor = 1./3.; _dhasa_cycles = int(_dhasa_cycles/_tribhagi_factor)
    jd = utils.julian_day_number(dob, tob)
    dhasa_lord, start_jd,_ = _dhasa_start(jd,place,star_position_from_moon=star_position_from_moon,
                                          divisional_chart_factor=divisional_chart_factor,chart_method=chart_method,
                                          seed_star=seed_star,dhasa_starting_planet=dhasa_starting_planet)
    retval = []
    for _ in range(_dhasa_cycles):
        for _ in range(len(dhasa_adhipathi_list)):
            _dhasa_duration = round(dhasa_adhipathi_list[dhasa_lord]*_tribhagi_factor,2)
            if include_antardhasa:
                bhukthis = _antardhasa(dhasa_lord)
                _dhasa_duration /= len(bhukthis)
                for bhukthi_lord in bhukthis:
                    y,m,d,h = utils.jd_to_gregorian(start_jd)
                    dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                    retval.append((dhasa_lord,bhukthi_lord,dhasa_start,_dhasa_duration))
                    start_jd += _dhasa_duration * year_duration
            else:
                y,m,d,h = utils.jd_to_gregorian(start_jd)
                dhasa_start = '%04d-%02d-%02d' %(y,m,d) +' '+utils.to_dms(h, as_string=True)
                retval.append((dhasa_lord,dhasa_start,_dhasa_duration))
                lord_duration = round(dhasa_adhipathi_list[dhasa_lord]*_tribhagi_factor,2)
                start_jd += lord_duration * year_duration
            dhasa_lord = _next_adhipati(dhasa_lord)
    return retval
if __name__ == "__main__":
    from jhora.tests import pvr_tests
    utils.set_language('en')
    pvr_tests._STOP_IF_ANY_TEST_FAILED = False
    pvr_tests.shodasottari_test()
    