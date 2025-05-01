from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import json
from datetime import datetime
from supabase import create_client, Client

# Configurações do Supabase
SUPABASE_URL = "https://cwrxdjfmxntmplwdbnpg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYwMDI0MzksImV4cCI6MjA2MTU3ODQzOX0.-kFUUiLn2plnEdopteCdxcixyY3pI5O-K-hIk1IL61s"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Criar a aplicação Flask
app = Flask(__name__, 
           template_folder='.',  # Usar diretório raiz como pasta de templates
           static_folder='static',
           static_url_path='/static')

# Configurar chave secreta para cookies e sessões
app.secret_key = os.urandom(24)

# Lista para armazenar usuários (na memória, apenas para demonstração)
usuarios = []

# Estado de filtros para persistir entre requests
filtros_profissionais = {
    'estado': '',
    'especialidade': '',
    'status': ''
}

# Lista de estados brasileiros
estados = [
    { 'id': 'AC', 'nome': 'Acre' },
    { 'id': 'AL', 'nome': 'Alagoas' },
    { 'id': 'AP', 'nome': 'Amapá' },
    { 'id': 'AM', 'nome': 'Amazonas' },
    { 'id': 'BA', 'nome': 'Bahia' },
    { 'id': 'CE', 'nome': 'Ceará' },
    { 'id': 'DF', 'nome': 'Distrito Federal' },
    { 'id': 'ES', 'nome': 'Espírito Santo' },
    { 'id': 'GO', 'nome': 'Goiás' },
    { 'id': 'MA', 'nome': 'Maranhão' },
    { 'id': 'MT', 'nome': 'Mato Grosso' },
    { 'id': 'MS', 'nome': 'Mato Grosso do Sul' },
    { 'id': 'MG', 'nome': 'Minas Gerais' },
    { 'id': 'PA', 'nome': 'Pará' },
    { 'id': 'PB', 'nome': 'Paraíba' },
    { 'id': 'PR', 'nome': 'Paraná' },
    { 'id': 'PE', 'nome': 'Pernambuco' },
    { 'id': 'PI', 'nome': 'Piauí' },
    { 'id': 'RJ', 'nome': 'Rio de Janeiro' },
    { 'id': 'RN', 'nome': 'Rio Grande do Norte' },
    { 'id': 'RS', 'nome': 'Rio Grande do Sul' },
    { 'id': 'RO', 'nome': 'Rondônia' },
    { 'id': 'RR', 'nome': 'Roraima' },
    { 'id': 'SC', 'nome': 'Santa Catarina' },
    { 'id': 'SP', 'nome': 'São Paulo' },
    { 'id': 'SE', 'nome': 'Sergipe' },
    { 'id': 'TO', 'nome': 'Tocantins' }
]

# Lista de especialidades
especialidades = [
    'Fibra Óptica',
    'Servidores TI',
    'Infraestrutura Fisica',
    'Wi-Fi Corporativo',
    'Solucoes ISP',
    'Telefonia VoIP',
    'Radio Comunicacao',
    'Consultoria'
]

# Lista de status para profissionais
status_profissionais = [
    'Pendente',
    'Aprovado',
    'Rejeitado',
    'Em Análise',
    'Inativo'
]

# Funções auxiliares
def formatar_data(data_str):
    try:
        # Supabase retorna data em formato ISO
        data = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
        return data.strftime('%d/%m/%Y %H:%M')
    except:
        return data_str

def obter_profissionais(filtros=None):
    try:
        query = supabase.table('parceiros_tecnicos').select('*')
        
        # Aplicar filtros se fornecidos
        if filtros:
            if filtros.get('estado'):
                query = query.eq('estado', filtros['estado'])
            if filtros.get('especialidade'):
                # Filtro para array de especialidades
                query = query.contains('especialidades', [filtros['especialidade']])
            if filtros.get('status'):
                query = query.eq('status', filtros['status'])
        
        # Ordenar por data de criação, mais recentes primeiro
        query = query.order('created_at', desc=True)
        
        response = query.execute()
        
        # Formatar datas
        profissionais = response.data if response.data else []
        for prof in profissionais:
            if 'created_at' in prof:
                prof['data_formatada'] = formatar_data(prof['created_at'])
        
        return profissionais
    except Exception as e:
        print(f"Erro ao buscar profissionais: {e}")
        return []

