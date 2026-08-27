# Mech plan additions: room tags, bath EF symbol, attic access hatch (2nd floor).
# args {"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, SpatialElement,
                               TextNote, TextNoteOptions, TextNoteType, GraphicsStyle,
                               HorizontalTextAlignment, BuiltInParameter as BIP,
                               XYZ as _XYZ, UV, Line, Arc, LinkElementId)
from Autodesk.Revit.DB.Architecture import Room, RoomTag
import math
dry = args.get('dry', True)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
VIEWS = {'ADU - 1st Floor Mechanical Plan': '1st Floor Level',
         'ADU - 2nd Floor Mechanical Plan': '2nd FLoor Plan'}
def getview(nm):
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: return x
    return None
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
dash = None
for g in FEC(doc).OfClass(GraphicsStyle):
    n = (g.Name or '').lower()
    if 'hidden' in n or 'dash' in n:
        dash = g; break
rooms = {}
for e in [r for r in FEC(doc).OfClass(SpatialElement) if isinstance(r, Room)]:
    try:
        if e.Area <= 0: continue
        p = e.Location.Point
        if not (X0 <= p.X <= X1 and Y0 <= p.Y <= Y1): continue
        lvl = doc.GetElement(e.LevelId).Name
        rooms.setdefault(lvl, []).append(e)
    except Exception: pass
L = ['dash style: %s' % (dash.Name if dash else 'none')]
EF = (1169.4, -130.9)      # bath exhaust fan symbol center
AA = (1170.9, -147.0)      # attic access over the entry closet (2nd floor)
if not dry:
    t = Transaction(doc, 'OneTake: mech adds'); _prep(t); t.Start()
    for nm, lvl in VIEWS.items():
        v = getview(nm)
        # room tags at room centers
        n = 0
        for r in rooms.get(lvl, []):
            try:
                p = r.Location.Point
                doc.Create.NewRoomTag(LinkElementId(r.Id), UV(p.X, p.Y), v.Id)
                n += 1
            except Exception as ex:
                L.append('  tag fail %s' % str(ex)[:50])
        # EF symbol: circle + blade cross + EF label
        c = _XYZ(EF[0], EF[1], 0)
        R = 0.45
        xa = _XYZ(1, 0, 0); ya = _XYZ(0, 1, 0)
        e1 = doc.Create.NewDetailCurve(v, Arc.Create(c, R, 0.0, math.pi, xa, ya))
        e2 = doc.Create.NewDetailCurve(v, Arc.Create(c, R, math.pi, 2 * math.pi, xa, ya))
        curves = [e1, e2]
        for ang in (0.785, 2.356):   # x cross inside
            d = _XYZ(math.cos(ang) * R, math.sin(ang) * R, 0)
            curves.append(doc.Create.NewDetailCurve(v, Line.CreateBound(c - d, c + d)))
        o = TextNoteOptions(tt.Id)
        o.HorizontalAlignment = HorizontalTextAlignment.Left
        TextNote.Create(doc, v.Id, _XYZ(EF[0] - 0.4, EF[1] + 1.7, 0), 'EF', o)
        if nm.startswith('ADU - 2nd'):
            x0, x1b = AA[0] - 0.92, AA[0] + 0.92
            y0, y1b = AA[1] - 1.25, AA[1] + 1.25
            pts = [(x0, y0), (x1b, y0), (x1b, y1b), (x0, y1b)]
            for i in range(4):
                a = _XYZ(pts[i][0], pts[i][1], 0)
                b = _XYZ(pts[(i + 1) % 4][0], pts[(i + 1) % 4][1], 0)
                ce = doc.Create.NewDetailCurve(v, Line.CreateBound(a, b))
                if dash:                       # attic hatch is dashed; EF stays solid
                    try: ce.LineStyle = dash
                    except Exception: pass
        L.append('%s: %d room tags + EF%s' % (nm, n,
                 ' + attic access' if nm.startswith('ADU - 2nd') else ''))
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
