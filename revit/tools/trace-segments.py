"""Extract straight wall-line segments from a scanned plan.
usage: trace-segments.py <png> <x0> <y0> <x1> <y1> [minlen_px] [out.json]
Coords are fractions of the image. Prints vertical and horizontal segments in crop pixels."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
import numpy as np
from PIL import Image

src = sys.argv[1]
f = [float(v) for v in sys.argv[2:6]]
minlen = int(sys.argv[6]) if len(sys.argv) > 6 else 45
outj = sys.argv[7] if len(sys.argv) > 7 else None
im = Image.open(src).convert('L')
W, H = im.size
box = (int(f[0]*W), int(f[1]*H), int(f[2]*W), int(f[3]*H))
a = np.asarray(im.crop(box), dtype=np.uint8)
ink = a < 120
h, w = ink.shape

def runs_along(mask, axis):
    """Return [(pos, start, end)] runs of True of length>=minlen along `axis`."""
    out = []
    n = mask.shape[1] if axis == 0 else mask.shape[0]
    for p in range(n):
        line = mask[:, p] if axis == 0 else mask[p, :]
        idx = np.flatnonzero(line)
        if idx.size == 0:
            continue
        brk = np.flatnonzero(np.diff(idx) > 2)
        starts = np.concatenate(([0], brk + 1))
        ends = np.concatenate((brk, [idx.size - 1]))
        for s, e in zip(starts, ends):
            L = idx[e] - idx[s] + 1
            if L >= minlen:
                out.append((p, int(idx[s]), int(idx[e])))
    return out

def merge(runs, tol=4, ovl=0.5):
    """Merge runs at neighbouring positions into segments."""
    runs = sorted(runs)
    segs = []
    for p, s, e in runs:
        placed = False
        for sg in segs:
            if abs(sg['p1'] - p) <= tol:
                lo, hi = max(sg['s'], s), min(sg['e'], e)
                if hi - lo > ovl * min(sg['e'] - sg['s'], e - s):
                    sg['p1'] = p
                    sg['ps'].append(p)
                    sg['s'] = min(sg['s'], s); sg['e'] = max(sg['e'], e)
                    placed = True
                    break
        if not placed:
            segs.append({'p0': p, 'p1': p, 'ps': [p], 's': s, 'e': e})
    for sg in segs:
        sg['pos'] = float(np.mean(sg['ps'])); sg['thick'] = sg['p1'] - sg['p0'] + 1
    return segs

vs = merge(runs_along(ink, 0))
hs = merge(runs_along(ink, 1))
minthick = int(os.environ.get("MINTHICK", "0"))
vs = [s for s in vs if s["e"] - s["s"] >= minlen and s["thick"] >= minthick]
hs = [s for s in hs if s["e"] - s["s"] >= minlen and s["thick"] >= minthick]
print('crop %s size %dx%d  vert=%d horiz=%d' % (box, w, h, len(vs), len(hs)))
print('--- VERTICAL  x  ytop  ybot  len  thick')
for s in sorted(vs, key=lambda s: -(s['e'] - s['s']))[:60]:
    print('  %7.1f %6d %6d %6d %4d' % (s['pos'], s['s'], s['e'], s['e'] - s['s'], s['thick']))
print('--- HORIZONTAL  y  xleft  xright  len  thick')
for s in sorted(hs, key=lambda s: -(s['e'] - s['s']))[:60]:
    print('  %7.1f %6d %6d %6d %4d' % (s['pos'], s['s'], s['e'], s['e'] - s['s'], s['thick']))
if outj:
    json.dump({'box': box, 'vert': [[s['pos'], s['s'], s['e'], s['thick']] for s in vs],
               'horiz': [[s['pos'], s['s'], s['e'], s['thick']] for s in hs]}, open(outj, 'w'))
    print('wrote', outj)