# Página principal - redireciona para login
@app.route('/')
def home():
    return redirect(url_for('admin_login'))

# Página de login
@app.route('/adm')
@app.route('/adm/login', methods=['GET', 'POST'])
def admin_login():
    # Se já estiver logado, redireciona para o dashboard
    if 'usuario_logado' in session:
        return redirect(url_for('admin_dashboard'))
    
    # Processar formulário de login
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        # Verificar se usuário existe
        for usuario in usuarios:
            if usuario['email'] == email and usuario['senha'] == senha:
                session['usuario_logado'] = email
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('admin_dashboard'))
        
        # Se chegou aqui, login falhou
        flash('Email ou senha incorretos.', 'danger')
    
    # Mostrar página de login
    return '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Administrativo</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body>
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow">
                        <div class="card-body p-5">
                            <h2 class="text-center mb-4">Painel Administrativo</h2>
                            
                            <form method="post">
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email:</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                        <input type="email" name="email" id="email" class="form-control" required>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="senha" class="form-label">Senha:</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                        <input type="password" name="senha" id="senha" class="form-control" required>
                                    </div>
                                </div>
                                
                                <div class="d-grid gap-2 mt-4">
                                    <button type="submit" class="btn btn-primary">Entrar</button>
                                </div>
                            </form>
                            
                            <div class="text-center mt-3">
                                <p>Não tem uma conta? <a href="/adm/cadastro">Cadastre-se</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# Página de cadastro de administrador
@app.route('/adm/cadastro', methods=['GET', 'POST'])
def admin_cadastro():
    # Processar formulário de cadastro
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        telefone = request.form.get('telefone', '')
        
        # Verificar se todos os campos obrigatórios foram preenchidos
        if not nome or not email or not senha:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return redirect(url_for('admin_cadastro'))
        
        # Verificar se o email já está cadastrado
        for usuario in usuarios:
            if usuario['email'] == email:
                flash('Este email já está cadastrado.', 'danger')
                return redirect(url_for('admin_cadastro'))
        
        # Adicionar novo usuário à lista
        novo_usuario = {
            'nome': nome,
            'email': email,
            'senha': senha,
            'telefone': telefone
        }
        usuarios.append(novo_usuario)
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('admin_login'))
    
    # Mostrar página de cadastro
    return '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cadastro de Administrador</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    </head>
    <body>
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card shadow">
                        <div class="card-body p-5">
                            <h2 class="text-center mb-4">Cadastro de Administrador</h2>
                            
                            <form method="post">
                                <div class="mb-3">
                                    <label for="nome" class="form-label">Nome Completo:</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-user"></i></span>
                                        <input type="text" name="nome" id="nome" class="form-control" required>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email:</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-envelope"></i></span>
                                        <input type="email" name="email" id="email" class="form-control" required>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="senha" class="form-label">Senha:</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-lock"></i></span>
                                        <input type="password" name="senha" id="senha" class="form-control" required>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="telefone" class="form-label">Telefone:</label>
                                    <div class="input-group">
                                        <span class="input-group-text"><i class="fas fa-phone"></i></span>
                                        <input type="tel" name="telefone" id="telefone" class="form-control">
                                    </div>
                                </div>
                                
                                <div class="d-grid gap-2 mt-4">
                                    <button type="submit" class="btn btn-primary">Cadastrar</button>
                                </div>
                            </form>
                            
                            <div class="text-center mt-3">
                                <p>Já tem uma conta? <a href="/adm/login">Faça login</a></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# Página de dashboard principal
