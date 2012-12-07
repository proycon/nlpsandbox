#! /usr/bin/env python
# -*- coding: utf8 -*-

import lxml.etree
import sys

doc = lxml.etree.parse(sys.argv[1]).getroot()
for e in doc.xpath('//seg'):
    print e.text
    
    

