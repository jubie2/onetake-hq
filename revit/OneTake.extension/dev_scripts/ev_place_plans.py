# A101: bring the two floor-plan viewports onto the sheet, 3/16" scale,
# 2nd floor left / 1st floor right, titles just below each plan.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ)
JOBS = {718579: (1.66, 1.28), 1715860: (0.58, 1.28)}  # view id -> sheet center
L = []
t = Transaction(doc, 'OneTake: A101 place plans'); _prep(t); t.Start()
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A101': continue
    for vp in FEC(doc, s.Id).OfClass(Viewport):
        vid = vp.ViewId.Value
        if vid in JOBS:
            v = doc.GetElement(vp.ViewId)
            if v.Scale != 64: v.Scale = 64
            doc.Regenerate()
            cx, cy = JOBS[vid]
            vp.SetBoxCenter(_XYZ(cx, cy, 0))
            doc.Regenerate()
            ol = vp.GetBoxOutline()
            try:
                vp.LabelOffset = _XYZ(0.06, -0.045, 0)
            except Exception as ex:
                L.append('label fail %s' % str(ex)[:50])
            L.append('%s -> center (%.2f,%.2f) box (%.2f,%.2f)-(%.2f,%.2f)' % (
                v.Name, cx, cy, ol.MinimumPoint.X, ol.MinimumPoint.Y,
                ol.MaximumPoint.X, ol.MaximumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
