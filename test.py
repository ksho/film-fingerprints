import pyffmpeg as pf
from PIL import Image

FRAME_SIZE = {}
bars = []
NEW = Image.new('RGB',(100, 720),(0,0,0))

def get_bar(f, i):
    size = f.size
    x = FRAME_SIZE['x'] / 2
    y = FRAME_SIZE['y']
    f = f.crop((x, 0, x + 1, y))
    #bars.append(f)
    NEW.paste(f, (i-1,0))
    #f.save('hey.png')
    #return c


def build_composite():
    num_bars = len(bars)
    print 'num_bars', num_bars, FRAME_SIZE
    composite = Image.new('RGB',(num_bars, FRAME_SIZE['y']),(255,255,255))
    for k in xrange(0, num_bars):
        composite.paste(bars[k], (k,0))
#    composite = composite.resize((composite.size[0], 70))
    return composite


def get_frame_size(tv):
    frame = tv.get_current_frame()[2]
    print frame.size
    FRAME_SIZE['x'] = frame.size[0]
    FRAME_SIZE['y'] = frame.size[1]
    print FRAME_SIZE


# create the reader object
mp = pf.FFMpegReader()

## open an audio-video file
mp.open("/home/karlshouler/Desktop/how.mkv", pf.TS_VIDEO_PIL)
tv = mp.get_tracks()[0]
# print 'fps', tv.get_fps(), tv.get_current_frame_pts(), tv.get_current_frame_frameno()

duration = mp.duration_time()
tv = mp.get_tracks()[0]
fps = tv.get_fps()
num_frames = int(fps * duration)
print 'fps', fps, duration, num_frames

frame_size = get_frame_size(tv)


i = 1

while i < 100:
    try:
        f = tv.get_next_frame()
        get_bar(f, i)
        #bars.append(bar)

        i = i + 1
        if i % 1 is 0:
            print i, f, tv.get_current_frame_pts(), tv.get_current_frame_frameno()
    except:
        print 'lalala'
        break

NEW.save('1111.png')

# print i
# tv.seek_to_frame(100000)
# print 'fps1', tv.get_fps(), tv.get_current_frame_pts(), tv.get_current_frame_frameno()

# frame = tv.get_current_frame()[2]

#composite_image = build_composite()

#composite_image.save('lala4.png')



