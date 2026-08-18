from Autodesk.Revit.DB import Dimension, View, BuiltInParameter
view = [v for v in FilteredElementCollector(doc).OfClass(View) if not v.IsTemplate and v.Name == args.get('view', 'Proposed Floor Plan')][0]
out = []
for d in FilteredElementCollector(doc, view.Id).OfClass(Dimension):
    try:
        bb = d.get_BoundingBox(view)
        c = [round((bb.Min.X + bb.Max.X) / 2, 1), round((bb.Min.Y + bb.Max.Y) / 2, 1)] if bb else None
    except Exception:
        c = None
    if c and args.get('region') and not (args['region'][0] <= c[0] <= args['region'][2] and args['region'][1] <= c[1] <= args['region'][3]):
        continue
    try:
        txt = d.ValueString
    except Exception:
        txt = None
    out.append({'id': d.Id.Value, 'text': txt, 'segments': d.NumberOfSegments, 'type': (d.DimensionType.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() if d.DimensionType else None), 'center': c})
result = out
