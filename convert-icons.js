// Este é um exemplo de script para converter SVG para PNG
// Este script é apenas um modelo, você deve ter o Node.js instalado e instalar o sharp:
// npm install sharp

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const sizes = [16, 32, 64, 96, 128, 180, 192, 512];
const iconDir = path.join(__dirname, 'assets', 'icons');

// Ensure directory exists
if (!fs.existsSync(iconDir)) {
  fs.mkdirSync(iconDir, { recursive: true });
}

// Convert favicon.svg to various PNG sizes
const faviconSvg = path.join(__dirname, 'assets', 'icons', 'favicon.svg');
sizes.forEach(size => {
  sharp(faviconSvg)
    .resize(size, size)
    .toFile(path.join(iconDir, `favicon-${size}x${size}.png`), err => {
      if (err) {
        console.error(`Error converting favicon to ${size}x${size}:`, err);
      } else {
        console.log(`Created favicon-${size}x${size}.png`);
      }
    });
});

// Create apple touch icon
const appleTouchSvg = path.join(__dirname, 'assets', 'icons', 'apple-touch-icon.svg');
sharp(appleTouchSvg)
  .resize(180, 180)
  .toFile(path.join(iconDir, 'apple-touch-icon.png'), err => {
    if (err) {
      console.error('Error converting apple-touch-icon:', err);
    } else {
      console.log('Created apple-touch-icon.png');
    }
  });

// Create Android Chrome icons
sharp(faviconSvg)
  .resize(192, 192)
  .toFile(path.join(iconDir, 'android-chrome-192x192.png'), err => {
    if (err) {
      console.error('Error creating android-chrome-192x192.png:', err);
    } else {
      console.log('Created android-chrome-192x192.png');
    }
  });

sharp(faviconSvg)
  .resize(512, 512)
  .toFile(path.join(iconDir, 'android-chrome-512x512.png'), err => {
    if (err) {
      console.error('Error creating android-chrome-512x512.png:', err);
    } else {
      console.log('Created android-chrome-512x512.png');
    }
  });

// Create MS Tile icons
[70, 150, 310].forEach(size => {
  sharp(faviconSvg)
    .resize(size, size)
    .toFile(path.join(iconDir, `mstile-${size}x${size}.png`), err => {
      if (err) {
        console.error(`Error creating mstile-${size}x${size}.png:`, err);
      } else {
        console.log(`Created mstile-${size}x${size}.png`);
      }
    });
});

// Create wide MS Tile icon
sharp(faviconSvg)
  .resize(310, 150)
  .extend({
    top: 0,
    bottom: 0,
    left: 75,
    right: 75,
    background: { r: 10, g: 61, b: 98, alpha: 1 }
  })
  .toFile(path.join(iconDir, 'mstile-310x150.png'), err => {
    if (err) {
      console.error('Error creating mstile-310x150.png:', err);
    } else {
      console.log('Created mstile-310x150.png');
    }
  });

// Create ICO file (using 16x16, 32x32, and 48x48 sizes)
console.log('To create ICO file, use a tool like https://convertico.com or a similar library');

console.log('Icon generation script completed - remember to run this with Node.js after installing sharp'); 