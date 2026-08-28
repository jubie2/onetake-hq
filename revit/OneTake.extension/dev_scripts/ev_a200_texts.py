# List MECHANICAL KEYNOTES legend texts + A200 sheet texts (ids, coords).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               TextNote, ScheduleSheetInstance)
L = []
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'MECHANICAL KEYNOTES':
        L.append('--- legend %s ---' % v.Id.Value)
        for e in FEC(doc, v.Id).OfClass(TextNote):
            c = e.Coord
            L.append('LEG %s (%.2f,%.2f): %s' % (e.Id.Value, c.X, c.Y,
                     (e.Text or '').replace('\r', '|').replace('\n', '|')[:60]))
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A200': continue
    L.append('--- sheet texts ---')
    for e in FEC(doc, s.Id).OfClass(TextNote):
        c = e.Coord
        L.append('TXT %s (%.2f,%.2f): %s' % (e.Id.Value, c.X, c.Y,
                 (e.Text or '').replace('\r', '|').replace('\n', '|')[:60]))
    for e in FEC(doc, s.Id).OfClass(ScheduleSheetInstance):
        L.append('SCHED %s %s at (%.2f,%.2f)' % (e.Id.Value, e.Name,
                 e.Point.X, e.Point.Y))
result = '\n'.join(L)
