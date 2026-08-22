# What can we tag in the ADU sections? args {"view":"ADU - Section 2"}
from Autodesk.Revit.DB import (View, FilteredElementCollector as FEC, BuiltInCategory, BuiltInParameter,
                               ElementId as EId, FamilySymbol)
name = args.get('view', 'ADU - Section 2')
v = [x for x in FEC(doc).OfClass(View) if not x.IsTemplate and x.Name == name][0]
L = ['VIEW %s (%s) id=%s' % (v.Name, v.ViewType, v.Id.Value)]
# elements visible in the view + their keynote values
cats = {'Walls': BuiltInCategory.OST_Walls, 'Roofs': BuiltInCategory.OST_Roofs,
        'Floors': BuiltInCategory.OST_Floors, 'Ceilings': BuiltInCategory.OST_Ceilings,
        'Structural Foundations': BuiltInCategory.OST_StructuralFoundation}
for nm, bic in cats.items():
    els = list(FEC(doc, v.Id).OfCategory(bic).WhereElementIsNotElementType())
    kn = 0
    sample = []
    for e in els[:14]:
        try:
            t = doc.GetElement(e.GetTypeId())
            p = t.get_Parameter(BuiltInParameter.KEYNOTE_PARAM) if t else None
            val = p.AsString() if p else None
            if val: kn += 1
            if len(sample) < 4:
                sample.append('%s=%s' % (e.Id.Value, val or '-'))
        except Exception: pass
    L.append('  %-24s visible=%-3d with keynote=%d   %s' % (nm, len(els), kn, ', '.join(sample)))
# rooms visible
rooms = list(FEC(doc, v.Id).OfCategory(BuiltInCategory.OST_Rooms))
L.append('  Rooms visible: %s' % ', '.join('%s(%s)' % (r.Id.Value,
        r.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()) for r in rooms[:8]))
# available tag families
for nm, bic in (('Keynote tag types', BuiltInCategory.OST_KeynoteTags), ('Room tag types', BuiltInCategory.OST_RoomTags)):
    ts = [t for t in FEC(doc).OfClass(FamilySymbol) if t.Category and t.Category.Id.Value == EId(bic).Value]
    L.append('  %s: %s' % (nm, ', '.join('%s:%s' % (t.Id.Value, t.FamilyName[:22]) for t in ts[:6])))
result = '\n'.join(L)
