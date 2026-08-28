# Tag ownership by element id + device visibility diagnosis.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ElementId,
                               BuiltInCategory as BIC, BuiltInParameter as BIP,
                               Category)
L = []
def tagids(vid):
    out = []
    for e in FEC(doc, ElementId(vid)).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
        try:
            if e.Symbol.Family.Name == 'TAG LABEL': out.append(e.Id.Value)
        except Exception: pass
    return set(out)
a = tagids(718579); b = tagids(2244742); c = tagids(2244891)
L.append('718579 n=%d; mech n=%d; elec n=%d; overlap a&b=%d a&c=%d' % (
    len(a), len(b), len(c), len(a & b), len(a & c)))
sample = None
for e in FEC(doc).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType():
    bb = e.get_BoundingBox(None)
    if bb and 1120 < (bb.Min.X + bb.Max.X) / 2 < 1200 and 80 < (bb.Min.Y + bb.Max.Y) / 2 < 128:
        ph = e.get_Parameter(BIP.PHASE_CREATED)
        L.append('device %s %s z=%.2f phase=%s demol=%s' % (
            e.Id.Value, e.Symbol.Family.Name, bb.Min.Z,
            ph.AsValueString() if ph else '?',
            e.get_Parameter(BIP.PHASE_DEMOLISHED).AsValueString()))
        sample = e
        if len(L) > 6: break
v = doc.GetElement(ElementId(2244891))
ecat = Category.GetCategory(doc, BIC.OST_ElectricalFixtures)
L.append('elec dup: cat hidden=%s phase=%s filter=%s' % (
    v.GetCategoryHidden(ecat.Id),
    v.get_Parameter(BIP.VIEW_PHASE).AsElementId().Value,
    v.get_Parameter(BIP.VIEW_PHASE_FILTER).AsValueString()))
result = '\n'.join(L)
