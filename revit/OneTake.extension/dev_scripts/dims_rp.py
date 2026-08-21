# Dimensions via short reference planes.  args {"view":..., "items":[{"planes":[[[x0,y0],[x1,y1]],[[..],[..]]], "at":[[lx0,ly0],[lx1,ly1]], "label":..},
#   or {"wall": wallId (centerline), "plane": [[x0,y0],[x1,y1]], "at": [[..],[..]]}]}
from Autodesk.Revit.DB import Options, Line, ReferenceArray, View, ReferencePlane, XYZ as _XYZ
def find_view(name):
    for v in FilteredElementCollector(doc).OfClass(View):
        if not v.IsTemplate and v.Name == name:
            return v
view = find_view(args.get('view', 'Proposed Floor Plan'))
def center_ref(wall):
    opt = Options(); opt.ComputeReferences = True; opt.IncludeNonVisibleObjects = True; opt.View = view
    lc = wall.Location.Curve
    for g in wall.get_Geometry(opt):
        if isinstance(g, Line) and g.Reference is not None:
            p0, p1 = g.GetEndPoint(0), g.GetEndPoint(1)
            if lc.Distance(_XYZ(p0.X, p0.Y, 0)) < 0.05 and lc.Distance(_XYZ(p1.X, p1.Y, 0)) < 0.05:
                return g.Reference
existing_names = set()
for _rp in FilteredElementCollector(doc).OfClass(ReferencePlane):
    try:
        existing_names.add(_rp.Name)
    except Exception:
        pass

def uniq(name):
    n = name; i = 2
    while n in existing_names:
        n = "%s %d" % (name, i); i += 1
    existing_names.add(n)
    return n

def make_rp(seg, name):
    name = uniq(name)
    a = _XYZ(float(seg[0][0]), float(seg[0][1]), 0); b = _XYZ(float(seg[1][0]), float(seg[1][1]), 0)
    rp = doc.Create.NewReferencePlane(a, b, _XYZ.BasisZ, view)
    try:
        rp.Name = name
    except Exception:
        pass
    return rp
out = []
t = Transaction(doc, 'OneTake: dims via reference planes')
_prep(t)
t.Start()
try:
    for i, it in enumerate(args.get('items', [])):
        r = dict(it)
        try:
            ra = ReferenceArray()
            if 'wall' in it:
                ra.Append(center_ref(doc.GetElement(ElementId(long(it['wall'])))))
                rp = make_rp(it['plane'], 'OneTake dim %s' % it.get('label', i))
                ra.Append(rp.GetReference()); r['rp'] = [rp.Id.Value]
            else:
                r['rp'] = []
                for j, seg in enumerate(it['planes']):
                    rp = make_rp(seg, 'OneTake dim %s-%d' % (it.get('label', i), j))
                    ra.Append(rp.GetReference()); r['rp'].append(rp.Id.Value)
            doc.Regenerate()
            at = it["at"]
            line = Line.CreateBound(_XYZ(float(at[0][0]), float(at[0][1]), 0), _XYZ(float(at[1][0]), float(at[1][1]), 0))
            dim = doc.Create.NewDimension(view, line, ra)
            doc.Regenerate()
            r['id'] = dim.Id.Value; r['value_ft'] = round(dim.Value, 3) if dim.Value is not None else None; r['text'] = dim.ValueString
        except Exception as ex:
            r['error'] = str(ex)
        out.append(r)
    t.Commit()
except Exception:
    t.RollBack(); raise
result = out
