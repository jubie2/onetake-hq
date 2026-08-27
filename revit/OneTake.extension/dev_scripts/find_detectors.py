# Find smoke/CO detector family instances in the ADU region, and which views show them.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, FamilyInstance,
                               XYZ as _XYZ)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
KEYS = ('smoke', 'carbon', 'detector', 'alarm', 'co_')
hits = []
L = []
for e in FEC(doc).OfClass(FamilyInstance):
    try:
        fn = e.Symbol.Family.Name.lower()
        if not any(k in fn for k in KEYS): continue
        b = e.get_BoundingBox(None)
        if b is None: continue
        c = _XYZ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2, (b.Min.Z + b.Max.Z) / 2)
        if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
        hits.append(e.Id.Value)
        L.append('id %s [%s] %s (%.1f,%.1f) z%.1f' % (e.Id.Value, e.Symbol.Family.Name[:30],
                 e.Category.Name[:20], c.X, c.Y, c.Z))
    except Exception: pass
for nm in ('ADU - 1st Floor Electrical Plan', 'ADU - 2nd Floor Electrical Plan',
           'ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan',
           'ADU - 1st Floor Plan', 'ADU - 2nd Floor Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: continue
    seen = [e.Id.Value for e in FEC(doc, v.Id).OfClass(FamilyInstance)
            if e.Id.Value in hits]
    L.append('%s shows: %s' % (nm, seen or 'none'))
result = '\n'.join(L)
