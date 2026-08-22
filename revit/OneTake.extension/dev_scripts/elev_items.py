# What is actually visible on each ADU elevation, with family/type and view position.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, BuiltInParameter as BIP,
                               XYZ as _XYZ, Wall)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
for nm in args.get('views', ['ADU - South Elevation']):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    bb = v.CropBox; inv = bb.Transform.Inverse
    walls = []
    rows = []
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            cn = e.Category.Name if e.Category else ''
            if cn not in ('Windows', 'Doors', 'Generic Models', 'Lighting Fixtures',
                          'Walls', 'Generic Annotations'): continue
            b = e.get_BoundingBox(None)
            if b is None: continue
            c = _XYZ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0,
                     (b.Min.Z + b.Max.Z) / 2.0)
            if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
            q = inv.OfPoint(c)
            if not (bb.Min.X <= q.X <= bb.Max.X and bb.Min.Y <= q.Y <= bb.Max.Y): continue
            if cn == 'Walls':
                walls.append(abs(q.Z)); continue
            try: fam = '%s : %s' % (e.Symbol.Family.Name,
                                    e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString())
            except Exception: fam = '?'
            mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
            rows.append((abs(q.Z), cn, fam, mk.AsString() if mk else '', q.X, q.Y))
        except Exception: pass
    nearD = min(walls) if walls else 0
    L.append('=== %s   nearest wall depth %.1f ft' % (nm, nearD))
    rows.sort()
    for d, cn, fam, mk, qx, qy in rows[:14]:
        L.append('   d=%5.1f %-16s %-42s mark=%-4s at (%.1f, %.1f)' % (d, cn, fam[:42], mk, qx, qy))
result = '\n'.join(L)
