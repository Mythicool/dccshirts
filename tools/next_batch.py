"""Make the next batch of designs from the taste profile, hands-free.

  next_batch.py generate --n 10 --track auto|personal|sell
      taste.py plans N slots (format/art/subject/humor/palette sampled from your votes)
      -> Codex (write engine) turns the slots into concepts + prompts: image-prompts/pack-auto-<k>.{md,json}
      -> validated and merged into designs.json (batch k)
      -> Codex (image engine) draws them into designs/raw
      -> pipeline.py preps print files and previews
  next_batch.py redo
      re-draws every design flagged "redo" in feedback.json with its original prompt, then preps it.

Progress goes to studio/job.json (read by the studio app). Run with the uv deps of pipeline.py.
"""
import json, re, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import taste

ROOT = taste.ROOT
STUDIO = ROOT / "studio"
JOB = STUDIO / "job.json"
DELEGATE = Path.home() / ".claude/skills/codex-delegate/delegate.mjs"
CHECK = "transparent background, one centered print graphic, exact lettering spelled as quoted, no shirt mockup, no watermark"
BY = "studio-auto"
state = {}


def status(step, **kw):
    state.update(kw, step=step, updated=time.time())
    state.setdefault("log", []).append(f"{time.strftime('%H:%M:%S')} {step}")
    STUDIO.mkdir(exist_ok=True)
    JOB.write_text(json.dumps(state, indent=1), encoding="utf-8")
    print(step, flush=True)


def delegate(*args):
    cmd = ["node", str(DELEGATE), "run", "--project", str(ROOT), "--by", BY, *args]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = p.stdout + p.stderr
    lines = [l for l in out.splitlines() if re.match(r"^(JOB|OK|MISSING)", l) or "limit" in l.lower()]
    state.setdefault("log", []).extend(lines[-30:])
    return out


def pipeline(ids):
    status(f"Preparing print files for {len(ids)} designs")
    subprocess.run([sys.executable, str(ROOT / "tools/pipeline.py"), "--only", ",".join(ids)], check=False)


def brief(k, slots, pack_md, pack_json):
    designs = json.loads((ROOT / "designs.json").read_text(encoding="utf-8"))
    titles = "; ".join(d["title"] for d in designs)
    slot_lines = "\n".join(
        f"{i + 1}. id prefix `A{k}_{i + 1:02d}_` · track **{s['track']}** · format **{s['format']}** · art style **{s['art']}**"
        f" · subject **{s['subject']}** · humor **{s['humor']}** · palette **{s['palette']}**" for i, s in enumerate(slots))
    return f"""# Goal
Write {len(slots)} new T-shirt design concepts and image prompts for the Dungeon Crawler Carl shirt project, one per slot below.

# Read first
- image-prompts/TASTE.md: what the user liked and disliked, with their notes. Lean into the likes; avoid what the dislikes have in common.
- image-prompts/STYLE.md: print rules (sent with every prompt automatically; do not repeat it).
- image-prompts/pack-d-fanart.md: the character descriptions at the top (copy them WORD FOR WORD when a character appears) and the prompt format to copy.
- image-prompts/pack-c-sellable.md: examples for the sellable track.

# Slots (each slot is one design; keep every attribute)
{slot_lines}

Rules per track:
- personal: fan art, may use names, quotes and characters from the books (subject names map to the characters in pack-d; "trio" = Carl, Donut and Mongo together; "system" = the dungeon AI, Borant or the show; "dungeon" = places, floors, items).
- sell: NO names, quotes, book titles or characters by name. Generic descriptions only (e.g. "a fluffy white flat-faced long-haired cat wearing a small jeweled gold tiara"). Write a marketplace listing title and 5 tags.
Each concept: a format people already buy plus a joke that lands for fans. No repeats of existing titles: {titles}

# Files to write (only these two)
1. image-prompts/pack-auto-{k}.md: heading line, then for each slot a section exactly like pack-d: "### `<id>.png`" then a ```text block with ONE prompt of 80-140 words. Order: subject, pose, framing, every piece of lettering in double quotes in capitals, palette (3-5 inks), style, "Centered, filling 80 percent of the frame. Transparent background, tall 2:3. No other text, no watermark." Max 12 words of lettering per design.
2. image-prompts/pack-auto-{k}.json: a JSON array, one object per slot in order: {{"id", "title", "style", "hook", "listing", "tags"}}. id = slot prefix + 2-4 word snake_case slug (lowercase, a-z0-9_). style = short art-style name. hook = one sentence on why it sells/lands. listing = "" and tags = ["fan art"] for personal; real listing and 5 tags for sell.

# Done when
Both files exist, the JSON parses, ids in both files match and are in slot order.

# Do not
Edit any other file, run image generation, or add dependencies.

# Reply
The list of ids and titles, under 15 lines.
"""


