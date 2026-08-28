# Make the 2nd FLoor Level plan crop match the 1st Floor Plan crop (same world
# region), so the two plans read identically on A101.
from Autodesk.Revit.DB import ElementId, XYZ as _XYZ, BoundingBoxXYZ
v1 = doc.GetElement(ElementId(718579))   # 1st Floor Plan
v2 = doc.GetElement(ElementId(1715860))  # 2nd FLoor Level
L = []
L.append('scales: v1=1:%d v2=1:%d' % (v1.Scale, v2.Scale))
cb1 = v1.CropBox; T1 = cb1.Transform
# world corners of v1 crop (at local z=0 plane)
corners = [
    T1.OfPoint(_XYZ(cb1.Min.X, cb1.Min.Y, 0)),
    T1.OfPoint(_XYZ(cb1.Max.X, cb1.Min.Y, 0)),
    T1.OfPoint(_XYZ(cb1.Max.X, cb1.Max.Y, 0)),
    T1.OfPoint(_XYZ(cb1.Min.X, cb1.Max.Y, 0)),
]
wx = [c.X for c in corners]; wy = [c.Y for c in corners]
L.append('v1 crop world: (%.2f,%.2f)-(%.2f,%.2f)' % (min(wx), min(wy), max(wx), max(wy)))
cb2 = v2.CropBox; T2 = cb2.Transform; inv2 = T2.Inverse
lc = [inv2.OfPoint(_XYZ(c.X, c.Y, T2.Origin.Z)) for c in corners]
lx = [c.X for c in lc]; ly = [c.Y for c in lc]
nb = BoundingBoxXYZ()
nb.Transform = T2
nb.Min = _XYZ(min(lx), min(ly), cb2.Min.Z)
nb.Max = _XYZ(max(lx), max(ly), cb2.Max.Z)
t = Transaction(doc, 'OneTake: 2nd floor crop match'); _prep(t); t.Start()
v2.CropBox = nb
v2.CropBoxActive = True
v2.CropBoxVisible = v1.CropBoxVisible
doc.Regenerate()
t.Commit()
cbn = v2.CropBox
L.append('v2 crop now local (%.1f,%.1f)-(%.1f,%.1f)' % (
    cbn.Min.X, cbn.Min.Y, cbn.Max.X, cbn.Max.Y))
Tn = cbn.Transform
cn = [Tn.OfPoint(_XYZ(cbn.Min.X, cbn.Min.Y, 0)), Tn.OfPoint(_XYZ(cbn.Max.X, cbn.Max.Y, 0))]
L.append('v2 crop world now: (%.2f,%.2f)-(%.2f,%.2f)' % (
    min(c.X for c in cn), min(c.Y for c in cn), max(c.X for c in cn), max(c.Y for c in cn)))
result = '\n'.join(L)
