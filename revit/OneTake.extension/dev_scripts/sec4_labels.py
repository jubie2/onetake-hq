# Room name labels for ADU - Section 4 (rooms behind the cut aren't 'visible' to the collector).
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote, TextNoteOptions,
                               TextNoteType, HorizontalTextAlignment, BuiltInParameter as BIP,
                               BuiltInCategory as BIC, ElementId, XYZ as _XYZ)
from System.Collections.Generic import List
NM = 'ADU - Section 4'
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == NM: v = x; break
tt = None
for t2 in FEC(doc).OfClass(TextNoteType):
    if (t2.get_Parameter(BIP.SYMBOL_NAME_PARAM).AsString() or '') == 'ARCH TEXT 12 1/8"':
        tt = t2; break
# rooms west of the cut plane (X < 1168), one label per room per floor
rooms = []
for r in FEC(doc).OfCategory(BIC.OST_Rooms).WhereElementIsNotElementType():
    try:
        if r.Area < 1: continue
        b = r.get_BoundingBox(None)
        cx = (b.Min.X + b.Max.X) / 2.0; cy = (b.Min.Y + b.Max.Y) / 2.0
        if not (1151.0 <= cx <= 1168.0 and -159.0 <= cy <= -119.0): continue
        z = r.Level.Elevation + 4.0
        rooms.append((r.get_Parameter(BIP.ROOM_NAME).AsString(), cy, z))
    except Exception: pass
L = ['rooms to label: %d' % len(rooms)]
t = Transaction(doc, 'OneTake: Section 4 labels'); _prep(t); t.Start()
kill = [e.Id for e in FEC(doc, v.Id).OfClass(TextNote)]
if kill: doc.Delete(List[ElementId](kill))
doc.Regenerate()
tf = v.CropBox.Transform; inv = tf.Inverse
n = 0
for nm2, cy, z in rooms:
    q = inv.OfPoint(_XYZ(1166.0, cy, z))
    p = tf.OfPoint(_XYZ(q.X, q.Y, 0.0))
    o = TextNoteOptions(tt.Id)
    o.HorizontalAlignment = HorizontalTextAlignment.Center
    TextNote.Create(doc, v.Id, p, nm2, o)
    n += 1
    L.append('  %-12s at Y %.1f Z %.1f' % (nm2, cy, z))
doc.Regenerate(); t.Commit()
L.append('placed %d' % n)
result = '\n'.join(L)
