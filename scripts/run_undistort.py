from __future__ import print_function
import numpy as np
import cv2

import os, sys, itertools, pickle

from util import *
from config import *

series = ['staircase']
for serie in series:
    processes = []
    s_dir = Data + serie + '/'
    print('generating', serie)
    for c in range(1, Num_cameras + 1):
        input_file = get_data_path(serie, c)
        name = get_name(input_file)
        output_file = s_dir + 'calibrated/' + name + '.mp4'
        make_dir(s_dir + 'calibrated/')
        if os.path.exists(output_file):
            continue
        cmd = 'python %sundistort.py %s %s %s' % (Scripts, input_file, Calibration + str(c) + '/', output_file)
        processes.append(shell(cmd, wait=False))
    for process in processes:
        out, err = process.communicate()
        print(out)
        print(err)
    print('finished', serie)
    print()