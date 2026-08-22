# Hide outliers ONE AT A TIME so a single un-hideable element doesn't fail the batch.
# args {"views":[...],"cats":[...],"margin":2.0,"dry":false}
from Autodesk.Revit.DB import View, FilteredElementCollector as FEC, XYZ as _XYZ, ElementId as EId
from System.Collections.Generic import List
L = []
dry = args.get('dry', False)
M = float(args.get('margin', 2.0))
t = None
if not dry:
    t = Transaction(doc, 'OneTake: hide outliers'); _prep(t); t.Start()
for nm in args['views']:
    vs = [x for x in FEC(doc).OfClass(View) if not x.IsTemplate and x.Name == nm]
    if not vs: L.append('%s not found' % nm); continue
    v = vs[0]; bb = v.CropBox; inv = bb.Transform.Inverse
    ok = 0; bad = 0; badcats = {}
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            cat = e.Category.Name if e.Category else ''
            if args.get('cats') and cat not in args['cats']: continue
            if e.IsHidden(v): continue
            b = e.get_BoundingBox(v)
            if b is None: continue
            xs = []; ys = []
            for cx in (b.Min.X, b.Max.X):
                for cy in (b.Min.Y, b.Max.Y):
                    for cz in (b.Min.Z, b.Max.Z):
                        p = inv.OfPoint(_XYZ(cx, cy, cz)); xs.append(p.X); ys.append(p.Y)
            over = max(bb.Min.X - min(xs), max(xs) - bb.Max.X,
                       bb.Min.Y - min(ys), max(ys) - bb.Max.Y)
            if over <= M: continue
            if dry: ok += 1; continue
            try:
                v.HideElements(List[EId]([e.Id])); ok += 1
            except Exception:
                bad += 1; badcats[cat] = badcats.get(cat, 0) + 1
        except Exception: pass
    if not dry: doc.Regenerate()
    L.append('%-24s hid %d, could not hide %d %s' % (nm[:24], ok, bad, badcats or ''))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
