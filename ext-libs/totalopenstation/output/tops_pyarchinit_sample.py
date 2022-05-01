#! /usr/bin/env python
# -*- coding: utf-8 -*-
# filename: tops_csv.py
# Copyright 2021 Enzo Cocca <enzo.ccc@gmail.com>
# 
#
# This file is part of Total Open Station.
#
# Total Open Station is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Total Open Station is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Total Open Station.  If not, see
# <http://www.gnu.org/licenses/>.

import csv
import io

from . import Builder


class OutputFormat(Builder):

    """
    Exports points data in CSV format.

    ``data`` should be an iterable containing Feature objects.
    """

    def __init__(self, data):
        self.data = data
        self.output = io.StringIO()
        fieldnames = ['gid','id_campion', 'sito', 'point_name','dataz','cronologia','link_immag','sigla_camp','z','x','y']
        self.writer = csv.DictWriter(self.output, quoting=csv.QUOTE_NONNUMERIC, fieldnames=fieldnames)
        self.writer.writeheader()

    def process(self):

        for feature in self.data:
            row = {
                'id_campion': feature.id,
                #'tipo_camp': feature.desc,
                'x': feature.geometry.x,
                'y': feature.geometry.y
            }

            try:  # not all input formats include z coordinates
                row['z'] = feature.geometry.z
            except ValueError:
                row['z'] = ''

            # a few cases with simple yes/no logic
            for prop in ['point_name']:
                row[prop] = feature.properties.get(prop, '')  # empty string as default value

            self.writer.writerow(row)

        return self.output.getvalue()
