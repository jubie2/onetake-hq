# Mech plan additions round 2, both floors: ceiling mini-split near the family
# window, SD in each bedroom + SD/CO in the hall. Symbols drawn + labeled.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               TextNoteOptions, TextNoteType, BuiltInParameter as BIP,
                               HorizontalTextAlignment, XYZ as _XYZ, Line, Arc)
import math
VIEWS = ['ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan']
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
CIRCLES = [  # (cx, cy, label)
 (1160.5, -142.8, 'SD'),
 (1160.9, -128.5, 'SD'),
 (1167.8, -138.6, 'SD'),
 (1167.8, -140.5, 'CO'),
]
MS = (1174.5, -148.0)   # mini split square center, near the south window
L = []
t = Transaction(doc, 'OneTake: SD/CO + mini split'); _prep(t); t.Start()
for nm in VIEWS:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    o = TextNoteOptions(tt.Id)
    o.HorizontalAlignment = HorizontalTextAlignment.Left
    xa = _XYZ(1, 0, 0); ya = _XYZ(0, 1, 0)
    for cx, cy, lab in CIRCLES:
        c = _XYZ(cx, cy, 0); R = 0.4
        doc.Create.NewDetailCurve(v, Arc.Create(c, R, 0.0, math.pi, xa, ya))
        doc.Create.NewDetailCurve(v, Arc.Create(c, R, math.pi, 2 * math.pi, xa, ya))
        TextNote.Create(doc, v.Id, _XYZ(cx - 0.55, cy + 0.55, 0), lab, o)
    # mini split: 2x2 square with diagonals + label
    h = 1.0
    p = [(MS[0]-h, MS[1]-h), (MS[0]+h, MS[1]-h), (MS[0]+h, MS[1]+h), (MS[0]-h, MS[1]+h)]
    for i in range(4):
        doc.Create.NewDetailCurve(v, Line.CreateBound(
            _XYZ(p[i][0], p[i][1], 0), _XYZ(p[(i+1)%4][0], p[(i+1)%4][1], 0)))
    doc.Create.NewDetailCurve(v, Line.CreateBound(_XYZ(p[0][0], p[0][1], 0), _XYZ(p[2][0], p[2][1], 0)))
    doc.Create.NewDetailCurve(v, Line.CreateBound(_XYZ(p[1][0], p[1][1], 0), _XYZ(p[3][0], p[3][1], 0)))
    TextNote.Create(doc, v.Id, _XYZ(MS[0] + 1.3, MS[1] - 1.0, 0),
                    'MINI SPLIT\n(CLG. MTD.)', o)
    L.append('%s: 4 detectors + mini split' % nm)
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
