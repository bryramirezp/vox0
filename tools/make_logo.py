"""Render every logo file the project ships, from the one drawing in the app.

Run it after changing _make_tray_icon so the icon, the logo and the app itself
never drift apart:

    py -3 tools/make_logo.py

Importing vox0 would start the app, so this pulls the drawing function
out of the source without executing the module-level setup.
"""
import os
import sys
import types

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
DOCS   = os.path.join(ROOT, "docs")

WEB = os.path.join(ROOT, "web", "public", "images")

from PIL import Image, ImageDraw, ImageFont  # noqa: E402


def _font(size):
    """Segoe UI if this is Windows, otherwise whatever Pillow can find."""
    for name in ("segoeui.ttf", "DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _load_drawing():
    """Return _make_tray_icon() without running the app.

    The module opens a mutex, shows a message box if one is already running and
    builds a Tk window at import time, so it cannot simply be imported here.
    """
    src = open(os.path.join(ROOT, "vox0.py"), encoding="utf-8").read()
    start = src.index("MARK_STATES = {")   # the palette the mark reads its colour from
    end   = src.index("TRAY_IDLE", start)
    mod = types.ModuleType("_logo_drawing")
    mod.__dict__.update(Image=Image, ImageDraw=ImageDraw)
    exec(compile(src[start:end], "vox0.py", "exec"), mod.__dict__)
    return mod._make_tray_icon


def main():
    make = _load_drawing()
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)
    os.makedirs(WEB, exist_ok=True)
    written = []

    def save(img, path):
        img.save(path)
        if os.path.dirname(path) == DOCS:
            img.save(os.path.join(WEB, os.path.basename(path)))
        written.append((os.path.relpath(path, ROOT), os.path.getsize(path)))

    # Windows wants every size in one file: 16 for the tray and title bar, 256
    # for the large view in Explorer.
    #
    # Keep the full logo even in small Explorer and Start menu icons.
    ico_sizes = [16, 32, 48, 64, 128, 256]
    frames = [make(False, n, compact=False) for n in ico_sizes]
    ico = os.path.join(ASSETS, "icon.ico")
    frames[-1].save(ico, format="ICO",
                    sizes=[(n, n) for n in ico_sizes],
                    append_images=frames[:-1])
    written.append(("assets/icon.ico", os.path.getsize(ico)))

    # README header.
    save(make(False, 256), os.path.join(DOCS, "logo.png"))

    # Repo social preview: what GitHub shows when the link is shared.
    card = Image.new("RGB", (1280, 640), (15, 15, 15))
    mark = make(False, 260)
    card.paste(mark, (510, 90), mark)
    d = ImageDraw.Draw(card)
    for text, y, size, fill in (
        ("Vox0",                     400, 64, (255, 255, 255)),
        ("Hold a key, speak, and it types.",   490, 30, (204, 204, 204)),
        ("Runs offline on Windows",            540, 26, (153, 153, 153)),
    ):
        d.text((640, y), text, font=_font(size), fill=fill, anchor="ma")
    save(card, os.path.join(DOCS, "social-preview.png"))

    for name, size in written:
        print(f"  {name:34s} {size/1024:8.1f} KB")


if __name__ == "__main__":
    sys.exit(main())
