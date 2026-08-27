# Export sheets to PDF with Revit's native PDF exporter. args {"sheets":["A01"],"name":"a01test"}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ElementId,
                               PDFExportOptions)
from System.Collections.Generic import List
ids = List[ElementId]()
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber in args['sheets']: ids.Add(s.Id)
opt = PDFExportOptions()
opt.FileName = args.get('name', 'export')
opt.Combine = True
outdir = args.get('dir', r'C:\dev\onetake-hq\revit\progress\views')
ok = doc.Export(outdir, ids, opt)
result = 'exported=%s count=%d to %s' % (ok, ids.Count, outdir)
