import fs from "node:fs/promises";
import path from "node:path";
import url from "node:url";

const __filename = url.fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dashboardRoot = path.resolve(__dirname, "..");
const manifestPath = path.join(dashboardRoot, "data-manifest.json");
const publicDataRoot = path.join(dashboardRoot, "public", "data");

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function main() {
  const raw = await fs.readFile(manifestPath, "utf8");
  const manifest = JSON.parse(raw);
  if (!manifest?.files?.length) {
    throw new Error("data-manifest.json has no files");
  }

  await ensureDir(publicDataRoot);

  const copied = [];
  for (const entry of manifest.files) {
    if (!entry?.source || !entry?.dest) continue;
    const srcAbs = path.resolve(dashboardRoot, entry.source);
    const destAbs = path.resolve(publicDataRoot, entry.dest);
    try {
      await ensureDir(path.dirname(destAbs));
      await fs.copyFile(srcAbs, destAbs);
      copied.push({ source: entry.source, dest: `public/data/${entry.dest}` });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn(`Skipping missing data file: ${entry.source}`);
    }
  }

  const stamp = new Date().toISOString();
  await fs.writeFile(
    path.join(publicDataRoot, "_build.json"),
    JSON.stringify({ stamp, copied }, null, 2),
    "utf8"
  );

  // eslint-disable-next-line no-console
  console.log(`Prepared ${copied.length} files into public/data/`);
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exitCode = 1;
});

