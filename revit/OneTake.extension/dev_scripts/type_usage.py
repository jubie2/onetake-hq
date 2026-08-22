# Are the ADU's wall/roof/floor types used outside the ADU? And what keynote do they carry?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, ElementId)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
def tname(t):
    try:
        p = t.get_Parameter(BIP.SYMBOL_NAME_PARAM)
        if p and p.AsString(): return p.AsString()
    except Exception: pass
    try:
        p = t.get_Parameter(BIP.ALL_MODEL_TYPE_NAME)
        if p and p.AsString(): return p.AsString()
    except Exception: pass
    return str(t.Id)
stats = {}
for bic, cn in ((BIC.OST_Walls, 'Walls'), (BIC.OST_Roofs, 'Roofs'),
                (BIC.OST_Floors, 'Floors'), (BIC.OST_Ceilings, 'Ceilings')):
    for e in FEC(doc).OfCategory(bic).WhereElementIsNotElementType():
        try:
            b = e.get_BoundingBox(None)
            if b is None: continue
            cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
            inside = X0 <= cx <= X1 and Y0 <= cy <= Y1
            t = doc.GetElement(e.GetTypeId())
            k = (cn, t.Id.IntegerValue, tname(t))
            d = stats.setdefault(k, [0, 0, None])
            d[0 if inside else 1] += 1
            if d[2] is None:
                p = t.get_Parameter(BIP.KEYNOTE_PARAM)
                d[2] = (p.AsString() if p else None, p is not None and not p.IsReadOnly)
        except Exception: pass
L = ['%-9s %-32s in-ADU outside  keynote  editable' % ('cat', 'type')]
for k in sorted(stats, key=lambda z: (-stats[z][0], z[0])):
    d = stats[k]
    if d[0] == 0: continue
    L.append('%-9s %-32s %5d %6d   %-8r %s' % (k[0], k[2][:32], d[0], d[1], d[2][0], d[2][1]))
result = '\n'.join(L)
