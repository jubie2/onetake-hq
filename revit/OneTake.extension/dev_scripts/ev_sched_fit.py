# The two Title-24 columns pushed the window schedule into the titleblock.
# Narrow the low-value columns and nudge the table left so it fits the sheet.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSchedule, ViewSheet,
                               ScheduleSheetInstance, XYZ as _XYZ)
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
NARROW = {'Description': 0.055, 'Manufacturer': 0.055, 'Model': 0.045,
          'Comments': 0.045, 'Level': 0.075, 'U- FACTOR': 0.05, 'SHGC': 0.04}
L = []
t = Transaction(pdoc, 'OneTake: fit window schedule'); _prep(t); t.Start()
for vs in FEC(pdoc).OfClass(ViewSchedule):
    if vs.Name != 'WINDOWS SCHEDULE': continue
    sd = vs.Definition
    tot = 0.0
    for i in range(sd.GetFieldCount()):
        f = sd.GetField(i)
        n = f.GetName()
        if n in NARROW:
            try: f.GridColumnWidth = NARROW[n]
            except Exception as ex: L.append('  %s width fail %s' % (n, str(ex)[:30]))
        try: tot += f.GridColumnWidth
        except Exception: pass
    L.append('window schedule total width now %.3f ft' % tot)
pdoc.Regenerate()
for s in FEC(pdoc).OfClass(ViewSheet):
    if s.SheetNumber != 'A102': continue
    for si in FEC(pdoc, s.Id).OfClass(ScheduleSheetInstance):
        vs = pdoc.GetElement(si.ScheduleId)
        if vs.Name != 'WINDOWS SCHEDULE': continue
        p = si.Point
        si.Point = _XYZ(1.62, p.Y, 0)
        pdoc.Regenerate()
        L.append('window schedule moved (%.2f,%.2f) -> (%.2f,%.2f)' % (
            p.X, p.Y, si.Point.X, si.Point.Y))
pdoc.Regenerate(); t.Commit()
result = '\n'.join(L)
