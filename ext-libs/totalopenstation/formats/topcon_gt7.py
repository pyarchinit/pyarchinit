# -*- coding: utf-8 -*-
# filename: formats/topcon_gts.py
# Copyright 2021 ENZO COCCA <enzo.ccc@gmail.com>

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


from . import Feature, Parser, Point
import re
class FormatParser(Parser):
    
    
    def is_point(self, line) :
        return True
            
    
    def get_point(self, t):
        #t=t.replace(',','     ')
        for row in t.splitlines():
            
            if row.startswith('SS'):
                
                
            
                
                desc=row[8:15]
                id='PT'
            
            if row.startswith('SD'): 
                
                y=row[8:16].lstrip(',') # Northing
            
            
                
                x=row[16:24].lstrip(',')  # Easting
                
            
                
                z=row[24:-1].lstrip(',')# Elevation     
            
              
        try:    
            point = Point(x, y, z)
            f = Feature(point,desc=desc,id=id)
                
        except:
            pass
        else:
            return f
    
    def search(self):
        
        a=re.sub(r"-"," ", self.data)  
        return a
        
        # p = re.compile(r'\d+\.\d+')  # Compile a pattern to capture float values
        # floats = [float(i) for i in p.findall(self.data)]  # Convert strings to float
        # if len(floats)<=6:
            # return floats
    def split_points(self):
        
        
        a=re.split(',1.5300|,1.5400|,1.5500|,1.5600|,1.5700|,1.5800|,1.5900|,1.6000|,1.6100|,1.6200|,1.6300|,1.6400|,1.6500|,1.6600|,1.6700|,1.6800|,1.6900|,1.7000|,1.7100|,1.7200|,1.7300|,1.7400|,1.7500|,1.7600|,1.7700|,1.7800|,1.7900|,1.8000|,1.8100|,1.8200|,1.8300|,1.8400|,1.8500|,1.8600|,1.8700|,1.8800|,1.8900|,1.9000|,1.9100|,1.9200|,1.9300|,1.9400|,1.9500|,1.9600|,1.9700|,1.9800|,1.9900|,2.000|,2.010|,2.020|,2.030|,2.040|,2.050|,2.060|,2.070|,2.080|,2.090|,2.100|,2.110|,2.120|,2.130|,2.140|,2.150|,2.160|,2.170|,2.180|,2.190|,2.200|,2.210|,2.220|,2.230|,2.240|,2.250|,2.260|,2.270|,2.280|,2.290|,2.300|,2.310|,2.320|,2.330|,2.340|,2.350|,2.360|,2.370|,2.380|,2.390|,2.400|,2.410|,2.420|,2.430|,2.440|,2.450|,2.460|,2.470|,2.480|,2.490|,2.500',self.search())
        
        #splitted_points= self.data.rpartition(',')
            
        return a