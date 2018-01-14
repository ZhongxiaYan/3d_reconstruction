from __future__ import print_function
import numpy as np
import cv2

import os, itertools, pickle

from util import *
from config import *

series = ('cory_front', 'soda_front', 'lounge', 'cory_breezeway')
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
        cmd = 'python undistort.py %s %s %s' % (input_file, Calibration + str(c) + '/', output_file)
        processes.append(shell(cmd, wait=False))
    for process in processes:
        out, err = process.communicate()
        print(out)
        print(err)
    print('finished', serie)
    print()