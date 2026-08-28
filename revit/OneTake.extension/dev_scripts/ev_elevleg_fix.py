# Rewrite elevation keynote legend for the flat-roof/deck ADU; add row 8 bubble.
from Autodesk.Revit.DB import ElementId, ElementTransformUtils, XYZ as _XYZ, TextNote
from System.Collections.Generic import List
t = Transaction(doc, 'OneTake: elev keynotes'); _prep(t); t.Start()
e = doc.GetElement(ElementId(1143995))
e.Text = ('KEYNOTES:\r\r'
          '42" HIGH GUARDRAIL @ ROOF DECK\r\r'
          'WINDOW PER SCHEDULE \r\r'
          'OPEN WOOD TRELLIS @ ROOF DECK\r\r'
          'STUCCO AT EXTERIOR WALL TO MATCH EXISTING\r\r'
          'EXTERIOR LIGHT\r\r'
          'EXTERIOR DOOR PER SCHEDULE\r\r'
          'SECTIONAL GARAGE DOOR\r\r'
          'EXTERIOR MTL STAIR W/ 42" GUARDRAIL')
lv = doc.GetElement(ElementId(1143900))
ids = List[ElementId](); ids.Add(ElementId(1144009))
new = ElementTransformUtils.CopyElements(lv, ids, lv, None, None)
for nid in new:
    ne = doc.GetElement(nid)
    ne.Coord = _XYZ(2.47, 5.645, 0)
    ne.Text = '8'
doc.Regenerate(); t.Commit()
result = 'legend rewritten, bubble 8 added'
