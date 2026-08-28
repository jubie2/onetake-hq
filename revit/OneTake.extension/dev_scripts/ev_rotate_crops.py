# Rotate the new mech/elec 1st-floor views' crops to match 718579 (14.3 deg),
# then set the crop window to the same world region.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Line,
                               XYZ as _XYZ, ElementTransformUtils, BoundingBoxXYZ,
                               BuiltInCategory as BIC, Wall)
src = doc.GetElement(ElementId(718579))
scb = src.CropBox; ST = scb.Transform
corners = [ST.OfPoint(_XYZ(scb.Min.X, scb.Min.Y, 0)),
           ST.OfPoint(_XYZ(scb.Max.X, scb.Min.Y, 0)),
           ST.OfPoint(_XYZ(scb.Max.X, scb.Max.Y, 0)),
           ST.OfPoint(_XYZ(scb.Min.X, scb.Max.Y, 0))]
ang = math.atan2(ST.BasisX.Y, ST.BasisX.X)
L = ['target angle %.4f rad' % ang]
def cropelem(v):
    ids0 = set(e.Value for e in FEC(doc, v.Id).ToElementIds())
    v.CropBoxVisible = True; doc.Regenerate()
    ids1 = set(e.Value for e in FEC(doc, v.Id).ToElementIds())
    new = ids1 - ids0
    return [ElementId(i) for i in new]
t = Transaction(doc, 'OneTake: rotate crops'); _prep(t); t.Start()
for vid in [2244950, 2244930]:
    v = doc.GetElement(ElementId(vid))
    v.CropBoxVisible = False; doc.Regenerate()
    ce = cropelem(v)
    if not ce:
        L.append('%s: crop element NOT found' % vid); continue
    cb = v.CropBox; T = cb.Transform
    cur = math.atan2(T.BasisX.Y, T.BasisX.X)
    delta = ang - cur
    cen = T.OfPoint(_XYZ((cb.Min.X + cb.Max.X) / 2, (cb.Min.Y + cb.Max.Y) / 2, 0))
    axis = Line.CreateBound(cen, _XYZ(cen.X, cen.Y, cen.Z + 1))
    try:
        ElementTransformUtils.RotateElement(doc, ce[0], axis, delta)
        doc.Regenerate()
    except Exception as ex:
        L.append('%s rotate FAIL %s' % (vid, str(ex)[:50])); continue
    cb2 = v.CropBox; T2 = cb2.Transform
    got = math.atan2(T2.BasisX.Y, T2.BasisX.X)
    if abs(got - ang) > 0.001:
        try:
            ElementTransformUtils.RotateElement(doc, ce[0], axis, -2 * delta)
            doc.Regenerate()
            cb2 = v.CropBox; T2 = cb2.Transform
            got = math.atan2(T2.BasisX.Y, T2.BasisX.X)
        except Exception as ex:
            L.append('%s flip FAIL %s' % (vid, str(ex)[:40]))
    inv = T2.Inverse
    loc = [inv.OfPoint(c) for c in corners]
    nb = BoundingBoxXYZ(); nb.Transform = T2
    nb.Min = _XYZ(min(p.X for p in loc), min(p.Y for p in loc), cb2.Min.Z)
    nb.Max = _XYZ(max(p.X for p in loc), max(p.Y for p in loc), cb2.Max.Z)
    v.CropBox = nb
    v.CropBoxVisible = False
    doc.Regenerate()
    nw = len(list(FEC(doc, v.Id).OfClass(Wall)))
    ne = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType()))
    L.append('%s: angle %.4f, walls=%d elec=%d' % (vid, got, nw, ne))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
