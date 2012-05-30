import pyffmpeg as pf
from PIL import Image
import math


"""
TODO:
- multithreading
- banner
"""

FRAME_SIZE = {}


def get_bar_from_frame(f, i):
    x = FRAME_SIZE['xmid']
    y = FRAME_SIZE['y']
    #f = f.crop((x, 0, x + 1, y))
    f = f.resize((1, FRAME_SIZE['y']))
    return f


def get_frame_size(video_track):
    #frame = video_track.get_current_frame()[2]
    size = video_track.get_size()
    FRAME_SIZE['x'] = size[0]
    FRAME_SIZE['y'] = size[1]
    FRAME_SIZE['xmid'] = FRAME_SIZE['x'] / 2
    print FRAME_SIZE


# Create reader object
reader = pf.FFMpegReader()

# Open an audio-video file
reader.open("/home/karlshouler/Desktop/how.mkv", pf.TS_VIDEO_PIL)

video_track = reader.get_tracks()[0]
fps = video_track.get_fps()
duration = reader.duration_time()
num_frames = math.floor(fps * duration) - 10
print 'fps', fps, duration, num_frames

get_frame_size(video_track)

#num_frames = 10000

#video_track.seek_to_frame(30000)
#num_frames = num_frames - 30000
#print num_frames

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
        print i, frame, video_track.get_current_frame_pts(), video_track.get_current_frame_frameno()

composite.save('2222.png')



