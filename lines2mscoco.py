#!/usr/bin/env python3

from __future__ import print_function, unicode_literals, division, absolute_import #in case you want to run in on python 2

import sys
import json

if len(sys.argv) <= 1 or sys.argv[1] in ('-h','--help'):
    print("Syntax: line2mscoco.py [files]",file=sys.stderr)
    sys.exit(0)

for filename in sys.argv[1:]:
    data = []
    with open(filename,'r',encoding='utf-8') as f:
        for i, line in enumerate(f):
            data.append({'image_id': str(i+1), 'caption': line.strip()})
    with open(filename.replace('.txt','') + '.json','w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
