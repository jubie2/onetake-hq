# Add SD / CO definitions to the MECHANICAL KEYNOTES legend.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               TextNoteOptions, ElementId, HorizontalTextAlignment,
                               XYZ as _XYZ, Arc, Line)
import math
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == 'MECHANICAL KEYNOTES': v = x; break
ttid = None
for e in FEC(doc, v.Id).OfClass(TextNote):
    ttid = e.GetTypeId(); break
t = Transaction(doc, 'OneTake: SD/CO legend'); _prep(t); t.Start()
o = TextNoteOptions(ttid)
o.HorizontalAlignment = HorizontalTextAlignment.Left
xa = _XYZ(1, 0, 0); ya = _XYZ(0, 1, 0)
rows = [
 ('SD', 34.35, 'SMOKE DETECTOR - HARD-WIRED W/ BATTERY BACKUP, INTERCONNECTED.\n'
               'EACH BEDROOM + OUTSIDE SLEEPING AREA, EACH LEVEL [CRC R314]'),
 ('CO', 33.45, 'CARBON MONOXIDE ALARM - OUTSIDE SLEEPING AREAS, EACH LEVEL [CRC R315]'),
]
for lab, y, txt in rows:
    c = _XYZ(6.0, y, 0); R = 0.14
    doc.Create.NewDetailCurve(v, Arc.Create(c, R, 0.0, math.pi, xa, ya))
    doc.Create.NewDetailCurve(v, Arc.Create(c, R, math.pi, 2 * math.pi, xa, ya))
    TextNote.Create(doc, v.Id, _XYZ(5.72, y + 0.42, 0), lab, o)
    TextNote.Create(doc, v.Id, _XYZ(6.35, y + 0.28, 0), 7.5, txt, o)
doc.Regenerate(); t.Commit()
result = 'SD/CO legend rows added'
