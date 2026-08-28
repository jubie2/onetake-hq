# Create 4 elevation-style sections of the new ADU building, scale 1:64.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewFamilyType,
                               ViewFamily, ViewSection, BoundingBoxXYZ, Transform,
                               XYZ as _XYZ)
vft = None
for x in FEC(doc).OfClass(ViewFamilyType):
    if x.ViewFamily == ViewFamily.Section: vft = x; break
CX, CY = 1160.75, 104.15
ZMIN, ZMAX = -4.0, 32.0
JOBS = [
 # name, basisX, basisZ(toward viewer), origin, halfwidth, fardepth
 ('ADU North Elev',  _XYZ(-1, 0, 0), _XYZ(0, 1, 0),  _XYZ(CX, 126.0, 0), 36, 46),
 ('ADU South Elev',  _XYZ(1, 0, 0),  _XYZ(0, -1, 0), _XYZ(CX, 82.0, 0),  36, 46),
 ('ADU East Elev',   _XYZ(0, 1, 0),  _XYZ(1, 0, 0),  _XYZ(1196.0, CY, 0), 25, 76),
 ('ADU West Elev',   _XYZ(0, -1, 0), _XYZ(-1, 0, 0), _XYZ(1122.0, CY, 0), 25, 76),
]
L = []
t = Transaction(doc, 'OneTake: ADU elevations'); _prep(t); t.Start()
for name, bx, bz, org, hw, depth in JOBS:
    tf = Transform.Identity
    tf.Origin = org
    tf.BasisX = bx
    tf.BasisY = _XYZ(0, 0, 1)
    tf.BasisZ = bz
    bb = BoundingBoxXYZ()
    bb.Transform = tf
    bb.Min = _XYZ(-hw, ZMIN, 0)
    bb.Max = _XYZ(hw, ZMAX, depth)
    v = ViewSection.CreateSection(doc, vft.Id, bb)
    v.Name = name
    v.Scale = 64
    L.append('%s id %s' % (name, v.Id.Value))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
