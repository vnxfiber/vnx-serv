# VNX FIBER SERVICE - Sistema de Gestão de Parceiros Técnicos

Este sistema permite gerenciar os cadastros de parceiros técnicos da VNX FIBER SERVICE, incluindo um formulário público de cadastro e uma dashboard administrativa protegida.

## Estrutura do Sistema

- `trabalhe-conosco.html`: Formulário público de cadastro de parceiros técnicos
- `dashboard-admin.html`: Dashboard administrativa para gestão dos parceiros (requer autenticação)
- `login.html`: Página de login para acesso à dashboard
- `auth.js`: Módulo de autenticação
- `assets/`: Diretório com arquivos estáticos (imagens, etc)

## Configuração do Supabase

1. Crie uma conta no [Supabase](https://supabase.com)
2. Crie um novo projeto
3. Crie uma tabela `parceiros_tecnicos` com a seguinte estrutura:

```sql
create table parceiros_tecnicos (
  id uuid default uuid_generate_v4() primary key,
  nome_completo text not null,
  estado text not null,
  cidade text not null,
  especialidades text[] not null,
  experiencia text,
  whatsapp text not null,
  email text not null,
  portfolio_link text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Habilitar RLS (Row Level Security)
alter table parceiros_tecnicos enable row level security;

-- Política para inserção pública (qualquer um pode se cadastrar)
create policy "Permitir inserção pública"
  on parceiros_tecnicos for insert
  with check (true);

-- Política para leitura/deleção apenas por usuários autenticados
create policy "Permitir leitura/deleção apenas por usuários autenticados"
  on parceiros_tecnicos for all
  using (auth.role() = 'authenticated');
```

4. Em "Authentication > Settings", habilite "Email Auth" e configure o domínio permitido

5. Em "Authentication > Users", crie um usuário administrativo

6. Em "Settings > API", copie a URL e a chave anon para configurar nos arquivos:
   - Atualize a URL e chave do Supabase em `auth.js`
   - Atualize a URL e chave do Supabase em `trabalhe-conosco.html`

## Configuração do Ambiente

1. Configure um servidor web (Apache, Nginx, etc) para servir os arquivos estáticos

2. Configure HTTPS para segurança (recomendado)

3. Faça upload dos arquivos para o servidor

4. Teste o acesso em:
   - Formulário público: `https://seu-dominio.com/trabalhe-conosco.html`
   - Dashboard admin: `https://seu-dominio.com/dashboard-admin.html`

## Funcionalidades

### Formulário Público (trabalhe-conosco.html)
- Cadastro de dados pessoais
- Seleção de especialidades técnicas
- Seleção de estado/cidade
- Upload de informações de contato
- Validação de campos
- Feedback visual de sucesso/erro

### Dashboard Administrativa (dashboard-admin.html)
- Login seguro
- Visualização de todos os cadastros
- Filtros por estado e especialidade
- Detalhes completos de cada parceiro
- Exportação para CSV
- Exclusão de registros
- Interface responsiva

## Segurança

- Autenticação via Supabase
- Row Level Security (RLS) no banco de dados
- CORS configurado apenas para domínios permitidos
- Proteção contra SQL Injection
- Validação de dados no frontend e backend

## Suporte

Para suporte técnico ou dúvidas, entre em contato:
- Email: contato@vnxfiber.com.br
- WhatsApp: (98) 99988-2215

## 🚀 Tecnologias Utilizadas

- HTML5
- CSS3 com variáveis para fácil personalização
- JavaScript moderno
- Bootstrap 5
- AOS (Animate On Scroll) para animações elegantes
- Swiper.js para carrosséis e sliders
- Font Awesome para ícones vetoriais

## ✨ Recursos do Site

- **Design responsivo** para todos os dispositivos
- **Animações suaves** com AOS e CSS nativo
- **Alta performance** com carregamento otimizado
- **Paleta de cores personalizável** através de variáveis CSS
- **Integração com WhatsApp** para comunicação rápida
- **Formulário de contato** interativo e validado
- **Carrossel de clientes** com transições elegantes
- **Menu de navegação fixo** com mudança de estilo ao rolar
- **Seções bem definidas** para apresentação dos serviços
- **Contador animado** para exibir estatísticas
- **Layout limpo e moderno** com efeitos sutis de hover
- **Botões de call-to-action** estrategicamente posicionados

## 📋 Pré-requisitos

- Node.js (versão 14 ou superior)
- NPM (Node Package Manager)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/vnx-fiber-service.git
cd vnx-fiber-service
```

2. Instale as dependências:
```bash
npm install
```

3. Inicie o servidor de desenvolvimento:
```bash
npm start
```

O site estará disponível em `http://localhost:1234`

## 📦 Build para Produção

Para criar uma versão de produção otimizada:

```bash
npm run build
```

Os arquivos otimizados serão gerados na pasta `dist`. Estes arquivos podem ser enviados para qualquer servidor web.

## 🎨 Personalização

### Cores
As cores principais do site podem ser facilmente alteradas editando as variáveis no arquivo `styles/main.css`:

```css
:root {
    --primary-color: #0a3d62;
    --secondary-color: #3498db;
    --accent-color: #2ecc71;
    --dark-color: #1e272e;
    --light-color: #f8f9fa;
    --text-color: #2d3436;
    --gradient-primary: linear-gradient(135deg, #0a3d62, #3498db);
}
```

### Imagens
Para personalizar as imagens do site:

- Logo: Substitua `assets/logo.png` (para header) e `assets/logo-white.png` (para footer)
- Banner principal: Substitua `assets/hero-bg.jpg`
- Sobre nós: Substitua `assets/about-image.jpg`
- Clientes: Adicione/substitua logos em `assets/clients/`

### Informações de Contato
Atualize as informações de contato nos seguintes locais:

1. Seção de contato
2. Rodapé
3. Link do WhatsApp (substitua "SEUNUMERO" pela sequência numérica do seu WhatsApp)

## 📱 Estrutura de Pastas

```
vnx-fiber-service/
├── assets/               # Imagens e recursos
│   ├── clients/          # Logos de clientes
│   ├── logo.png          # Logo principal
│   └── ...               # Outras imagens
├── js/                   # Arquivos JavaScript
│   └── main.js           # JavaScript principal
├── styles/               # Arquivos CSS
│   └── main.css          # CSS principal
├── index.html            # Página HTML principal
├── package.json          # Dependências e scripts
└── README.md             # Documentação
```

## ✅ Checklist de Deploy

Antes de publicar o site:

1. ✅ Atualize todas as informações de contato
2. ✅ Substitua as imagens de placeholder por imagens reais da empresa
3. ✅ Teste o formulário de contato
4. ✅ Verifique todos os links
5. ✅ Teste em diferentes dispositivos e navegadores
6. ✅ Otimize todas as imagens para web
7. ✅ Verifique a performance do site

## 📈 Otimizações para SEO

- Meta tags otimizadas
- Estrutura HTML semântica
- Texto alternativo para imagens
- Carregamento rápido
- Design responsivo (mobile-friendly)
- URLs amigáveis

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie uma Branch para sua Feature (`git checkout -b feature/RecursoIncrivel`)
3. Commit suas mudanças (`git commit -m 'Adicionando recurso incrível'`)
4. Push para a Branch (`git push origin feature/RecursoIncrivel`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Contato

VNX FIBER SERVICE - [contato@vnxfiberservice.com.br](mailto:contato@vnxfiberservice.com.br)

## Geração de Ícones e Favicons

O site utiliza ícones em SVG para melhor qualidade e escalabilidade. Para gerar as versões em PNG para melhor compatibilidade com todos os navegadores, siga os passos:

1. Instale o Node.js se ainda não tiver instalado
2. Instale a biblioteca sharp:
   ```
   npm install sharp
   ```
3. Execute o script de conversão:
   ```
   node convert-icons.js
   ```

Isso irá gerar todas as versões necessárias dos ícones em PNG a partir dos arquivos SVG presentes na pasta `assets/icons/`.

Se você não tiver Node.js, pode usar ferramentas online como:
- [SVGOMG](https://jakearchibald.github.io/svgomg/) para otimizar os SVGs
- [RealFaviconGenerator](https://realfavicongenerator.net/) para gerar os favicons a partir de um arquivo de imagem

---
Desenvolvido com ❤️ para VNX FIBER SERVICE 