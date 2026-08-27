# Move bedroom SD circles+labels next to each room's entry door, both floors.
# Collect BEFORE starting the transaction (in-transaction curve collection has
# silently returned 0 on the 2nd-floor view before).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               CurveElement, ElementId, XYZ as _XYZ, Line, Arc)
from System.Collections.Generic import List
import math
OLD = [(1160.5, -142.8), (1160.9, -128.5)]
NEW = [(1164.2, -143.0), (1165.5, -132.6)]   # Bed-1 door 1167.1,-141.2 / Bed-2 door 1167.1,-135.4
plans = {}
for nm in ('ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    kill = []
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            if isinstance(e, CurveElement):
                m = e.GeometryCurve.Evaluate(0.5, True)
                if any(abs(m.X - o[0]) < 0.8 and abs(m.Y - o[1]) < 0.8 for o in OLD):
                    kill.append(e.Id)
            elif isinstance(e, TextNote):
                if (e.Text or '').strip() == 'SD':
                    p = e.Coord
                    if any(abs(p.X - o[0]) < 1.2 and abs(p.Y - o[1]) < 1.2 for o in OLD):
                        kill.append(e.Id)
        except Exception: pass
    plans[nm] = (v, kill)
L = []
t = Transaction(doc, 'OneTake: SD near doors'); _prep(t); t.Start()
from Autodesk.Revit.DB import TextNoteOptions, TextNoteType, BuiltInParameter as BIP, HorizontalTextAlignment
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
for nm, (v, kill) in plans.items():
    if kill: doc.Delete(List[ElementId](kill))
    o = TextNoteOptions(tt.Id)
    o.HorizontalAlignment = HorizontalTextAlignment.Left
    xa = _XYZ(1, 0, 0); ya = _XYZ(0, 1, 0)
    for cx, cy in NEW:
        c = _XYZ(cx, cy, 0); R = 0.4
        doc.Create.NewDetailCurve(v, Arc.Create(c, R, 0.0, math.pi, xa, ya))
        doc.Create.NewDetailCurve(v, Arc.Create(c, R, math.pi, 2 * math.pi, xa, ya))
        TextNote.Create(doc, v.Id, _XYZ(cx - 0.55, cy + 0.55, 0), 'SD', o)
    L.append('%s: removed %d old, placed 2 SD by doors' % (nm, len(kill)))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
