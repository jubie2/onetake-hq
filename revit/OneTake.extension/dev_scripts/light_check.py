from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, BuiltInCategory as BIC,
                               BuiltInParameter as BIP, XYZ as _XYZ)
L = []
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L.append('=== the 4 ADU lights')
lights = []
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    b = e.get_BoundingBox(None)
    if b is None: continue
    cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
    if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
    lights.append(e)
    L.append('  %s at (%.1f, %.1f, %.1f)  bbox z %.1f..%.1f' % (
        e.Id, cx, cy, (b.Min.Z + b.Max.Z) / 2.0, b.Min.Z, b.Max.Z))
for nm in ('ADU - North Elevation', 'ADU - South Elevation',
           'ADU - East Elevation', 'ADU - West Elevation'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    got = [e.Id for e in FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures)
           .WhereElementIsNotElementType()]
    hid = [str(e.Id) for e in lights if e.IsHidden(v)]
    bb = v.CropBox; inv = bb.Transform.Inverse
    pos = []
    for e in lights:
        b = e.get_BoundingBox(None)
        q = inv.OfPoint(_XYZ((b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0,
                             (b.Min.Z + b.Max.Z) / 2.0))
        inx = bb.Min.X <= q.X <= bb.Max.X and bb.Min.Y <= q.Y <= bb.Max.Y
        pos.append('%s:(%.0f,%.0f,d%.0f)%s' % (e.Id, q.X, q.Y, abs(q.Z), '' if inx else ' OUT'))
    L.append('%-22s in view: %d   element-hidden: %s' % (nm, len(got), hid or '-'))
    L.append('     %s' % '  '.join(pos))
result = '\n'.join(L)
