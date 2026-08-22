# Move a section view's cut plane by shifting its crop transform origin.
# args {"view":"ADU - Section 4","d":[-8.4,0,0]}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSection, BoundingBoxXYZ,
                               XYZ as _XYZ, Transform)
nm = args['view']; d = args.get('d', [0, 0, 0])
v = None
for x in FEC(doc).OfClass(ViewSection):
    if not x.IsTemplate and x.Name == nm: v = x; break
L = []
o = v.Origin
L.append('before origin (%.2f, %.2f, %.2f)' % (o.X, o.Y, o.Z))
t = Transaction(doc, 'OneTake: move section'); _prep(t); t.Start()
bb = v.CropBox
tf = bb.Transform
nt = Transform.Identity
nt.BasisX = tf.BasisX; nt.BasisY = tf.BasisY; nt.BasisZ = tf.BasisZ
nt.Origin = _XYZ(tf.Origin.X + d[0], tf.Origin.Y + d[1], tf.Origin.Z + d[2])
nb = BoundingBoxXYZ()
nb.Transform = nt
nb.Min = bb.Min
nb.Max = bb.Max
v.CropBox = nb
doc.Regenerate()
t.Commit()
o2 = v.Origin
L.append('after  origin (%.2f, %.2f, %.2f)' % (o2.X, o2.Y, o2.Z))
result = '\n'.join(L)
