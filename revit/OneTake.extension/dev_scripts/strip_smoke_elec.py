# Delete 'Smoke' generic-annotation instances from the electrical plan views.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId,
                               BuiltInCategory as BIC)
from System.Collections.Generic import List
L = []
t = Transaction(doc, 'OneTake: SD/CO off electrical'); _prep(t); t.Start()
for nm in ('ADU - 1st Floor Electrical Plan', 'ADU - 2nd Floor Electrical Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    kill = []
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name == 'Smoke': kill.append(e.Id)
        except Exception: pass
    if kill: doc.Delete(List[ElementId](kill))
    L.append('%s: removed %d' % (nm, len(kill)))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
