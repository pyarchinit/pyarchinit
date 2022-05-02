# -*- coding: utf-8 -*-
# filename: formats/sokkia_sdr33.py
# Copyright 2014 Stefano Costa <steko@iosa.it>
# Copyright 2021 enzo Cocca <enzo.ccc@gmail.com>
# This file is part of Total Open Station.

# Total Open Station is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# Total Open Station is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Total Open Station.  If not, see
# <http://www.gnu.org/licenses/>.

from . import Feature, Parser, Point


class FormatParser(Parser):

    def is_point(self, line) :
        if line[0:4] == ('69TM'):
            return True
        else:
            return False

    def get_point(self, line):
        try :
            id = str(line[4:20])
        except ValueError:
            id = int(line[4:20])
        y = float(line[20:36])  # Northing
        x = float(line[36:51])  # Easting
        z = float(line[51:68])  # Elevation

       
        if line[0:4] == '69TM':   # Measurement
            desc = line[68:84].strip()
        
        point = Point(x, y, z)
        feature = Feature(point, desc=desc, id=id)
        return feature