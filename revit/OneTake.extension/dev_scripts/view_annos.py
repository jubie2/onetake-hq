# Count annotation by category in views with a name prefix. args {"prefix":"ADU - "}
from Autodesk.Revit.DB import View, FilteredElementCollector as FEC, BuiltInCategory
cats = {'Keynote Tags': BuiltInCategory.OST_KeynoteTags, 'Room Tags': BuiltInCategory.OST_RoomTags,
        'Generic Tags': BuiltInCategory.OST_GenericAnnotation, 'Text': BuiltInCategory.OST_TextNotes,
        'Dimensions': BuiltInCategory.OST_Dimensions, 'Detail Items': BuiltInCategory.OST_DetailComponents,
        'Rooms visible': BuiltInCategory.OST_Rooms}
L = []
for v in FEC(doc).OfClass(View):
    if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
    if str(v.ViewType) not in ('Section', 'Elevation', 'FloorPlan'): continue
    row = []
    for nm, bic in cats.items():
        try:
            n = len(list(FEC(doc, v.Id).OfCategory(bic).WhereElementIsNotElementType()))
        except Exception:
            n = -1
        if n: row.append('%s=%d' % (nm, n))
    L.append('%-26s %-10s %s' % (v.Name[:26], str(v.ViewType), ', '.join(row) or 'none'))
result = '\n'.join(sorted(L))
