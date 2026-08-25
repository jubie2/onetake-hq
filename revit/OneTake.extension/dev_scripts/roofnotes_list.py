from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, TextNote, XYZ as _XYZ
rv = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'ADU - Roof Plan': rv = v; break
L = []
for tn in FEC(doc, rv.Id).OfClass(TextNote):
    c = tn.Coord
    L.append('%s at (%.1f, %.1f) rot=%.2f %r' % (tn.Id, c.X, c.Y, tn.GetRotation() if hasattr(tn,'GetRotation') else -1, (tn.Text or '')[:52].replace('\r',' / ').replace('\n',' / ')))
result = '\n'.join(L)
