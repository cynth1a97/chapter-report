#!/usr/bin/env python3
"""Get readable pages out of a chapter PDF.

Usage: python3 pdf_pages.py <chapter.pdf> <out_dir>

* If the PDF has a text layer, writes <out_dir>/text.txt (one "=== pN ===" block per page).
* Always extracts the embedded page images (scanned books) as <out_dir>/pNN.png,
  resized to 1400 px wide so they are easy to read.
Needs: pip install pypdf  (and Pillow, or macOS `sips`, for PNG conversion)
"""
import pathlib
import shutil
import subprocess
import sys

try:
    import pypdf
except ImportError:
    sys.exit("Please install pypdf first:  pip install pypdf")

src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
reader = pypdf.PdfReader(str(src))
print(f"{len(reader.pages)} pages")

# 1. text layer
blocks = [f"=== p{i + 1} ===\n{(p.extract_text() or '').strip()}" for i, p in enumerate(reader.pages)]
text = "\n\n".join(blocks)
if sum(len(b) for b in blocks) > 40 * len(blocks):
    (out / "text.txt").write_text(text)
    print("text layer found → text.txt")
else:
    print("no usable text layer (scanned PDF) → read the page images")


def to_png(raw: pathlib.Path, png: pathlib.Path) -> None:
    try:
        from PIL import Image
        img = Image.open(raw)
        if img.width > 1400:
            img = img.resize((1400, round(img.height * 1400 / img.width)))
        img.convert("RGB").save(png)
    except ImportError:
        if shutil.which("sips"):
            subprocess.run(["sips", "-s", "format", "png", "--resampleWidth", "1400", str(raw), "--out", str(png)],
                           check=True, capture_output=True)
        else:
            sys.exit("Install Pillow (pip install Pillow) to convert page images.")
    raw.unlink()


# 2. page images
count = 0
for i, page in enumerate(reader.pages):
    for j, im in enumerate(page.images):
        suffix = pathlib.Path(im.name).suffix or ".bin"
        raw = out / f"p{i + 1:02d}_{j}{suffix}"
        raw.write_bytes(im.data)
        png = out / (f"p{i + 1:02d}.png" if j == 0 else f"p{i + 1:02d}_{j}.png")
        to_png(raw, png)
        count += 1
print(f"{count} page images → {out}")
