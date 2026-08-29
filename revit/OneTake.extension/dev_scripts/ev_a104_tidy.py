# A104: move the two sheet notes clear of the new framing view, rename the sheet,
# and report whether the A01 index is a sheet-list schedule (auto-updating).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ElementId,
                               ScheduleSheetInstance, XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: A104 tidy'); _prep(t); t.Start()
e = doc.GetElement(ElementId(1848104))          # "NEW ROOF DECK - CLASS A ..."
e.Coord = _XYZ(0.30, 1.72, 0)
L.append('deck note -> (0.30,1.72)')
e2 = doc.GetElement(ElementId(2115201))         # "ROOF MATERIALS INFO:"
e2.Coord = _XYZ(0.28, 0.82, 0)
L.append('materials block -> (0.28,0.82)')
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'A104':
        s.Name = 'Roof / Framing Plan'
        L.append('A104 renamed "%s"' % s.Name)
doc.Regenerate(); t.Commit()
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A01': continue
    n = 0
    for si in FEC(doc, s.Id).OfClass(ScheduleSheetInstance):
        vs = doc.GetElement(si.ScheduleId)
        L.append('A01 schedule "%s" at (%.2f,%.2f)' % (vs.Name, si.Point.X, si.Point.Y))
        n += 1
    if n == 0: L.append('A01 index is TEXT, not a sheet list - needs manual edit')
result = '\n'.join(L)
