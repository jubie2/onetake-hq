# Find elements in a view that extend beyond the crop. args {"view":"ADU - North Elevation","margin":2.0}
from Autodesk.Revit.DB import View, FilteredElementCollector as FEC, XYZ as _XYZ
name = args['view']; M = float(args.get('margin', 2.0))
v = [x for x in FEC(doc).OfClass(View) if not x.IsTemplate and x.Name == name][0]
bb = v.CropBox; inv = bb.Transform.Inverse
L = ['%s  crop local X %.1f..%.1f  Y %.1f..%.1f' % (v.Name, bb.Min.X, bb.Max.X, bb.Min.Y, bb.Max.Y)]
rows = []
for e in FEC(doc, v.Id).WhereElementIsNotElementType():
    try:
        b = e.get_BoundingBox(v)
        if b is None: continue
        xs, ys = [], []
        for cx in (b.Min.X, b.Max.X):
            for cy in (b.Min.Y, b.Max.Y):
                for cz in (b.Min.Z, b.Max.Z):
                    p = inv.OfPoint(_XYZ(cx, cy, cz))
                    xs.append(p.X); ys.append(p.Y)
        lo, hi = min(xs), max(xs)
        over = max(bb.Min.X - lo, hi - bb.Max.X)
        if over > M:
            cat = e.Category.Name if e.Category else '?'
            rows.append((over, '%-9s %-26s %-22s localX %8.1f..%8.1f  (over %6.1f ft)' %
                         (e.Id.Value, cat[:26], (e.Name or '')[:22], lo, hi, over)))
    except Exception:
        pass
rows.sort(reverse=True)
L.append('elements extending past the crop: %d' % len(rows))
for _, s in rows[:18]: L.append('  ' + s)
result = '\n'.join(L)
