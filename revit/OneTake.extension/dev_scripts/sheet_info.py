# Inspect an existing sheet's parameters + list legends and view templates. args {"sheet":"A101"}
from Autodesk.Revit.DB import (ViewSheet, View, BuiltInCategory, FamilyInstance, StorageType,
                               BuiltInParameter, Viewport)
L = []
want = args.get('sheet', 'A101')
sh = None
for s in FilteredElementCollector(doc).OfClass(ViewSheet):
    if s.SheetNumber == want: sh = s; break
if sh:
    L.append('SHEET %s  "%s"  id=%s' % (sh.SheetNumber, sh.Name, sh.Id.Value))
    for p in sh.Parameters:
        try:
            if p.StorageType == StorageType.String and p.AsString():
                L.append('   param  %-32s = %s' % (p.Definition.Name[:32], p.AsString()[:46]))
        except Exception: pass
    L.append('   placed views:')
    for vp in FilteredElementCollector(doc, sh.Id).OfClass(Viewport):
        v = doc.GetElement(vp.ViewId)
        c = vp.GetBoxCenter()
        L.append('      %-9s %-30s %-12s at (%.3f, %.3f)' % (v.Id.Value, v.Name[:30], str(v.ViewType), c.X, c.Y))
    # titleblock on the sheet
    for ti in FilteredElementCollector(doc, sh.Id).OfCategory(BuiltInCategory.OST_TitleBlocks):
        L.append('   titleblock: %s : %s (type id %s)' % (ti.Symbol.FamilyName,
                 ti.Symbol.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(), ti.Symbol.Id.Value))
L.append('LEGENDS:')
for v in FilteredElementCollector(doc).OfClass(View):
    if v.IsTemplate or str(v.ViewType) != 'Legend': continue
    try: sn = v.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER).AsString() or '-'
    except Exception: sn = '-'
    L.append('   %-9s %-40s sheet=%s' % (v.Id.Value, v.Name[:40], sn))
L.append('VIEW TEMPLATES:')
for v in FilteredElementCollector(doc).OfClass(View):
    if not v.IsTemplate: continue
    L.append('   %-9s %-44s %s' % (v.Id.Value, v.Name[:44], str(v.ViewType)))
result = '\n'.join(L)
