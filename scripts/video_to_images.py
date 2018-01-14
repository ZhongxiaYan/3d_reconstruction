from util import *
import sys, os

data_path = sys.argv[1] + '/'
n = int(sys.argv[2])
frames_dir = data_path + 'frames/'
make_dir(frames_dir)

mp4_files = list_dir(data_path, 'mp4', return_name=True)
print(mp4_files)
mov_files = list_dir(data_path, 'mov', return_name=True)
image_list = []
for name, file in mp4_files + mov_files:
    output_dir = frames_dir + name + '/'
    if not os.path.exists(output_dir):
        frame_paths = video_to_frames(file, output_dir, n)
        # make_dir(output_dir)
        # cmd = 'ffmpeg -i %s -vf "select=not(mod(n\, %s))" -vsync vfr -qscale:v 2 -threads 8 %s/%%04d.jpg' % (file, n, output_dir)
        # print(cmd)
        # shell(cmd)
    else:
        print('skipping', name, 'output directory already exists')
        frame_paths = list_dir(output_dir, 'jpg')
    image_list += ['frames/%s/%s' % (name, x) for x in os.listdir(output_dir)]

output_list = data_path + '/image_list.txt'
with open(output_list, 'w+') as f:
    f.write('\n'.join(image_list))
