# Arquivos e Pastas para Excluir da Produção

Este documento lista todos os arquivos e pastas que devem ser excluídos antes de enviar o projeto para produção.

## Diretórios para Excluir

- `.git/` - Diretório de controle de versão
- `node_modules/` - Dependências do Node.js
- `.venv/` - Ambiente virtual Python
- `__pycache__/` - Cache do Python
- `.cursor/` - Configurações do editor
- `logs/` - Arquivos de log

## Arquivos para Excluir

- `DEBUG.md` - Arquivo de debug
- `minify-css.js` - Script de minificação (usar apenas em desenvolvimento)
- `convert-icons.js` - Script de conversão de ícones (usar apenas em desenvolvimento)
- `package-lock.json` - Arquivo de lock do npm
- `.gitignore` - Configuração do Git

## Arquivos de Desenvolvimento

Estes arquivos são usados apenas durante o desenvolvimento e podem ser excluídos da produção:

- `requirements.txt` - Dependências Python (manter apenas se necessário para deploy)
- `package.json` - Configuração npm (manter apenas se necessário para deploy)

## Recomendações Adicionais

1. Minifique todos os arquivos CSS e JavaScript antes do deploy
2. Otimize todas as imagens em `assets/`
3. Remova quaisquer comentários de debug dos arquivos
4. Certifique-se de que todas as variáveis de ambiente sensíveis estão configuradas corretamente
5. Verifique se o `sitemap.xml` está atualizado

## Observações

- Mantenha backups dos arquivos excluídos em seu ambiente de desenvolvimento
- Documente quaisquer processos de build necessários para gerar arquivos de produção
- Mantenha uma cópia do `.gitignore` e outros arquivos de configuração em seu ambiente de desenvolvimento

# Primeiro otimiza os arquivos
npm run build

# Depois cria a versão de produção
npm run production

# Criar ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# No Windows:
.\venv\Scripts\activate

# Instalar dependências
pip install -r scripts/requirements.txt 