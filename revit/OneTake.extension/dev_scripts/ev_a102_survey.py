# A102: schedule instances, their filters, and new-ADU door/window marks.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet,
                               ScheduleSheetInstance, ViewSchedule,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber != 'A102': continue
    for e in FEC(doc, s.Id).OfClass(ScheduleSheetInstance):
        vs = doc.GetElement(e.ScheduleId)
        L.append('SCHED "%s" at (%.2f,%.2f) inst %s' % (vs.Name, e.Point.X, e.Point.Y, e.Id.Value))
        try:
            sd = vs.Definition
            for i in range(sd.GetFilterCount()):
                f = sd.GetFilter(i)
                fld = sd.GetField(f.FieldId)
                L.append('   filter: %s %s %s' % (fld.GetName(), f.FilterType, f.GetStringValue()))
        except Exception as ex:
            L.append('   filt? %s' % str(ex)[:40])
nd = nw = 0
marks = []
for cat in [BIC.OST_Doors, BIC.OST_Windows]:
    for e in FEC(doc).OfCategory(cat).WhereElementIsNotElementType():
        try:
            p = e.Location.Point
            if not (1120 < p.X < 1200 and 80 < p.Y < 128): continue
        except Exception: continue
        mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
        cm = e.get_Parameter(BIP.ALL_MODEL_INSTANCE_COMMENTS)
        marks.append('%s %s mark=%r cmt=%r' % (
            'D' if cat == BIC.OST_Doors else 'W', e.Id.Value,
            mk.AsString() if mk else None, cm.AsString() if cm else None))
result = '\n'.join(L) + '\n' + '\n'.join(sorted(marks))
