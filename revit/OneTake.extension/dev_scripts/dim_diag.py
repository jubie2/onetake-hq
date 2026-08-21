# aligned dimension for the diagonal wall between two reference planes made in a prior transaction
from Autodesk.Revit.DB import Line, ReferenceArray, View, XYZ as _XYZ, ReferencePlane
view = [v for v in FilteredElementCollector(doc).OfClass(View) if not v.IsTemplate and v.Name == 'Proposed Floor Plan'][0]
a = args.get('a', [6.3, 49.25]); b = args.get('b', [33.53, 63.167])
p0 = _XYZ(float(a[0]), float(a[1]), 0); p1 = _XYZ(float(b[0]), float(b[1]), 0)
u = (p1 - p0).Normalize(); n = _XYZ(-u.Y, u.X, 0)
t = Transaction(doc, 'rp'); _prep(t); t.Start()
rp0 = doc.Create.NewReferencePlane(p0 - n * 0.5, p0 + n * 3.5, _XYZ.BasisZ, view)
rp1 = doc.Create.NewReferencePlane(p1 - n * 0.5, p1 + n * 3.5, _XYZ.BasisZ, view)
t.Commit()
t = Transaction(doc, 'dim'); _prep(t); t.Start()
ra = ReferenceArray(); ra.Append(rp0.GetReference()); ra.Append(rp1.GetReference())
line = Line.CreateBound(p0 + n * 3.0, p1 + n * 3.0)
dim = doc.Create.NewDimension(view, line, ra)
doc.Regenerate()
val = dim.Value; txt = dim.ValueString
if val is None or val < 0:
    t.RollBack()
    t2 = Transaction(doc, 'cleanup'); _prep(t2); t2.Start(); doc.Delete(rp0.Id); doc.Delete(rp1.Id); t2.Commit()
    result = {'failed': True, 'value': val, 'text': txt}
else:
    t.Commit()
    result = {'id': dim.Id.Value, 'value': val, 'text': txt, 'rps': [rp0.Id.Value, rp1.Id.Value]}
