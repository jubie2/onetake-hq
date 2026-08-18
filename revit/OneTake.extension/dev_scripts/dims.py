# Centerline dimensions between walls / family reference planes.
# args {"view":"Proposed Floor Plan","dims":[{"a":wallId,"b":wallId,"axis":"x"|"y","at":coord} |
#        {"wall":id,"offset":3.0} (length of one wall between its end refs) |
#        {"fam":id,"refs":"lr"|"fb","offset":2.0}]}
from Autodesk.Revit.DB import (Options, Line, ReferenceArray, View, Wall, FamilyInstance,
                               FamilyInstanceReferenceType, XYZ as _XYZ)
def find_view(name):
    for v in FilteredElementCollector(doc).OfClass(View):
        if not v.IsTemplate and v.Name == name:
            return v
view = find_view(args.get('view', 'Proposed Floor Plan'))
def center_ref(wall):
    """Reference of the wall's centerline (non-visible location line)."""
    opt = Options(); opt.ComputeReferences = True; opt.IncludeNonVisibleObjects = True; opt.View = view
    for g in wall.get_Geometry(opt):
        if isinstance(g, Line) and g.Reference is not None:
            # the location line is the one lying on the wall's location curve
            lc = wall.Location.Curve
            p0, p1 = g.GetEndPoint(0), g.GetEndPoint(1)
            q0, q1 = _XYZ(p0.X, p0.Y, 0), _XYZ(p1.X, p1.Y, 0)
            if lc.Distance(q0) < 0.05 and lc.Distance(q1) < 0.05:
                return g, g.Reference
    return None, None
out = []
t = Transaction(doc, 'OneTake: dimensions')
_prep(t)
t.Start()
try:
    for d in args.get('dims', []):
        r = dict(d)
        try:
            ra = ReferenceArray()
            if 'a' in d:
                wa = doc.GetElement(ElementId(long(d['a']))); wb = doc.GetElement(ElementId(long(d['b'])))
                la, refa = center_ref(wa); lb, refb = center_ref(wb)
                if refa is None or refb is None:
                    r['error'] = 'no centerline reference'; out.append(r); continue
                ra.Append(refa); ra.Append(refb)
                pa = wa.Location.Curve.GetEndPoint(0); pb = wb.Location.Curve.GetEndPoint(0)
                if d['axis'] == 'x':
                    line = Line.CreateBound(_XYZ(pa.X, float(d['at']), 0), _XYZ(pb.X, float(d['at']), 0))
                else:
                    line = Line.CreateBound(_XYZ(float(d['at']), pa.Y, 0), _XYZ(float(d['at']), pb.Y, 0))
            elif 'wall' in d:
                w = doc.GetElement(ElementId(long(d['wall'])))
                lw, ref = center_ref(w)
                if lw is None:
                    r['error'] = 'no centerline'; out.append(r); continue
                r0, r1 = lw.GetEndPointReference(0), lw.GetEndPointReference(1)
                if r0 is None or r1 is None:
                    r['error'] = 'no end refs'; out.append(r); continue
                ra.Append(r0); ra.Append(r1)
                lc = w.Location.Curve
                dirv = (lc.GetEndPoint(1) - lc.GetEndPoint(0)).Normalize()
                n = _XYZ(-dirv.Y, dirv.X, 0) * float(d.get('offset', 3.0))
                line = Line.CreateBound(lc.GetEndPoint(0) + n, lc.GetEndPoint(1) + n)
            else:
                fi = doc.GetElement(ElementId(long(d['fam'])))
                if d.get('refs', 'lr') == 'lr':
                    rt0, rt1 = FamilyInstanceReferenceType.Left, FamilyInstanceReferenceType.Right
                else:
                    rt0, rt1 = FamilyInstanceReferenceType.Front, FamilyInstanceReferenceType.Back
                refs0 = list(fi.GetReferences(rt0)); refs1 = list(fi.GetReferences(rt1))
                if not refs0 or not refs1:
                    r['error'] = 'family has no such reference planes'; out.append(r); continue
                ra.Append(refs0[0]); ra.Append(refs1[0])
                bb = fi.get_BoundingBox(None); c = (bb.Min + bb.Max) * 0.5
                off = float(d.get('offset', 2.0))
                if d.get('refs', 'lr') == 'lr':   # dimension line runs along hand direction
                    h = fi.HandOrientation; f = fi.FacingOrientation
                else:
                    h = fi.FacingOrientation; f = fi.HandOrientation
                base = c + f * off
                line = Line.CreateBound(base - h * 5, base + h * 5)
            dim = doc.Create.NewDimension(view, line, ra)
            doc.Regenerate()
            r['id'] = dim.Id.Value
            try:
                r['value_ft'] = round(dim.Value, 3); r['text'] = dim.ValueString
            except Exception:
                pass
        except Exception as ex:
            r['error'] = str(ex)
        out.append(r)
    t.Commit()
except Exception:
    t.RollBack()
    raise
result = out

# --- extra mode: {"a": wallId (centerline), "bend": wallId, "which": 0|1, "axis": "x"|"y", "at": c}
#     dimension from wall a's centerline to the endpoint reference of wall bend's location line
if args.get('extra'):
    out2 = []
    t = Transaction(doc, 'OneTake: dimensions (end refs)')
    _prep(t)
    t.Start()
    try:
        for d in args['extra']:
            r = dict(d)
            try:
                wa = doc.GetElement(ElementId(long(d['a']))); wb = doc.GetElement(ElementId(long(d['bend'])))
                la, refa = center_ref(wa); lb, refb = center_ref(wb)
                re = lb.GetEndPointReference(int(d.get('which', 1)))
                if refa is None or re is None:
                    r['error'] = 'refs missing (a=%s end=%s)' % (refa is not None, re is not None); out2.append(r); continue
                ra = ReferenceArray(); ra.Append(refa); ra.Append(re)
                pa = wa.Location.Curve.GetEndPoint(0); pe = lb.GetEndPoint(int(d.get('which', 1)))
                if d['axis'] == 'x':
                    line = Line.CreateBound(_XYZ(pa.X, float(d['at']), 0), _XYZ(pe.X, float(d['at']), 0))
                else:
                    line = Line.CreateBound(_XYZ(float(d['at']), pa.Y, 0), _XYZ(float(d['at']), pe.Y, 0))
                dim = doc.Create.NewDimension(view, line, ra)
                doc.Regenerate()
                r['id'] = dim.Id.Value; r['value_ft'] = round(dim.Value, 3); r['text'] = dim.ValueString
            except Exception as ex:
                r['error'] = str(ex)
            out2.append(r)
        t.Commit()
    except Exception:
        t.RollBack(); raise
    result = {'dims': out, 'extra': out2}
