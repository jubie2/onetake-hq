# Hide crop region outlines. args {"prefix":"ADU - "}
from Autodesk.Revit.DB import View, FilteredElementCollector as FEC
L = []
t = Transaction(doc, 'OneTake: crop visibility'); _prep(t); t.Start()
for v in FEC(doc).OfClass(View):
    try:
        if v.IsTemplate or not v.Name.startswith(args.get('prefix', 'ADU - ')): continue
        if v.CropBoxVisible:
            v.CropBoxVisible = False
            L.append('%s: crop outline hidden' % v.Name[:30])
    except Exception: pass
doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'all already hidden'
