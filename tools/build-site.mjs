// Build the public Shirt Studio site into dist/ (static, previews only, no print files).
// Run: node tools/build-site.mjs
// Netlify runs this on every push (netlify.toml); deploy-netlify.ps1 runs it before the CLI deploy.
import { cp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");
const tplDir = join(root, "mockups", "tpl");

function replaceOnce(text, from, to) {
  if (!text.includes(from)) throw new Error(`gallery.html is missing: ${from}`);
  return text.split(from).join(to);
}

await rm(dist, { recursive: true, force: true });
await mkdir(join(dist, "mockups", "tpl"), { recursive: true });
await cp(join(root, "designs", "preview"), join(dist, "designs", "preview"), { recursive: true });
for (const name of await readdir(tplDir)) {
  if (/\.(jpg|png)$/.test(name)) await cp(join(tplDir, name), join(dist, "mockups", "tpl", name));
}
await cp(join(root, "CREDITS.md"), join(dist, "CREDITS.md"));

const tpl = (await readFile(join(tplDir, "index.json"), "utf8")).trim();
let html = await readFile(join(root, "gallery.html"), "utf8");
html = replaceOnce(html, 'const SERVER=location.protocol.startsWith("http");', 'const SERVER=/^(localhost|127\\.0\\.0\\.1)$/.test(location.hostname);');
html = replaceOnce(html, "S=Object.assign(S,EMBED||{});", `S=Object.assign(S,EMBED||{},{templates:${tpl}});`);
await writeFile(join(dist, "index.html"), html, "utf8");
console.log(`dist/ ready: index.html ${html.length} chars, previews and mockup templates copied`);
