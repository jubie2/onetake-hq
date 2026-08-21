# Crop a plan view to a model-space rectangle, export PNG, restore the previous crop state.
# args {"view":"Proposed Floor Plan","region":[xmin,ymin,xmax,ymax],"width_px":2600,"path":"C:/.../x.png"}
from Autodesk.Revit.DB import (View, ImageExportOptions, ImageFileType, ExportRange,
                               ZoomFitType, ImageResolution, BoundingBoxXYZ)
from System.Collections.Generic import List
import os, glob
name = args.get('view', 'Proposed Floor Plan')
view = [v for v in FilteredElementCollector(doc).OfClass(View) if not v.IsTemplate and v.Name == name][0]
r = args.get('region')
prev_active, prev_box = view.CropBoxActive, view.CropBox
if r:
    bb = view.CropBox            # keep its Transform, set Min/Max in box-local coords
    tf = bb.Transform
    inv = tf.Inverse
    pts = [inv.OfPoint(XYZ(float(r[0]), float(r[1]), 0)), inv.OfPoint(XYZ(float(r[2]), float(r[3]), 0))]
    xs = [p.X for p in pts]; ys = [p.Y for p in pts]
    nb = BoundingBoxXYZ(); nb.Transform = tf
    nb.Min = XYZ(min(xs), min(ys), bb.Min.Z); nb.Max = XYZ(max(xs), max(ys), bb.Max.Z)
    t = Transaction(doc, 'OneTake: crop'); _prep(t); t.Start()
    view.CropBox = nb; view.CropBoxActive = True; view.CropBoxVisible = False
    t.Commit()
path = args.get('path', 'C:/dev/onetake-hq/revit/progress/views/shot.png')
d = os.path.dirname(path); stem = os.path.splitext(os.path.basename(path))[0]
for f in glob.glob(os.path.join(d, stem + '*.png')):
    try: os.remove(f)
    except Exception: pass
opts = ImageExportOptions()
opts.ExportRange = ExportRange.SetOfViews
ids = List[ElementId](); ids.Add(view.Id); opts.SetViewsAndSheets(ids)
opts.FilePath = path
opts.HLRandWFViewsFileType = ImageFileType.PNG
opts.ShadowViewsFileType = ImageFileType.PNG
opts.ZoomType = ZoomFitType.FitToPage
opts.PixelSize = int(args.get('width_px', 2600))
opts.ImageResolution = ImageResolution.DPI_150
doc.ExportImage(opts)
files = glob.glob(os.path.join(d, stem + '*.png'))
if r and args.get('restore', True):
    t = Transaction(doc, 'OneTake: restore crop'); _prep(t); t.Start()
    view.CropBox = prev_box; view.CropBoxActive = prev_active
    t.Commit()
result = {'files': files, 'view': view.Name, 'scale': view.Scale}
