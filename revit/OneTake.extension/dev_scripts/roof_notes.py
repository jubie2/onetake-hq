# Slope arrows + ridge/eave notes on a roof plan, derived from the roof solid.
# NOTE: a roof plane's outward normal tilts TOWARD the downhill side, so the
# downslope direction is +horizontal-component-of-normal (not its negation).
# args {"view":"ADU - Roof Plan","texttype":"ARCH TEXT","dry":true}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, RoofBase, Options,
                               PlanarFace, Solid, GeometryInstance, XYZ as _XYZ, Line,
                               TextNote, TextNoteOptions, TextNoteType,
                               HorizontalTextAlignment, BuiltInParameter as BIP,
                               ViewDetailLevel)
import math
nm = args.get('view', 'ADU - Roof Plan')
dry = args.get('dry', True)
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
L = ['view %s scale %s' % (nm, v.Scale)]
tf = v.CropBox.Transform; inv = tf.Inverse

def on_plane(p):
    q = inv.OfPoint(p)
    return tf.OfPoint(_XYZ(q.X, q.Y, 0.0))

def local_angle(d):
    a = inv.OfVector(d)
    ang = math.atan2(a.Y, a.X)
    if ang > math.pi / 2 + 1e-6 or ang < -math.pi / 2 + 1e-6:
        ang += math.pi          # never let text render upside down
    return ang

roofs = list(FEC(doc, v.Id).OfClass(RoofBase))
if not roofs:
    result = 'no roof in view'
else:
    r = roofs[0]
    op = Options(); op.DetailLevel = ViewDetailLevel.Fine; op.ComputeReferences = False
    solids = []
    def walk(g):
        for o in g:
            if isinstance(o, Solid):
                if o.Volume > 1.0: solids.append(o)
            elif isinstance(o, GeometryInstance):
                walk(o.GetInstanceGeometry())
    walk(r.get_Geometry(op))
    faces = []; allpts = []
    for s in solids:
        for f in s.Faces:
            if not isinstance(f, PlanarFace): continue
            n = f.FaceNormal
            if n.Z < 0.05 or f.Area < 20.0: continue
            pts = list(f.Triangulate().Vertices)
            allpts.extend(pts)
            hl = math.sqrt(n.X * n.X + n.Y * n.Y)
            if hl < 1e-6:
                L.append('  flat face %.0f sf - skipped' % f.Area); continue
            down = _XYZ(n.X / hl, n.Y / hl, 0.0)      # <-- downhill = +horiz of normal
            ts = [p.X * down.X + p.Y * down.Y for p in pts]
            faces.append({'down': down, 'rise12': (hl / n.Z) * 12.0,
                          'run': max(ts) - min(ts),
                          'lo': max(ts), 'area': f.Area})
            L.append('  slope %.0f sf  %.2f:12  downhill (%.2f,%.2f)  ridge-to-eave %.1f'
                     % (f.Area, (hl / n.Z) * 12.0, down.X, down.Y, max(ts) - min(ts)))

    maxz = max(p.Z for p in allpts)
    rp = [p for p in allpts if p.Z > maxz - 0.1]
    if (max(p.X for p in rp) - min(p.X for p in rp)) >= (max(p.Y for p in rp) - min(p.Y for p in rp)):
        ry = sum(p.Y for p in rp) / len(rp)
        a = _XYZ(min(p.X for p in rp), ry, 0.0); b = _XYZ(max(p.X for p in rp), ry, 0.0)
    else:
        rx = sum(p.X for p in rp) / len(rp)
        a = _XYZ(rx, min(p.Y for p in rp), 0.0); b = _XYZ(rx, max(p.Y for p in rp), 0.0)
    u = (b - a).Normalize(); rlen = a.DistanceTo(b)
    L.append('  ridge (%.1f,%.1f)->(%.1f,%.1f) len %.1f' % (a.X, a.Y, b.X, b.Y, rlen))

    def along(t):     # point on the ridge at fraction t
        return _XYZ(a.X + u.X * rlen * t, a.Y + u.Y * rlen * t, 0.0)

    plan = []
    for i, fc in enumerate(faces):
        d = fc['down']; h = fc['run']
        base = along(0.66)
        s = _XYZ(base.X + d.X * 2.5, base.Y + d.Y * 2.5, 0.0)
        e = _XYZ(base.X + d.X * (h - 2.0), base.Y + d.Y * (h - 2.0), 0.0)
        rise = fc['rise12']
        txt = '%d:12' % round(rise) if abs(rise - round(rise)) < 0.05 else '%.1f:12' % rise
        mid = _XYZ((s.X + e.X) / 2.0 + u.X * 1.7, (s.Y + e.Y) / 2.0 + u.Y * 1.7, 0.0)
        eav = along(0.30)
        eav = _XYZ(eav.X + d.X * (h - 1.7), eav.Y + d.Y * (h - 1.7), 0.0)
        plan.append((s, e, d, txt, mid, eav))
        L.append('  arrow%d shaft (%.1f,%.1f)->(%.1f,%.1f)  "%s" at (%.1f,%.1f)  EAVE (%.1f,%.1f)'
                 % (i, s.X, s.Y, e.X, e.Y, txt, mid.X, mid.Y, eav.X, eav.Y))
    rl = along(0.22)
    L.append('  RIDGE label at (%.1f,%.1f)' % (rl.X, rl.Y))

    if not dry:
        tt = None; want = args.get('texttype', 'ARCH TEXT')
        for t2 in FEC(doc).OfClass(TextNoteType):
            n2 = t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()
            if n2 == want: tt = t2; break
            if tt is None: tt = t2
        t = Transaction(doc, 'OneTake: roof notes'); _prep(t); t.Start()
        made = []
        def dline(p0, p1):
            made.append(doc.Create.NewDetailCurve(v, Line.CreateBound(on_plane(p0), on_plane(p1))))
        def note(p, txt, ang):
            o = TextNoteOptions(tt.Id)
            o.HorizontalAlignment = HorizontalTextAlignment.Center
            o.Rotation = ang
            made.append(TextNote.Create(doc, v.Id, on_plane(p), txt, o))
        BARB = 1.1; BA = math.radians(17)
        for s, e, d, txt, mid, eav in plan:
            dline(s, e)
            back = math.atan2(-d.Y, -d.X)
            for sgn in (1, -1):
                ang = back + sgn * BA
                dline(e, _XYZ(e.X + math.cos(ang) * BARB, e.Y + math.sin(ang) * BARB, 0.0))
            note(mid, txt, local_angle(d))
            note(eav, 'EAVE, TYP.', local_angle(u))
        note(rl, 'RIDGE', local_angle(u))
        doc.Regenerate(); t.Commit()
        L.append('  created %d elements' % len(made))
    result = '\n'.join(L)
