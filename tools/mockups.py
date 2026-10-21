"""Shirt mockups: blank white-shirt photos -> recolourable templates -> design-on-shirt JPGs.

  prep                              build mockups/tpl/<name>.{jpg,png,json} from mockups/templates/mockup_<name>.png
  render [--ids a,b] [--liked] [--tpl flatlay,hanger,model] [--colors Black,Navy]
                                    write mockups/out/<id>__<tpl>__<color>.jpg (full template resolution)

Template files: <name>.jpg is the photo, <name>.png is the shade map (grey = fabric light relative to the
chest median, alpha = shirt mask) and <name>.json has the print rectangle. The studio page uses the same
three files to render live mockups in a canvas, so both paths match.
Run with: uv run --with pillow --with numpy --with scipy tools/mockups.py <cmd>
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC, TPL, OUT = ROOT / "mockups/templates", ROOT / "mockups/tpl", ROOT / "mockups/out"
COLORS = {"Black": "#151517", "Charcoal": "#3b3b40", "Navy": "#1d2a44", "Maroon": "#5a1f2b", "Forest": "#24402f",
          "Heather": "#9a9ca1", "Pink": "#f2b8c8", "White": "#f4f4f2"}
MAXSIDE = 1400


def prep_one(src):
    name = src.stem.replace("mockup_", "")
    im = Image.open(src).convert("RGB")
    if max(im.size) > MAXSIDE:
        im.thumbnail((MAXSIDE, MAXSIDE), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    mask = (sat < 0.25) & (mx > 0.38)  # white/grey fabric vs saturated backdrop, skin, wood, dark jeans
    mask = ndimage.binary_opening(mask, iterations=2)
    lab, n = ndimage.label(mask)
    if n:
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        mask = lab == (1 + int(np.argmax(sizes)))
    mask = ndimage.binary_fill_holes(ndimage.binary_closing(mask, iterations=3))
    ys, xs = np.nonzero(mask)
    top, bot = int(ys.min()), int(ys.max())
    sh = bot - top
    row = top + int(sh * 0.72)  # below the sleeves: torso span
    cols = np.nonzero(mask[row])[0]
    tl, tr = int(cols.min()), int(cols.max())
    tw = tr - tl
    pw = int(tw * 0.60)
    px = int((tl + tr) / 2 - pw / 2)
    py = top + int(sh * (0.20 if name != "model" else 0.17))
    ph = int(sh * 0.50)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    chest = lum[py:py + ph, px:px + pw][mask[py:py + ph, px:px + pw]]
    med = float(np.median(chest))
    shade = np.clip(lum / med, 0, 1.0)
    soft = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    sp = Image.fromarray((shade * 255).astype(np.uint8)).convert("RGB")
    sp.putalpha(soft)
    TPL.mkdir(parents=True, exist_ok=True)
    im.save(TPL / f"{name}.jpg", quality=90)
    sp.save(TPL / f"{name}.png", optimize=True)
    meta = {"name": name, "w": im.width, "h": im.height, "print": {"x": px, "y": py, "w": pw, "h": ph},
            "chestMedian": round(med, 3)}
    (TPL / f"{name}.json").write_text(json.dumps(meta), encoding="utf-8")
    return meta


def prep():
    metas = [prep_one(p) for p in sorted(SRC.glob("mockup_*.png"))]
    (TPL / "index.json").write_text(json.dumps(metas), encoding="utf-8")
    for m in metas:
        print("TPL", m["name"], m["w"], "x", m["h"], "print", m["print"])
    return metas


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255


def compose(meta, design_png, color_hex):
    name = meta["name"]
    base = np.asarray(Image.open(TPL / f"{name}.jpg").convert("RGB")).astype(np.float32) / 255
    sp = np.asarray(Image.open(TPL / f"{name}.png").convert("RGBA")).astype(np.float32) / 255
    shade, m = sp[..., :1], sp[..., 3:4]
    col = hex_rgb(color_hex)
    shirt = col * shade
    if col.mean() < 0.35:  # dark shirts: keep some fold highlights visible
        shirt = shirt + (shade - 0.85).clip(0) * 0.35
    out = base * (1 - m) + shirt * m
    if design_png:
        r = meta["print"]
        d = Image.open(design_png).convert("RGBA")
        bb = d.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        if bb:
            d = d.crop(bb)
        s = min(r["w"] / d.width, r["h"] / d.height)
        d = d.resize((max(1, round(d.width * s)), max(1, round(d.height * s))), Image.LANCZOS)
        x0, y0 = r["x"] + (r["w"] - d.width) // 2, r["y"]
        da = np.asarray(d).astype(np.float32) / 255
        reg = (slice(y0, y0 + d.height), slice(x0, x0 + d.width))
        sh = np.clip(shade[reg], 0.55, 1.0)
        alpha = da[..., 3:4] * 0.97 * m[reg]
        out[reg] = out[reg] * (1 - alpha) + (da[..., :3] * sh) * alpha
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def render(ids=None, tpls=None, colors=None, liked=False):
    designs = json.loads((ROOT / "designs.json").read_text(encoding="utf-8"))
    if liked:
        fb = ROOT / "feedback.json"
        votes = json.loads(fb.read_text(encoding="utf-8")) if fb.exists() else {}
        ids = [k for k, v in votes.items() if v.get("vote") == 1]
    if ids:
        designs = [d for d in designs if d["id"] in ids]
    metas = json.loads((TPL / "index.json").read_text(encoding="utf-8"))
    metas = [m for m in metas if not tpls or m["name"] in tpls]
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for d in designs:
        src = ROOT / "designs/print" / f"{d['id']}.png"
        if not src.exists():
            print("MISSING", d["id"])
            continue
        for m in metas:
            for c in colors or ["Black"]:
                p = OUT / f"{d['id']}__{m['name']}__{c}.jpg"
                compose(m, src, COLORS.get(c, c)).save(p, quality=88)
                n += 1
                print("OK", p.name, flush=True)
    print(f"{n} mockups in {OUT}")


def arg(flag):
    return sys.argv[sys.argv.index(flag) + 1].split(",") if flag in sys.argv else None


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "prep"
    if cmd == "prep":
        prep()
    elif cmd == "render":
        render(arg("--ids"), arg("--tpl"), arg("--colors"), "--liked" in sys.argv)
