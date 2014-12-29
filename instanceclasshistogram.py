#!/usr/bin/env python3

from __future__ import print_function, unicode_literals, division, absolute_import

import glob
from collections import defaultdict

hist_instances = defaultdict(int)
hist_classes = defaultdict(int)

for filename in glob.glob("*.train"):
    with open(filename,'r',encoding='utf-8') as f:
        instances = 0
        classes = defaultdict(int)
        for line in f:
            if line:
                instances += 1
                classes[line.split("\t")[-1]] += 1
        hist_instances[instances] += 1
        hist_classes[len(classes)] += 1


with open("instances_histogram.dat",'w') as f:
    for c, freq in sorted(hist_instances.items(), key=lambda x: -1 * x[1]):
        print(str(c) + "\t" + str(freq),file=f)

with open("classes_histogram.dat",'w') as f:
    for c, freq in sorted(hist_classes.items(), key=lambda x: -1 * x[1]):
        print(str(c) + "\t" + str(freq),file=f)


