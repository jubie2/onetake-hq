# Turn on the annotation crop for views by name prefix, so viewports hug the drawing.
# args {"prefix":"ADU - ","dry":true}
from Autodesk.Revit.DB import View, BuiltInParameter
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: annotation crop'); _prep(t); t.Start()
for v in FilteredElementCollector(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        p = v.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE)
        was = p.AsInteger() if p else None
        if p and not p.IsReadOnly and not args.get('dry', True):
            p.Set(1)
        L.append('%-30s anno_crop %s -> %s' % (v.Name[:30], was, 1 if p else 'n/a'))
    except Exception as ex:
        L.append('err %s' % ex)
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
