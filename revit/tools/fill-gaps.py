"""Walk each traced wall line in the source scan, find its true full extent, and record the
breaks (= window/door openings).  usage:
  fill-gaps.py <png> <walls.json> <x0px> <y0px> <ppf> <cropx0> <cropy0> <out_walls.json> <out_openings.json>
Coordinates in walls.json are house feet (x right, y up) with origin at (x0px, y0px) of the FULL page image."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
import numpy as np
from PIL import Image

png, wf = sys.argv[1], sys.argv[2]
X0, Y0, PPF = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
CX, CY = float(sys.argv[6]), float(sys.argv[7])       # crop offset used when tracing
outw, outo = sys.argv[8], sys.argv[9]
im = Image.open(png).convert('L')
A = np.asarray(im, dtype=np.uint8)
INK = A < 120
H, W = INK.shape

def px(xft, yft):
    return X0 + CX + xft*PPF, Y0 + CY - yft*PPF

BAND = 3            # +/- px perpendicular tolerance
SEARCH = 8.0        # ft to search beyond current ends
MIN_RUN = int(0.4*PPF)
MAX_GAP_FT = 12.0   # merge across breaks up to this (openings)
walls = json.load(open(wf))
new, openings = [], []
for w in walls:
    if w['dir'] == 'V':
        xp, _ = px(w['x'], 0)
        xp = int(round(xp))
        lo_ft, hi_ft = w['y0'] - SEARCH, w['y1'] + SEARCH
        _, y_lo = px(0, hi_ft); _, y_hi = px(0, lo_ft)
        r0, r1 = max(0, int(y_lo)), min(H-1, int(y_hi))
        if xp-BAND < 0 or xp+BAND >= W or r1 <= r0: continue
        line = INK[r0:r1+1, xp-BAND:xp+BAND+1].any(axis=1)
        idx = np.flatnonzero(line)
        if idx.size == 0: continue
        # runs of ink
        brk = np.flatnonzero(np.diff(idx) > 2)
        starts = np.concatenate(([0], brk+1)); ends = np.concatenate((brk, [idx.size-1]))
        runs = [(int(idx[s]), int(idx[e])) for s, e in zip(starts, ends) if idx[e]-idx[s] >= MIN_RUN]
        if not runs: continue
        # merge runs separated by <= MAX_GAP
        merged, gaps = [runs[0]], []
        for s, e in runs[1:]:
            if (s - merged[-1][1]) <= MAX_GAP_FT*PPF:
                gaps.append((merged[-1][1], s)); merged[-1] = (merged[-1][0], e)
            else:
                merged.append((s, e))
        seg = max(merged, key=lambda r: r[1]-r[0])
        ytop = (Y0 + CY - (r0 + seg[0]))/PPF; ybot = (Y0 + CY - (r0 + seg[1]))/PPF
        y1, y2 = min(ytop, ybot), max(ytop, ybot)
        if y2 - y1 < 1.5: continue
        new.append({'dir': 'V', 'x': w['x'], 'y0': round(y1, 3), 'y1': round(y2, 3), 't': w['t'],
                    'len': round(y2-y1, 2)})
        for g0, g1 in gaps:
            a = (Y0 + CY - (r0+g0))/PPF; b = (Y0 + CY - (r0+g1))/PPF
            lo, hi = min(a, b), max(a, b)
            if 1.2 <= hi-lo <= MAX_GAP_FT and y1 <= lo and hi <= y2:
                openings.append({'dir': 'V', 'x': w['x'], 'a': round(lo,3), 'b': round(hi,3), 'w': round(hi-lo,2)})
    else:
        _, yp = px(0, w['y']); yp = int(round(yp))
        lo_ft, hi_ft = w['x0'] - SEARCH, w['x1'] + SEARCH
        x_lo, _ = px(lo_ft, 0); x_hi, _ = px(hi_ft, 0)
        c0, c1 = max(0, int(x_lo)), min(W-1, int(x_hi))
        if yp-BAND < 0 or yp+BAND >= H or c1 <= c0: continue
        line = INK[yp-BAND:yp+BAND+1, c0:c1+1].any(axis=0)
        idx = np.flatnonzero(line)
        if idx.size == 0: continue
        brk = np.flatnonzero(np.diff(idx) > 2)
        starts = np.concatenate(([0], brk+1)); ends = np.concatenate((brk, [idx.size-1]))
        runs = [(int(idx[s]), int(idx[e])) for s, e in zip(starts, ends) if idx[e]-idx[s] >= MIN_RUN]
        if not runs: continue
        merged, gaps = [runs[0]], []
        for s, e in runs[1:]:
            if (s - merged[-1][1]) <= MAX_GAP_FT*PPF:
                gaps.append((merged[-1][1], s)); merged[-1] = (merged[-1][0], e)
            else:
                merged.append((s, e))
        seg = max(merged, key=lambda r: r[1]-r[0])
        x1 = (c0 + seg[0] - X0 - CX)/PPF; x2 = (c0 + seg[1] - X0 - CX)/PPF
        if x2 - x1 < 1.5: continue
        new.append({'dir': 'H', 'y': w['y'], 'x0': round(x1,3), 'x1': round(x2,3), 't': w['t'],
                    'len': round(x2-x1, 2)})
        for g0, g1 in gaps:
            a = (c0+g0 - X0 - CX)/PPF; b = (c0+g1 - X0 - CX)/PPF
            if 1.2 <= b-a <= MAX_GAP_FT and x1 <= a and b <= x2:
                openings.append({'dir': 'H', 'y': w['y'], 'a': round(a,3), 'b': round(b,3), 'w': round(b-a,2)})
# de-duplicate walls that now coincide
uniq = []
for w in sorted(new, key=lambda w: -w['len']):
    dup = False
    for u in uniq:
        if u['dir'] != w['dir']: continue
        if w['dir'] == 'V' and abs(u['x']-w['x']) < 0.4 and not (w['y1'] < u['y0']-0.3 or w['y0'] > u['y1']+0.3):
            dup = True; break
        if w['dir'] == 'H' and abs(u['y']-w['y']) < 0.4 and not (w['x1'] < u['x0']-0.3 or w['x0'] > u['x1']+0.3):
            dup = True; break
    if not dup: uniq.append(w)
json.dump(uniq, open(outw, 'w'), indent=1)
json.dump(openings, open(outo, 'w'), indent=1)
print('walls in %d -> out %d (total %.1f ft)   openings found %d' %
      (len(walls), len(uniq), sum(w['len'] for w in uniq), len(openings)))
ws = sorted(openings, key=lambda o: -o['w'])[:12]
for o in ws:
    print('   opening %s %.2f ft @ %s' % (o['dir'], o['w'], round(o.get('x', o.get('y')), 2)))
