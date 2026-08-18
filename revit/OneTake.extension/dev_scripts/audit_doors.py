from Autodesk.Revit.DB import BuiltInCategory, FamilyInstance
out = []
for d in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType():
    try:
        loc = d.Location
        if loc is None or not hasattr(loc, 'Point'): continue
        p = loc.Point
        if not (-5 < p.X < 70 and -30 < p.Y < 70): continue
        out.append({'id': d.Id.Value, 'xy': [round(p.X, 1), round(p.Y, 1)], 'facing': [round(d.FacingOrientation.X), round(d.FacingOrientation.Y)],
                    'hand': [round(d.HandOrientation.X), round(d.HandOrientation.Y)], 'host': d.Host.Id.Value if d.Host else None,
                    'type': d.Symbol.get_Parameter(__import__('Autodesk').Revit.DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()})
    except Exception as ex:
        out.append({'id': d.Id.Value, 'error': str(ex)})
result = sorted(out, key=lambda r: (r.get('xy') or [0,0])[1])
