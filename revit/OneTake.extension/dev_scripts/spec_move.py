from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote, XYZ as _XYZ)
rv = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'ADU - Roof Plan': rv = v; break
tf = rv.CropBox.Transform; inv = tf.Inverse
L = []
t = Transaction(doc, 'OneTake: move shingle spec'); _prep(t); t.Start()
for tn in FEC(doc, rv.Id).OfClass(TextNote):
    if (tn.Text or '').startswith('ROOF SHINGLE: OWENS'):
        q = inv.OfPoint(_XYZ(1147.6, -152.5, 0.0))
        tn.Coord = tf.OfPoint(_XYZ(q.X, q.Y, 0.0))
        try: tn.SetRotation(0.0)
        except Exception:
            pass
        L.append('moved %s' % tn.Id)
doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'not found'
