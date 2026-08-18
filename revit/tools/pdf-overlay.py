"""Register the PDF Equipment Plan line work to model feet, overlay with the live model walls, and
report PDF wall-like lines that have no model wall nearby.  Usage: python.exe tools/pdf-overlay.py [walls.json]"""
import sys, os, json, math, urllib.request
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, 'pylib'))
from PIL import Image, ImageDraw   # PyMuPDF bundles no PIL; install below if missing
data = json.load(open(os.path.join(here, '..', 'reference', 'equipment-plan-lines.json')))
S = data['pt_per_ft']
segs = data['segments_pt']
# --- registration: longest horizontal segment near the bottom of the plan = the 52'-7" S wall (52.58 ft = 946.5 pt)
def L(s): return math.hypot(s[2]-s[0], s[3]-s[1])
horiz = [s for s in segs if abs(s[3]-s[1]) < 0.5 and 940 < L(s) < 953]
vert = [s for s in segs if abs(s[2]-s[0]) < 0.5 and 536 < L(s) < 548]   # 30'-1" = 541.5 pt
print('candidates 52-7:', [(round(min(s[0],s[2])), round(s[1]), round(L(s)/S,2)) for s in horiz])
print('candidates 30-1:', [(round(s[0]), round(min(s[1],s[3])), round(L(s)/S,2)) for s in vert])
if not horiz:
    sys.exit('no S wall candidate')
sw = max(horiz, key=lambda s: s[1])          # lowest on the sheet (largest y) among candidates
X0 = min(sw[0], sw[2])
# Y from the 30-1 east wall (its top = y 30.083); the 52-7 line is the dimension line, 6 ft below the wall
Y0 = (min(vert[0][1], vert[0][3]) + 30.083 * S) if vert else sw[1]
def to_ft(x, y): return (11 + (x - X0) / S, (Y0 - y) / S)
print('origin pt', X0, Y0)
# --- model walls
walls_file = sys.argv[1] if len(sys.argv) > 1 else None
if walls_file:
    walls = json.load(open(walls_file))['walls']
else:
    walls = json.load(urllib.request.urlopen('http://localhost:48884/onetake-v1/walls', timeout=120))['walls']
walls = [w for w in walls if -5 <= w['start'][0] <= 70 and -30 <= w['start'][1] <= 70]
# --- overlay image
X_MIN, X_MAX, Y_MIN, Y_MAX, PX = -4, 68, -28, 66, 16
W, H = int((X_MAX-X_MIN)*PX), int((Y_MAX-Y_MIN)*PX)
im = Image.new('RGB', (W, H), 'white'); dr = ImageDraw.Draw(im)
def P(x, y): return ((x-X_MIN)*PX, (Y_MAX-y)*PX)
ft_segs = []
for s in segs:
    a = to_ft(s[0], s[1]); b = to_ft(s[2], s[3])
    if not (X_MIN-2 <= a[0] <= X_MAX+2 and Y_MIN-2 <= a[1] <= Y_MAX+2): continue
    ft_segs.append((a, b, L(s)/S))
    dr.line([P(*a), P(*b)], fill=(120,120,120), width=1)
for w in walls:
    col = (220,0,0) if 'Generic' in w['type'] else (0,90,220)
    dr.line([P(*w['start']), P(*w['end'])], fill=col, width=3)
for x in range(0, 70, 10):
    dr.line([P(x, Y_MIN), P(x, Y_MAX)], fill=(230,230,230)); dr.text((P(x, Y_MAX)[0]+2, 2), str(x), fill=(0,0,0))
for y in range(-20, 70, 10):
    dr.line([P(X_MIN, y), P(X_MAX, y)], fill=(230,230,230)); dr.text((2, P(0, y)[1]), str(y), fill=(0,0,0))
out = os.path.join(here, '..', 'progress', 'pdf-vs-model-overlay.png'); im.save(out); print('overlay', out)
# --- gaps: long PDF segments (>= 2.5 ft, axis-aligned or diagonal) with no model wall within 0.35 ft (both endpoints)
def dist_pt_seg(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx-ax, by-ay; l2 = dx*dx+dy*dy
    t = 0 if l2 == 0 else max(0, min(1, ((px-ax)*dx+(py-ay)*dy)/l2))
    return math.hypot(px-(ax+t*dx), py-(ay+t*dy))
def near_wall(a, b):
    for w in walls:
        if dist_pt_seg(a, w['start'], w['end']) < 0.45 and dist_pt_seg(b, w['start'], w['end']) < 0.45:
            return True
    return False
missing = [(a, b, l) for a, b, l in ft_segs if l >= 2.5 and not near_wall(a, b)]
missing.sort(key=lambda t: -t[2])
print('PDF lines >=2.5ft with no model wall:', len(missing))
for a, b, l in missing[:80]:
    print('  (%.1f,%.1f)-(%.1f,%.1f) %.1f ft' % (a[0], a[1], b[0], b[1], l))
json.dump({'origin_pt': [X0, Y0], 'missing': [[a, b, l] for a, b, l in missing]}, open(os.path.join(here, '..', 'progress', 'pdf-gaps.json'), 'w'))
