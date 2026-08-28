# A104 texts: retitle deck note, delete stray shingle note, rewrite materials info;
# also list ROOF LEGEND legend view contents.
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, View, TextNote,
                               ElementId, XYZ as _XYZ)
L = []
t = Transaction(doc, 'OneTake: A104 texts'); _prep(t); t.Start()
doc.Delete(ElementId(1639199))
e = doc.GetElement(ElementId(1848104))
e.Text = 'NEW ROOF DECK - CLASS A\rWATERPROOF DECK SYSTEM'
e.Coord = _XYZ(1.86, 1.35, 0)
e2 = doc.GetElement(ElementId(2115201))
e2.Text = ('ROOF MATERIALS INFO:\r'
           'ROOF DECK: CLASS A FIRE-RATED WALKABLE WATERPROOF\r'
           'DECK SYSTEM (ICC-ES LISTED), INSTALLED PER\r'
           'MANUFACTURER SPECIFICATION.\r'
           'SLOPE 1/4" PER FOOT MIN. TO ROOF DRAINS.\r'
           'PROVIDE OVERFLOW DRAINS / SCUPPERS PER CRC R903.4.1\r\r'
           'GUARDRAIL: 42" HIGH MIN. AT ROOF DECK PERIMETER,\r'
           'OPENINGS SHALL REJECT A 4" SPHERE PER CRC R312.\r\r'
           'OPEN WOOD TRELLIS: PER PLAN, PRESSURE TREATED OR\r'
           'NATURALLY DURABLE WOOD.')
doc.Regenerate(); t.Commit()
L.append('sheet texts updated')
for v in FEC(doc).OfClass(View):
    if not v.IsTemplate and v.Name == 'ROOF LEGEND':
        for e3 in FEC(doc, v.Id).OfClass(TextNote):
            c = e3.Coord
            L.append('LEG %s (%.2f,%.2f): %s' % (e3.Id.Value, c.X, c.Y,
                     (e3.Text or '').replace('\r', '|').replace('\n', '|')[:60]))
result = '\n'.join(L)
