"""Overlay traced segments on the source crop. usage: draw-segs.py <png> <segs.json> <out.png> [width]"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
from PIL import Image, ImageDraw
src, segf, out = sys.argv[1], sys.argv[2], sys.argv[3]
ow = int(sys.argv[4]) if len(sys.argv) > 4 else 1800
d = json.load(open(segf)); box = d['box']
im = Image.open(src).convert('RGB').crop(box)
dr = ImageDraw.Draw(im)
for x, s, e, t in d['vert']:
    dr.line([(x, s), (x, e)], fill=(255, 0, 0), width=max(3, t//2))
for y, s, e, t in d['horiz']:
    dr.line([(s, y), (e, y)], fill=(0, 140, 255), width=max(3, t//2))
w, h = im.size
im = im.resize((ow, int(h*ow/float(w))), Image.LANCZOS)
dr2 = ImageDraw.Draw(im)
sc = ow/float(w)
for gx in range(0, w, 250):
    X = int(gx*sc); dr2.line([(X,0),(X,im.size[1])], fill=(0,200,0)); dr2.text((X+3,3), str(gx), fill=(0,150,0))
for gy in range(0, h, 250):
    Y = int(gy*sc); dr2.line([(0,Y),(ow,Y)], fill=(0,200,0)); dr2.text((3,Y+3), str(gy), fill=(0,150,0))
im.save(out); print('wrote', out, im.size)
