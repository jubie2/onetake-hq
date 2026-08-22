# Numbered keynote bubbles for the ADU sections, matching the KEYNOTES SECTION legend.
# Drawn as leader + circle + number so they render regardless of the CSI keynote table,
# which does not contain this office's keynote list.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag, ElementId,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, XYZ as _XYZ,
                               Line, Arc, TextNote, TextNoteOptions, TextNoteType,
                               HorizontalTextAlignment, CurveElement)
from System.Collections.Generic import List
import math
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
dry = args.get('dry', True)
R = 0.55          # bubble radius, model ft (about 3/16" on a 1/4" = 1'-0" sheet)
VIEWS = ['ADU - Section 1', 'ADU - Section 2', 'ADU - Section 3', 'ADU - Section 4']
# keynote number -> (category, which point on the element)
SPEC = [('1',  'Roofs',    'top'),
        ('9',  'Roofs',    'under'),
        ('7',  'Walls',    'walltop'),
        ('2',  'Walls',    'wallmid'),
        ('4',  'Walls',    'innermid'),
        ('6',  'Walls',    'wallbase'),
        ('10', 'Walls',    'wallmid2'),
        ('8',  'Walls',    'innermid2'),
        ('5',  'Walls',    'weep'),
        ('11', 'Roofs',    'ceil'),
        ('3',  'Floors',   'mid'),
        ('12', 'Floors',   'below')]
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
L = ['text type %s' % (tt.Id if tt else None)]
for nm in VIEWS:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    bb = v.CropBox; tfm = bb.Transform; inv = tfm.Inverse
    # gather candidate elements, in view-local coords
    cand = {}
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            cn = e.Category.Name if e.Category else ''
            if cn not in ('Roofs', 'Walls', 'Floors'): continue
            b = e.get_BoundingBox(None)
            if b is None: continue
            cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
            if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
            vb = e.get_BoundingBox(v)
            if vb is None: continue
            pmin = inv.OfPoint(vb.Min); pmax = inv.OfPoint(vb.Max)
            lo = (min(pmin.X, pmax.X), min(pmin.Y, pmax.Y))
            hi = (max(pmin.X, pmax.X), max(pmin.Y, pmax.Y))
            if hi[0] < bb.Min.X or lo[0] > bb.Max.X: continue
            ext = 'Exterior' if (hasattr(e, 'WallType') and str(e.WallType.Function) == 'Exterior') else 'Interior'
            cand.setdefault(cn, []).append((lo, hi, ext, hi[1] - lo[1]))
        except Exception: pass
    def pick(cat, kind):
        lst = cand.get(cat, [])
        if not lst: return None
        if cat == 'Walls':
            ext = [w for w in lst if w[2] == 'Exterior']
            inn = [w for w in lst if w[2] == 'Interior']
            grp = ext or lst
            if not grp: grp = lst
            w = max(grp, key=lambda z: z[1][0])      # rightmost wall
            mx = w[1][0] - (1.2 if kind == "innermid" else 0.2)
            if kind == 'walltop':   return (mx, w[1][1] - 0.8)
            if kind == 'wallbase':  return (mx, w[0][1] + 0.8)
            if kind == 'weep':      return (mx, w[0][1] + 1.9)
            if kind == 'wallmid2':  return (mx, (w[0][1] + w[1][1]) / 2.0 + 2.5)
            if kind == 'innermid2': return (mx, (w[0][1] + w[1][1]) / 2.0 - 2.5)
            return (mx, (w[0][1] + w[1][1]) / 2.0)
        w = max(lst, key=lambda z: (z[1][0] - z[0][0]))
        mx = w[1][0] - 2.0                            # near the right end
        if kind == 'top':   return (mx, w[0][1] + 0.5)   # roof surface at the right eave
        if kind == 'under': return (mx, w[0][1] - 1.6)
        if kind == 'ceil':  return (mx, w[0][1] - 3.2)
        if kind == 'below': return (mx, w[0][1] - 1.0)
        return (mx, (w[0][1] + w[1][1]) / 2.0)
    jobs = []
    for num, cat, kind in SPEC:
        p = pick(cat, kind)
        if p is None: continue
        jobs.append((num, p))
    L.append('%-18s %d bubbles: %s' % (nm, len(jobs), ','.join(j[0] for j in jobs)))
    if dry: continue
    t = Transaction(doc, 'OneTake: section keynote bubbles'); _prep(t); t.Start()
    kill = [x.Id for x in FEC(doc, v.Id).OfClass(IndependentTag)]
    if kill: doc.Delete(List[ElementId](kill))
    doc.Regenerate()
    bx = bb.Max.X - 5.2                      # bubble column, close to the building
    top = bb.Max.Y - 3.0
    step = (top - (bb.Min.Y + 3.0)) / max(1, len(jobs) - 1)
    def W(x, y):
        return tfm.OfPoint(_XYZ(x, y, 0.0))
    n = 0
    for i, (num, (tx, ty)) in enumerate(jobs):
        by = top - i * step
        try:
            doc.Create.NewDetailCurve(v, Line.CreateBound(W(tx, ty), W(bx - R, by)))
            c = W(bx, by)
            xa = (W(bx + 1, by) - c).Normalize()
            ya = (W(bx, by + 1) - c).Normalize()
            doc.Create.NewDetailCurve(v, Arc.Create(c, R, 0.0, math.pi, xa, ya))
            doc.Create.NewDetailCurve(v, Arc.Create(c, R, math.pi, 2 * math.pi, xa, ya))
            o = TextNoteOptions(tt.Id)
            o.HorizontalAlignment = HorizontalTextAlignment.Center
            TextNote.Create(doc, v.Id, W(bx, by + 0.28), num, o)
            n += 1
        except Exception as ex:
            L.append('    %s fail %s' % (num, str(ex)[:50]))
    doc.Regenerate(); t.Commit()
    L.append('    placed %d bubbles (removed %d dead tags)' % (n, len(kill)))
result = '\n'.join(L)
