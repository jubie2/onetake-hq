from Autodesk.Revit.DB import (FilteredElementCollector as FEC, Wall, BuiltInParameter as BIP,
                               WallFunction)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
ext = []
for w in FEC(doc).OfClass(Wall):
    try:
        b = w.get_BoundingBox(None)
        if b is None: continue
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (X0 <= cx <= X1 and Y0 <= cy <= Y1): continue
        lv = doc.GetElement(w.LevelId).Name if w.LevelId and w.LevelId.IntegerValue > 0 else '?'
        c = w.Location.Curve
        p0 = c.GetEndPoint(0); p1 = c.GetEndPoint(1)
        fn = str(w.WallType.Function)
        th = w.Width
        L.append('%-22s %-16s %-9s w%.2f (%.1f,%.1f)-(%.1f,%.1f) len %.1f' % (
            w.Name[:22], lv, fn, th, p0.X, p0.Y, p1.X, p1.Y, c.Length))
        if fn == 'Exterior' and lv == '1st Floor Level':
            ext.append((p0.X, p0.Y, p1.X, p1.Y, th))
    except Exception: pass
L.append('--- exterior walls on 1st Floor Level: %d' % len(ext))
if ext:
    xs = [v for e in ext for v in (e[0], e[2])]; ys = [v for e in ext for v in (e[1], e[3])]
    L.append('    footprint X %.1f..%.1f  Y %.1f..%.1f' % (min(xs), max(xs), min(ys), max(ys)))
result = '\n'.join(L)
