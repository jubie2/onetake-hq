from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, BuiltInCategory as BIC,
                               BuiltInParameter as BIP)
L = []
L.append('=== all lighting fixtures in the model and where they are')
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    b = e.get_BoundingBox(None)
    if b is None: continue
    L.append('  %s %-34s at (%.0f, %.0f, %.1f)' % (
        e.Id, e.Symbol.Family.Name[:34], (b.Min.X + b.Max.X) / 2.0,
        (b.Min.Y + b.Max.Y) / 2.0, (b.Min.Z + b.Max.Z) / 2.0))
L.append('=== which views show any lighting fixture')
for v in FEC(doc).OfClass(View):
    try:
        if v.IsTemplate: continue
        if str(v.ViewType) not in ('Elevation', 'Section', 'FloorPlan', 'ThreeD'): continue
        n = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures)
                     .WhereElementIsNotElementType()))
        if n: L.append('  %-34s %s  %d' % (v.Name[:34], v.ViewType, n))
    except Exception: pass
result = '\n'.join(L)
