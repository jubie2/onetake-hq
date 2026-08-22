# Does a different wall-light family actually render in an elevation? args {"apply":false}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, FamilySymbol,
                               BuiltInCategory as BIC, BuiltInParameter as BIP)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
alt = None
for s in FEC(doc).OfClass(FamilySymbol):
    try:
        if s.Category is None or s.Category.Id.IntegerValue != int(BIC.OST_LightingFixtures): continue
        if s.Family.Name == 'Emergency Wall Light' and \
           (s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == '120V':
            alt = s; break
    except Exception: pass
L.append('alternate family: %s' % (alt.Id if alt else 'NOT FOUND'))
lights = []
for e in FEC(doc).OfCategory(BIC.OST_LightingFixtures).WhereElementIsNotElementType():
    b = e.get_BoundingBox(None)
    if b is None: continue
    cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
    if X0 <= cx <= X1 and Y0 <= cy <= Y1: lights.append(e)
L.append('ADU lights: %d' % len(lights))
if alt and lights:
    t = Transaction(doc, 'OneTake: lamp swap test'); _prep(t); t.Start()
    if not alt.IsActive: alt.Activate()
    doc.Regenerate()
    for e in lights:
        try: e.Symbol = alt
        except Exception as ex: L.append('  swap fail %s' % str(ex)[:45])
    doc.Regenerate()
    for nm in ('ADU - East Elevation', 'ADU - West Elevation',
               'ADU - North Elevation', 'ADU - South Elevation'):
        v = None
        for x in FEC(doc).OfClass(View):
            if not x.IsTemplate and x.Name == nm: v = x; break
        n = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures)
                     .WhereElementIsNotElementType()))
        L.append('  %-24s visible after swap: %d' % (nm, n))
    if args.get('apply'):
        t.Commit(); L.append('KEPT the swap')
    else:
        t.RollBack(); L.append('rolled back - test only')
result = '\n'.join(L)
