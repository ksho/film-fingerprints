import pyffmpeg as pf
from PIL import Image
import math
import threading
import Queue


"""
TODO:
- multithreading
- banner
"""


FRAME_SIZE = {}


def get_bar_from_frame(f, i):
    x = FRAME_SIZE['xmid']
    y = FRAME_SIZE['y']
    f = f.crop((x, 0, x + 1, y))
    #f = f.resize((1, FRAME_SIZE['y']), Image.ANTIALIAS)
    return f


def get_frame_size(video_track):
    #frame = video_track.get_current_frame()[2]
    size = video_track.get_size()
    FRAME_SIZE['x'] = size[0]
    FRAME_SIZE['y'] = size[1]
    FRAME_SIZE['xmid'] = FRAME_SIZE['x'] / 2
    print FRAME_SIZE

def do_the_stuff(video_track, start, end, tnum):
    print 'start', start, end
    num_frames = end - start
    video_track.seek_to_frame(start)
    composite = Image.new('RGB', (num_frames, FRAME_SIZE['y']), (255, 255, 255))
    video_track.prepare_to_read_ahead()

    i = 0
    frame = video_track.get_current_frame()[2]
    bar = get_bar_from_frame(frame, i)
    composite.paste(bar, (i, 0))

    i += 1
    while i < num_frames:
        frame = video_track.get_next_frame()
        bar = get_bar_from_frame(frame, i)
        composite.paste(bar, (i, 0))
        i += 1
        if i % 1000 is 0:
            print tnum, i, frame, video_track.get_current_frame_pts()
    print 'stop'
    q.put(composite)#composite


q = Queue.Queue()

# Create reader object
reader = pf.FFMpegReader()
reader2= pf.FFMpegReader()

# Open an audio-video file
reader.open("/home/karlshouler/Desktop/bttf.mkv", pf.TS_VIDEO_PIL)
reader2.open("/home/karlshouler/Desktop/bttf.mkv", pf.TS_VIDEO_PIL)

video_track = reader.get_tracks()[0]
video_track2 = reader2.get_tracks()[0]
fps = video_track.get_fps()
duration = reader.duration_time()
num_frames = math.floor(fps * duration) - 100
print 'fps', fps, duration, num_frames

get_frame_size(video_track)

num_frames = 10000


video_track.seek_to_frame(100)
num_frames = num_frames - 100
print num_frames

start1 = 100
start2 = num_frames / 2;
end1 = start2 - 1
end2 = num_frames

t1 = threading.Thread(target=do_the_stuff, args=(video_track,start1,end1,1))
t2 = threading.Thread(target=do_the_stuff, args=(video_track2,start2,end2,2))
t1.start()
t2.start()

composite = q.get()
print composite
composite2 = q.get()
print composite2

composite.save('333.png')
composite2.save('444.png')



