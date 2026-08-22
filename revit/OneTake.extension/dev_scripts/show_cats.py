# args {"view":"ADU - Section 4","cats":["Rooms"]}
from Autodesk.Revit.DB import FilteredElementCollector as FEC, View
L = []
v = None
for x in FEC(doc).OfClass(View):
    if not x.IsTemplate and x.Name == args['view']: v = x; break
cats = doc.Settings.Categories
t = Transaction(doc, 'OneTake: show categories'); _prep(t); t.Start()
for cn in args['cats']:
    try:
        c = cats.get_Item(cn)
        was = v.GetCategoryHidden(c.Id)
        v.SetCategoryHidden(c.Id, False)
        L.append('%s: %s hidden %s -> False' % (args['view'], cn, was))
    except Exception as ex:
        L.append('%s ERR %s' % (cn, str(ex)[:50]))
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
