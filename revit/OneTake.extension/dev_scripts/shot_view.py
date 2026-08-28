# Export a single view PNG by view ID. args {"id":718579,"width_px":2000,"path":"..."}
from Autodesk.Revit.DB import (ImageExportOptions, ImageFileType, ExportRange,
                               ZoomFitType, ImageResolution, ElementId)
from System.Collections.Generic import List
import os, glob
path = args['path']
d = os.path.dirname(path); stem = os.path.splitext(os.path.basename(path))[0]
for f in glob.glob(os.path.join(d, stem + ' - *.png')):
    try: os.remove(f)
    except Exception: pass
opts = ImageExportOptions()
opts.ExportRange = ExportRange.SetOfViews
ids = List[ElementId](); ids.Add(ElementId(int(args['id'])))
opts.SetViewsAndSheets(ids)
opts.FilePath = path
opts.HLRandWFViewsFileType = ImageFileType.PNG
opts.ShadowViewsFileType = ImageFileType.PNG
opts.ZoomType = ZoomFitType.FitToPage
opts.PixelSize = int(args.get('width_px', 2000))
opts.ImageResolution = ImageResolution.DPI_150
doc.ExportImage(opts)
result = {'files': glob.glob(os.path.join(d, stem + '*.png'))}
