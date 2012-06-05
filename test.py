#!/usr/bin/env python2.6

import pyffmpeg as pf
from PIL import Image
import math
import threading
from multiprocessing import Process, Queue


"""
TODO:
- banner
"""

FACTOR = 10
FRAME_SIZE = {}
VIDEO_LOC = "/home/karlshouler/Desktop/how.mkv"
VIDEO_NAME = "how"
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


def do_the_stuff(vt, start, end, tnum):
    
    num_frames = int(end - start)
    print 'start', tnum, start, end, num_frames
    vt.seek_to_frame(start)
    print 'seek complete', tnum
    composite = Image.new('RGB', (num_frames/FACTOR, FRAME_SIZE['y']), (255, 255, 255))
    vt.prepare_to_read_ahead()

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
            if i % 100 is 0:
                print tnum, i, frame, vt.get_current_frame_pts(), vt.get_current_frame_frameno()
            if i % 5000 is 0:
                composite.save(VIDEO_NAME + 'part' + str(tnum) + '.png')
        except:
            break
    print 'stop'
    image_str = composite.tostring()
    q.put({'half': tnum, 'str': image_str, 'size': composite.size, 'mode': composite.mode})
    composite.save(VIDEO_NAME + 'part' + str(tnum) + '.png')


########################
########################

q = Queue()

readers = []
# Create reader object
reader = pf.FFMpegReader()
reader2= pf.FFMpegReader()

# Open an audio-video file
reader.open(VIDEO_LOC, pf.TS_VIDEO_PIL)
reader2.open(VIDEO_LOC, pf.TS_VIDEO_PIL)



video_track = reader.get_tracks()[0]
video_track2 = reader2.get_tracks()[0]
fps = video_track.get_fps()
duration = reader.duration_time()
num_frames = math.floor(fps * duration) - 100
print 'fps', fps, duration, num_frames

get_frame_size(video_track)

num_frames = 2000

video_track.seek_to_frame(100)
num_frames = num_frames - 100
print num_frames

start1 = 0
start2 = int(num_frames / 2);
end1 = start2 - 1
end2 = num_frames

p1 = Process(target=do_the_stuff, args=[video_track,start1,end1,1])
p2 = Process(target=do_the_stuff, args=[video_track2,start2,end2,2])
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
    if h['half'] is 1:
        first = Image.fromstring(h['mode'], h['size'], h['str'])
        print 's1', first.size
    elif h['half'] is 2:
        second = Image.fromstring(h['mode'], h['size'], h['str'])
        print 's2', second.size

delta = first.size[0] - second.size[0]


composite = Image.new('RGB', (num_frames/FACTOR + delta, FRAME_SIZE['y']), (255, 255, 255))
composite.paste(first, (0, 0))
composite.paste(second, (num_frames/FACTOR/2 + delta, 0))

composite.save('sup.png')
