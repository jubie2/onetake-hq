# Flip the ADU exterior lamps to the outside face of the wall.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, BuiltInCategory as BIC, View,
                               XYZ as _XYZ)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
lights = []
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    b = e.get_BoundingBox(None)
    if b is None: continue
    cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
    if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
    lights.append(e)
t = Transaction(doc, 'OneTake: flip lamps'); _prep(t); t.Start()
for e in lights:
    b = e.get_BoundingBox(None)
    before = (b.Min.X + b.Max.X) / 2.0
    try:
        e.flipFacing()
    except Exception as ex:
        L.append('  flip failed %s' % str(ex)[:50])
doc.Regenerate()
for e in lights:
    b = e.get_BoundingBox(None)
    L.append('  %s now at (%.2f, %.2f, %.1f)' % (
        e.Id, (b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0, (b.Min.Z + b.Max.Z) / 2.0))
t.Commit()
for nm in ('ADU - East Elevation', 'ADU - West Elevation'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    n = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures)
                 .WhereElementIsNotElementType()))
    L.append('%-22s lights now visible: %d' % (nm, n))
result = '\n'.join(L)
