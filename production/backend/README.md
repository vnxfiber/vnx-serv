# VNX FIBER SERVICE - Backend

## Estrutura do Projeto

```
backend/
│
├── app/                    # Pasta principal da aplicação
│   ├── __init__.py         # Inicializa a aplicação Flask
│   ├── app.py              # Aplicação principal
│   │
│   ├── admin/              # Módulo de administração
│   │   ├── __init__.py     # Inicializa o módulo admin
│   │   ├── routes.py       # Rotas de administração
│   │   └── logger_config.py # Configuração de logs
│   │
│   ├── templates/          # Templates HTML
│   └── static/             # Arquivos estáticos (CSS, JS, imagens)
│
├── logs/                   # Logs da aplicação
├── migrations/             # Migrações de banco de dados
├── config.py               # Configurações do projeto
├── requirements.txt        # Dependências do projeto
└── run.py                  # Script para executar a aplicação
```

## Como executar

1. Ative o ambiente virtual:
   ```
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Execute o servidor:
   ```
   python run.py
   ```

4. Acesse em: http://localhost:5000 