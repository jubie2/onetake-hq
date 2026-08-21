# Open a project document and close the previously active one (saving it first if modified).
# args {"path": "C:/.../file.rvt", "save_old": true}
import os
path = args['path']
if not os.path.exists(path):
    raise Exception('not found: ' + path)
old = uiapp.ActiveUIDocument.Document if uiapp.ActiveUIDocument else None
old_title = old.Title if old else None
old_mod = bool(old.IsModified) if old else False
saved_old = False
if old is not None and old_mod and args.get('save_old', True):
    old.Save()
    saved_old = True
uidoc = uiapp.OpenAndActivateDocument(path)
new = uidoc.Document
closed_old = False
if old is not None and old.PathName != new.PathName:
    try:
        closed_old = bool(old.Close(False))
    except Exception as ex:
        closed_old = 'error: %s' % ex
result = {'old_title': old_title, 'old_was_modified': old_mod, 'saved_old': saved_old,
          'closed_old': closed_old, 'new_title': new.Title, 'new_path': new.PathName}
