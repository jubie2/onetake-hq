# Re-cut the 4 elevations + 4 sections SQUARE to the building (14.3 deg), replacing
# the world-axis-aligned ones.  bx = paper-right, by = world Z, bz = bx X by = side
# of the cut plane that is visible.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewFamilyType,
                               ViewFamily, ViewSection, BoundingBoxXYZ, Transform,
                               ElementId, XYZ as _XYZ, Category,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from System.Collections.Generic import List
A = math.radians(14.3)
UX, UY = math.cos(A), math.sin(A)      # building "east"
VX, VY = -math.sin(A), math.cos(A)     # building "north"
CX, CY = 1161.1251, 98.8210            # oriented-box center (world)
HS, HT = 30.22, 19.57                  # half extents along u, v
def W(s, t):                           # building station -> world XY
    return (CX + UX * s + VX * t, CY + UY * s + VY * t)
U = _XYZ(UX, UY, 0); V = _XYZ(VX, VY, 0)
nU = _XYZ(-UX, -UY, 0); nV = _XYZ(-VX, -VY, 0)
# name, title, bx, origin(s,t), halfwidth, depth
JOBS = [
 ('ADU North Elev', 'North Elev.',  U,  (0.0,  HT + 6.0), 35.0, 52.0),
 ('ADU South Elev', 'South Elev.',  nU, (0.0, -HT - 6.0), 35.0, 52.0),
 ('ADU East Elev',  'East Elev.',   nV, ( HS + 6.0, 0.0), 25.0, 73.0),
 ('ADU West Elev',  'West Elev.',   V,  (-HS - 6.0, 0.0), 25.0, 73.0),
 ('ADU Section 1',  'Section 1',    V,  (-20.0, 0.0), 25.0, 58.0),
 ('ADU Section 2',  'Section 2',    nV, ( 14.0, 0.0), 25.0, 52.0),
 ('ADU Section 3',  'Section 3',    U,  (0.0,  11.0), 35.0, 39.0),
 ('ADU Section 4',  'Section 4',    nU, (0.0,  -3.0), 35.0, 31.0),
]
OLD = [2244603, 2244612, 2244621, 2244630, 2244668, 2244677, 2244686, 2244695]
vft = None
for x in FEC(doc).OfClass(ViewFamilyType):
    if x.ViewFamily == ViewFamily.Section: vft = x; break
seccat = Category.GetCategory(doc, BIC.OST_Sections)
elevcat = Category.GetCategory(doc, BIC.OST_Elev)
L = []
t = Transaction(doc, 'OneTake: re-cut square to building'); _prep(t); t.Start()
kill = List[ElementId]()
for vid in OLD:
    if doc.GetElement(ElementId(vid)) is not None: kill.Add(ElementId(vid))
if kill.Count:
    doc.Delete(kill); L.append('deleted %d old views' % kill.Count)
doc.Regenerate()
for name, title, bx, (os_, ot), hw, depth in JOBS:
    ox, oy = W(os_, ot)
    tf = Transform.Identity
    tf.Origin = _XYZ(ox, oy, 0)
    tf.BasisX = bx
    tf.BasisY = _XYZ(0, 0, 1)
    tf.BasisZ = bx.CrossProduct(_XYZ(0, 0, 1))
    bb = BoundingBoxXYZ()
    bb.Transform = tf
    bb.Min = _XYZ(-hw, -4.0, 0)
    bb.Max = _XYZ(hw, 32.0, depth)
    v = ViewSection.CreateSection(doc, vft.Id, bb)
    v.Name = name
    v.Scale = 64
    p = v.get_Parameter(BIP.VIEW_DESCRIPTION)
    if p and not p.IsReadOnly: p.Set(title)
    for c in (seccat, elevcat):
        try: v.SetCategoryHidden(c.Id, True)
        except Exception: pass
    d = v.ViewDirection
    L.append('%-16s id %-9s origin (%.2f,%.2f) viewdir (%.3f,%.3f)' % (
        name, v.Id.Value, ox, oy, d.X, d.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
