# change wall types: args {"ids":[...], "type":"Generic - 6\""}
from Autodesk.Revit.DB import WallType, BuiltInParameter, Wall
want = args['type']
wt = None
for w in FilteredElementCollector(doc).OfClass(WallType):
    if w.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString() == want:
        wt = w; break
if wt is None:
    raise Exception('wall type not found: ' + want)
done, err = [], []
t = Transaction(doc, 'OneTake: wall types'); _prep(t); t.Start()
for i in args['ids']:
    try:
        w = doc.GetElement(ElementId(long(i)))
        w.WallType = wt
        done.append(i)
    except Exception as ex:
        err.append({'id': i, 'error': str(ex)})
t.Commit()
result = {'changed': done, 'errors': err}
