# Look for real Revit Wire elements (the Electrical > Wire tool) in the project doc.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
from Autodesk.Revit.DB.Electrical import Wire, WireType
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
L = ['project: %s' % pdoc.Title]
n = 0
for e in FEC(pdoc).OfCategory(BIC.OST_Wire).WhereElementIsNotElementType():
    n += 1
    try:
        v = pdoc.GetElement(e.OwnerViewId)
        vn = v.Name if v else '?'
    except Exception: vn = '?'
    pts = []
    try:
        for i in range(e.NumberOfVertices):
            p = e.GetVertex(i)
            pts.append('(%.1f,%.1f)' % (p.X, p.Y))
    except Exception as ex:
        pts.append('verts? %s' % str(ex)[:30])
    wt = ''
    try: wt = pdoc.GetElement(e.GetTypeId()).Name
    except Exception: pass
    L.append('  WIRE %-9s view=%-26s type=%-16s %s' % (e.Id.Value, vn[:26], wt, ' '.join(pts)))
L.append('total wires: %d' % n)
L.append('--- wire types available ---')
for wt in FEC(pdoc).OfClass(WireType):
    L.append('  %-9s %s' % (wt.Id.Value, wt.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
result = '\n'.join(L)