@app.route('/adm/dashboard')
def admin_dashboard():
    # Verificar se usuário está logado
    if 'usuario_logado' not in session:
        flash('Você precisa fazer login para acessar o dashboard.', 'danger')
        return redirect(url_for('admin_login'))
    
    try:
        # Buscar estatísticas gerais
        prof_count = len(obter_profissionais())
        
        # Contagem por status
        status_counts = {}
        for status in status_profissionais:
            filtro = {'status': status}
            status_counts[status] = len(obter_profissionais(filtro))
        
        # Contagem por estado (top 5)
        estado_counts = {}
        for estado in estados:
            filtro = {'estado': estado['id']}
            count = len(obter_profissionais(filtro))
            if count > 0:
                estado_counts[estado['nome']] = count
        
        # Ordenar por contagem e pegar os 5 primeiros
        top_estados = dict(sorted(estado_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Contagem por especialidade
        esp_counts = {}
        for esp in especialidades:
            filtro = {'especialidade': esp}
            count = len(obter_profissionais(filtro))
            if count > 0:
                esp_counts[esp] = count
                
        # Obter últimos profissionais cadastrados (5 mais recentes)
        ultimos_profissionais = obter_profissionais()[:5]
        
        return f'''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard Administrativo</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                .sidebar {{
                    min-height: 100vh;
                    background-color: #212529;
                    color: white;
                }}
                .sidebar .nav-link {{
                    color: rgba(255,255,255,.75);
                    padding: 10px 20px;
                    margin: 5px 0;
                    border-radius: 5px;
                }}
                .sidebar .nav-link:hover, .sidebar .nav-link.active {{
                    color: white;
                    background-color: rgba(255,255,255,.1);
                }}
                .sidebar .nav-link i {{
                    margin-right: 10px;
                }}
                .stat-card {{
                    border-left: 4px solid;
                    border-radius: 5px;
                }}
                .card-pendente {{ border-color: #dc3545; }}
                .card-aprovado {{ border-color: #198754; }}
                .card-analise {{ border-color: #0d6efd; }}
                .card-rejeitado {{ border-color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="row">
                    <!-- Sidebar -->
                    <div class="col-md-3 col-lg-2 d-md-block sidebar collapse p-0">
                        <div class="p-3 text-center mb-3">
                            <img src="/static/assets/logo.svg" alt="VNX Logo" class="img-fluid mb-3" style="height: 40px;">
                            <h6 class="text-white">Painel Administrativo</h6>
                        </div>
                        <ul class="nav flex-column ps-3 pe-3">
                            <li class="nav-item">
                                <a class="nav-link active" href="/adm/dashboard">
                                    <i class="fas fa-tachometer-alt"></i> Dashboard
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/adm/profissionais">
                                    <i class="fas fa-users"></i> Profissionais
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/adm/logout">
                                    <i class="fas fa-sign-out-alt"></i> Sair
                                </a>
                            </li>
                        </ul>
                    </div>
                    
                    <!-- Conteúdo Principal -->
                    <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
                        <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                            <h1 class="h2">Dashboard</h1>
                            <div class="btn-toolbar mb-2 mb-md-0">
                                <div class="btn-group me-2">
                                    <a href="/adm/profissionais" class="btn btn-sm btn-outline-secondary">
                                        <i class="fas fa-users"></i> Gerenciar Profissionais
                                    </a>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Cards de Estatísticas -->
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="card stat-card card-pendente h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">Pendentes</h5>
                                        <h3 class="display-6">{status_counts.get('Pendente', 0)}</h3>
                                        <p class="card-text">Profissionais aguardando análise</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card stat-card card-aprovado h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">Aprovados</h5>
                                        <h3 class="display-6">{status_counts.get('Aprovado', 0)}</h3>
                                        <p class="card-text">Profissionais ativos</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card stat-card card-analise h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">Em Análise</h5>
                                        <h3 class="display-6">{status_counts.get('Em Análise', 0)}</h3>
                                        <p class="card-text">Profissionais em processo</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card stat-card card-rejeitado h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">Rejeitados</h5>
                                        <h3 class="display-6">{status_counts.get('Rejeitado', 0)}</h3>
                                        <p class="card-text">Profissionais não aprovados</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mb-4">
                            <div class="col-lg-8">
                                <!-- Últimos Profissionais Cadastrados -->
                                <div class="card h-100">
                                    <div class="card-header">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <h5 class="mb-0">Últimos Profissionais Cadastrados</h5>
                                            <a href="/adm/profissionais" class="btn btn-sm btn-primary">Ver Todos</a>
                                        </div>
                                    </div>
                                    <div class="card-body p-0">
                                        <div class="table-responsive">
                                            <table class="table table-hover mb-0">
                                                <thead>
                                                    <tr>
                                                        <th>Nome</th>
                                                        <th>Estado</th>
                                                        <th>Status</th>
                                                        <th>Data</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {''.join([f"""
                                                    <tr>
                                                        <td>
                                                            <a href="/adm/profissionais/{prof.get('id', '')}" class="text-decoration-none">
                                                                {prof.get('nome_completo', 'N/A')}
                                                            </a>
                                                        </td>
                                                        <td>{prof.get('estado', 'N/A')}</td>
                                                        <td>
                                                            <span class="badge {
                                                                'bg-warning' if prof.get('status') == 'Pendente' else
                                                                'bg-success' if prof.get('status') == 'Aprovado' else
                                                                'bg-primary' if prof.get('status') == 'Em Análise' else
                                                                'bg-secondary' if prof.get('status') == 'Rejeitado' else
                                                                'bg-info'
                                                            }">
                                                                {prof.get('status', 'Pendente')}
                                                            </span>
                                                        </td>
                                                        <td>{prof.get('data_formatada', 'N/A')}</td>
                                                    </tr>
                                                    """ for prof in ultimos_profissionais])}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-4">
                                <!-- Estatísticas por Estado -->
                                <div class="card h-100">
                                    <div class="card-header">
                                        <h5 class="mb-0">Top 5 Estados</h5>
                                    </div>
                                    <div class="card-body">
                                        <ul class="list-group list-group-flush">
                                            {''.join([f"""
                                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                                {estado}
                                                <span class="badge bg-primary rounded-pill">{count}</span>
                                            </li>
                                            """ for estado, count in top_estados.items()])}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-12">
                                <!-- Especialidades -->
                                <div class="card mb-4">
                                    <div class="card-header">
                                        <h5 class="mb-0">Especialidades</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            {''.join([f"""
                                            <div class="col-md-3 mb-3">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <div>{esp}</div>
                                                    <span class="badge bg-info rounded-pill">{count}</span>
                                                </div>
                                            </div>
                                            """ for esp, count in esp_counts.items()])}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </main>
                </div>
            </div>
            
            <!-- Bootstrap JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
        </body>
        </html>
        '''
    except Exception as e:
        print(f"Erro ao carregar dashboard: {e}")
        flash(f'Erro ao carregar dashboard: {str(e)}', 'danger')
        return redirect(url_for('admin_login'))

# Página de detalhes de um profissional
@app.route('/adm/profissionais/<string:id>')
def detalhe_profissional(id):
    # Verificar se usuário está logado
    if 'usuario_logado' not in session:
        flash('Você precisa fazer login para acessar esta página.', 'danger')
        return redirect(url_for('admin_login'))
    
    try:
        # Buscar profissional no Supabase
        response = supabase.table('parceiros_tecnicos').select('*').eq('id', id).execute()
        
        # Verificar se profissional existe
        if not response.data or len(response.data) == 0:
            flash('Profissional não encontrado.', 'danger')
            return redirect(url_for('listar_profissionais'))
        
        # Obter dados do profissional
        profissional = response.data[0]
        
        # Formatar data de cadastro
        if 'created_at' in profissional:
            profissional['data_formatada'] = formatar_data(profissional['created_at'])
        
        # Definir classe CSS do badge de status
        status_class = {
            'Pendente': 'bg-warning',
            'Aprovado': 'bg-success',
            'Em Análise': 'bg-primary',
            'Rejeitado': 'bg-secondary',
            'Inativo': 'bg-danger'
        }.get(profissional.get('status', 'Pendente'), 'bg-info')
        
        # Formatar especialidades
        especialidades_html = ""
        if 'especialidades' in profissional and profissional['especialidades']:
            for esp in profissional['especialidades']:
                especialidades_html += f'<span class="badge bg-info me-1 mb-1">{esp}</span>'
        
        return f'''
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Detalhes do Profissional - VNX</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                .sidebar {{
                    min-height: 100vh;
                    background-color: #212529;
                    color: white;
                }}
                .sidebar .nav-link {{
                    color: rgba(255,255,255,.75);
                    padding: 10px 20px;
                    margin: 5px 0;
                    border-radius: 5px;
                }}
                .sidebar .nav-link:hover, .sidebar .nav-link.active {{
                    color: white;
                    background-color: rgba(255,255,255,.1);
                }}
                .sidebar .nav-link i {{
                    margin-right: 10px;
                }}
                .profile-header {{
                    background-color: #f8f9fa;
                    border-radius: 0.5rem;
                    padding: 20px;
                }}
                .profile-info .icon {{
                    width: 24px;
                    color: #6c757d;
                    text-align: center;
                    margin-right: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="row">
                    <!-- Sidebar -->
                    <div class="col-md-3 col-lg-2 d-md-block sidebar collapse p-0">
                        <div class="p-3 text-center mb-3">
                            <img src="/static/assets/logo.svg" alt="VNX Logo" class="img-fluid mb-3" style="height: 40px;">
                            <h6 class="text-white">Painel Administrativo</h6>
                        </div>
                        <ul class="nav flex-column ps-3 pe-3">
                            <li class="nav-item">
                                <a class="nav-link" href="/adm/dashboard">
                                    <i class="fas fa-tachometer-alt"></i> Dashboard
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link active" href="/adm/profissionais">
                                    <i class="fas fa-users"></i> Profissionais
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/adm/logout">
                                    <i class="fas fa-sign-out-alt"></i> Sair
                                </a>
                            </li>
                        </ul>
                    </div>
                    
                    <!-- Conteúdo Principal -->
                    <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
                        <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3">
                            <h1 class="h2">Detalhes do Profissional</h1>
                            <div class="btn-toolbar mb-2 mb-md-0">
                                <div class="btn-group me-2">
                                    <a href="/adm/profissionais" class="btn btn-sm btn-outline-secondary">
                                        <i class="fas fa-arrow-left"></i> Voltar
                                    </a>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Profile Header -->
                        <div class="profile-header d-flex justify-content-between mb-4">
                            <div>
                                <h3>{profissional.get('nome_completo', 'Nome não disponível')}</h3>
                                <p class="text-muted mb-0">
                                    <i class="fas fa-map-marker-alt me-2"></i>
                                    {profissional.get('cidade', 'N/A')}, {profissional.get('estado', 'N/A')}
                                </p>
                            </div>
                            <div>
                                <span class="badge {status_class} p-2 fs-6">
                                    {profissional.get('status', 'Pendente')}
                                </span>
                            </div>
                        </div>
                        
                        <div class="row">
                            <!-- Coluna de informações principais -->
                            <div class="col-md-8">
                                <div class="card mb-4">
                                    <div class="card-header">
                                        <h5 class="mb-0">Informações de Contato</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="profile-info mb-3">
                                            <div class="d-flex">
                                                <div class="icon"><i class="fas fa-envelope"></i></div>
                                                <div>
                                                    <p class="mb-0 fw-bold">Email</p>
                                                    <p class="mb-0">{profissional.get('email', 'Não informado')}</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="profile-info mb-3">
                                            <div class="d-flex">
                                                <div class="icon"><i class="fas fa-phone"></i></div>
                                                <div>
                                                    <p class="mb-0 fw-bold">WhatsApp</p>
                                                    <p class="mb-0">{profissional.get('whatsapp', 'Não informado')}</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="profile-info mb-3">
                                            <div class="d-flex">
                                                <div class="icon"><i class="fas fa-link"></i></div>
                                                <div>
                                                    <p class="mb-0 fw-bold">Portfólio / LinkedIn</p>
                                                    <p class="mb-0">
                                                        {'<a href="' + profissional.get('portfolio_link', '#') + '" target="_blank">' + profissional.get('portfolio_link', 'Não informado') + '</a>' 
                                                        if profissional.get('portfolio_link') else 'Não informado'}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="card mb-4">
                                    <div class="card-header">
                                        <h5 class="mb-0">Experiência e Certificações</h5>
                                    </div>
                                    <div class="card-body">
                                        <p>{profissional.get('experiencia', 'Não informado').replace('\\n', '<br>') if profissional.get('experiencia') else 'Não informado'}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Coluna lateral -->
                            <div class="col-md-4">
                                <div class="card mb-4">
                                    <div class="card-header">
                                        <h5 class="mb-0">Especialidades</h5>
                                    </div>
                                    <div class="card-body">
                                        {especialidades_html if especialidades_html else 'Nenhuma especialidade informada'}
                                    </div>
                                </div>
                                
                                <div class="card mb-4">
                                    <div class="card-header">
                                        <h5 class="mb-0">Informações Adicionais</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="profile-info mb-3">
                                            <div class="d-flex">
                                                <div class="icon"><i class="fas fa-calendar-alt"></i></div>
                                                <div>
                                                    <p class="mb-0 fw-bold">Data de Cadastro</p>
                                                    <p class="mb-0">{profissional.get('data_formatada', 'N/A')}</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="profile-info mb-3">
                                            <div class="d-flex">
                                                <div class="icon"><i class="fas fa-id-badge"></i></div>
                                                <div>
                                                    <p class="mb-0 fw-bold">ID do Profissional</p>
                                                    <p class="mb-0">{profissional.get('id', 'N/A')}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="card">
                                    <div class="card-header">
                                        <h5 class="mb-0">Ações</h5>
                                    </div>
                                    <div class="card-body">
                                        <form id="statusForm" action="/adm/profissionais/alterar-status" method="POST">
                                            <input type="hidden" name="id" value="{profissional.get('id', '')}">
                                            <div class="mb-3">
                                                <label for="status" class="form-label">Alterar Status</label>
                                                <select class="form-select" id="status" name="status">
                                                    {''.join([f'<option value="{s}" {"selected" if s == profissional.get("status", "Pendente") else ""} >{s}</option>' for s in status_profissionais])}
                                                </select>
                                            </div>
                                            <button type="submit" class="btn btn-primary w-100">
                                                <i class="fas fa-save me-2"></i>Salvar Alterações
                                            </button>
                                        </form>
                                        <hr>
                                        <div class="d-grid gap-2">
                                            <a href="mailto:{profissional.get('email', '')}" class="btn btn-outline-secondary">
                                                <i class="fas fa-envelope me-2"></i>Enviar Email
                                            </a>
                                            <a href="https://wa.me/{profissional.get('whatsapp', '').replace('(', '').replace(')', '').replace('-', '').replace(' ', '')}" 
                                               target="_blank" class="btn btn-outline-success">
                                                <i class="fab fa-whatsapp me-2"></i>Contato WhatsApp
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </main>
                </div>
            </div>
            
            <!-- Bootstrap JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        '''
    except Exception as e:
        print(f"Erro ao exibir detalhes do profissional: {e}")
        flash(f'Erro ao exibir detalhes do profissional: {str(e)}', 'danger')
        return redirect(url_for('listar_profissionais'))

# Rota para alterar o status de um profissional
@app.route('/adm/profissionais/alterar-status', methods=['POST'])
def alterar_status_profissional():
    # Verificar se usuário está logado
    if 'usuario_logado' not in session:
        flash('Você precisa fazer login para realizar esta ação.', 'danger')
        return redirect(url_for('admin_login'))
    
    try:
        # Obter dados do formulário
        id_profissional = request.form.get('id')
        novo_status = request.form.get('status')
        
        # Validar dados
        if not id_profissional or not novo_status:
            flash('Dados incompletos para alterar o status.', 'danger')
            return redirect(url_for('listar_profissionais'))
        
        # Verificar se o status é válido
        if novo_status not in status_profissionais:
            flash('Status inválido.', 'danger')
            return redirect(url_for('listar_profissionais'))
        
        # Atualizar status no Supabase
        response = supabase.table('parceiros_tecnicos').update({'status': novo_status}).eq('id', id_profissional).execute()
        
        # Verificar se a atualização foi bem-sucedida
        if not response.data or len(response.data) == 0:
            flash('Erro ao atualizar status do profissional.', 'danger')
            return redirect(url_for('listar_profissionais'))
        
        # Registrar o sucesso
        flash(f'Status do profissional atualizado para "{novo_status}".', 'success')
        
        # Redirecionar para a página de detalhes
        return redirect(url_for('detalhe_profissional', id=id_profissional))
    
    except Exception as e:
        print(f"Erro ao alterar status do profissional: {e}")
        flash(f'Erro ao alterar status: {str(e)}', 'danger')
        return redirect(url_for('listar_profissionais'))

# Rota para exportar profissionais em CSV
@app.route('/adm/profissionais/exportar-csv')
def exportar_profissionais_csv():
    # Verificar se usuário está logado
    if 'usuario_logado' not in session:
        flash('Você precisa fazer login para realizar esta ação.', 'danger')
        return redirect(url_for('admin_login'))
    
    try:
        # Obter filtros da requisição
        estado = request.args.get('estado', '')
        especialidade = request.args.get('especialidade', '')
        status = request.args.get('status', '')
        busca = request.args.get('busca', '')
        
        # Aplicar filtros
        filtros = {}
        if estado:
            filtros['estado'] = estado
        if especialidade:
            filtros['especialidade'] = especialidade
        if status:
            filtros['status'] = status
            
        # Obter profissionais
        profissionais = obter_profissionais(filtros)
        
        # Aplicar filtro de busca manualmente (caso não seja possível via API)
        if busca:
            profissionais = [p for p in profissionais if 
                            busca.lower() in (p.get('nome_completo', '').lower() or '') or 
                            busca.lower() in (p.get('email', '').lower() or '') or
                            busca.lower() in (p.get('cidade', '').lower() or '')]
        
        # Gerar CSV
        csv_data = "Nome;Email;WhatsApp;Estado;Cidade;Status;Data de Cadastro;Especialidades\n"
        for prof in profissionais:
            # Formatando especialidades como string
            especialidades_str = ", ".join(prof.get('especialidades', [])) if prof.get('especialidades') else ""
            
            # Adicionar linha no CSV
            csv_data += f"{prof.get('nome_completo', 'N/A')};{prof.get('email', 'N/A')};{prof.get('whatsapp', 'N/A')};" \
                      f"{prof.get('estado', 'N/A')};{prof.get('cidade', 'N/A')};{prof.get('status', 'Pendente')};" \
                      f"{prof.get('data_formatada', 'N/A')};{especialidades_str}\n"
        
        # Retornar o CSV como um arquivo para download
        from flask import Response
        response = Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=profissionais_vnx.csv"}
        )
        return response
    
    except Exception as e:
        print(f"Erro ao exportar profissionais para CSV: {e}")
        flash(f'Erro ao exportar dados: {str(e)}', 'danger')
        return redirect(url_for('listar_profissionais'))

# Logout
@app.route('/adm/logout')
def admin_logout():
    # Remover dados da sessão
    session.pop('usuario_logado', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('admin_login'))

# Executa o servidor quando o arquivo é executado diretamente
if __name__ == '__main__':
    # Adiciona um usuário de teste para facilitar o login
    usuarios.append({
        'nome': 'Administrador',
        'email': 'admin@exemplo.com',
        'senha': 'admin123',
        'telefone': '(00) 00000-0000'
    })
    
    # Inicia o servidor em modo debug
    print("Servidor iniciado! Acesse http://localhost:5000/adm")
    app.run(debug=True, host='0.0.0.0', port=5000) 