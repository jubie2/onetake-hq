# What text / viewports / schedules sit on a given sheet.  args {"num":"A201"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, Viewport,
                               TextNote, ScheduleSheetInstance)
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
L = []
for s in FEC(pdoc).OfClass(ViewSheet):
    if s.SheetNumber != args['num']: continue
    L.append('SHEET %s - %s' % (s.SheetNumber, s.Name))
    for vp in FEC(pdoc, s.Id).OfClass(Viewport):
        v = pdoc.GetElement(vp.ViewId)
        c = vp.GetBoxCenter()
        L.append('  VP  [%s] %-28s at (%.2f,%.2f)' % (v.ViewType, v.Name[:28], c.X, c.Y))
    for si in FEC(pdoc, s.Id).OfClass(ScheduleSheetInstance):
        vs = pdoc.GetElement(si.ScheduleId)
        L.append('  SCH %-30s at (%.2f,%.2f)' % (vs.Name[:30], si.Point.X, si.Point.Y))
    for e in FEC(pdoc, s.Id).OfClass(TextNote):
        c = e.Coord
        t = (e.Text or '').replace('\r', ' ').replace('\n', ' ')
        L.append('  TXT %-9s (%.2f,%.2f) %d chars: %s' % (
            e.Id.Value, c.X, c.Y, len(t), t[:90]))
result = '\n'.join(L)
