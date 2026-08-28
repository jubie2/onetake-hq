# Add trailing blank rows so right legend column aligns 8..12 with its bubbles.
from Autodesk.Revit.DB import ElementId
t = Transaction(doc, 'OneTake: legend align'); _prep(t); t.Start()
e2 = doc.GetElement(ElementId(1732114))
e2.Text = ('2x4 STUDS @ 16" O.C. \r\r'
           'ROOF/FLR JOISTS PER PLAN \r\r'
           'R-15 BATT INSULATION\r\r'
           'R-30 BATT INSULATION\r\r'
           'FOOTING PER DETAIL ON SD1\r\r\r\r')
doc.Regenerate(); t.Commit()
result = 'aligned'
