# List every schedule in the open doc: id, name, category, where it is placed.
# Reads NO cell text -- reading table data is what crashes Revit on a foreign or
# damaged schedule (stack overflow, 0xC00000FD).  Safe to run on any model.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSchedule,
                               ScheduleSheetInstance)

placed = {}
for ssi in FEC(doc).OfClass(ScheduleSheetInstance):
    try:
        owner = doc.GetElement(ssi.OwnerViewId)
        placed.setdefault(ssi.ScheduleId.Value, []).append(
            getattr(owner, 'SheetNumber', None) or (owner.Name if owner else '?'))
    except Exception:
        pass

out = ['doc: %s' % doc.Title, '--- schedules (no table data read) ---']
n = 0
for v in FEC(doc).OfClass(ViewSchedule):
    try:
        name = v.Name
    except Exception as ex:
        out.append('  id %s  <name failed: %s>' % (v.Id.Value, ex))
        continue
    tags = []
    if v.IsTemplate:
        tags.append('template')
    if v.IsTitleblockRevisionSchedule:
        tags.append('revision')
    on = placed.get(v.Id.Value)
    out.append('  %-10s %-52s %-12s %s' % (
        v.Id.Value, name[:52], ','.join(tags) or '-',
        ('on sheets: ' + ', '.join(on)) if on else 'not placed'))
    n += 1
out.append('--- %d schedules ---' % n)
result = '\n'.join(out)
