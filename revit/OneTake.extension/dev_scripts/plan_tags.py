# IndependentTags in the ADU plan views: what type, what they tag.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag,
                               BuiltInParameter as BIP, XYZ as _XYZ)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
for nm in ('ADU - 1st Floor Plan', 'ADU - 2nd Floor Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    L.append('--- %s ---' % nm)
    n_in = n_out = 0
    for e in FEC(doc, v.Id).OfClass(IndependentTag):
        try:
            h = e.TagHeadPosition
            inreg = X0 <= h.X <= X1 and Y0 <= h.Y <= Y1
            tt = doc.GetElement(e.GetTypeId())
            fam = '%s:%s' % (tt.FamilyName, tt.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString())
            cat = ''
            try:
                ids = list(e.GetTaggedLocalElementIds())
                if ids:
                    te = doc.GetElement(ids[0])
                    cat = te.Category.Name if te and te.Category else '?'
            except Exception: pass
            if inreg:
                n_in += 1
                L.append('  IN  %s "%s" tags %s at (%.1f,%.1f)' % (
                    fam, e.TagText, cat, h.X, h.Y))
            else: n_out += 1
        except Exception: pass
    L.append('  (%d in ADU region, %d outside)' % (n_in, n_out))
result = '\n'.join(L)
