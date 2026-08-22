from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag, TextNote,
                               CurveElement, BuiltInCategory as BIC)
L = []
for nm in ('North Elev. (Bldg-1)', 'South Elev. (Bldg-1)', 'East Elev.', 'West Elev.'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: L.append('%s not found' % nm); continue
    tags = list(FEC(doc, v.Id).OfClass(IndependentTag))
    txt = [(t2.Text or '').strip() for t2 in FEC(doc, v.Id).OfClass(TextNote)]
    nums = [s for s in txt if s.isdigit() and len(s) <= 2]
    lights = len(list(FEC(doc, v.Id).OfCategory(BIC.OST_LightingFixtures)
                      .WhereElementIsNotElementType()))
    L.append('%-22s keynote tags=%d  number texts=%s  lighting fixtures drawn=%d' % (
        nm, len(tags), nums or '-', lights))
    for t2 in tags[:6]:
        try: L.append('     tag text=%r' % t2.TagText)
        except Exception: pass
result = '\n'.join(L)
