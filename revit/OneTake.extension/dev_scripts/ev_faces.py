# Dump doors/windows/lights/railings of the new ADU with world coords + face guess,
# and check which keynote tag families exist in this doc.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, FamilyInstance,
                               FamilySymbol, BuiltInCategory as BIC)
X0, X1, Y0, Y1 = 1120, 1200, 80, 128
def face(p):
    f = []
    if abs(p.Y - 85.9) < 2.0: f.append('S')
    if abs(p.Y - 122.4) < 2.0: f.append('N')
    if abs(p.X - 1129.2) < 2.0: f.append('W')
    if abs(p.X - 1192.3) < 2.0: f.append('E')
    return '/'.join(f) or '-'
L = []
for catname, cat in [('DOOR', BIC.OST_Doors), ('WIN', BIC.OST_Windows),
                     ('LIGHT', BIC.OST_LightingFixtures)]:
    for e in FEC(doc).OfCategory(cat).WhereElementIsNotElementType():
        try:
            p = e.Location.Point
        except Exception:
            bb = e.get_BoundingBox(None)
            if bb is None: continue
            from Autodesk.Revit.DB import XYZ as _XYZ
            p = _XYZ((bb.Min.X + bb.Max.X) / 2, (bb.Min.Y + bb.Max.Y) / 2, bb.Min.Z)
        if not (X0 < p.X < X1 and Y0 < p.Y < Y1): continue
        w = 0
        try: w = e.Symbol.get_Parameter(__import__('Autodesk').Revit.DB.BuiltInParameter.DOOR_WIDTH).AsDouble()
        except Exception: pass
        L.append('%s %s %s (%.1f,%.1f,%.1f) w=%.1f %s' % (
            catname, e.Id.Value, face(p), p.X, p.Y, p.Z, w, e.Symbol.Family.Name[:24]))
for e in FEC(doc).OfCategory(BIC.OST_StairsRailing).WhereElementIsNotElementType():
    bb = e.get_BoundingBox(None)
    if bb is None: continue
    cx = (bb.Min.X + bb.Max.X) / 2; cy = (bb.Min.Y + bb.Max.Y) / 2
    if X0 < cx < X1 and Y0 - 10 < cy < Y1:
        L.append('RAIL %s (%.1f,%.1f) z %.1f..%.1f span x %.1f..%.1f y %.1f..%.1f' % (
            e.Id.Value, cx, cy, bb.Min.Z, bb.Max.Z, bb.Min.X, bb.Max.X, bb.Min.Y, bb.Max.Y))
fams = set()
for s in FEC(doc).OfClass(FamilySymbol).OfCategory(BIC.OST_GenericAnnotation):
    if 'TAG' in s.Family.Name.upper(): fams.add(s.Family.Name)
L.append('TAG FAMILIES: %s' % sorted(fams))
result = '\n'.join(L)
