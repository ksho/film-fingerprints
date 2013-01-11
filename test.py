#!/usr/bin/env python2.6

import pyffmpeg as pf
from PIL import Image
import math
import threading
from multiprocessing import Process, Queue, Pool
import shutil
import sys


"""
TODO:
- banner
"""

FACTOR = 10
FRAME_SIZE = {}
VIDEO_LOC = "/home/karlshouler/Desktop/eternal.mkv"
VIDEO_NAME = "eternal"
NUM_PROCESSES = 2

def get_bar_from_frame(f, i):
    x = FRAME_SIZE['xmid']
    y = FRAME_SIZE['y']
    #f = f.crop((x, 0, x + 1, y))
    f = f.resize((1, FRAME_SIZE['y']), Image.ANTIALIAS)
    return f


def get_frame_size(video_track):
    #frame = video_track.get_current_frame()[2]
    size = video_track.get_size()
    FRAME_SIZE['x'] = size[0]
    FRAME_SIZE['y'] = size[1]
    FRAME_SIZE['xmid'] = FRAME_SIZE['x'] / 2
    print FRAME_SIZE


def do_the_stuff(o, vt):
    num_frames = int(o['end'] - o['start'])
    print 'start', o['half'], o['start'], o['end'], num_frames
    vt.seek_to_frame(o['start'])
    print 'seek complete', o['half']
    composite = Image.new('RGB', (num_frames/FACTOR, FRAME_SIZE['y']), (255, 255, 255))
    # o['vt'].prepare_to_read_ahead()

    i = 0
    frame = vt.get_current_frame()[2]
    bar = get_bar_from_frame(frame, i)
    composite.paste(bar, (i/FACTOR, 0))

    i += 1
    while i < num_frames:
        try:
            frame = vt.get_next_frame()
            if i % FACTOR is 0:
                bar = get_bar_from_frame(frame, i)
                composite.paste(bar, (i/FACTOR, 0))
            i += 1
            if i % 500 is 0:
                print o['half'], i, frame, vt.get_current_frame_pts(), vt.get_current_frame_frameno()
            if i % 5000 is 0:
                composite.save(VIDEO_NAME + 'part' + str(o['half']) + '.png')
        except:
            break
    print 'stop'
    image_str = composite.tostring()
    q.put({'half': o['half'], 'str': image_str, 'size': composite.size, 'mode': composite.mode})
    composite.save(VIDEO_NAME + 'part' + str(o['half']) + '.png')


########################
########################

q = Queue()

readers = []

# shutil.copy(VIDEO_LOC, VIDEO_LOC+'copy')

# sys.exit()

for i in range(NUM_PROCESSES):
    # Create reader object
    o = {}
    o['half'] = i
    o['reader'] = pf.FFMpegReader()

    # Open an audio-video file
    o['reader'].open(VIDEO_LOC, pf.TS_VIDEO_PIL)

    o['vt'] = o['reader'].get_tracks()[0]
    readers.append(o)

r = readers

v0 = r[0]['vt']
v1 = r[1]['vt']

print 'r0', str(r[0])
print 'r1', str(r[1])

get_frame_size(v0)
fps = v0.get_fps()
duration = r[0]['reader'].duration_time()
total_num_frames = math.floor(fps * duration) - 100

print 'fps', fps, duration, total_num_frames

# total_num_frames = 2000

v0.seek_to_frame(100)
total_num_frames = total_num_frames - 100
print total_num_frames

r[0]['start'] = 0
r[1]['start'] = int(total_num_frames / 2);
r[0]['end'] = r[1]['start'] - 1
r[1]['end'] = total_num_frames

print r[0]

pool = Pool(processes=2)
# p1 = pool.apply_async(do_the_stuff, [r[0],v0,])
# print p1.get()
# p2 = pool.apply_async(do_the_stuff, [r[1],v1,])

p1 = Process(target=do_the_stuff, args=(r[0],v0))
p2 = Process(target=do_the_stuff, args=(r[1],v1))
p1.start()
p2.start()


print '!!!!!!!!!!!!!!!!!!!'
halves = []
halves.append(q.get())
halves.append(q.get())

p1.join()
p2.join()

for h in halves:
    print 'lala'
    if h['half'] is 0:
        first = Image.fromstring(h['mode'], h['size'], h['str'])
        print 's1', first.size
    elif h['half'] is 1:
        second = Image.fromstring(h['mode'], h['size'], h['str'])
        print 's2', second.size

delta = first.size[0] - second.size[0]


composite = Image.new('RGB', (total_num_frames/FACTOR + delta, FRAME_SIZE['y']), (255, 255, 255))
composite.paste(first, (0, 0))
composite.paste(second, (total_num_frames/FACTOR/2 + delta, 0))

composite.save('sup.png')
