# For every elevation keynote: what it points at, and whether anything is DRAWN there.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, XYZ as _XYZ, Wall)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
LEG = {'1': 'ROOF SHINGLES', '2': 'WINDOW PER SCHEDULE', '3': '14"x24" LOUVER',
       '4': 'STUCCO AT EXT WALL', '5': 'EXTERIOR LIGHT', '6': 'EXTERIOR DOOR'}
L = []
for nm in ('ADU - North Elevation', 'ADU - South Elevation',
           'ADU - East Elevation', 'ADU - West Elevation'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    bb = v.CropBox; inv = bb.Transform.Inverse
    visible = set()
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        visible.add(e.Id.IntegerValue)
    pool = []
    for e in FEC(doc).OfCategory(BIC.OST_Roofs).WhereElementIsNotElementType(): pool.append(('1', e))
    for e in FEC(doc).OfCategory(BIC.OST_Windows).WhereElementIsNotElementType(): pool.append(('2', e))
    for e in FEC(doc).OfCategory(BIC.OST_GenericModel).WhereElementIsNotElementType(): pool.append(('3', e))
    for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType(): pool.append(('5', e))
    for e in FEC(doc).OfCategory(BIC.OST_Doors).WhereElementIsNotElementType(): pool.append(('6', e))
    walls = []
    for w in FEC(doc).OfClass(Wall):
        b = w.get_BoundingBox(None)
        if b is None: continue
        c = ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0)
        if not (X0 <= c[0] <= X1 and Y0 <= c[1] <= Y1): continue
        q = inv.OfPoint(_XYZ(c[0], c[1], (b.Min.Z + b.Max.Z) / 2.0))
        walls.append(abs(q.Z))
    nearD = min(walls) if walls else 0
    best = {}
    for key, e in pool:
        try:
            b = e.get_BoundingBox(None)
            if b is None: continue
            c = _XYZ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0,
                     (b.Min.Z + b.Max.Z) / 2.0)
            if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
            q = inv.OfPoint(c)
            if not (bb.Min.X + 0.5 <= q.X <= bb.Max.X - 0.5): continue
            if not (bb.Min.Y + 0.5 <= q.Y <= bb.Max.Y - 0.5): continue
            if key == '2' and (b.Max.Z - b.Min.Z) <= 2.5: continue
            if key == '6' and (b.Max.X - b.Min.X) <= 2.4: continue
            if key == '3' and 'ouver' not in e.Symbol.Family.Name and 'ent' not in e.Symbol.Family.Name:
                continue
            d = abs(q.Z)
            if key not in best or d < best[key][0]:
                try: fam = e.Symbol.Family.Name
                except Exception: fam = e.Name if hasattr(e, 'Name') else '?'
                best[key] = (d, e, fam)
        except Exception: pass
    L.append('=== %s   near face at depth %.1f ft' % (nm, nearD))
    for k in ('1', '2', '3', '4', '5', '6'):
        if k == '4':
            L.append('   %s %-22s -> blank stucco wall on this face   DRAWN' % (k, LEG[k]))
            continue
        if k not in best:
            L.append('   %s %-22s -> nothing found' % (k, LEG[k])); continue
        d, e, fam = best[k]
        drawn = e.Id.IntegerValue in visible
        behind = d - nearD
        L.append('   %s %-22s -> %-30s depth %5.1f (%+.1f past the face)  %s' % (
            k, LEG[k], fam[:30], d, behind, 'DRAWN' if drawn else '*** NOT DRAWN HERE ***'))
result = '\n'.join(L)
