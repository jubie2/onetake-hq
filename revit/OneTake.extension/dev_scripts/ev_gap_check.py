# Two suspected gaps vs the approved set:
#  1. section / elevation reference bubbles on the floor plans
#  2. U-Factor + SHGC columns on the window schedule (Title-24)
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, Category,
                               ViewSchedule, BuiltInCategory as BIC)
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
L = []
for vid, nm in ((718579, '1st Floor Plan'), (1715860, '2nd FLoor Level')):
    v = pdoc.GetElement(ElementId(vid))
    for bic, cn in ((BIC.OST_Sections, 'Sections'), (BIC.OST_Elev, 'Elevations')):
        c = Category.GetCategory(pdoc, bic)
        try: hid = v.GetCategoryHidden(c.Id)
        except Exception as ex: hid = '? %s' % str(ex)[:20]
        L.append('  %-16s %-11s hidden=%s' % (nm, cn, hid))
    n = len(list(FEC(pdoc, v.Id).OfCategory(BIC.OST_Sections).WhereElementIsNotElementType()))
    L.append('  %-16s section marks visible: %d' % (nm, n))
L.append('--- schedules ---')
for vs in FEC(pdoc).OfClass(ViewSchedule):
    if vs.Name not in ('WINDOWS SCHEDULE', 'DOOR SCHEDULE'): continue
    sd = vs.Definition
    fields = []
    for i in range(sd.GetFieldCount()):
        f = sd.GetField(i)
        fields.append(f.GetName() + ('*' if f.IsHidden else ''))
    L.append('  %s: %s' % (vs.Name, ', '.join(fields)))
    if vs.Name == 'WINDOWS SCHEDULE':
        avail = []
        for sf in sd.GetSchedulableFields():
            try:
                n2 = sf.GetName(pdoc)
                if any(k in n2.lower() for k in ('factor', 'shgc', 'solar', 'heat trans')):
                    avail.append(n2)
            except Exception: pass
        L.append('    available Title-24 fields: %s' % (', '.join(sorted(set(avail))) or 'NONE'))
result = '\n'.join(L)
