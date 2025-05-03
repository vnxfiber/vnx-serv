const fs = require('fs');
const path = require('path');

// Função simples para minificar CSS (sem dependências externas)
function minifyCSS(css) {
  return css
    // Remover comentários
    .replace(/\/\*[\s\S]*?\*\//g, '')
    // Remover espaços em branco desnecessários
    .replace(/\s+/g, ' ')
    .replace(/\s*([{}:;,])\s*/g, '$1')
    .replace(/;\}/g, '}')
    .replace(/\s*{\s*/g, '{')
    .replace(/\s*}\s*/g, '}')
    .replace(/\s*;\s*/g, ';')
    .replace(/\s*:\s*/g, ':')
    .replace(/\s*,\s*/g, ',')
    .trim();
}

// Caminhos de arquivo
const inputFile = path.join(__dirname, 'styles', 'main.css');
const outputFile = path.join(__dirname, 'styles', 'main.min.css');

try {
  // Ler arquivo CSS
  console.log('Lendo o arquivo CSS...');
  const css = fs.readFileSync(inputFile, 'utf8');
  
  // Minificar CSS
  console.log('Minificando o CSS...');
  const minified = minifyCSS(css);
  
  // Escrever arquivo minificado
  console.log('Gravando o arquivo minificado...');
  fs.writeFileSync(outputFile, minified);
  
  // Calcular economia de tamanho
  const originalSize = css.length;
  const minifiedSize = minified.length;
  const savings = ((originalSize - minifiedSize) / originalSize * 100).toFixed(2);
  
  console.log(`Minificação concluída com sucesso!`);
  console.log(`Tamanho original: ${originalSize} bytes`);
  console.log(`Tamanho minificado: ${minifiedSize} bytes`);
  console.log(`Economia: ${savings}%`);
} catch (error) {
  console.error('Erro ao minificar o CSS:', error);
  process.exit(1);
} 