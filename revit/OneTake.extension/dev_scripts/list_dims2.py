from Autodesk.Revit.DB import Dimension, View, BuiltInParameter, ReferencePlane
view = [v for v in FilteredElementCollector(doc).OfClass(View) if not v.IsTemplate and v.Name == args.get('view','Proposed Floor Plan')][0]
reg = args.get('region', [-10,-30,75,70])
out = []
for d in FilteredElementCollector(doc, view.Id).OfClass(Dimension):
    bb = d.get_BoundingBox(view)
    c = [round((bb.Min.X+bb.Max.X)/2,1), round((bb.Min.Y+bb.Max.Y)/2,1)] if bb else None
    if c and not (reg[0] <= c[0] <= reg[2] and reg[1] <= c[1] <= reg[3]):
        continue
    refs = []
    try:
        for r in d.References:
            el = doc.GetElement(r.ElementId)
            nm = el.GetType().Name
            try:
                if isinstance(el, ReferencePlane):
                    p0 = el.BubbleEnd; nm = 'RefPlane(%.2f,%.2f)' % (p0.X, p0.Y)
                elif hasattr(el, 'Location') and hasattr(el.Location, 'Curve'):
                    cu = el.Location.Curve
                    nm = 'Wall %s (%.2f,%.2f)-(%.2f,%.2f)' % (el.Id.Value, cu.GetEndPoint(0).X, cu.GetEndPoint(0).Y, cu.GetEndPoint(1).X, cu.GetEndPoint(1).Y)
                else:
                    nm = '%s %s' % (nm, el.Id.Value)
            except Exception:
                pass
            refs.append(nm)
    except Exception as ex:
        refs.append('err ' + str(ex))
    try: txt = d.ValueString
    except Exception: txt = None
    out.append({'id': d.Id.Value, 'text': txt, 'center': c, 'refs': refs})
result = sorted(out, key=lambda r: -(r['center'] or [0,0])[1])
