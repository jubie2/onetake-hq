# Replace attic-vent note in ROOF LEGEND with roof-deck drainage note.
from Autodesk.Revit.DB import ElementId
t = Transaction(doc, 'OneTake: roof legend note'); _prep(t); t.Start()
e = doc.GetElement(ElementId(1181067))
e.Text = ('\rNOTES: ROOF DECK SHALL BE SLOPED MIN. 1/4" PER FOOT\r'
          'TO ROOF DRAINS. PROVIDE EMERGENCY OVERFLOW\r'
          'DRAINS / SCUPPERS PER CRC R903.4.1.')
doc.Regenerate(); t.Commit()
result = 'roof legend note updated'
