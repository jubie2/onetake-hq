# Redo Site crop with 4-corner mapping (view is rotated), then re-place viewport.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               XYZ as _XYZ, BoundingBoxXYZ)
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A02': sh = s
v = None
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    vv = doc.GetElement(vp.ViewId)
    if vv.Name == 'Site': v = vv; svp = vp
t = Transaction(doc, 'OneTake: A02 crop redo'); _prep(t); t.Start()
cb = v.CropBox; T = cb.Transform; inv = T.Inverse
W = [(1085, 20), (1235, 20), (1235, 128), (1085, 128)]
loc = [inv.OfPoint(_XYZ(x, y, T.Origin.Z)) for (x, y) in W]
xs = [p.X for p in loc]; ys = [p.Y for p in loc]
nb = BoundingBoxXYZ(); nb.Transform = T
nb.Min = _XYZ(min(xs), min(ys), cb.Min.Z)
nb.Max = _XYZ(max(xs), max(ys), cb.Max.Z)
v.CropBox = nb
doc.Regenerate()
svp.SetBoxCenter(_XYZ(0.85, 1.32, 0))
doc.Regenerate()
ol = svp.GetBoxOutline()
try: svp.LabelOffset = _XYZ(0.30, -0.03, 0)
except Exception: pass
doc.Regenerate(); t.Commit()
result = 'Site box (%.2f,%.2f)-(%.2f,%.2f)' % (
    ol.MinimumPoint.X, ol.MinimumPoint.Y, ol.MaximumPoint.X, ol.MaximumPoint.Y)
