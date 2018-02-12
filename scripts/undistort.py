from __future__ import print_function
import numpy as np
import matplotlib
matplotlib.use('Agg')
import cv2
import sys, os

from util import *
from putil import *

input_path = sys.argv[1]
camera_i = int(sys.argv[2])
output_path = sys.argv[3]

assert(camera_i in Cam_ids)

camera_matrix, distortion_coef, new_camera_matrix = load_calibration(camera_i)

if is_video(input_path):
    video = read_video(input_path)
else:
    video = [cv2.imread(input_path)]

output_video = (cv2.undistort(frame, camera_matrix, distortion_coef, None, new_camera_matrix) for frame in video)

if is_video(output_path):
    write_video(output_video, output_path)
else:
    cv2.imwrite(output_path, next(output_video))
