# Save the PROJECT document (the active document may be a family editor).
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
pdoc.Save()
result = 'saved %s' % pdoc.Title
