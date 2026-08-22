# Hide imported CAD (ImportInstance) elements in views by prefix. args {"prefix":"ADU - ","dry":false}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, ImportInstance, ElementId
from System.Collections.Generic import List
L = []
dry = args.get('dry', False)
t = None
if not dry:
    t = Transaction(doc, 'OneTake: hide imports'); _prep(t); t.Start()
for v in FEC(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        ids = []
        for e in FEC(doc, v.Id).OfClass(ImportInstance):
            if e.CanBeHidden(v) and not e.IsHidden(v): ids.append(e.Id)
        if not ids: continue
        L.append('%-28s %d import(s)' % (v.Name[:28], len(ids)))
        if not dry: v.HideElements(List[ElementId](ids))
    except Exception as ex:
        L.append('%-28s ERR %s' % (v.Name[:28], str(ex)[:60]))
if not dry:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'no imports visible in ADU views'
