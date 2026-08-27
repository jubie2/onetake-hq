# Shift the right column of MECHANICAL KEYNOTES +0.4 in x.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               BuiltInCategory as BIC, XYZ as _XYZ)
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'MECHANICAL KEYNOTES': v = x; break
t = Transaction(doc, 'OneTake: legend shift'); _prep(t); t.Start()
n = 0
d = _XYZ(0.4, 0, 0)
for e in FEC(doc, v.Id).OfClass(TextNote):
    if 10.5 < e.Coord.X < 12.0:
        e.Coord = e.Coord + d; n += 1
for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name == 'TAG LABEL' and 10.3 < e.Location.Point.X < 11.5:
            e.Location.Move(d); n += 1
    except Exception: pass
doc.Regenerate(); t.Commit()
result = 'shifted %d elements' % n
