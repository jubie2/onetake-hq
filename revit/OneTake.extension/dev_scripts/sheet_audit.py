# What is on every sheet: viewports (view + type) and any schedules.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               ScheduleSheetInstance, View)
rows = []
for s in sorted(FEC(doc).OfClass(ViewSheet), key=lambda z: z.SheetNumber):
    items = []
    for vpid in s.GetAllViewports():
        vp = doc.GetElement(vpid); v = doc.GetElement(vp.ViewId)
        items.append('%s[%s]' % (v.Name, str(v.ViewType)))
    for si in FEC(doc, s.Id).OfClass(ScheduleSheetInstance):
        try: items.append('%s[Schedule]' % doc.GetElement(si.ScheduleId).Name)
        except Exception: pass
    rows.append('%-7s %-34s | %s' % (s.SheetNumber, s.Name[:34], '; '.join(items)))
result = '\n'.join(rows)
