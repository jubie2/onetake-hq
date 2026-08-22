# Create sheet ADU-7 with the ADU door + window schedules (+ reusable legend).
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ViewSchedule,
                               ScheduleSheetInstance, FamilySymbol, ElementId, XYZ as _XYZ,
                               View, Viewport, SectionType, BuiltInCategory as BIC)
dry = args.get('dry', True)
NUM = 'ADU-7'; NAME = '4439 Keeler Ave ADU - Door & Window Schedule'
TB = ElementId(311500)
L = []
scheds = {}
for s in FEC(doc).OfClass(ViewSchedule):
    if s.Name in ('ADU DOOR SCHEDULE', 'ADU WINDOW SCHEDULE'):
        scheds[s.Name] = s
        try:
            td = s.GetTableData().GetSectionData(SectionType.Body)
            L.append('%s: %d rows x %d cols' % (s.Name, td.NumberOfRows, td.NumberOfColumns))
        except Exception as ex:
            L.append('%s: row read err %s' % (s.Name, str(ex)[:40]))
existing = [x for x in FEC(doc).OfClass(ViewSheet) if x.SheetNumber == NUM]
L.append('sheet %s exists: %s' % (NUM, bool(existing)))
if not dry:
    t = Transaction(doc, 'OneTake: build ADU-7'); _prep(t); t.Start()
    if existing:
        sh = existing[0]
    else:
        sh = ViewSheet.Create(doc, TB)
        sh.SheetNumber = NUM
    sh.Name = NAME
    doc.Regenerate()
    placed = set()
    for si in FEC(doc, sh.Id).OfClass(ScheduleSheetInstance):
        try: placed.add(doc.GetElement(si.ScheduleId).Name)
        except Exception: pass
    spots = {'ADU DOOR SCHEDULE': _XYZ(0.12, 1.72, 0),
             'ADU WINDOW SCHEDULE': _XYZ(1.35, 1.72, 0)}
    for nm2, pt in spots.items():
        if nm2 in placed:
            L.append('  %s already placed' % nm2); continue
        s = scheds.get(nm2)
        if s is None: L.append('  %s missing' % nm2); continue
        ScheduleSheetInstance.Create(doc, sh.Id, s.Id, pt)
        L.append('  placed %s at (%.2f, %.2f)' % (nm2, pt.X, pt.Y))
    # reusable legend from A102
    for v in FEC(doc).OfClass(View):
        if v.IsTemplate or v.Name != 'FLOOR PLAN GENERAL NOTE': continue
        if Viewport.CanAddViewToSheet(doc, sh.Id, v.Id):
            vp = Viewport.Create(doc, sh.Id, v.Id, _XYZ(2.45, 1.30, 0))
            L.append('  placed legend FLOOR PLAN GENERAL NOTE')
        else:
            L.append('  legend cannot be added')
    doc.Regenerate(); t.Commit()
    L.append('sheet %s = %s' % (NUM, sh.Id))
result = '\n'.join(L)
