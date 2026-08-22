"""Detect long straight wall lines in a scanned plan page and report them in pixels.
usage: trace-plan.py <png> [x0 y0 x1 y1 (fractions)] """
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
import numpy as np
from PIL import Image
src = sys.argv[1]
im = Image.open(src).convert('L')
W, H = im.size
if len(sys.argv) > 5:
    f = [float(v) for v in sys.argv[2:6]]
    box = (int(f[0]*W), int(f[1]*H), int(f[2]*W), int(f[3]*H))
    im = im.crop(box)
else:
    box = (0, 0, W, H)
a = np.asarray(im, dtype=np.uint8)
dark = (a < 110).astype(np.uint8)          # ink
h, w = dark.shape
print('crop box %s  size %dx%d  ink %.2f%%' % (box, w, h, 100.0*dark.mean()))
# column/row ink profiles -> candidate wall lines (long runs)
colsum = dark.sum(axis=0)
rowsum = dark.sum(axis=1)
def peaks(profile, minfrac, gap=6):
    thr = minfrac * profile.max()
    idx = np.where(profile >= thr)[0]
    groups, cur = [], []
    for i in idx:
        if cur and i - cur[-1] > gap:
            groups.append(cur); cur = []
        cur.append(i)
    if cur: groups.append(cur)
    out = []
    for g in groups:
        gi = np.array(g)
        seg = profile[gi]
        c = int(round(float(np.average(gi, weights=seg))))
        out.append((c, int(profile[c]), g[0], g[-1]))
    return out
print('--- vertical lines (x, ink, span):')
for c, v, g0, g1 in peaks(colsum, 0.45):
    print('   x=%5d ink=%6d width=%d' % (c, v, g1-g0+1))
print('--- horizontal lines (y, ink, span):')
for c, v, g0, g1 in peaks(rowsum, 0.45):
    print('   y=%5d ink=%6d width=%d' % (c, v, g1-g0+1))
