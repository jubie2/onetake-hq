# Doors + windows in the ADU plan views with positions and Marks; also list
# available Door/Window tag families and what's on ADU-1 sheet.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, ViewSheet,
                               FamilySymbol, BuiltInCategory as BIC, XYZ as _XYZ,
                               BuiltInParameter as BIP)
X0, X1, Y0, Y1 = 1151.0, 1195.0, -159.0, -119.0
L = []
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == 'ADU-1':
        L.append('ADU-1 viewports:')
        for vpid in s.GetAllViewports():
            vp = doc.GetElement(vpid); vv = doc.GetElement(vp.ViewId)
            L.append('  %s' % vv.Name)
for nm in ('ADU - 1st Floor Plan', 'ADU - 2nd Floor Plan'):
    v = None
    for x in FEC(doc).OfClass(View):
        if not x.IsTemplate and x.Name == nm: v = x; break
    L.append('--- %s ---' % nm)
    for bic, lab in ((BIC.OST_Doors, 'DOOR'), (BIC.OST_Windows, 'WIN ')):
        for e in FEC(doc, v.Id).OfCategory(bic).WhereElementIsNotElementType():
            try:
                b = e.get_BoundingBox(None)
                c = _XYZ((b.Min.X + b.Max.X) / 2, (b.Min.Y + b.Max.Y) / 2,
                         (b.Min.Z + b.Max.Z) / 2)
                if not (X0 <= c.X <= X1 and Y0 <= c.Y <= Y1): continue
                mk = e.get_Parameter(BIP.ALL_MODEL_MARK)
                fam = e.Symbol.Family.Name
                tp = e.Symbol.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()
                L.append('%s id %s mark %-6s (%.1f,%.1f) z%.1f  [%s:%s]' % (
                    lab, e.Id.Value, mk.AsString() if mk else '?', c.X, c.Y, c.Z,
                    fam[:22], tp[:14]))
            except Exception: pass
L.append('--- tag families ---')
for bic in (BIC.OST_DoorTags, BIC.OST_WindowTags):
    for s in FEC(doc).OfClass(FamilySymbol).OfCategory(bic):
        L.append('%s : %s : %s' % (s.Category.Name, s.Family.Name,
                 s.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString()))
result = '\n'.join(L)
