"""Extract a PDF page's native embedded scan and enhance it for reading (local contrast + unsharp).
usage: enhance.py <pdf> <page> <out.png>"""
import sys, os, io
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pylib'))
import numpy as np, pymupdf
from PIL import Image, ImageFilter, ImageOps
pdf, page, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
d = pymupdf.open(pdf)
xref = d[page].get_images(full=True)[0][0]
info = d.extract_image(xref)
im = Image.open(io.BytesIO(info['image'])).convert('L')
a = np.asarray(im, dtype=np.float32)
# local background estimate (big box blur) -> divide out uneven lighting of the photo
bg = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.BoxBlur(60)), dtype=np.float32)
flat = np.clip(a / np.maximum(bg, 1) * 200.0, 0, 255).astype(np.uint8)
img = Image.fromarray(flat)
img = ImageOps.autocontrast(img, cutoff=1)
img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=180, threshold=2))
img.save(out)
print('native %d x %d -> %s' % (im.size[0], im.size[1], out))
