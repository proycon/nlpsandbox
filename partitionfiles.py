#!/usr/bin/env python3

import sys
import glob
import os
from shutil import copyfile


pattern = sys.argv[1]
size = int(sys.argv[2])
batch = 1
os.mkdir(str(batch))

for i, file in enumerate(glob.glob(pattern)):
    if (i+1) % size == 0:
        batch += 1
        os.mkdir(str(batch))
    print(i+1,batch,file,file=sys.stderr)
    if os.path.islink(file):
        os.symlink(os.readlink(file), str(batch) + "/" + os.path.basename(file))
    else:
        copyfile(file, str(batch) + "/" + os.path.basename(file))


