"""Overlay a labelled pixel grid on an image so coordinates can be read off it.
usage: grid-overlay.py <src> <out> <step_px> [outwidth]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
from PIL import Image, ImageDraw
src, out, step = sys.argv[1], sys.argv[2], int(sys.argv[3])
ow = int(sys.argv[4]) if len(sys.argv) > 4 else None
im = Image.open(src).convert('RGB')
if ow:
    w, h = im.size
    im = im.resize((ow, int(h*ow/float(w))), Image.LANCZOS)
d = ImageDraw.Draw(im)
W, H = im.size
for x in range(0, W, step):
    d.line([(x, 0), (x, H)], fill=(255, 0, 0) if x % (step*5) == 0 else (255, 190, 190), width=1)
    if x % (step*5) == 0:
        d.text((x+3, 3), str(x), fill=(255, 0, 0))
        d.text((x+3, H-14), str(x), fill=(255, 0, 0))
for y in range(0, H, step):
    d.line([(0, y), (W, y)], fill=(0, 0, 255) if y % (step*5) == 0 else (190, 190, 255), width=1)
    if y % (step*5) == 0:
        d.text((3, y+3), str(y), fill=(0, 0, 255))
        d.text((W-46, y+3), str(y), fill=(0, 0, 255))
im.save(out)
print('grid %dpx on %dx%d -> %s' % (step, W, H, out))
