from Autodesk.Revit.DB import BuiltInParameter as BIP
t = Transaction(doc, 'OneTake: issue date'); _prep(t); t.Start()
p = doc.ProjectInformation.get_Parameter(BIP.PROJECT_ISSUE_DATE)
old = p.AsString()
p.Set('08.24.26')
t.Commit()
result = 'Project Issue Date %r -> 08.24.26' % old
