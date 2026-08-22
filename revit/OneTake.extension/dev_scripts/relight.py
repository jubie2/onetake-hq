# Delete the ADU lamps and re-place them clearly OUTSIDE the wall face so they read in elevation.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, Level, FamilySymbol,
                               BuiltInCategory as BIC, BuiltInParameter as BIP, ElementId,
                               XYZ as _XYZ, View)
from Autodesk.Revit.DB.Structure import StructuralType
from System.Collections.Generic import List
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
sym = None
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        if s.Category is None or s.Category.Id.IntegerValue != int(BIC.OST_LightingFixtures): continue
        if s.Family.Name == 'Antique_Doorwall_lamp_10251': sym = s; break
    except Exception: pass
old = []
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    b = e.get_BoundingBox(None)
    if b is None: continue
    cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
    if X0 <= cx <= X1 and Y0 <= cy <= Y1: old.append(e.Id)
# place the point OUTSIDE the wall so Revit hosts on the exterior face
SPOTS = [(1187.4, -138.4, 'east wall, outside'), (1157.0, -145.0, 'west wall, outside')]
lv = {}
for l in FEC(doc).OfClass(Level):
    if l.Name in ('1st Floor Level', '2nd FLoor Plan'): lv[l.Name] = l
t = Transaction(doc, 'OneTake: re-place ADU lamps'); _prep(t); t.Start()
if old:
    doc.Delete(List[ElementId](old)); doc.Regenerate()
    L.append('removed %d old lamps' % len(old))
if not sym.IsActive: sym.Activate()
doc.Regenerate()
made = []
for lname in ('1st Floor Level', '2nd FLoor Plan'):
    lev = lv[lname]
    for wx, wy, why in SPOTS:
        host = None; bestd = 99
        for w in FEC(doc).OfClass(Wall):
            try:
                if doc.GetElement(w.LevelId).Name != lname: continue
                if str(w.WallType.Function) != 'Exterior': continue
                c = w.Location.Curve
                p = c.Project(_XYZ(wx, wy, c.GetEndPoint(0).Z)).XYZPoint
                d = ((p.X - wx) ** 2 + (p.Y - wy) ** 2) ** 0.5
                if d < bestd: bestd = d; host = w
            except Exception: pass
        if host is None: continue
        try:
            fi = doc.Create.NewFamilyInstance(_XYZ(wx, wy, lev.Elevation + 6.5), sym, host,
                                              lev, StructuralType.NonStructural)
            made.append((fi, lname, why))
        except Exception as ex:
            L.append('  place fail %s' % str(ex)[:50])
doc.Regenerate()
for fi, lname, why in made:
    b = fi.get_BoundingBox(None)
    L.append('  %-16s %-22s centre x %.2f y %.2f' % (
        lname, why, (b.Min.X + b.Max.X) / 2.0, (b.Min.Y + b.Max.Y) / 2.0))
t.Commit()
for nm in ('ADU - East Elevation', 'ADU - West Elevation',
           'ADU - North Elevation', 'ADU - South Elevation'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    n = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures)
                 .WhereElementIsNotElementType()))
    L.append('%-24s lamps visible: %d' % (nm, n))
result = '\n'.join(L)
