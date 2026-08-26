# List every annotation in a view: tags, generic annotations, text notes, detail curves.
# args {"view":"ADU - West Elevation"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag,
                               TextNote, CurveElement, FamilyInstance,
                               BuiltInParameter as BIP)
nm = args.get('view', 'ADU - West Elevation')
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
if v is None:
    result = 'view not found'
else:
    L = ['view %s id %s' % (nm, v.Id.Value)]
    for e in FEC(doc, v.Id).WhereElementIsNotElementType():
        try:
            cn = e.Category.Name if e.Category else '?'
            if isinstance(e, IndependentTag):
                txt = ''
                try: txt = e.TagText
                except Exception: txt = '?'
                fam = ''
                try:
                    tt = doc.GetElement(e.GetTypeId())
                    fam = '%s : %s' % (tt.FamilyName,
                        tt.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString())
                except Exception: pass
                h = e.TagHeadPosition
                L.append('TAG %s id %s [%s] "%s" head (%.1f,%.1f,%.1f) leader %s' % (
                    cn, e.Id.Value, fam, txt, h.X, h.Y, h.Z, e.HasLeader))
            elif isinstance(e, FamilyInstance) and cn in ('Generic Annotations',):
                fam = e.Symbol.Family.Name
                tn = e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()
                lp = e.Location
                pt = lp.Point if hasattr(lp, 'Point') else None
                ps = '(%.1f,%.1f,%.1f)' % (pt.X, pt.Y, pt.Z) if pt else '?'
                pars = []
                for p in e.Parameters:
                    try:
                        if p.StorageType.ToString() == 'String' and p.AsString():
                            pars.append('%s=%s' % (p.Definition.Name, p.AsString()))
                    except Exception: pass
                L.append('GA  id %s [%s : %s] at %s %s' % (
                    e.Id.Value, fam, tn, ps, ' '.join(pars[:4])))
            elif isinstance(e, TextNote):
                L.append('TXT id %s "%s"' % (e.Id.Value, (e.Text or '').replace('\r', ' / ')[:60].strip()))
            elif isinstance(e, CurveElement):
                c = e.GeometryCurve
                L.append('CRV id %s %s len %.2f' % (e.Id.Value, c.GetType().Name, c.Length))
        except Exception as ex:
            L.append('ERR %s %s' % (e.Id.Value, str(ex)[:40]))
    result = '\n'.join(L)
