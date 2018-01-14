import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2, imageio

import os, itertools, subprocess, pickle

from config import *

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

def get_name(path):
    return '.'.join(path.split('/')[-1].split('.')[:-1])
        
def get_data_path(data_name, camera):
    assert 1 <= camera <= Num_cameras
    for name, path in list_dir(Data + data_name + '/', 'mp4', return_name=True):
        if name.startswith('A00%s' % camera):
            return path
    raise RuntimeException('File not found')
    
def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def save_pickle(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
    
def is_video(path):
    return path.split('.')[-1].lower() in ['mp4']
    
def read_video(video_path):
    return imageio.get_reader(video_path)

def write_video(video, output_path):
    writer = imageio.get_writer(output_path, fps=Fps)
    for f in video:
        writer.append_data(f)
    writer.close()
    
def video_to_frames(video_path, output_dir, nth=1, return_name=False):
    make_dir(output_dir)
    name = get_name(video_path)
    cmd = 'ffmpeg -i %s -threads 4 -filter:v "select=not(mod(n\,%s))" %s/%s_%%04d.jpg -frames:v 1 -vsync vfr' % (video_path, nth, output_dir, name)
    shell(cmd)
    return list_dir(output_dir, 'jpg', return_name=return_name)
    # video = cv2.VideoCapture(video_path)
    # success, image = video.read()
    # frame_paths = []
    # success = True
    # make_dir(output_dir)
    # index = 0
    # num_fail = 0
    # while num_fail < 30:
    #     if success:
    #         name = get_name(video_path)
    #         frame_paths.append(output_dir + '%s_%04d.jpg' % (name, index))
    #         cv2.imwrite(frame_paths[-1], image)
    #         num_fail = 0
    #     else:
    #         num_fail += 1
    #     index += nth
    #     if nth > 1:
    #         video.set(1, index)
    #     success, image = video.read()
    # video.release()

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

def list_dir(dir, ext, return_name=False):
    ext = '.' + ext.lower()
    if return_name:
        return sorted([(file[:-len(ext)], dir + file) for file in os.listdir(dir) if file[-len(ext):].lower() == ext])
    else:
        return sorted([dir + file for file in os.listdir(dir) if file[-len(ext):].lower() == ext])

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def remove(path):
    if not os.path.exists(path):
        return
    elif os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path)
        
def extract(input_path, output_path=None):
    if input_path[-3:] == '.gz':
        if not output_path:
            output_path = input_path[:-3]
        with gzip.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
    else:
        raise RuntimeError('Don\'t know file extension for ' + input_path)

def get_temp_file(ext, N=10):
    return Temp + '_temp' + ''.join(random.sample(string.digits, k=N)) + ext

def get_temp_dir(N=10):
    return get_temp_file('/', N)

def shell(cmd, wait=True, ignore_error=True):
    if type(cmd) != str:
        cmd = ' '.join(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not wait:
        return process
    out, err = process.communicate()
    if err and not ignore_error:
        print(err.decode('UTF-8'))
        raise RuntimeError('Error in command line call')
    return out.decode('UTF-8'), err.decode('UTF-8') if err else None
