# Set ProjectInformation to the 6633 Electric Ave ADU project facts.
pi = doc.ProjectInformation
VALS = {
    'Project Name': 'Steven Truong Res-New ADU',
    'Project Address': '6633 Electric Ave\r\nLa Jolla, CA 92037',
    'Project Number': '022225',
    'Client Name': 'Steven Truong',
    'Project Issue Date': '08.27.26',
}
L = []
t = Transaction(doc, 'OneTake: project info'); _prep(t); t.Start()
for k, v in VALS.items():
    p = pi.LookupParameter(k)
    if p and not p.IsReadOnly:
        p.Set(v); L.append('%s -> %s' % (k, v.replace('\r\n', ' / ')))
    else:
        L.append('%s SKIP' % k)
doc.Regenerate(); t.Commit()
result = '\n'.join(L)
