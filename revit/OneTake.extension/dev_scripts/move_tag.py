# Move a TAG LABEL (by view + TEXT value) to a new point and reset its leader.
# args {"view":"ADU - East Elevation","n":"3","pt":[..],"elbow":[..],"end":[..]}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View,
                               BuiltInCategory as BIC, XYZ as _XYZ)
nm = args['view']
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
hit = None
for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
    if e.Symbol.Family.Name != 'TAG LABEL': continue
    p = e.LookupParameter('TEXT')
    if p and p.AsString() == args['n']: hit = e; break
if hit is None:
    result = 'tag %s not found in %s' % (args['n'], nm)
else:
    t = Transaction(doc, 'OneTake: move tag'); _prep(t); t.Start()
    old = hit.Location.Point
    npt = _XYZ(*[float(q) for q in args['pt']])
    hit.Location.Move(npt - old)
    doc.Regenerate()
    try:
        lds = list(hit.GetLeaders())
    except Exception:
        lds = []
        la = hit.Leaders
        for i in range(la.Size): lds.append(la.get_Item(i))
    if lds and args.get('end'):
        lds[0].End = _XYZ(*[float(q) for q in args['end']])
        if args.get('elbow'):
            lds[0].Elbow = _XYZ(*[float(q) for q in args['elbow']])
    doc.Regenerate(); t.Commit()
    result = 'moved %s in %s' % (args['n'], nm)
