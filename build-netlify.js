const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const templatePath = path.join(ROOT, 'taxi-map.template.html');
const dataPath = path.join(ROOT, 'taxi.txt');
const vocalesDir = path.join(ROOT, '487_vocales');
const distDir = path.join(ROOT, 'dist');
const distVocales = path.join(distDir, 'vocales');

function parseVocaleName(filename) {
  const m = filename.match(/^(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})_(\d+m\d+s)(?:_v\d+)?\.mp4$/i);
  if (!m) return null;
  const [, date, hh, mm, durRaw] = m;
  const durationLabel = durRaw.replace(/(\d+)m(\d+)s/, '$1:$2');
  return {
    file: `vocales/${filename}`,
    datetime: `${date} ${hh}:${mm}:00`,
    durationLabel,
    label: `${date} ${hh}:${mm}`,
  };
}

function buildVocalesManifest() {
  if (!fs.existsSync(vocalesDir)) return [];
  return fs
    .readdirSync(vocalesDir)
    .filter((f) => f.toLowerCase().endsWith('.mp4'))
    .map(parseVocaleName)
    .filter(Boolean)
    .sort((a, b) => a.datetime.localeCompare(b.datetime));
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const name of fs.readdirSync(src)) {
    const from = path.join(src, name);
    const to = path.join(dest, name);
    if (fs.statSync(from).isDirectory()) copyDir(from, to);
    else fs.copyFileSync(from, to);
  }
}

const template = fs.readFileSync(templatePath, 'utf8');
const taxiData = fs.readFileSync(dataPath, 'utf8');
JSON.parse(taxiData);

const vocales = buildVocalesManifest();
let html = template.replace('/*__TAXI_DATA__*/{}', taxiData);
html = html.replace('/*__VOCALES_DATA__*/[]', JSON.stringify(vocales));

fs.mkdirSync(distDir, { recursive: true });
fs.writeFileSync(path.join(distDir, 'index.html'), html, 'utf8');

if (fs.existsSync(vocalesDir)) {
  fs.rmSync(distVocales, { recursive: true, force: true });
  copyDir(vocalesDir, distVocales);
}

// local single-file build too
fs.writeFileSync(path.join(ROOT, 'taxi-map.html'), html, 'utf8');

const distMb = (fs.statSync(path.join(distDir, 'index.html')).size / 1024 / 1024).toFixed(2);
let vocalesMb = 0;
if (fs.existsSync(distVocales)) {
  for (const f of fs.readdirSync(distVocales)) {
    vocalesMb += fs.statSync(path.join(distVocales, f)).size;
  }
}
console.log(`Built dist/index.html (${distMb} MB)`);
console.log(`Vocales: ${vocales.length} files (${(vocalesMb / 1024 / 1024).toFixed(1)} MB) -> dist/vocales/`);
console.log('Deploy: drag dist/ to Netlify, or connect repo with build command "node build-netlify.js"');
