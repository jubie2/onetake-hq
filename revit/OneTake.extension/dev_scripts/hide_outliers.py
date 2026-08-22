# Hide elements that stick out past a view's crop (by category). args {"views":[...],"cats":["Levels"],"margin":5.0,"dry":true}
from Autodesk.Revit.DB import View, FilteredElementCollector as FEC, XYZ as _XYZ, ElementId as EId
from System.Collections.Generic import List
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: hide outliers'); _prep(t); t.Start()
for nm in args['views']:
    vs = [x for x in FEC(doc).OfClass(View) if not x.IsTemplate and x.Name == nm]
    if not vs: L.append('%s not found' % nm); continue
    v = vs[0]; bb = v.CropBox; inv = bb.Transform.Inverse
    M = float(args.get('margin', 5.0))
    victims = []
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            cat = e.Category.Name if e.Category else ''
            if args.get('cats') and cat not in args['cats']: continue
            b = e.get_BoundingBox(v)
            if b is None: continue
            xs = []
            for cx in (b.Min.X, b.Max.X):
                for cy in (b.Min.Y, b.Max.Y):
                    for cz in (b.Min.Z, b.Max.Z):
                        xs.append(inv.OfPoint(_XYZ(cx, cy, cz)).X)
            if max(bb.Min.X - min(xs), max(xs) - bb.Max.X) > M:
                victims.append(e)
        except Exception: pass
    if victims and not args.get('dry', True):
        ids = List[EId]()
        for e in victims: ids.Add(e.Id)
        try:
            v.HideElements(ids); doc.Regenerate()
        except Exception as ex:
            L.append('  hide failed: %s' % str(ex)[:50])
    L.append('%-24s hid %d: %s' % (nm[:24], len(victims),
             ', '.join('%s %s' % (e.Category.Name if e.Category else '?', e.Name) for e in victims[:4])))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
