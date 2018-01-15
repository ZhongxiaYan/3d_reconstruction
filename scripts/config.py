import os

user = os.environ['USER']
if user == 'zxyan':
    Root = '/scratch/zxyan/bdd/'
elif user == 'hoaxingz':
    Root = '/mnt/c/Users/zhong/Desktop/bdd/'
Data = Root + 'data/'
Calibration = Root + 'calibration/'
Scripts = Root + 'scripts/'
Image_height, Image_width = 3000, 4000
Video_height, Video_width = 2032, 2704
Fps = 29.97
Num_cameras = 6
