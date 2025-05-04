// Este é um exemplo de script para converter SVG para PNG
// Este script é apenas um modelo, você deve ter o Node.js instalado e instalar o sharp:
// npm install sharp

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const faviconDir = path.join(__dirname, 'assets', 'favicons');

// Ensure directory exists
if (!fs.existsSync(faviconDir)) {
  fs.mkdirSync(faviconDir, { recursive: true });
}

// Base SVG file
const faviconSvg = path.join(__dirname, 'assets', 'favicons', 'favicon.svg');

// Gerar favicon PNG em vários tamanhos
const sizes = [16, 32, 70, 144, 150, 180, 192, 310, 512];
sizes.forEach(size => {
  sharp(faviconSvg)
    .resize(size, size)
    .toFile(path.join(faviconDir, `favicon-${size}x${size}.png`))
    .then(() => console.log(`✓ Criado favicon-${size}x${size}.png`))
    .catch(err => console.error(`✗ Erro ao criar favicon-${size}x${size}.png:`, err));
});

// Gerar apple-touch-icon
sharp(faviconSvg)
  .resize(180, 180)
  .toFile(path.join(faviconDir, 'apple-touch-icon.png'))
  .then(() => console.log('✓ Criado apple-touch-icon.png'))
  .catch(err => console.error('✗ Erro ao criar apple-touch-icon.png:', err));

sharp(faviconSvg)
  .resize(180, 180)
  .toFile(path.join(faviconDir, 'apple-touch-icon-180x180.png'))
  .then(() => console.log('✓ Criado apple-touch-icon-180x180.png'))
  .catch(err => console.error('✗ Erro ao criar apple-touch-icon-180x180.png:', err));

// Gerar ícones MS Tile
['70x70', '144x144', '150x150', '310x310'].forEach(size => {
  const [width, height] = size.split('x').map(Number);
  sharp(faviconSvg)
    .resize(width, height)
    .toFile(path.join(faviconDir, `mstile-${size}.png`))
    .then(() => console.log(`✓ Criado mstile-${size}.png`))
    .catch(err => console.error(`✗ Erro ao criar mstile-${size}.png:`, err));
});

// Gerar MS Tile wide
sharp(faviconSvg)
  .resize(310, 150)
  .extend({
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    background: { r: 10, g: 61, b: 98, alpha: 1 }
  })
  .toFile(path.join(faviconDir, 'mstile-310x150.png'))
  .then(() => console.log('✓ Criado mstile-310x150.png'))
  .catch(err => console.error('✗ Erro ao criar mstile-310x150.png:', err));

// Gerar ICO file (combinando 16x16, 32x32 e 48x48)
const ico = require('sharp-ico');
Promise.all([16, 32, 48].map(size =>
  sharp(faviconSvg)
    .resize(size, size)
    .toBuffer()
))
.then(buffers => {
  fs.writeFileSync(
    path.join(faviconDir, 'favicon.ico'),
    ico.encode(buffers)
  );
  console.log('✓ Criado favicon.ico');
})
.catch(err => console.error('✗ Erro ao criar favicon.ico:', err));

console.log('\nPara executar este script:');
console.log('1. Instale as dependências: npm install sharp sharp-ico');
console.log('2. Execute: node convert-icons.js'); 