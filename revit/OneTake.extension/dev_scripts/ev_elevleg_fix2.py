# Widen elevation keynote text so items stay one line; strip underline.
from Autodesk.Revit.DB import ElementId
t = Transaction(doc, 'OneTake: legend format'); _prep(t); t.Start()
e = doc.GetElement(ElementId(1143995))
L = ['width was %.2f' % e.Width]
try:
    e.Width = e.Width * 1.45
    L.append('width now %.2f' % e.Width)
except Exception as ex:
    L.append('width fail %s' % str(ex)[:50])
try:
    ft = e.GetFormattedText()
    ft.SetUnderlineStatus(False)
    e.SetFormattedText(ft)
    L.append('underline stripped')
except Exception as ex:
    L.append('fmt fail %s' % str(ex)[:50])
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
