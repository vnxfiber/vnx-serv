const fs = require('fs-extra');
const path = require('path');

// Diretório onde ficarão os arquivos de produção
const PRODUCTION_DIR = 'production';

// Arquivos e diretórios que NÃO devem ir para produção
const EXCLUDED_ITEMS = [
    'node_modules',
    '.git',
    '.venv',
    '__pycache__',
    '.cursor',
    'logs',
    'DEBUG.md',
    'exclude-from-production.md',
    'build.js',
    'build-production.js',
    'convert-icons.js',
    'minify-css.js',
    'package-lock.json',
    'requirements.txt'
];

// Função para verificar se um item deve ser excluído
const shouldExclude = (item) => {
    return EXCLUDED_ITEMS.some(excluded => item === excluded || item.startsWith(excluded + '/'));
};

// Função principal para copiar arquivos
async function buildProduction() {
    try {
        // Limpa o diretório de produção se ele existir
        await fs.remove(PRODUCTION_DIR);
        
        // Cria o diretório de produção
        await fs.mkdir(PRODUCTION_DIR);

        // Lista todos os arquivos e diretórios no diretório atual
        const items = await fs.readdir('.');

        // Copia cada item que não deve ser excluído
        for (const item of items) {
            if (!shouldExclude(item)) {
                const sourcePath = path.join('.', item);
                const destPath = path.join(PRODUCTION_DIR, item);
                
                try {
                    await fs.copy(sourcePath, destPath);
                    console.log(`✓ Copiado: ${item}`);
                } catch (err) {
                    console.error(`✗ Erro ao copiar ${item}:`, err);
                }
            } else {
                console.log(`• Ignorado: ${item}`);
            }
        }

        console.log('\n✨ Build de produção concluído com sucesso!');
        console.log(`📁 Os arquivos estão no diretório: ${PRODUCTION_DIR}/`);

    } catch (err) {
        console.error('Erro durante o build:', err);
    }
}

// Executa o build
buildProduction(); 