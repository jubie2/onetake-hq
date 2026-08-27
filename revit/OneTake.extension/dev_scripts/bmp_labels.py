# Separate the WM-8 / WM-9 labels on the Keeler BMP view.
from Autodesk.Revit.DB import FilteredElementCollector as FEC, ElementId, TextNote, XYZ as _XYZ
v = doc.GetElement(ElementId(2196450))
t = Transaction(doc, 'OneTake: BMP labels'); _prep(t); t.Start()
for e in FEC(doc, v.Id).OfClass(TextNote):
    txt = e.Text or ''
    if 'WM-8' in txt:
        e.Coord = _XYZ(1189.8, -134.2, 0)
    elif 'WM-9' in txt:
        e.Coord = _XYZ(1199.0, -149.5, 0)
doc.Regenerate(); t.Commit()
result = 'labels moved'
