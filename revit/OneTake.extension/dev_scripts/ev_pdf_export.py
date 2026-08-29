# Export sheets from the PROJECT doc regardless of which document is active.
# args {"sheets":["A201"],"name":"x","dir":"..."}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ElementId,
                               PDFExportOptions)
from System.Collections.Generic import List
import os
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
ids = List[ElementId]()
for s in FEC(pdoc).OfClass(ViewSheet):
    if s.SheetNumber in args['sheets']: ids.Add(s.Id)
opt = PDFExportOptions()
opt.FileName = args.get('name', 'export')
opt.Combine = True
outdir = args.get('dir', r'C:\dev\onetake-hq\revit\progress\views')
if not os.path.isdir(outdir): os.makedirs(outdir)
ok = pdoc.Export(outdir, ids, opt)
result = 'doc=%s exported=%s count=%d -> %s' % (pdoc.Title[:28], ok, ids.Count, outdir)
