# Set scale + crop on for views whose name starts with a prefix. args {"prefix":"ADU - ","scale":48,"dry":true}
from Autodesk.Revit.DB import View, BuiltInParameter
pre = args.get('prefix', 'ADU - '); sc = int(args.get('scale', 48))
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: normalize views'); _prep(t); t.Start()
for v in FilteredElementCollector(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(pre): continue
        vt = str(v.ViewType)
        old = v.Scale
        crop = v.CropBoxActive
        if not args.get('dry', True):
            if vt in ('FloorPlan', 'CeilingPlan', 'Elevation', 'Section', 'EngineeringPlan'):
                try:
                    if v.ViewTemplateId.Value != -1: v.ViewTemplateId = ElementId(-1)
                except Exception: pass
                try: v.Scale = sc
                except Exception: pass
                try:
                    v.CropBoxActive = True; v.CropBoxVisible = False
                except Exception: pass
        L.append('%-9s %-30s %-12s scale %s->%s  crop %s->%s' %
                 (v.Id.Value, v.Name[:30], vt, old, sc, crop, True))
    except Exception as ex:
        L.append('err %s' % ex)
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
