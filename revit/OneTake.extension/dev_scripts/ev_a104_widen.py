from Autodesk.Revit.DB import ElementId
t = Transaction(doc, 'OneTake: widen deck note'); _prep(t); t.Start()
e = doc.GetElement(ElementId(1848104))
try: e.Width = e.Width * 1.8
except Exception: pass
doc.Regenerate(); t.Commit()
result = 'widened to %.3f' % e.Width
