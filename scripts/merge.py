from __future__ import print_function
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import sys, os, itertools

from util import *

directory = sys.argv[1]
output_path = os.path.abspath(os.path.join(directory, 'merged.mp4'))

print('generating', output_path)

videos = []
for i in range(1, Num_cameras + 1):
    videos.append(read_video(get_data_path(directory, i, name_is_dir=True)))

def merge(videos):
    try:
        for i, frames in enumerate(itertools.izip(*videos)):
            row1 = np.concatenate(frames[0:2], axis=1)
            row2 = np.concatenate(frames[2:4], axis=1)
            row3 = np.concatenate(frames[4:6], axis=1)
            whole = np.concatenate((row1, row2, row3), axis=0)
            resized = cv2.resize(whole, (1280, 1440))
            yield resized
    except imageio.core.format.CannotReadFrameError:
        raise StopIteration()
        
output_video = merge(videos)
write_video(output_video, output_path)
