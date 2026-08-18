# list all non-empty type+instance dimension-ish params for symbols/elements: args {"symbol_ids":[..], "element_ids":[..]}
from Autodesk.Revit.DB import StorageType, BuiltInParameter
def dump(el):
    d = {}
    for p in el.Parameters:
        n = p.Definition.Name
        if p.StorageType == StorageType.Double and not p.IsReadOnly:
            try:
                d[n] = p.AsValueString()
            except Exception:
                pass
    return d
out = {}
for sid in args.get('symbol_ids', []):
    s = doc.GetElement(ElementId(long(sid)))
    out['sym %s' % sid] = {'family': s.FamilyName, 'type': s.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString(), 'type_params': dump(s)}
for eid in args.get('element_ids', []):
    e = doc.GetElement(ElementId(long(eid)))
    out['el %s' % eid] = {'inst_params': dump(e), 'type_params': dump(e.Symbol)}
result = out
