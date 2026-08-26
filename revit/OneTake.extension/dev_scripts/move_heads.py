# Nudge IndependentTag heads (door tags) by tag text within a view.
# args {"view":"...","moves":[{"text":"202","to":[x,y]}]}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, IndependentTag,
                               XYZ as _XYZ)
nm = args['view']
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == nm: v = x; break
t = Transaction(doc, 'OneTake: move tag heads'); _prep(t); t.Start()
L = []
for mv in args['moves']:
    hit = None
    for e in FEC(doc, v.Id).OfClass(IndependentTag):
        try:
            if e.TagText == mv['text']: hit = e; break
        except Exception: pass
    if hit is None:
        L.append('%s not found' % mv['text']); continue
    old = hit.TagHeadPosition
    hit.TagHeadPosition = _XYZ(float(mv['to'][0]), float(mv['to'][1]), old.Z)
    L.append('%s moved' % mv['text'])
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
