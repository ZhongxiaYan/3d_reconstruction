import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2, imageio

import os, itertools, subprocess, pickle

from util import *
from config import *

# cv2.imread(image_path)
# cv2.imwrite(image_path, image)

def show_group(group):
    images = [mpimg.imread(file) for file in group]
    fig = plt.figure(figsize=(12, 14))
    for i, image in enumerate(images):
        plt.subplot(3, 2, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.imshow(image)
    fig.subplots_adjust(wspace=0, hspace=0)
    plt.show()

def save_calibration(camera_i, camera_matrix, distortion_coefficients, new_camera_matrix):
    cam_dir = Calibrations + str(camera_i) + '/'
    np.savetxt(cam_dir + 'camera_matrix.txt', camera_matrix)
    np.savetxt(cam_dir + 'distortion_coefficients.txt', distortion_coefficients)
    np.savetxt(cam_dir + 'new_camera_matrix.txt', new_camera_matrix)

def load_calibration(camera_i):
    cam_dir = Calibrations + str(camera_i) + '/'
    if not os.path.exists(cam_dir + 'new_camera_matrix.txt'):
        return None
    return (
        np.genfromtxt(cam_dir + 'camera_matrix.txt'),
        np.genfromtxt(cam_dir + 'distortion_coefficients.txt'),
        np.genfromtxt(cam_dir + 'new_camera_matrix.txt')
    )

def load_camera_matrix(camera_i):
    cam_dir = Calibrations + str(camera_i) + '/'
    if not os.path.exists(cam_dir + 'new_camera_matrix.txt'):
        return None
    return np.genfromtxt(cam_dir + 'new_camera_matrix.txt')
    
def get_name(path):
    return os.path.splitext(os.path.basename(path))[0]

def get_data_path(data_name, camera, name_is_dir=False):
    assert 1 <= camera <= Num_cameras
    dir_ = data_name
    if not name_is_dir:
        dir_ = os.path.join(Data, data_name)
    for name, path in list_dir(dir_, 'mp4', return_name=True):
        if name.startswith('A00%s' % camera):
            return path
    raise RuntimeException('File not found')
    
def is_video(path):
    return path.split('.')[-1].lower() in ['mp4']

def read_video(video_path, multithreaded=False):
    if multithreaded:
        def iterator():
            fvs = FileVideoStream(get_data_path('pool_room', 1)).start()
            while fvs.more():
                yield fvs.read()
        return iterator
    else:
        return imageio.get_reader(video_path)

def write_video(video, output_path):
    writer = imageio.get_writer(output_path, fps=Fps, macro_block_size=None)
    for f in video:
        writer.append_data(f)
    writer.close()
    
def video_to_frames(video_path, output_dir, nth=1, return_name=False, start=None, duration=None):
    make_dir(output_dir)
    name = get_name(video_path)
    cmd = 'ffmpeg'
    if start is not None:
        cmd += ' -ss %s' % start
    cmd += ' -i %s' % video_path
    if duration is not None:
        cmd += ' -t %s' % duration
    cmd += ' -threads 4 -filter:v "select=not(mod(n\,%s))" %s/%s_%%04d.jpg -frames:v 1 -vsync vfr' % (nth, output_dir, name)
    print(cmd)
    shell(cmd)
    return list_dir(output_dir, 'jpg', return_name=return_name)

def frames_to_video(frame_dir, video_output, frame_prefix=''):
    cmd = 'ffmpeg -r %s -f image2 -s %sx%s -i %s/%s%%*.jpg -threads 4 -vcodec libx264 -crf 25 -pix_fmt yuv420p %s' % (Fps, Video_width, Video_height, frame_dir, frame_prefix, video_output)
    shell(cmd)
    # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    # writer = cv2.VideoWriter(video_output, fourcc, Fps, (Video_width, Video_height))
    # for frame_path in frame_paths:
    #     frame = cv2.imread(frame_path)
    #     writer.write(frame)
    # writer.release()

def cut_video(original_file, new_file, start_time, duration):
    '''
    start_time and duraction in format hh:mm:ss
    '''
    shell('ffmpeg -ss %s -i %s -t %s -vcodec copy -acodec copy %s' % (start_time, original_file, duration, new_file))

from Queue import Queue
from threading import Thread, Semaphore, Condition

class FileVideoStream:
    def __init__(self, path, queueSize=128):
        self.stream = cv2.VideoCapture(path)
        self.Q = Queue(maxsize=queueSize)
        self.dequeuer_sema = Semaphore(0)
        self.enqueuer_cv = Condition()
        self.stopped = False
    
    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    
    def update(self):
        success, frame = self.stream.read()

        num_consecutive_fails = 0
        while num_consecutive_fails < 3:
            if success:
                self.enqueuer_cv.acquire()
                if self.Q.full():
                    self.enqueuer_cv.wait()
                self.enqueuer_cv.release()
                num_consecutive_fails = 0
                self.Q.put(frame)
                self.dequeuer_sema.release()
            else:
                num_consecutive_fails += 1
            
            success, frame = self.stream.read()
        self.stopped = True
        self.dequeuer_sema.release()
        
    def read(self):
        self.enqueuer_cv.acquire()
        frame = self.Q.get()
        self.enqueuer_cv.notify()
        self.enqueuer_cv.release()
        return frame
    
    def more(self):
        self.dequeuer_sema.acquire()
        return not self.stopped or self.Q.qsize() > 0
