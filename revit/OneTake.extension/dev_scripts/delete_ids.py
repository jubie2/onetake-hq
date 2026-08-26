# Delete elements by id. args {"ids":[...]}
from Autodesk.Revit.DB import ElementId
from System.Collections.Generic import List
ids = [ElementId(int(i)) for i in args['ids']]
t = Transaction(doc, 'OneTake: delete'); _prep(t); t.Start()
doc.Delete(List[ElementId](ids))
t.Commit()
result = 'deleted %d' % len(ids)
