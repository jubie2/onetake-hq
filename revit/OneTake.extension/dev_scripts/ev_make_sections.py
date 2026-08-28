# Create 4 building sections of the new ADU (visible region = +BasisZ).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewFamilyType,
                               ViewFamily, ViewSection, BoundingBoxXYZ, Transform,
                               XYZ as _XYZ, BuiltInParameter as BIP)
vft = None
for x in FEC(doc).OfClass(ViewFamilyType):
    if x.ViewFamily == ViewFamily.Section: vft = x; break
CY = 104.15
JOBS = [
 ('ADU Section 1', 'Section 1', _XYZ(0, -1, 0), _XYZ(-1, 0, 0), _XYZ(1150, CY, 0), 27, 23),
 ('ADU Section 2', 'Section 2', _XYZ(0, 1, 0),  _XYZ(1, 0, 0),  _XYZ(1168, CY, 0), 27, 27),
 ('ADU Section 3', 'Section 3', _XYZ(-1, 0, 0), _XYZ(0, 1, 0),  _XYZ(1160.75, 100, 0), 37, 25),
 ('ADU Section 4', 'Section 4', _XYZ(1, 0, 0),  _XYZ(0, -1, 0), _XYZ(1160.75, 110, 0), 37, 27),
]
L = []
t = Transaction(doc, 'OneTake: ADU sections'); _prep(t); t.Start()
for name, title, bx, bz, org, hw, depth in JOBS:
    tf = Transform.Identity
    tf.Origin = org
    tf.BasisX = bx
    tf.BasisY = _XYZ(0, 0, 1)
    tf.BasisZ = bz
    bb = BoundingBoxXYZ()
    bb.Transform = tf
    bb.Min = _XYZ(-hw, -4.0, 0)
    bb.Max = _XYZ(hw, 32.0, depth)
    v = ViewSection.CreateSection(doc, vft.Id, bb)
    v.Name = name
    v.Scale = 64
    p = v.get_Parameter(BIP.VIEW_DESCRIPTION)
    if p and not p.IsReadOnly: p.Set(title)
    L.append('%s id %s' % (name, v.Id.Value))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
