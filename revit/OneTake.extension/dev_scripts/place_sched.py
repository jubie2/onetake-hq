# Place existing schedules onto sheets. args {"items":[["TABLE 4.303.2","ADU-1",2.30,0.80]]}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ViewSchedule,
                               ScheduleSheetInstance, XYZ as _XYZ, SectionType)
L = []
t = Transaction(doc, 'OneTake: place schedules'); _prep(t); t.Start()
for nm, sn, x, y in args['items']:
    s = None
    for z in FEC(doc).OfClass(ViewSchedule):
        if z.Name == nm: s = z; break
    sh = None
    for z in FEC(doc).OfClass(ViewSheet):
        if z.SheetNumber == sn: sh = z; break
    if s is None or sh is None:
        L.append('%-34s / %s NOT FOUND' % (nm[:34], sn)); continue
    have = None
    for si in FEC(doc, sh.Id).OfClass(ScheduleSheetInstance):
        if si.ScheduleId == s.Id: have = si; break
    try:
        if have:
            from Autodesk.Revit.DB import ElementTransformUtils
            p = have.Point
            ElementTransformUtils.MoveElement(doc, have.Id, _XYZ(x - p.X, y - p.Y, 0))
            L.append('%-34s moved on %s' % (nm[:34], sn))
        else:
            ScheduleSheetInstance.Create(doc, sh.Id, s.Id, _XYZ(x, y, 0))
            try:
                td = s.GetTableData().GetSectionData(SectionType.Body)
                rows = td.NumberOfRows
            except Exception: rows = '?'
            L.append('%-34s placed on %s at (%.2f,%.2f)  %s rows' % (nm[:34], sn, x, y, rows))
    except Exception as ex:
        L.append('%-34s FAIL %s' % (nm[:34], str(ex)[:60]))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
