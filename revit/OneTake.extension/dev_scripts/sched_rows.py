# Dump rows of schedules placed on a sheet. args {"sheet":"ADU-7"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet,
                               ScheduleSheetInstance, SectionType)
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == args.get('sheet', 'ADU-7'): sh = s; break
L = []
for ssi in FEC(doc, sh.Id).OfClass(ScheduleSheetInstance):
    vs = doc.GetElement(ssi.ScheduleId)
    try: nm = vs.Name
    except Exception: continue
    L.append('=== %s ===' % nm)
    try:
        td = vs.GetTableData()
        sec = td.GetSectionData(SectionType.Body)
        rows = sec.NumberOfRows; cols = sec.NumberOfColumns
        for r in range(min(rows, 40)):
            vals = []
            for c in range(cols):
                try: vals.append(vs.GetCellText(SectionType.Body, r, c))
                except Exception: vals.append('?')
            L.append(' | '.join(vals))
        if rows > 40: L.append('... %d rows total' % rows)
    except Exception as ex:
        L.append('ERR %s' % str(ex)[:60])
result = '\n'.join(L)
