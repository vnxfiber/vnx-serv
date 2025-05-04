const fs = require('fs');
const path = require('path');
const uglifyJS = require('uglify-js');
const cleanCSS = require('clean-css');
const imagemin = require('imagemin');
const imageminJpegtran = require('imagemin-jpegtran');
const imageminPngquant = require('imagemin-pngquant');
const imageminSvgo = require('imagemin-svgo');

// Configuração dos diretórios
const dirs = {
    css: './styles',
    js: './js',
    assets: './assets',
    dist: './dist'
};

// Criar diretório dist se não existir
if (!fs.existsSync(dirs.dist)) {
    fs.mkdirSync(dirs.dist);
    fs.mkdirSync(path.join(dirs.dist, 'css'));
    fs.mkdirSync(path.join(dirs.dist, 'js'));
    fs.mkdirSync(path.join(dirs.dist, 'assets'));
}

// Minificar CSS
async function minifyCSS() {
    console.log('Minificando arquivos CSS...');
    const cssFiles = fs.readdirSync(dirs.css).filter(file => file.endsWith('.css'));
    
    for (const file of cssFiles) {
        if (!file.includes('.min.')) {
            const content = fs.readFileSync(path.join(dirs.css, file), 'utf8');
            const minified = new cleanCSS().minify(content);
            const outputPath = path.join(dirs.dist, 'css', file.replace('.css', '.min.css'));
            fs.writeFileSync(outputPath, minified.styles);
            console.log(`✓ ${file} minificado`);
        }
    }
}

// Minificar JavaScript
async function minifyJS() {
    console.log('Minificando arquivos JavaScript...');
    const jsFiles = fs.readdirSync(dirs.js).filter(file => file.endsWith('.js'));
    
    for (const file of jsFiles) {
        if (!file.includes('.min.')) {
            const content = fs.readFileSync(path.join(dirs.js, file), 'utf8');
            const minified = uglifyJS.minify(content, {
                compress: true,
                mangle: true
            });
            const outputPath = path.join(dirs.dist, 'js', file.replace('.js', '.min.js'));
            fs.writeFileSync(outputPath, minified.code);
            console.log(`✓ ${file} minificado`);
        }
    }
}

// Otimizar imagens
async function optimizeImages() {
    console.log('Otimizando imagens...');
    const files = await imagemin([`${dirs.assets}/**/*.{jpg,png,svg}`], {
        destination: path.join(dirs.dist, 'assets'),
        plugins: [
            imageminJpegtran(),
            imageminPngquant({
                quality: [0.6, 0.8]
            }),
            imageminSvgo({
                plugins: [{
                    name: 'removeViewBox',
                    active: false
                }]
            })
        ]
    });
    
    console.log(`✓ ${files.length} imagens otimizadas`);
}

// Remover comentários de debug
async function removeDebugComments() {
    console.log('Removendo comentários de debug...');
    const jsFiles = fs.readdirSync(dirs.js).filter(file => file.endsWith('.js'));
    
    for (const file of jsFiles) {
        let content = fs.readFileSync(path.join(dirs.js, file), 'utf8');
        // Remove console.log statements
        content = content.replace(/console\.(log|debug|info|warn|error)\((.*?)\);?/g, '');
        // Remove comentários de debug (começando com // DEBUG)
        content = content.replace(/\/\/ DEBUG.*$/gm, '');
        fs.writeFileSync(path.join(dirs.dist, 'js', file), content);
        console.log(`✓ Comentários de debug removidos de ${file}`);
    }
}

// Executar todas as tarefas
async function build() {
    try {
        await minifyCSS();
        await minifyJS();
        await optimizeImages();
        await removeDebugComments();
        console.log('Build completo! ✨');
    } catch (error) {
        console.error('Erro durante o build:', error);
    }
}

build(); 