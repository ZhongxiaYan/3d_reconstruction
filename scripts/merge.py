from __future__ import print_function
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2
import sys, os

from util import *

directory = sys.argv[1]
output_path = os.path.join(Data, directory, 'merged.mp4')

videos = []
for i in range(1, Num_cameras + 1):
    videos.append(read_video(get_data_path(directory, i)))

def merge(videos):
    for i, frames in enumerate(zip(*videos)):
        print('Merged %s frames' % i)
        row1 = np.concatenate(frames[0:3], axis=1)
        row2 = np.concatenate(frames[3:6], axis=1)
        whole = np.concatenate((row1, row2), axis=0)
        resized = cv2.resize(whole, (640, 480))
        plt.imshow(resized)
        plt.savefig('temp.png', format='png')
        yield resized

output_video = merge(videos)
write_video(output_video, output_path)
