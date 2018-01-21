import numpy as np
import os

user = os.environ['USER']
if user == 'zxyan':
    Root = '/scratch/zxyan/bdd/'
elif user == 'hoaxingz':
    Root = '/mnt/c/Users/zhong/Desktop/bdd/'
Data = Root + 'data/'
Calibrations = Root + 'calibrations/'
Reconstructions = Root + 'reconstructions/'
Scripts = Root + 'scripts/'
Video_hw = np.array([2028, 2704], dtype=int)
Video_wh = np.flip(Video_hw, axis=0)
Image_height, Image_width = 3000, 4000
Video_height, Video_width = Video_hw
Fps = 29.97
Num_cameras = 6
