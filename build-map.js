const fs = require('fs');
const path = require('path');

const templatePath = path.join(__dirname, 'taxi-map.template.html');
const dataPath = path.join(__dirname, 'taxi.txt');
const outPath = path.join(__dirname, 'taxi-map.html');

const template = fs.readFileSync(templatePath, 'utf8');
const data = fs.readFileSync(dataPath, 'utf8');
JSON.parse(data);

const output = template
  .replace('/*__TAXI_DATA__*/{}', data)
  .replace('/*__VOCALES_DATA__*/[]', '[]');
fs.writeFileSync(outPath, output, 'utf8');

const mb = (fs.statSync(outPath).size / 1024 / 1024).toFixed(2);
console.log(`Built ${outPath} (${mb} MB)`);
