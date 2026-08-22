# Copy crop rectangle from a source view to target views (same direction only).
# args {"pairs":[["ADU - East Elevation","East Elev."],["ADU - West Elevation","West Elev."]],"dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, BoundingBoxXYZ,
                               XYZ as _XYZ, Transaction as _T)
byname = {}
for v in FEC(doc).OfClass(View):
    try:
        if not v.IsTemplate: byname[v.Name] = v
    except Exception: pass
L = []
dry = args.get('dry', True)
t = None
if not dry:
    t = Transaction(doc, 'OneTake: copy crops'); _prep(t); t.Start()
for src_n, dst_n in args.get('pairs', []):
    s = byname.get(src_n); d = byname.get(dst_n)
    if s is None or d is None:
        L.append('MISSING %s -> %s' % (src_n, dst_n)); continue
    sd = s.ViewDirection; dd = d.ViewDirection
    dot = sd.X*dd.X + sd.Y*dd.Y + sd.Z*dd.Z
    sb = s.CropBox; db = d.CropBox
    L.append('%s -> %s  dirdot %.3f' % (src_n, dst_n, dot))
    L.append('   src local %.2f..%.2f x %.2f..%.2f' % (sb.Min.X, sb.Max.X, sb.Min.Y, sb.Max.Y))
    L.append('   dst local %.2f..%.2f x %.2f..%.2f' % (db.Min.X, db.Max.X, db.Min.Y, db.Max.Y))
    if dot < 0.999:
        L.append('   SKIP - view directions differ'); continue
    # map source local corners through source transform into world, then into dst local
    st = sb.Transform; dt = db.Transform; inv = dt.Inverse
    xs = []; ys = []
    for x in (sb.Min.X, sb.Max.X):
        for y in (sb.Min.Y, sb.Max.Y):
            p = inv.OfPoint(st.OfPoint(_XYZ(x, y, 0.0)))
            xs.append(p.X); ys.append(p.Y)
    nb = BoundingBoxXYZ()
    nb.Transform = dt
    nb.Min = _XYZ(min(xs), min(ys), db.Min.Z)
    nb.Max = _XYZ(max(xs), max(ys), db.Max.Z)
    L.append('   NEW dst local %.2f..%.2f x %.2f..%.2f' % (nb.Min.X, nb.Max.X, nb.Min.Y, nb.Max.Y))
    if not dry:
        d.CropBoxActive = True
        d.CropBox = nb
        try: d.CropBoxVisible = False
        except Exception: pass
if not dry:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
