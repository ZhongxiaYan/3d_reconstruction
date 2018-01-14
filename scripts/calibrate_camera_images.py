import numpy as np
import pandas as pd
import tensorflow as tf
import cv2
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
plt.style.use('ggplot')

import sys

from util import *
from config import *

from matplotlib.patches import Rectangle

class Annotate(object):
    def __init__(self, image):
        self.ax = plt.gca()
        self.ax.imshow(image)
        self.rect = Rectangle((0, 0), 1, 1)
        self.rect.fill = False
        self.x0 = self.y0 = self.x1 = self.y1 = None
        self.pressing = False
        self.ax.add_patch(self.rect)
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.motion)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.ax.figure.canvas.mpl_connect('key_press_event', self.on_key)
    
    def run(self):
        plt.show()

    def on_press(self, event):
        self.x0 = event.xdata
        self.y0 = event.ydata
        self.pressing = True
    
    def motion(self, event):
        if self.pressing:
            x1 = event.xdata
            y1 = event.ydata
            self.rect.set_width(x1 - self.x0)
            self.rect.set_height(y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            self.ax.figure.canvas.draw()

    def on_release(self, event):
        self.x1 = event.xdata
        self.y1 = event.ydata
        self.pressing = False
    
    def on_key(self, event):
        if event.key == 'enter' and a.x1:
            plt.close()

camera_dir = root_ + 'calibration/' + sys.argv[1] + '/'
corner_dir = camera_dir + 'corners/'
make_dir(corner_dir)
mtx_path = camera_dir + 'camera_matrix.npy'
dist_path = camera_dir + 'distortion_coefficients.npy'
if os.path.exists(mtx_path) and os.path.exists(dist_path):
    mtx = np.load(mtx_path)
    dist_coef = np.load(dist_path)
    print('Already have coefficients')
else:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    w, h = 9, 6
    objp = np.zeros((w * h, 3), np.float32)
    objp[:, :2] = np.mgrid[:w, :h].T.reshape(-1, 2)

    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane

    for img_path, img_name in list_dir(camera_dir, 'jpg', name=True):
        corner_path = corner_dir + img_name + '.npy'
        found_saved_corners = os.path.exists(corner_path)
        if found_saved_corners:
            saved_corners = np.load(corner_path)
            objpoints.append(objp)
            imgpoints.append(saved_corners)
            img = cv2.imread(img_path)
            corner_img = cv2.drawChessboardCorners(img, (w, h), saved_corners, True)
            plt.imshow(corner_img)
            plt.show()
            continue
        
        img = cv2.imread(img_path)
        done = False
        while not done:
            a = Annotate(img)
            a.run()
            x0, x1 = sorted([int(a.x0), int(a.x1)])
            y0, y1 = sorted([int(a.y0), int(a.y1)])

            img_slice = img[y0 : y1, x0 : x1]
            gray = cv2.cvtColor(img_slice, cv2.COLOR_BGR2GRAY)

            gray = clahe.apply(gray)

            ret, corners = cv2.findChessboardCorners(gray, (w, h))
            if ret:
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                corners += np.array([[[x0, y0]]])
                corner_img = cv2.drawChessboardCorners(img.copy(), (w, h), corners, True)

                print('number of corners', len(corners))
                plt.imshow(corner_img)
                plt.show()
            else:
                print('No chessboard found')
            while True:
                keep = input('keep?')
                if keep == 'y':
                    objpoints.append(objp)
                    imgpoints.append(corners)
                    np.save(corner_path, corners)
                    done = True
                    break
                elif keep == 'n':
                    done = True
                    os.remove(img_path)
                    break
                elif keep == 'r':
                    break
    
    ret, mtx, dist_coef, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (Image_width, Image_height), None, None, flags=cv2.CALIB_RATIONAL_MODEL)

    tot_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist_coef)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        tot_error += error

    print("total error:", tot_error / len(objpoints))

    np.save(mtx_path, mtx)
    np.save(dist_path, dist_coef)

newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist_coef, (Image_width, Image_height), 1)
if not any(roi):
    print('zeros for roi')
    exit()
for img_path, img_name in list_dir(camera_dir + 'test/', 'jpg', name=True):
    if 'undistorted' in img_name:
        continue
    img = cv2.imread(img_path)
    dst = cv2.undistort(img, mtx, dist_coef, None, newcameramtx)

    x, y, w, h = roi
    dst = dst[y : y + h, x : x + w]
    undistorted_path = '.'.join(img_path.split('.')[:-1] + ['undistorted', 'jpg'])
    cv2.imwrite(undistorted_path, dst)
    fig = plt.figure()
    for i, image in enumerate([img, dst]):
        plt.subplot(1, 2, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.imshow(image)
    fig.subplots_adjust(wspace=0, hspace=0)
    plt.show()
