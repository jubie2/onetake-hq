path = r'C:\Users\francis nguyen\Dropbox\2024\RESIDENTIAL\Cuong House\Cuong House ADU REV-2.rvt'
app = uiapp.Application
res = 'not open'
for d in list(app.Documents):
    try:
        if not d.IsLinked and d.PathName == path:
            res = 'closed: %s' % d.Close(False)
            break
    except Exception as ex:
        res = 'err %s' % str(ex)[:60]
result = res
