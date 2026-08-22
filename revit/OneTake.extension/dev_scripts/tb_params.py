# Titleblock instance params on a sheet + project info. args {"sheet":"ADU-1"}
from Autodesk.Revit.DB import ViewSheet, BuiltInCategory, StorageType, BuiltInParameter
L = []
for s in FilteredElementCollector(doc).OfClass(ViewSheet):
    if s.SheetNumber != args.get('sheet', 'ADU-1'): continue
    for ti in FilteredElementCollector(doc, s.Id).OfCategory(BuiltInCategory.OST_TitleBlocks):
        L.append('TITLEBLOCK INSTANCE %s (%s)' % (ti.Id.Value, ti.Symbol.FamilyName))
        for p in ti.Parameters:
            try:
                if p.StorageType == StorageType.String:
                    L.append('   %-34s = %s%s' % (p.Definition.Name[:34], (p.AsString() or '')[:44],
                             '' if not p.IsReadOnly else '   [read-only]'))
            except Exception: pass
pi = doc.ProjectInformation
L.append('PROJECT INFORMATION:')
for p in pi.Parameters:
    try:
        if p.StorageType == StorageType.String and p.AsString():
            L.append('   %-34s = %s' % (p.Definition.Name[:34], p.AsString()[:50]))
    except Exception: pass
result = '\n'.join(L)
