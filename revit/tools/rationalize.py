"""Tidy a traced wall set: merge near-collinear lines, snap to the inch, force known printed dims.
usage: rationalize.py <walls.json> <out.json> [anchors_x] [anchors_y]
anchors are comma-separated feet values that traced lines should be pulled onto if within 0.5 ft."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
inf, out = sys.argv[1], sys.argv[2]
AX = [float(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 and sys.argv[3] else []
AY = [float(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 and sys.argv[4] else []
W = json.load(open(inf))
INCH = 1/12.0
def snap_inch(v): return round(round(v/INCH)*INCH, 4)
def cluster(vals, tol=0.35):
    vals = sorted(vals); groups = []
    for v in vals:
        if groups and v - groups[-1][-1] <= tol: groups[-1].append(v)
        else: groups.append([v])
    return {v: sum(g)/len(g) for g in groups for v in g}
def anchor(v, anchors, tol=0.6):
    for a in anchors:
        if abs(v-a) <= tol: return a
    return v
mapV = cluster([w['x'] for w in W if w['dir'] == 'V'])
mapH = cluster([w['y'] for w in W if w['dir'] == 'H'])
# also cluster the endpoint coordinates so corners meet
endsX = cluster([w['x0'] for w in W if w['dir']=='H'] + [w['x1'] for w in W if w['dir']=='H'] +
                [w['x'] for w in W if w['dir']=='V'])
endsY = cluster([w['y0'] for w in W if w['dir']=='V'] + [w['y1'] for w in W if w['dir']=='V'] +
                [w['y'] for w in W if w['dir']=='H'])
res = []
for w in W:
    if w['dir'] == 'V':
        x = snap_inch(anchor(mapV.get(w['x'], w['x']), AX))
        y0 = snap_inch(anchor(endsY.get(w['y0'], w['y0']), AY))
        y1 = snap_inch(anchor(endsY.get(w['y1'], w['y1']), AY))
        if abs(y1-y0) < 1.0: continue
        res.append({'dir':'V','x':x,'y0':min(y0,y1),'y1':max(y0,y1),'t':w['t'],'len':round(abs(y1-y0),2)})
    else:
        y = snap_inch(anchor(mapH.get(w['y'], w['y']), AY))
        x0 = snap_inch(anchor(endsX.get(w['x0'], w['x0']), AX))
        x1 = snap_inch(anchor(endsX.get(w['x1'], w['x1']), AX))
        if abs(x1-x0) < 1.0: continue
        res.append({'dir':'H','y':y,'x0':min(x0,x1),'x1':max(x0,x1),'t':w['t'],'len':round(abs(x1-x0),2)})
# drop duplicates
uniq = []
for w in sorted(res, key=lambda w: -w['len']):
    d = False
    for u in uniq:
        if u['dir'] != w['dir']: continue
        if w['dir']=='V' and abs(u['x']-w['x'])<0.2 and not (w['y1']<u['y0']-0.2 or w['y0']>u['y1']+0.2): d=True; break
        if w['dir']=='H' and abs(u['y']-w['y'])<0.2 and not (w['x1']<u['x0']-0.2 or w['x0']>u['x1']+0.2): d=True; break
    if not d: uniq.append(w)
json.dump(uniq, open(out,'w'), indent=1)
xs = [w['x'] for w in uniq if w['dir']=='V']; ys = [w['y'] for w in uniq if w['dir']=='H']
print('%s: %d -> %d walls, %.1f ft   x %.2f..%.2f  y %.2f..%.2f' %
      (os.path.basename(inf), len(W), len(uniq), sum(w['len'] for w in uniq), min(xs), max(xs), min(ys), max(ys)))
print('distinct wall lines: %d vertical, %d horizontal' % (len(set(xs)), len(set(ys))))
