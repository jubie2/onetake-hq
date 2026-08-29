# Did the whole rebuild transaction get undone?
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC)
L = []
for i in range(2245709, 2245721):
    e = doc.GetElement(ElementId(i))
    L.append('  %s %s' % (i, 'MISSING' if e is None else
                          (e.Category.Name if e.Category else '?')))
n1 = n2 = 0
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    try: p = e.Location.Point
    except Exception: continue
    if p is None or not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    if p.Z < 10: n1 += 1
    else: n2 += 1
L.append('devices: %d 1st, %d 2nd' % (n1, n2))
mx = 0
for e in FEC(doc).WhereElementIsNotElementType():
    if e.Id.Value > mx: mx = e.Id.Value
L.append('highest element id: %d' % mx)
result = '\n'.join(L)
