# Report the view-range planes of the electrical views + current can heights.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ElementId,
                               PlanViewPlane, BuiltInCategory as BIC)
L = []
for vid in (2244950, 2244908):
    v = doc.GetElement(ElementId(vid))
    vr = v.GetViewRange()
    lvl = doc.GetElement(v.GenLevel.Id)
    L.append('%s (level %s elev %.2f)' % (v.Name, lvl.Name, lvl.Elevation))
    for nm, pl in (('Top', PlanViewPlane.TopClipPlane), ('Cut', PlanViewPlane.CutPlane),
                   ('Bottom', PlanViewPlane.BottomClipPlane),
                   ('Depth', PlanViewPlane.ViewDepthPlane)):
        try:
            off = vr.GetOffset(pl)
            lid = vr.GetLevelId(pl)
            base = doc.GetElement(lid).Elevation if doc.GetElement(lid) else 0.0
            L.append('   %-6s offset %6.2f  -> z %6.2f' % (nm, off, base + off))
        except Exception as ex:
            L.append('   %-6s ?? %s' % (nm, str(ex)[:30]))
zs = {}
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name != 'Downlight - Recessed Can': continue
        p = e.Location.Point
    except Exception: continue
    if not (1120 < p.X < 1200 and 78 < p.Y < 128): continue
    k = round(p.Z, 2)
    zs[k] = zs.get(k, 0) + 1
L.append('can heights: %s' % sorted(zs.items()))
result = '\n'.join(L)
