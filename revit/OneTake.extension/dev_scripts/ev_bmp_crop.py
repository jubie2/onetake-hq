# Tighten BMP view crop to the work area and place in A06 top strip.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ, BoundingBoxXYZ,
                               BuiltInParameter as BIP)
v = doc.GetElement(ElementId(2244991))
t = Transaction(doc, 'OneTake: BMP crop'); _prep(t); t.Start()
cb = v.CropBox; T = cb.Transform; inv = T.Inverse
W = [(1100, 53), (1212, 53), (1212, 137), (1100, 137)]
loc = [inv.OfPoint(_XYZ(x, y, T.Origin.Z)) for (x, y) in W]
nb = BoundingBoxXYZ(); nb.Transform = T
nb.Min = _XYZ(min(p.X for p in loc), min(p.Y for p in loc), cb.Min.Z)
nb.Max = _XYZ(max(p.X for p in loc), max(p.Y for p in loc), cb.Max.Z)
v.CropBox = nb
v.CropBoxActive = True
v.CropBoxVisible = False
p = v.get_Parameter(BIP.VIEWER_ANNOTATION_CROP_ACTIVE)
if p and not p.IsReadOnly: p.Set(1)
doc.Regenerate()
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A06':
        for vp in FEC(doc, s.Id).OfClass(Viewport):
            if vp.ViewId.Value == 2244991:
                vp.SetBoxCenter(_XYZ(1.45, 1.55, 0))
                doc.Regenerate()
                try: vp.LabelOffset = _XYZ(0.35, 0.0, 0)
                except Exception: pass
                ol = vp.GetBoxOutline()
                L.append('vp (%.2f,%.2f)-(%.2f,%.2f)' % (
                    ol.MinimumPoint.X, ol.MinimumPoint.Y,
                    ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
