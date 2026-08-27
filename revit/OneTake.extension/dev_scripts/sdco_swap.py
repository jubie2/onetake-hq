# The 'Smoke' family type names are inverted vs their graphics. Swap every placed
# instance's type in the two mech views.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId,
                               BuiltInCategory as BIC)
A, B = ElementId(1027474), ElementId(1027472)
L = []
t = Transaction(doc, 'OneTake: SD/CO type swap'); _prep(t); t.Start()
for nm in ('ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    n = 0
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name != 'Smoke': continue
            tid = e.GetTypeId()
            e.ChangeTypeId(B if tid == A else A)
            n += 1
        except Exception: pass
    L.append('%s: swapped %d' % (nm, n))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
