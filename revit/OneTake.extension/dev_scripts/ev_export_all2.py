# Export every sheet of the PROJECT doc to progress/pdfset-ev/pg-<NUM>.pdf
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet, ElementId,
                               PDFExportOptions)
from System.Collections.Generic import List
import os
pdoc = None
for d in doc.Application.Documents:
    if not d.IsFamilyDocument and 'Electric Ave' in d.Title: pdoc = d; break
outdir = r'C:\dev\onetake-hq\revit\progress\pdfset-ev'
if not os.path.isdir(outdir): os.makedirs(outdir)
L = []
for s in FEC(pdoc).OfClass(ViewSheet):
    num = s.SheetNumber
    if num.startswith('X-'): continue
    ids = List[ElementId](); ids.Add(s.Id)
    opt = PDFExportOptions()
    opt.FileName = 'pg-' + num
    opt.Combine = True
    ok = pdoc.Export(outdir, ids, opt)
    L.append('%s%s' % (num, '' if ok else ' FAIL'))
result = ', '.join(L)
