# Export a sheet PNG by SHEET NUMBER. args {"num":"A104","width_px":3000,"path":"..."}
from Autodesk.Revit.DB import (FilteredElementCollector as FEC, ViewSheet,
                               ImageExportOptions, ImageFileType, ExportRange,
                               ZoomFitType, ImageResolution, ElementId)
from System.Collections.Generic import List
import os, glob
sh = None
for s in FEC(doc).OfClass(ViewSheet):
    if s.SheetNumber == args['num']: sh = s; break
path = args['path']
d = os.path.dirname(path); stem = os.path.splitext(os.path.basename(path))[0]
for f in glob.glob(os.path.join(d, stem + '*.png')):
    try: os.remove(f)
    except Exception: pass
opts = ImageExportOptions()
opts.ExportRange = ExportRange.SetOfViews
ids = List[ElementId](); ids.Add(sh.Id); opts.SetViewsAndSheets(ids)
opts.FilePath = path
opts.HLRandWFViewsFileType = ImageFileType.PNG
opts.ShadowViewsFileType = ImageFileType.PNG
opts.ZoomType = ZoomFitType.FitToPage
opts.PixelSize = int(args.get('width_px', 3000))
opts.ImageResolution = ImageResolution.DPI_150
doc.ExportImage(opts)
result = {'files': glob.glob(os.path.join(d, stem + '*.png'))}
