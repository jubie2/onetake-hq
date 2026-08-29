# Move the smoke / CO symbols next to the room doors (smoke reaches a detector by the
# door far sooner than one in the middle of the room), and re-point their keynotes.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
# view: [(old xy, new xy)]  - SD just inside each bedroom door, CO/hall SD by the doors
MOVES = {
 2244930: [((1135.8, 106.0), (1139.2, 106.4)),    # Bed-1  -> beside its door
           ((1138.2, 92.0),  (1140.2, 97.4)),     # Bed-2  -> beside its door
           ((1143.5, 101.5), (1142.2, 101.9)),    # hall   -> between the bedroom doors
           ((1144.8, 102.8), (1143.6, 103.6))],   # CO     -> hall, by the doors
 2244778: [((1138.5, 107.0), (1141.3, 109.1)),    # Master Bed -> beside its door
           ((1141.0, 93.5),  (1141.6, 97.6)),     # Bed-2      -> beside its door
           ((1146.5, 102.5), (1144.8, 102.2)),    # hall
           ((1147.6, 103.6), (1145.9, 103.4))],   # CO
}
L = []
t = Transaction(doc, 'OneTake: SD/CO by doors'); _prep(t); t.Start()
for vid, moves in MOVES.items():
    v = doc.GetElement(ElementId(vid))
    syms = []
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name == 'Smoke': syms.append(e)
        except Exception: pass
    nmoved = 0
    for (ox, oy), (nx, ny) in moves:
        best = None; bd = 3.0
        for e in syms:
            p = e.Location.Point
            d = math.hypot(p.X - ox, p.Y - oy)
            if d < bd: bd = d; best = e
        if best is None:
            L.append('  no symbol near (%.1f,%.1f)' % (ox, oy)); continue
        p = best.Location.Point
        best.Location.Move(_XYZ(nx - p.X, ny - p.Y, 0))
        syms.remove(best)
        nmoved += 1
        # drag the matching keynote leader along
        for e2 in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
            try:
                if e2.Symbol.Family.Name != 'TAG LABEL': continue
                pp = e2.LookupParameter('TEXT')
                if not pp or pp.AsString() not in ('12', '13'): continue
                lds = list(e2.GetLeaders())
                if not lds: continue
                en = lds[0].End
                if math.hypot(en.X - ox, en.Y - oy) > 1.2: continue
                lds[0].End = _XYZ(nx, ny, 0)
            except Exception: pass
    L.append('%s: %d symbols moved to doors' % (v.Name, nmoved))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
