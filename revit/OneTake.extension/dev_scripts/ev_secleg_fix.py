# Update section keynote legend items 1 and 9 for the flat-roof/deck design.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, View, TextNote
lv = None
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'KEYNOTES SECTION': lv = v; break
L = []
t = Transaction(doc, 'OneTake: section keynotes'); _prep(t); t.Start()
for e in FEC(doc, lv.Id).OfClass(TextNote):
    txt = e.Text or ''
    if 'ROOF SHINGLE' in txt.upper():
        e.Text = 'CLASS A WATERPROOF ROOF\rDECK SYSTEM'
        L.append('item1 -> roof deck (id %s)' % e.Id.Value)
    elif txt.strip().upper().startswith('ROOF TRUSS'):
        e.Text = 'ROOF / FLOOR JOISTS PER\rFRAMING PLAN'
        L.append('item9 -> joists (id %s)' % e.Id.Value)
doc.Regenerate(); t.Commit()
result = '\n'.join(L) or 'no matching legend texts found'
