from __future__ import print_function
import numpy as np
import matplotlib
matplotlib.use('Agg')
import cv2
import sys, os

from util import *

input_path = sys.argv[1]
camera_dir = sys.argv[2]
output_path = sys.argv[3]

camera_matrix = np.load(os.path.join(camera_dir, 'camera_matrix.npy'))
distortion_coef = np.load(os.path.join(camera_dir, 'distortion_coefficients.npy'))
new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coef, (Video_width, Video_height), 0)

if is_video(input_path):
    video = read_video(input_path)
else:
    video = [cv2.imread(input_path)]
    
def undistort_video(video, camera_matrix, distortion_coef, new_camera_matrix, roi):
    for i, frame in enumerate(video):
        if i % 10 == 0:
            print('Undistorted %s frames' % i)
#         x, y, w, h = roi
        yield cv2.undistort(frame, camera_matrix, distortion_coef, None, new_camera_matrix)
    
output_video = undistort_video(video, camera_matrix, distortion_coef, new_camera_matrix, roi)

if is_video(output_path):
    write_video(output_video, output_path)
else:
    cv2.imwrite(output_path, next(output_video))
