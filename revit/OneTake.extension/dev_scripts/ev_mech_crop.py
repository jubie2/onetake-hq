# Fix mech plan crops: copy the source views' local crop boxes verbatim, re-center.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               Viewport, BoundingBoxXYZ, XYZ as _XYZ)
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
JOBS = [('1st Floor Plan', 'ADU 1st Floor Mech Plan', 2.36),
        ('2nd FLoor Level', 'ADU 2nd Floor Mech Plan', 1.30)]
L = []
t = Transaction(doc, 'OneTake: mech crops'); _prep(t); t.Start()
for srcn, dstn, cx in JOBS:
    src = getview(srcn); dst = getview(dstn)
    scb = src.CropBox
    nb = BoundingBoxXYZ(); nb.Transform = scb.Transform
    nb.Min = scb.Min; nb.Max = scb.Max
    dst.CropBox = nb
    dst.CropBoxActive = True
    try:
        dst.GetCropRegionShapeManager().RemoveCropRegionShape()
    except Exception: pass
doc.Regenerate()
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A200': sh = s
for vp in FEC(doc, sh.Id).OfClass(Viewport):
    v = doc.GetElement(vp.ViewId)
    for srcn, dstn, cx in JOBS:
        if v.Name == dstn:
            vp.SetBoxCenter(_XYZ(cx, 1.42, 0))
            doc.Regenerate()
            ol = vp.GetBoxOutline()
            L.append('%s box (%.2f,%.2f)-(%.2f,%.2f)' % (
                dstn, ol.MinimumPoint.X, ol.MinimumPoint.Y,
                ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
