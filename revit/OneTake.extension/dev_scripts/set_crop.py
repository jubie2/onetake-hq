# Turn a view's crop on/off. args {"view_id":1844391, "on":true}
from Autodesk.Revit.DB import View
v = doc.GetElement(ElementId(long(args['view_id'])))
t = Transaction(doc, 'OneTake: crop toggle'); _prep(t); t.Start()
v.CropBoxActive = bool(args.get('on', True))
v.CropBoxVisible = bool(args.get('visible', True))
t.Commit()
result = {'view': v.Name, 'id': v.Id.Value, 'crop_active': v.CropBoxActive, 'crop_visible': v.CropBoxVisible}
