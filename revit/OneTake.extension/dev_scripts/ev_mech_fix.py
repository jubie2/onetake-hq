# 'Smoke' family type names are INVERTED vs their graphics (type CARBONMONOXIDE
# draws "SD", type Smoke Detector[1] draws the CO circle) - swap every instance.
# Also shift the condensing unit clear of the entry stair.
import math
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId, XYZ as _XYZ,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
SD_WANT = ElementId(1027472)   # draws "SD"
CO_WANT = ElementId(1027474)   # draws the CO circle
L = []
t = Transaction(doc, 'OneTake: mech symbol swap'); _prep(t); t.Start()
for vid in (2244930, 2244778):
    v = doc.GetElement(ElementId(vid))
    n = 0
    for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name != 'Smoke': continue
        except Exception:
            continue
        cur = e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or ''
        want = SD_WANT if 'CARBON' not in cur.upper() else CO_WANT
        try:
            e.Symbol = doc.GetElement(want)
            n += 1
        except Exception as ex:
            L.append('  swap fail %s' % str(ex)[:40])
    L.append('%s: %d smoke/CO symbols swapped' % (v.Name, n))
    # move the condensing unit (1st floor only) east, clear of the stair
    if vid == 2244930:
        A = math.radians(14.3)
        UX, UY = math.cos(A), math.sin(A)
        VX, VY = -math.sin(A), math.cos(A)
        old = (1171.1, 92.1)
        new = (1161.1251 + UX * 16.0 + VX * -9.5, 98.8210 + UY * 16.0 + VY * -9.5)
        dx, dy = new[0] - old[0], new[1] - old[1]
        moved = 0
        for e in FEC(doc, v.Id).OfCategory(BIC.OST_Lines).WhereElementIsNotElementType():
            if e.OwnerViewId != v.Id: continue
            bb = e.get_BoundingBox(v)
            if bb is None: continue
            cx = (bb.Min.X + bb.Max.X) / 2.0; cy = (bb.Min.Y + bb.Max.Y) / 2.0
            if abs(cx - old[0]) < 2.5 and abs(cy - old[1]) < 2.5:
                e.Location.Move(_XYZ(dx, dy, 0)); moved += 1
        for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
            try:
                if e.Symbol.Family.Name != 'TAG LABEL': continue
                p = e.LookupParameter('TEXT')
                if not p or p.AsString() != '3': continue
            except Exception:
                continue
            e.Location.Move(_XYZ(dx, dy, 0))
            try:
                lds = list(e.GetLeaders())
                if lds:
                    lds[-1].End = _XYZ(new[0], new[1], 0)
                    en = lds[-1].Elbow
                    lds[-1].Elbow = _XYZ(en.X + dx, en.Y + dy, 0)
            except Exception: pass
            moved += 1
        L.append('  condenser moved to (%.1f,%.1f), %d elements' % (new[0], new[1], moved))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
