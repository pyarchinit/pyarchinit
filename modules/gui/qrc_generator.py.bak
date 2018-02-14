#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
untitled.py

Created by pyarchinit on 2008-03-30.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import os, sys



def main():
	(filepath, filename) = os.path.split(sys.argv[0])
	str_cmd = ('%s%s%s%s%s') % ('pyrcc4 -o ', filepath, '/resources_rc.py ', filepath, '/resources.qrc')
	print str_cmd
	os.system(str_cmd)

if __name__ == '__main__':
	main()
