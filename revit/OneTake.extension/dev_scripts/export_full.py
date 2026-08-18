# export a view (uncropped) to PNG; args: name, path, width_px
from Autodesk.Revit.DB import ImageExportOptions, ImageFileType, ExportRange, ZoomFitType, ImageResolution, View
from System.Collections.Generic import List
import os
name = args.get('name', 'Proposed Floor Plan')
view = None
for v in FilteredElementCollector(doc).OfClass(View):
    if not v.IsTemplate and v.Name == name:
        view = v
        break
if view is None:
    raise Exception('view not found: ' + name)
t = Transaction(doc, 'OneTake: uncrop')
_prep(t)
t.Start()
view.CropBoxActive = False
view.CropBoxVisible = False
t.Commit()
opts = ImageExportOptions()
opts.ExportRange = ExportRange.SetOfViews
ids = List[ElementId]()
ids.Add(view.Id)
opts.SetViewsAndSheets(ids)
opts.FilePath = args.get('path', 'C:/dev/onetake-hq/revit/progress/views/full.png')
opts.HLRandWFViewsFileType = ImageFileType.PNG
opts.ShadowViewsFileType = ImageFileType.PNG
opts.ZoomType = ZoomFitType.FitToPage
opts.PixelSize = int(args.get('width_px', 3000))
opts.ImageResolution = ImageResolution.DPI_150
doc.ExportImage(opts)
d = os.path.dirname(opts.FilePath)
result = {'files': [f for f in os.listdir(d) if f.lower().endswith('.png')], 'scale': view.Scale,
          'template': view.ViewTemplateId.Value}
