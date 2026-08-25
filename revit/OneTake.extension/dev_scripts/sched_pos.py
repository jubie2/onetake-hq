from Autodesk.Revit.DB import FilteredElementCollector as FEC, ViewSheet, ScheduleSheetInstance
L = []
for sn in args['sheets']:
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber != sn: continue
        for si in FEC(doc, s.Id).OfClass(ScheduleSheetInstance):
            try:
                sc = doc.GetElement(si.ScheduleId)
                p = si.Point
                b = si.get_BoundingBox(s)
                L.append('%-6s %-28s at (%.2f,%.2f)  box (%.2f,%.2f)-(%.2f,%.2f)' % (
                    sn, sc.Name[:28], p.X, p.Y, b.Min.X, b.Min.Y, b.Max.X, b.Max.Y))
            except Exception: pass
result = '\n'.join(L)
