# Recreate the 4 ADU elevations with corrected orientation (visible region = +BasisZ).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewFamilyType,
                               ViewFamily, ViewSection, BoundingBoxXYZ, Transform,
                               ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
kill = List[ElementId]()
for vid in [2244567, 2244576, 2244585, 2244594]:
    if doc.GetElement(ElementId(vid)) is not None: kill.Add(ElementId(vid))
vft = None
for x in FEC(doc).OfClass(ViewFamilyType):
    if x.ViewFamily == ViewFamily.Section: vft = x; break
CX, CY = 1160.75, 104.15
ZMIN, ZMAX = -4.0, 32.0
JOBS = [
 ('ADU North Elev', _XYZ(1, 0, 0),  _XYZ(0, -1, 0), _XYZ(CX, 126.0, 0), 36, 46),
 ('ADU South Elev', _XYZ(-1, 0, 0), _XYZ(0, 1, 0),  _XYZ(CX, 82.0, 0),  36, 46),
 ('ADU East Elev',  _XYZ(0, -1, 0), _XYZ(-1, 0, 0), _XYZ(1196.0, CY, 0), 25, 76),
 ('ADU West Elev',  _XYZ(0, 1, 0),  _XYZ(1, 0, 0),  _XYZ(1122.0, CY, 0), 25, 76),
]
L = []
t = Transaction(doc, 'OneTake: ADU elevations v2'); _prep(t); t.Start()
if kill.Count: doc.Delete(kill)
doc.Regenerate()
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
