# Dump TAG LABEL leader geometry in a view. args {"view":"ADU - West Elevation"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View,
                               BuiltInCategory as BIC)
nm = args.get('view')
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
L = ['view %s' % nm]
for e in FEC(doc, v.Id).OfCategory(BIC.OST_GenericAnnotation).WhereElementIsNotElementType():
    try:
        if e.Symbol.Family.Name != 'TAG LABEL': continue
        pt = e.Location.Point
        txt = ''
        p = e.LookupParameter('TEXT')
        if p: txt = p.AsString()
        info = ['%s at (%.2f,%.2f,%.2f)' % (txt, pt.X, pt.Y, pt.Z)]
        try:
            lds = list(e.GetLeaders())
        except Exception:
            lds = []
            try:
                la = e.Leaders
                for i in range(la.Size): lds.append(la.get_Item(i))
            except Exception: pass
        for ld in lds:
            try:
                en = ld.End; el = ld.Elbow
                info.append('leader end (%.2f,%.2f,%.2f) elbow (%.2f,%.2f,%.2f)' % (
                    en.X, en.Y, en.Z, el.X, el.Y, el.Z))
            except Exception as ex:
                info.append('leader ? %s' % str(ex)[:40])
        L.append('  ' + ' | '.join(info))
    except Exception as ex:
        L.append('ERR %s' % str(ex)[:60])
result = '\n'.join(L)
