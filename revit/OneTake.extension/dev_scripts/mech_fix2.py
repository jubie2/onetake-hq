# Move the IAQ fan (circle + keynote 15) from Bed-1 to the family area, both floors.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, CurveElement,
                               BuiltInCategory as BIC, ElementId, XYZ as _XYZ, Line, Arc)
from System.Collections.Generic import List
import math
OLD = _XYZ(1163.3, -144.0, 0)
NEW = (1177.8, -142.8)
L = []
t = Transaction(doc, 'OneTake: move IAQ'); _prep(t); t.Start()
for nm in ('ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    kill = []
    for e in FEC(doc, v.Id).OfClass(CurveElement):
        try:
            m = e.GeometryCurve.Evaluate(0.5, True)
            if m.DistanceTo(OLD) < 0.8: kill.append(e.Id)
        except Exception: pass
    if kill: doc.Delete(List[ElementId](kill))
    c = _XYZ(NEW[0], NEW[1], 0); R = 0.4
    xa = _XYZ(1, 0, 0); ya = _XYZ(0, 1, 0)
    doc.Create.NewDetailCurve(v, Arc.Create(c, R, 0.0, math.pi, xa, ya))
    doc.Create.NewDetailCurve(v, Arc.Create(c, R, math.pi, 2 * math.pi, xa, ya))
    for ang in (0.785, 2.356):
        d = _XYZ(math.cos(ang) * R, math.sin(ang) * R, 0)
        doc.Create.NewDetailCurve(v, Line.CreateBound(c - d, c + d))
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name == 'TAG LABEL':
                p = e.LookupParameter('TEXT')
                if p and p.AsString() == '15':
                    q = e.Location.Point
                    e.Location.Move(_XYZ(1176.5 - q.X, -141.6 - q.Y, 0))
        except Exception: pass
    L.append('%s: IAQ moved (%d old curves)' % (nm, len(kill)))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
