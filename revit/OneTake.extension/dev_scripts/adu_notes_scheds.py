# Duplicate the project's note views + spec schedules for the ADU and place them.
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet, ViewSchedule,
                               ViewDuplicateOption, ScheduleSheetInstance, Viewport,
                               XYZ as _XYZ, SectionType)
dry = args.get('dry', True)
# (source name, new name, sheet, x, y)
VIEWS = [('KEY NOTES Floor Plan',  'ADU - KEY NOTES Floor Plan', 'ADU-1', 1.55, 0.45),
         ('GREEN CODE NOTES',      'ADU - GREEN CODE NOTES',     'ADU-7', 0.55, 0.60),
         ('ATTIC SECTION',         'ADU - ATTIC SECTION',        'ADU-5', 2.20, 1.35)]
SCHEDS = [('TABLE 4.303.2',                    'ADU - TABLE 4.303.2',            'ADU-1', 2.30, 0.80),
          ('HEATING FURNACE SCHEDULE',         'ADU - HEATING FURNACE SCHEDULE', 'ADU-5', 0.15, 0.62),
          ('DRYER SCHEDULE',                   'ADU - DRYER SCHEDULE',           'ADU-5', 1.30, 0.62),
          ('Exhaust Fan Schedule',             'ADU - EXHAUST FAN SCHEDULE',     'ADU-5', 0.15, 0.30),
          ('WATER HEATER SCHEDULE (HEATPUMP )','ADU - WATER HEATER SCHEDULE',    'ADU-5', 1.30, 0.30),
          ('Electrical Notes',                 'ADU - ELECTRICAL NOTES',         'ADU-6', 2.15, 0.85),
          ('SHEAR WALL SCHEDULE',              'ADU - SHEAR WALL SCHEDULE',      'ADU-8', 0.20, 0.85)]
L = []
def findv(nm):
    for v in FEC(doc).OfClass(View):
        if not v.IsTemplate and v.Name == nm: return v
    return None
def finds(nm):
    for s in FEC(doc).OfClass(ViewSchedule):
        if s.Name == nm: return s
    return None
def sheet(nm):
    for s in FEC(doc).OfClass(ViewSheet):
        if s.SheetNumber == nm: return s
    return None
for a, b, sn, x, y in VIEWS:
    L.append('view  %-24s -> %-28s %s  src:%s dst:%s' % (a[:24], b[:28], sn, findv(a) is not None, findv(b) is not None))
for a, b, sn, x, y in SCHEDS:
    L.append('sched %-24s -> %-28s %s  src:%s dst:%s' % (a[:24], b[:28], sn, finds(a) is not None, finds(b) is not None))
if not dry:
    t = Transaction(doc, 'OneTake: ADU notes + schedules'); _prep(t); t.Start()
    for a, b, sn, x, y in VIEWS:
        sh = sheet(sn)
        v = findv(b)
        if v is None:
            src = findv(a)
            if src is None: L.append('  MISSING source %s' % a); continue
            nid = src.Duplicate(ViewDuplicateOption.WithDetailing)
            v = doc.GetElement(nid); v.Name = b
            doc.Regenerate()
            L.append('  duplicated %s' % b)
        on = None
        for vp in FEC(doc, sh.Id).OfClass(Viewport):
            if vp.ViewId == v.Id: on = vp; break
        p = _XYZ(x, y, 0)
        if on: on.SetBoxCenter(p)
        elif Viewport.CanAddViewToSheet(doc, sh.Id, v.Id):
            vp = Viewport.Create(doc, sh.Id, v.Id, p); vp.LabelOffset = _XYZ(0, 0, 0)
        else:
            L.append('  cannot place %s on %s' % (b, sn)); continue
        doc.Regenerate()
        for vp in FEC(doc, sh.Id).OfClass(Viewport):
            if vp.ViewId == v.Id:
                ol = vp.GetBoxOutline()
                L.append('  %-28s on %s at (%.2f,%.2f) box %.2f x %.2f' % (
                    b[:28], sn, x, y, ol.MaximumPoint.X - ol.MinimumPoint.X,
                    ol.MaximumPoint.Y - ol.MinimumPoint.Y))
    for a, b, sn, x, y in SCHEDS:
        sh = sheet(sn)
        s = finds(b)
        if s is None:
            src = finds(a)
            if src is None: L.append('  MISSING source %s' % a); continue
            opt = None
            for o in (ViewDuplicateOption.Duplicate, ViewDuplicateOption.WithDetailing):
                try:
                    if src.CanViewBeDuplicated(o): opt = o; break
                except Exception: pass
            if opt is None:
                L.append('  %s CANNOT be duplicated - skipped' % a); continue
            try:
                nid = src.Duplicate(opt)
            except Exception as ex:
                L.append('  %s duplicate failed: %s' % (a, str(ex)[:45])); continue
            s = doc.GetElement(nid); s.Name = b
            doc.Regenerate()
            L.append('  duplicated %s' % b)
        have = None
        for si in FEC(doc, sh.Id).OfClass(ScheduleSheetInstance):
            if si.ScheduleId == s.Id: have = si; break
        if have is None:
            ScheduleSheetInstance.Create(doc, sh.Id, s.Id, _XYZ(x, y, 0))
            L.append('  %-28s placed on %s at (%.2f,%.2f)' % (b[:28], sn, x, y))
        else:
            L.append('  %-28s already on %s' % (b[:28], sn))
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
