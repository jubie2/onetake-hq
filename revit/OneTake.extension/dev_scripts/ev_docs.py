# List every open document so scripts can target the project, not the active family.
L = []
try:
    for d in doc.Application.Documents:
        L.append('%-55s family=%s  path=%s' % (d.Title, d.IsFamilyDocument, d.PathName[:70]))
except Exception as ex:
    L.append('enumerate failed: %s' % str(ex)[:60])
L.append('ACTIVE: %s (family=%s)' % (doc.Title, doc.IsFamilyDocument))
result = '\n'.join(L)
