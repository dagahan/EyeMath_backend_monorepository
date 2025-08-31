import { readFileSync, writeFileSync } from "node:fs";
import { execSync } from "node:child_process";
import path from "node:path";

const CHECK = process.argv.includes("--check");
const EXTS = new Set([".css", ".js", ".jsx"]);

function gitListFiles() {
  const out = execSync('git ls-files -z  "*.css" "*.js" "*.jsx"', {
    encoding: "buffer",
  });
  return out
    .toString("utf8")
    .split("\0")
    .filter(Boolean)
    .filter((f) => EXTS.has(path.extname(f).toLowerCase()));
}

const filesArg = process.argv
  .slice(2)
  .filter((a) => !a.startsWith("-") && EXTS.has(path.extname(a).toLowerCase()));
const files = filesArg.length ? filesArg : gitListFiles();
let changed = false;

for (const file of files) {
  const ext = path.extname(file).toLowerCase();
  const src = readFileSync(file, "utf8");
  const res =
    ext === ".css"
      ? fixCSS(src)
      : ext === ".js" || ext === ".jsx"
        ? fixJS(src)
        : src;

  if (res !== src) {
    if (CHECK) {
      console.error(`[enforce-blank-lines] Need 2 blank lines in: ${file}`);
      changed = true;
    } else {
      writeFileSync(file, res, "utf8");
      console.log(`[enforce-blank-lines] Fixed: ${file}`);
    }
  }
}

if (CHECK && changed) process.exit(2);

function normalize(s) {
  return s.replace(/\r\n/g, "\n").replace(/[ \t]+\n/g, "\n");
}

function fixCSS(s) {
  s = normalize(s);
  s = s.replace(/\n{3,}/g, "\n\n\n");
  return s.replace(/}\n+(?=\s*([.#@\w[]))/g, "}\n\n\n");
}

function fixJS(s) {
  s = normalize(s);
  s = s.replace(/\n{3,}/g, "\n\n\n");

  const lines = s.split("\n");
  let depth = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const stripped = stripCommentsAndStrings(line);
    const isTopLevel = depth === 0;
    const isVarDecl = /^\s*(export\s+)?(const|let|var)\b/.test(line);
    const isBlockDecl = /^\s*(export\s+)?(function|class)\b/.test(line);
    const isImportExport =
      /^\s*import\b/.test(line) ||
      /^\s*export\s+(default|{|\*|\w+\s+from\b)/.test(line);

    if (isTopLevel && (isBlockDecl || isImportExport)) {
      let j = i - 1;
      while (j >= 0 && lines[j].trim() === "") j--;
      const bof = j < 0;
      const want = 2;
      if (!bof) {
        let k = j + 1,
          empty = 0;
        while (k < i && lines[k].trim() === "") {
          empty++;
          k++;
        }
        if (empty !== want) {
          const toSplice = i - (j + 1);
          lines.splice(j + 1, toSplice, "", "");
          i = j + 3;
        }
      } else {
        let k = 0;
        while (k < i && lines[k].trim() === "") k++;
        if (k !== i) {
          lines.splice(0, i - k);
          i = 0;
        }
      }
    } else if (isTopLevel && isVarDecl) {
      let j = i - 1;
      while (j >= 0 && lines[j].trim() === "") j--;
      if (j >= 0 && /^\s*(export\s+)?(const|let|var)\b/.test(lines[j])) {
        const toRemove = i - (j + 1);
        if (toRemove > 0) {
          lines.splice(j + 1, toRemove); // убрать все пустые между var-строками
          i = j + 1;
        }
      }
    }

    depth += (stripped.match(/{/g) || []).length;
    depth -= (stripped.match(/}/g) || []).length;
    if (depth < 0) depth = 0;
  }

  return lines.join("\n");
}

function stripCommentsAndStrings(line) {
  let s = line;
  s = s.replace(/\/\*.*?\*\//g, "");
  s = s.replace(/"(?:[^"\\]|\\.)*"/g, '""');
  s = s.replace(/'(?:[^'\\]|\\.)*'/g, "''");
  s = s.replace(/`(?:[^`\\]|\\.)*`/g, "``");
  s = s.replace(/\/\/.*$/g, "");
  return s;
}
