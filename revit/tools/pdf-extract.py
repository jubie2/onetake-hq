"""Extract the EQUIPMENT PLAN sheet from the vector PDF: render PNG + dump line segments (feet).
Run with pyRevit's CPython:  python.exe tools/pdf-extract.py  (adds tools/pylib to sys.path)
Scale 1/4" = 1'-0"  ->  1 ft = 18 pt (PDF points).  Output: reference/equipment-plan.png, reference/equipment-plan-lines.json"""
import sys, os, json
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, 'pylib'))
import pymupdf
pdf = os.path.join(here, '..', 'reference', 'pho-hung-el-cajon-plans.pdf')
doc = pymupdf.open(pdf)
page = None
for p in doc:
    if 'EQUIPMENT PLAN' in p.get_text() and 'EQUIPMENT SCHEDULE' in p.get_text():
        page = p
        break
if page is None:
    page = doc[0]
print('sheet page index', page.number, 'text words', len(page.get_text().split()))
zoom = 4
pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
out_png = os.path.join(here, '..', 'reference', 'equipment-plan.png')
pix.save(out_png)
print('png', pix.width, pix.height, out_png)
segs, texts = [], []
for d in page.get_drawings():
    w = d.get('width') or 0
    for it in d['items']:
        if it[0] == 'l':
            a, b = it[1], it[2]
            segs.append([round(a.x, 2), round(a.y, 2), round(b.x, 2), round(b.y, 2), round(w, 2)])
        elif it[0] == 're':
            r = it[1]
            segs.append([round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y0, 2), round(w, 2)])
            segs.append([round(r.x1, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2), round(w, 2)])
            segs.append([round(r.x1, 2), round(r.y1, 2), round(r.x0, 2), round(r.y1, 2), round(w, 2)])
            segs.append([round(r.x0, 2), round(r.y1, 2), round(r.x0, 2), round(r.y0, 2), round(w, 2)])
for b in page.get_text('words'):
    texts.append([round(b[0], 1), round(b[1], 1), round(b[2], 1), round(b[3], 1), b[4]])
json.dump({'page': page.number, 'pt_per_ft': 18, 'zoom': zoom, 'segments_pt': segs, 'words': texts},
          open(os.path.join(here, '..', 'reference', 'equipment-plan-lines.json'), 'w'))
print('segments', len(segs), 'words', len(texts))
