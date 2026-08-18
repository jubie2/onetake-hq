# report type + instance params of given symbols/elements: args {"symbol_ids":[...], "names":[...]}
from Autodesk.Revit.DB import FamilySymbol, StorageType, BuiltInParameter
out = {}
names = args.get('names') or ['Width', 'Height', 'Default Sill Height', 'Sill Height', 'Rough Width', 'Rough Height', 'Depth', 'Length']
for sid in args.get('symbol_ids', []):
    s = doc.GetElement(ElementId(long(sid)))
    d = {'family': s.FamilyName, 'type': s.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(), 'params': {}}
    for p in s.Parameters:
        n = p.Definition.Name
        if n in names:
            d['params'][n] = p.AsValueString() if p.StorageType != StorageType.String else p.AsString()
            d['params'][n + '_ro'] = p.IsReadOnly
    out[str(sid)] = d
result = out
