# args {"views":["West Elev.","East Elev."],"cat":"Levels"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, Level,
                               DatumExtentType, DatumEnds, BuiltInCategory as BIC)
L = []
for nm in args['views']:
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    if v is None: L.append('%s NOT FOUND' % nm); continue
    c = doc.Settings.Categories.get_Item(BIC.OST_Levels)
    L.append('%s: Levels category visible = %s' % (nm, v.GetCategoryHidden(c.Id) == False))
    for l in FEC(doc).OfClass(Level):
        try:
            cs = list(l.GetCurvesInView(DatumExtentType.ViewSpecific, v))
            if not cs: continue
            b0 = l.IsBubbleVisibleInView(DatumEnds.End0, v)
            b1 = l.IsBubbleVisibleInView(DatumEnds.End1, v)
            L.append('   %-18s len %.1f  bubbles %s/%s  hidden %s' % (
                l.Name[:18], cs[0].Length, b0, b1, l.IsHidden(v)))
        except Exception as ex:
            L.append('   %-18s ERR %s' % (l.Name[:18], str(ex)[:50]))
result = '\n'.join(L)
