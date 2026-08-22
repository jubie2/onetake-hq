"""Convert traced pixel segments to wall centerlines in feet.
usage: segs-to-walls.py <segs.json> <x0_px> <y0_px> <pxperft> <out.json> [minlen_ft]"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
segf, x0, y0, ppf, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
minlen = float(sys.argv[6]) if len(sys.argv) > 6 else 1.5
d = json.load(open(segf))

def snap(v, step=1/12.0):
    return round(round(v/step)*step, 4)

def cluster(segs, tol_px=7.0):
    """segs: [pos, s, e, thick]; merge same-position segments whose ranges touch."""
    segs = sorted(segs, key=lambda s: (s[0], s[1]))
    groups = []
    for pos, s, e, t in segs:
        hit = None
        for g in groups:
            if abs(g['pos'] - pos) <= tol_px:
                for r in g['ranges']:
                    if not (e < r[0] - 25 or s > r[1] + 25):
                        hit = (g, r); break
                if hit: break
        if hit:
            g, r = hit
            r[0] = min(r[0], s); r[1] = max(r[1], e)
            g['w'].append(t); g['p'].append(pos)
            g['pos'] = sum(g['p'])/len(g['p'])
        else:
            found = None
            for g in groups:
                if abs(g['pos'] - pos) <= tol_px:
                    found = g; break
            if found:
                found['ranges'].append([s, e]); found['w'].append(t); found['p'].append(pos)
                found['pos'] = sum(found['p'])/len(found['p'])
            else:
                groups.append({'pos': pos, 'p': [pos], 'ranges': [[s, e]], 'w': [t]})
    out = []
    for g in groups:
        for r in g['ranges']:
            out.append((g['pos'], r[0], r[1], max(g['w'])))
    return out

V = cluster(d['vert'])
H = cluster(d['horiz'])
walls = []
for pos, s, e, t in V:
    X = snap((pos - x0)/ppf); Y1 = snap((y0 - e)/ppf); Y2 = snap((y0 - s)/ppf)
    if abs(Y2-Y1) >= minlen:
        walls.append({'dir': 'V', 'x': X, 'y0': Y1, 'y1': Y2, 'len': round(abs(Y2-Y1), 2), 'thick_in': round(t/ppf*12, 1)})
for pos, s, e, t in H:
    Y = snap((y0 - pos)/ppf); X1 = snap((s - x0)/ppf); X2 = snap((e - x0)/ppf)
    if abs(X2-X1) >= minlen:
        walls.append({'dir': 'H', 'y': Y, 'x0': X1, 'x1': X2, 'len': round(abs(X2-X1), 2), 'thick_in': round(t/ppf*12, 1)})
json.dump(walls, open(out, 'w'), indent=1)
print('walls: %d  (V=%d H=%d)' % (len(walls), sum(1 for w in walls if w['dir']=='V'), sum(1 for w in walls if w['dir']=='H')))
xs = [w['x'] for w in walls if w['dir']=='V']; ys = [w['y'] for w in walls if w['dir']=='H']
print('extent  x %.2f .. %.2f   y %.2f .. %.2f' % (min(xs), max(xs), min(ys), max(ys)))
for w in sorted(walls, key=lambda w: -w['len'])[:40]:
    if w['dir'] == 'V':
        print('  V x=%7.2f  y %7.2f -> %7.2f   len %6.2f  t %.1f"' % (w['x'], w['y0'], w['y1'], w['len'], w['thick_in']))
    else:
        print('  H y=%7.2f  x %7.2f -> %7.2f   len %6.2f  t %.1f"' % (w['y'], w['x0'], w['x1'], w['len'], w['thick_in']))
