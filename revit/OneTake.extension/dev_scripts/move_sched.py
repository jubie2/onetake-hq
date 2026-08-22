# Move schedule instances / viewports on a sheet.
# args {"sheet":"ADU-7","scheds":[["ADU DOOR SCHEDULE",0.10,1.74]],"vps":[["FLOOR PLAN GENERAL NOTE",2.45,1.20]]}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet,
                               ScheduleSheetInstance, Viewport, XYZ as _XYZ,
                               ElementTransformUtils)
sn = args['sheet']
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == sn: sh = s; break
L = []
t = Transaction(doc, 'OneTake: move sheet items'); _prep(t); t.Start()
for nm, x, y in args.get('scheds', []):
    for si in FEC(doc, sh.Id).OfClass(ScheduleSheetInstance):
        if doc.GetElement(si.ScheduleId).Name != nm: continue
        p = si.Point
        ElementTransformUtils.MoveElement(doc, si.Id, _XYZ(x - p.X, y - p.Y, 0))
        L.append('%-22s (%.2f,%.2f) -> (%.2f,%.2f)' % (nm[:22], p.X, p.Y, x, y))
for nm, x, y in args.get('vps', []):
    for vp in FEC(doc, sh.Id).OfClass(Viewport):
        if doc.GetElement(vp.ViewId).Name != nm: continue
        vp.SetBoxCenter(_XYZ(x, y, 0))
        ol = vp.GetBoxOutline()
        L.append('%-22s -> (%.2f,%.2f) box %.2f x %.2f' % (
            nm[:22], x, y, ol.MaximumPoint.X - ol.MinimumPoint.X,
            ol.MaximumPoint.Y - ol.MinimumPoint.Y))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
