# Sanity check: which doc is open, and what electrical content still exists?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC)
L = ['DOC: %s' % doc.Title]
tot = 0
zone = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    tot += 1
    try: p = e.Location.Point
    except Exception: p = None
    if p is not None and 1120 < p.X < 1200 and 78 < p.Y < 128: zone += 1
L.append('electrical fixtures: %d total, %d in the ADU zone' % (tot, zone))
nl = 0
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is not None and 1120 < p.X < 1200 and 78 < p.Y < 128: nl += 1
L.append('lighting fixtures in zone: %d' % nl)
for vid in (2244950, 2244908):
    v = doc.GetElement(ElementId(vid))
    if v is None:
        L.append('view %s MISSING' % vid); continue
    nc = len([e for e in FEC(doc, v.Id).OfCategory(BIC.OST_Lines).WhereElementIsNotElementType()
              if e.OwnerViewId == v.Id])
    ne = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType()))
    nlt = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType()))
    L.append('%s: %d detail lines, %d elec, %d lights' % (v.Name, nc, ne, nlt))
mx = 0
for e in FEC(doc).WhereElementIsNotElementType():
    if e.Id.Value > mx: mx = e.Id.Value
L.append('highest element id in doc: %d' % mx)
result = '\n'.join(L)
