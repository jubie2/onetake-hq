# Give every mech keynote a drawn device like the approved A200, both floors:
# T-box thermostat (1), bath wall diffuser (3), dryer + kitchen duct runs w/ arrows
# (5/6, 8/9), IAQ fan circle (15).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               TextNoteOptions, TextNoteType, BuiltInParameter as BIP,
                               HorizontalTextAlignment, BuiltInCategory as BIC,
                               XYZ as _XYZ, Line, Arc)
import math
VIEWS = ['ADU - 1st Floor Mechanical Plan', 'ADU - 2nd Floor Mechanical Plan']
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
L = []
t = Transaction(doc, 'OneTake: mech devices'); _prep(t); t.Start()
BARB = 0.8; BA = math.radians(20)
for nm in VIEWS:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    o = TextNoteOptions(tt.Id)
    o.HorizontalAlignment = HorizontalTextAlignment.Left
    xa = _XYZ(1, 0, 0); ya = _XYZ(0, 1, 0)
    def line(a, b):
        return doc.Create.NewDetailCurve(v, Line.CreateBound(
            _XYZ(a[0], a[1], 0), _XYZ(b[0], b[1], 0)))
    def arrow(a, b):
        line(a, b)
        back = math.atan2(a[1] - b[1], a[0] - b[0])
        for sgn in (1, -1):
            ang = back + sgn * BA
            line(b, (b[0] + math.cos(ang) * BARB, b[1] + math.sin(ang) * BARB))
    def circleX(cx, cy, R):
        c = _XYZ(cx, cy, 0)
        doc.Create.NewDetailCurve(v, Arc.Create(c, R, 0.0, math.pi, xa, ya))
        doc.Create.NewDetailCurve(v, Arc.Create(c, R, math.pi, 2 * math.pi, xa, ya))
        for ang in (0.785, 2.356):
            d = (math.cos(ang) * R, math.sin(ang) * R)
            line((cx - d[0], cy - d[1]), (cx + d[0], cy + d[1]))
    # 1: thermostat T-box on the bath/kitchen wall
    h = 0.45
    for a, b in (((1175.6, -136.0), (1176.5, -136.0)), ((1176.5, -136.0), (1176.5, -135.1)),
                 ((1176.5, -135.1), (1175.6, -135.1)), ((1175.6, -135.1), (1175.6, -136.0))):
        line(a, b)
    TextNote.Create(doc, v.Id, _XYZ(1175.65, -135.15, 0), 'T', o)
    # 3: 6"x12" wall diffuser on the bath south wall + tag via retag later
    for a, b in (((1169.6, -135.8), (1170.6, -135.8)), ((1170.6, -135.8), (1170.6, -135.3)),
                 ((1170.6, -135.3), (1169.6, -135.3)), ((1169.6, -135.3), (1169.6, -135.8))):
        line(a, b)
    line((1169.6, -135.55), (1170.6, -135.55))
    # 5/6: dryer duct run from W/D to the south wall
    arrow((1170.9, -143.2), (1170.9, -149.9))
    # 8/9: kitchen hood duct run to the north wall
    arrow((1175.4, -129.4), (1175.4, -126.1))
    # 15: IAQ fan circle by its tag
    circleX(1163.3, -144.0, 0.4)
    L.append('%s: devices drawn' % nm)
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
