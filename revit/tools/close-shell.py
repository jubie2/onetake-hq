"""Snap traced wall segments into a coherent layout: cluster collinear lines, extend ends to
nearby perpendiculars, drop stubs.  usage: close-shell.py <segs.json> <x0> <y0> <ppf> <out.json>"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
segf, x0, y0, ppf, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
d = json.load(open(segf))
def ft(v): return v/ppf
V = [( (p-x0)/ppf, (y0-e)/ppf, (y0-s)/ppf, t/ppf*12 ) for p, s, e, t in d['vert']]     # x, ylo, yhi, thick_in
H = [( (y0-p)/ppf, (s-x0)/ppf, (e-x0)/ppf, t/ppf*12 ) for p, s, e, t in d['horiz']]   # y, xlo, xhi, thick_in
def cluster_axis(items, tol=0.45):
    """merge items whose position is within tol and whose ranges overlap/touch"""
    items = sorted(items, key=lambda a: (a[0], a[1]))
    res = []
    for pos, lo, hi, th in items:
        done = False
        for r in res:
            if abs(r[0]-pos) <= tol and not (hi < r[1]-1.2 or lo > r[2]+1.2):
                n = r[4]+1
                r[0] = (r[0]*r[4]+pos)/n; r[1] = min(r[1], lo); r[2] = max(r[2], hi)
                r[3] = max(r[3], th); r[4] = n
                done = True; break
        if not done:
            res.append([pos, lo, hi, th, 1])
    return [(round(r[0],3), round(r[1],3), round(r[2],3), round(r[3],1)) for r in res]
V = cluster_axis(V); H = cluster_axis(H)
V = [v for v in V if v[2]-v[1] >= 1.2]
H = [h for h in H if h[2]-h[1] >= 1.2]
# extend ends to nearby perpendicular lines (closes corners)
TOL = 1.6
def extend(lines, perps, is_v):
    out = []
    for pos, lo, hi, th in lines:
        for i, end in ((1, lo), (2, hi)):
            best = None
            for ppos, plo, phi, pth in perps:
                if plo - TOL <= pos <= phi + TOL and abs(ppos - end) <= TOL:
                    if best is None or abs(ppos - end) < abs(best - end):
                        best = ppos
            if best is not None:
                if i == 1: lo = best
                else: hi = best
        out.append((pos, round(lo,3), round(hi,3), th))
    return out
V = extend(V, H, True)
H = extend(H, V, False)
walls = [{'dir':'V','x':v[0],'y0':v[1],'y1':v[2],'t':v[3],'len':round(v[2]-v[1],2)} for v in V] + \
        [{'dir':'H','y':h[0],'x0':h[1],'x1':h[2],'t':h[3],'len':round(h[2]-h[1],2)} for h in H]
json.dump(walls, open(out,'w'), indent=1)
xs=[w['x'] for w in walls if w['dir']=='V']; ys=[w['y'] for w in walls if w['dir']=='H']
print('walls %d (V %d, H %d)  x %.2f..%.2f  y %.2f..%.2f' % (len(walls), len(xs), len(ys), min(xs), max(xs), min(ys), max(ys)))
print('total wall length %.1f ft' % sum(w['len'] for w in walls))
