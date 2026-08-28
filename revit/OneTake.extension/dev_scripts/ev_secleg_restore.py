# Restore section keynote legend columns with flat-roof wording.
from Autodesk.Revit.DB import ElementId, XYZ as _XYZ
t = Transaction(doc, 'OneTake: section legend restore'); _prep(t); t.Start()
e = doc.GetElement(ElementId(1143776))
e.Text = ('CLASS A ROOF DECK SYSTEM\r\r'
          'STUCCO @ EXTERIOR\r\r'
          '4" MIN. CONC. SLAB ON GRADE\r\r'
          '1/2" GYP. BD.\r\r'
          'WEEP SCREED\r\r'
          'PRESSURE TREATED BOTTOM PLATE\r\r'
          'DOUBLE TOP PLATE')
e.Coord = _XYZ(2.84, 7.03, 0)
e2 = doc.GetElement(ElementId(1732114))
e2.Text = ('2x4 STUDS @ 16" O.C. \r\r'
           'ROOF/FLR JOISTS PER PLAN \r\r'
           'R-15 BATT INSULATION\r\r'
           'R-30 BATT INSULATION\r\r'
           'FOOTING PER DETAIL ON SD1')
doc.Regenerate(); t.Commit()
result = 'legend columns restored'