def generate(n, track, dry=False):
    designs = json.loads((ROOT / "designs.json").read_text(encoding="utf-8"))
    k = max(d.get("batch", 1) for d in designs) + 1
    pack_md, pack_json = ROOT / f"image-prompts/pack-auto-{k}.md", ROOT / f"image-prompts/pack-auto-{k}.json"
    taste.write_report()
    slots = taste.plan(n, track)
    status(f"Batch {k}: planned {n} slots from your taste", batch=k, slots=slots, state="running")
    bf = STUDIO / f"brief-batch-{k}.md"
    bf.write_text(brief(k, slots, pack_md, pack_json), encoding="utf-8")
    status("Codex is writing concepts and prompts")
    delegate("--engine", "write", "--tier", "workhorse", "--task", f"dcc auto batch {k} prompts", "--brief", str(bf))
    try:
        meta = json.loads(pack_json.read_text(encoding="utf-8"))
        prompts = re.findall(r"### `([^`]+)\.png`\s*```text\s*\n([\s\S]*?)\n```", pack_md.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return status(f"FAILED: Codex did not write valid pack files ({e})", state="failed")
    ids = [p[0] for p in prompts]
    if len(meta) != len(slots) or [m["id"] for m in meta] != ids:
        return status(f"FAILED: pack files do not match the {len(slots)} slots", state="failed")
    existing = {d["id"] for d in designs}
    for m, s in zip(meta, slots):
        if m["id"] in existing or not re.fullmatch(r"A\d+_\d\d_[a-z0-9_]+", m["id"]):
            return status(f"FAILED: bad or duplicate id {m['id']}", state="failed")
        m.update(track=s["track"], batch=k, attrs={x: s[x] for x in taste.DIMS})
        if s["track"] == "personal":
            m["listing"], m["tags"] = "", ["fan art"]
    if dry:  # test the plan -> Codex -> validation chain without adding or drawing anything
        for p in (pack_md, pack_json):
            p.rename(p.with_name(p.stem + "-dryrun" + p.suffix))
        return status(f"Dry run OK: {len(meta)} valid concepts ({', '.join(m['title'] for m in meta)})", state="done")
    designs += meta
    (ROOT / "designs.json").write_text(json.dumps(designs, indent=1, ensure_ascii=False), encoding="utf-8")
    status(f"Added {len(meta)} designs; Codex is drawing them (about 1-2 min each)", ids=ids)
    delegate("--engine", "image", "--pack", str(pack_md), "--out", "designs/raw", "--task", f"dcc auto batch {k} images",
             "--checklist", CHECK)
    pipeline(ids)
    made = [i for i in ids if (ROOT / "designs/preview" / f"{i}.png").exists()]
    status(f"Done: {len(made)}/{len(ids)} new designs ready to rate", state="done", made=made)


def pack_of(design_id):
    for p in sorted((ROOT / "image-prompts").glob("pack-*.md")):
        if f"### `{design_id}.png`" in p.read_text(encoding="utf-8"):
            return p


def redo():
    fb = json.loads((ROOT / "feedback.json").read_text(encoding="utf-8"))
    ids = [k for k, v in fb.items() if v.get("qa") == "redo"]
    if not ids:
        return status("Nothing is flagged for redo", state="done")
    status(f"Re-drawing {len(ids)} flagged designs", state="running", ids=ids)
    groups = {}
    for i in ids:
        p = pack_of(i)
        if p:
            groups.setdefault(p, []).append(i)
    for p, g in groups.items():
        delegate("--engine", "image", "--pack", str(p), "--only", ",".join(f"{i}.png" for i in g), "--out", "designs/raw",
                 "--task", "dcc redo flagged", "--checklist", CHECK)
    pipeline(ids)
    fb = json.loads((ROOT / "feedback.json").read_text(encoding="utf-8"))
    for i in ids:
        fb.get(i, {}).pop("qa", None)
    (ROOT / "feedback.json").write_text(json.dumps(fb, indent=1), encoding="utf-8")
    status(f"Done: re-drew {len(ids)} designs", state="done", made=ids)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "generate"
    try:
        if cmd == "redo":
            redo()
        else:
            n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 10
            tr = sys.argv[sys.argv.index("--track") + 1] if "--track" in sys.argv else "auto"
            generate(n, tr, dry="--dry" in sys.argv)
    except Exception as e:  # noqa: BLE001
        status(f"FAILED: {e}", state="failed")
        raise
