# Match 1st-floor elec view phase/filter/range to 718579; recount devices.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               BuiltInCategory as BIC, BuiltInParameter as BIP,
                               PlanViewPlane)
src = doc.GetElement(ElementId(718579))
v = doc.GetElement(ElementId(2244950))
mv = doc.GetElement(ElementId(2244930))
L = []
t = Transaction(doc, 'OneTake: elec phase'); _prep(t); t.Start()
for tgt in [v, mv]:
    for bip in [BIP.VIEW_PHASE, BIP.VIEW_PHASE_FILTER]:
        ps = src.get_Parameter(bip); pt = tgt.get_Parameter(bip)
        if ps and pt and not pt.IsReadOnly:
            pt.Set(ps.AsElementId())
    L.append('%s: phase %s filter %s' % (tgt.Name,
             tgt.get_Parameter(BIP.VIEW_PHASE).AsElementId().Value,
             tgt.get_Parameter(BIP.VIEW_PHASE_FILTER).AsValueString()))
try:
    vr = v.GetViewRange()
    vr.SetOffset(PlanViewPlane.TopClipPlane, 10.5)
    v.SetViewRange(vr)
except Exception as ex:
    L.append('range %s' % str(ex)[:40])
doc.Regenerate(); t.Commit()
ne = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_ElectricalFixtures).WhereElementIsNotElementType()))
nl = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType()))
L.append('1st elec view now: elec=%d light=%d' % (ne, nl))
result = '\n'.join(L)
