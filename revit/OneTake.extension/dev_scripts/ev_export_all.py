# Export every sheet to its own PDF page: progress/pdfset-ev/pg-<NUM>.pdf
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ElementId,
                               PDFExportOptions)
from System.Collections.Generic import List
import os
outdir = r'C:\dev\onetake-hq\revit\progress\pdfset-ev'
if not os.path.isdir(outdir): os.makedirs(outdir)
L = []
for s in FEC(doc).OfClass(ViewSheet):
    num = s.SheetNumber
    if num.startswith('X-'): continue
    ids = List[ElementId](); ids.Add(s.Id)
    opt = PDFExportOptions()
    opt.FileName = 'pg-' + num
    opt.Combine = True
    ok = doc.Export(outdir, ids, opt)
    L.append('%s %s' % (num, 'ok' if ok else 'FAIL'))
result = '\n'.join(L)
