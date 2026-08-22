# Set Project Information text params. args {"set":{"Project Name":"...","Project Address":"..."},"dry":true}
from Autodesk.Revit.DB import StorageType
pi = doc.ProjectInformation
L = []
t = None
if not args.get('dry', True):
    t = Transaction(doc, 'OneTake: project info'); _prep(t); t.Start()
for k, val in (args.get('set') or {}).items():
    p = pi.LookupParameter(k)
    if p is None or p.StorageType != StorageType.String:
        L.append('%s: not found' % k); continue
    old = p.AsString()
    if not args.get('dry', True) and not p.IsReadOnly:
        p.Set(str(val))
    L.append('%-20s "%s" -> "%s"' % (k, old, val))
if t is not None:
    doc.Regenerate(); t.Commit()
result = '\n'.join(L)
