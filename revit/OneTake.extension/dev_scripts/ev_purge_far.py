# Delete view-owned annotations lying outside the ADU region in the new
# 1st-floor mech/elec views; re-center viewports.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
L = []
for vid, sheet, cx, cy in [(2244930, 'A200', 2.36, 1.42), (2244950, 'A201', 1.76, 1.30)]:
    v = doc.GetElement(ElementId(vid))
    kill = []
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            if e.OwnerViewId != v.Id: continue
            bb = e.get_BoundingBox(v)
            if bb is None: continue
            cxx = (bb.Min.X + bb.Max.X) / 2.0; cyy = (bb.Min.Y + bb.Max.Y) / 2.0
            if not (1100 < cxx < 1220 and 60 < cyy < 150):
                kill.append(e.Id)
        except Exception: pass
    t = Transaction(doc, 'OneTake: purge far %s' % vid); _prep(t); t.Start()
    if kill: doc.Delete(List[ElementId](kill))
    doc.Regenerate()
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == sheet:
            for vp in FEC(doc, s.Id).OfClass(Viewport):
                if vp.ViewId.Value == vid:
                    vp.SetBoxCenter(_XYZ(cx, cy, 0))
                    doc.Regenerate()
                    ol = vp.GetBoxOutline()
                    L.append('%s: purged %d, vp (%.2f,%.2f)-(%.2f,%.2f)' % (
                        sheet, len(kill), ol.MinimumPoint.X, ol.MinimumPoint.Y,
                        ol.MaximumPoint.X, ol.MaximumPoint.Y))
    t.Commit()
result = '\n'.join(L)
