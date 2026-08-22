"""Crop a region from a big PNG.  usage: crop.py <src> <out> <x0> <y0> <x1> <y1> [outwidth]
Coordinates are fractions (0-1) of the source image."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = [float(v) for v in sys.argv[3:7]]
ow = int(sys.argv[7]) if len(sys.argv) > 7 else 1500
im = Image.open(src); W, H = im.size
box = (int(x0*W), int(y0*H), int(x1*W), int(y1*H))
c = im.crop(box)
w, h = c.size
c = c.resize((ow, max(1, int(h*ow/float(w)))), Image.LANCZOS)
c.save(out)
print('src %dx%d  box %s  out %s %dx%d' % (W, H, box, out, c.size[0], c.size[1]))
