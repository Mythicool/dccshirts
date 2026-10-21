"""DCC shirt pipeline: raw Codex images -> print-ready PNGs + previews + static gallery.html.

Run: uv run --with pillow --with numpy --with scipy tools/pipeline.py [--only id1,id2] [--force]
Skips designs whose print file is newer than the raw file unless --force or --only names them.
QA notes go to designs/notes.json. The live app (Shirt Studio.cmd) reads the same files.
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW, PRINT, PREV = ROOT / "designs/raw", ROOT / "designs/print", ROOT / "designs/preview"
NOTES = ROOT / "designs/notes.json"
STRIP = Path.home() / ".claude/skills/generate-images/strip-checkerboard.py"
CANVAS = (4500, 5400)  # standard POD front print at 300 DPI (15x18 in)
STICKER = (1800, 1800)  # 6x6 in die-cut sticker at 300 DPI
MARGIN = 0.04


def has_alpha_bg(im):
    a = im.getchannel("A")
    w, h = im.size
    return all(a.getpixel(p) < 24 for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])


def prep(src, sticker=False):
    im = Image.open(src).convert("RGBA")
    notes = []
    if not has_alpha_bg(im):
        fixed = ROOT / "designs/cleaned" / src.name
        fixed.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, str(STRIP), str(src), str(fixed)], check=True)
        im = Image.open(fixed).convert("RGBA")
        notes.append("background stripped")
        if not has_alpha_bg(im):
            notes.append("CHECK: background still opaque")
    mask = im.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    im = im.crop(mask.getbbox())
    canvas = STICKER if sticker else CANVAS
    cw, ch = canvas
    s = min(cw * (1 - 2 * MARGIN) / im.width, ch * (1 - 2 * MARGIN) / im.height)
    art = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    out = Image.new("RGBA", canvas, (0, 0, 0, 0))
    top = (ch - art.height) // 2 if sticker else round(ch * MARGIN)  # stickers centered, shirts top-aligned (chest print)
    out.paste(art, ((cw - art.width) // 2, top), art)
    out.save(PRINT / f"{src.stem}.png", dpi=(300, 300), optimize=True)
    prev = im.copy()
    prev.thumbnail((700, 700))
    prev.save(PREV / f"{src.stem}.png", optimize=True)
    return notes + [f"upscale {s:.1f}x"]


def build_gallery(designs, notes):
    """Static fallback page (file://): same app as the server, data embedded, votes kept in the browser."""
    for d in designs:
        d["ready"] = (PREV / f"{d['id']}.png").exists()
        d["notes"] = notes.get(d["id"], [])
    tpl = (ROOT / "tools/studio.html").read_text(encoding="utf-8")
    (ROOT / "gallery.html").write_text(tpl.replace("/*DATA*/null", json.dumps({"designs": designs})), encoding="utf-8")


def main():
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    force = "--force" in sys.argv
    PRINT.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    designs = json.loads((ROOT / "designs.json").read_text(encoding="utf-8"))
    notes = json.loads(NOTES.read_text(encoding="utf-8")) if NOTES.exists() else {}
    for d in designs:
        src, dst = RAW / f"{d['id']}.png", PRINT / f"{d['id']}.png"
        if only and d["id"] not in only:
            continue
        if not src.exists():
            print("MISSING", d["id"], flush=True)
            continue
        if not (force or only) and dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            continue
        notes[d["id"]] = prep(src, d.get("product") == "sticker")
        print("OK", d["id"], *notes[d["id"]], flush=True)
    NOTES.write_text(json.dumps(notes, indent=1), encoding="utf-8")
    build_gallery(designs, notes)
    print("gallery.html written")


if __name__ == "__main__":
    main()
