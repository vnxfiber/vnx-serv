from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
# Removendo a dependência do dotenv
# from dotenv import load_dotenv
from supabase import create_client, Client
import json
from markupsafe import Markup

# Não precisamos mais carregar variáveis do .env
# load_dotenv()

app = Flask(__name__, template_folder='adm', static_folder='static')
app.secret_key = os.urandom(24)  # Chave secreta para sessões Flask

# Adicionando filtro nl2br para Jinja2
@app.template_filter('nl2br')
def nl2br(value):
    if not value:
        return ''
    return Markup(value.replace('\n', '<br>'))

# Configuração do Supabase - definindo manualmente
SUPABASE_URL = "https://cwrxdjfmxntmplwdbnpg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYwMDI0MzksImV4cCI6MjA2MTU3ODQzOX0.-kFUUiLn2plnEdopteCdxcixyY3pI5O-K-hIk1IL61s"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rota principal
@app.route('/')
def home():
    return redirect(url_for('admin_login'))

# Rota para login de admin
@app.route('/adm/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('username')  # O campo username pode ser o email
        password = request.form.get('password')
        
        try:
            # Tentar fazer login no Supabase
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            # Se chegou aqui, login bem-sucedido
            session['user'] = {
                'id': response.user.id,
                'email': response.user.email
            }
            session['token'] = response.session.access_token
            
            # Redirecionar para o dashboard após login bem-sucedido
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            flash('Login falhou. Verifique suas credenciais. ' + str(e), 'danger')
    
    # Se for GET ou se o login falhou
    return render_template('index.html')

# Rota para cadastro de admin
@app.route('/adm/cadastro', methods=['GET', 'POST'])
def admin_cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        telefone = request.form.get('telefone')
        
        try:
            # Criar usuário no Auth do Supabase
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "nome": nome,
                        "username": username,
                        "telefone": telefone
                    }
                }
            })
            
            # Se chegou aqui, cadastro bem-sucedido
            user_id = auth_response.user.id
            
            # Inserir dados adicionais na tabela de administradores
            supabase.table('administradores').insert({
                "id": user_id,
                "nome": nome,
                "username": username,
                "email": email,
                "telefone": telefone
            }).execute()
            
            flash('Administrador cadastrado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('admin_login'))
            
        except Exception as e:
            error_msg = str(e)
            if 'User already registered' in error_msg:
                error_msg = 'Este email já está cadastrado.'
            flash(f'Erro no cadastro: {error_msg}', 'danger')
    
    # Se for GET ou se o cadastro falhou
    return render_template('cadastro.html')

# Rota para o dashboard do admin
@app.route('/adm/dashboard')
def admin_dashboard():
    # Verificar se o usuário está logado
    if 'user' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Buscar todos os profissionais
    try:
        response = supabase.table('profissionais').select('*').execute()
        profissionais = response.data
    except Exception as e:
        profissionais = []
        flash(f'Erro ao buscar profissionais: {str(e)}', 'danger')
    
    # Use the dashboard.html in the adm directory
    return render_template('dashboard.html', profissionais=profissionais, user=session['user'])

# Rota para logout
@app.route('/adm/logout')
def admin_logout():
    # Limpar a sessão
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('admin_login'))

# Rota para adicionar um novo profissional
@app.route('/adm/profissionais/novo', methods=['GET', 'POST'])
def novo_profissional():
    # Verificar se o usuário está logado
    if 'user' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Capturar dados do formulário
        dados = {
            "nome": request.form.get('nome'),
            "email": request.form.get('email'),
            "telefone": request.form.get('telefone'),
            "profissao": request.form.get('profissao'),
            "experiencia": request.form.get('experiencia'),
            "disponibilidade": request.form.get('disponibilidade')
        }
        
        try:
            # Inserir no Supabase
            supabase.table('profissionais').insert(dados).execute()
            flash('Profissional cadastrado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Erro ao cadastrar profissional: {str(e)}', 'danger')
    
    return render_template('novo_profissional.html', user=session['user'])

# Rota para visualizar candidatos do Trabalhe Conosco
@app.route('/adm/candidatos')
def admin_candidatos():
    # Verificar se o usuário está logado
    if 'user' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Parâmetros de filtro e paginação
    page = request.args.get('page', 1, type=int)
    per_page = 10  # quantidade de itens por página
    filtro_especialidade = request.args.get('especialidade', '')
    filtro_estado = request.args.get('estado', '')
    filtro_status = request.args.get('status', '')
    termo_busca = request.args.get('busca', '')
    
    try:
        # Construir a consulta base
        query = supabase.table('candidatos_trabalhe_conosco').select('*')
        
        # Aplicar filtros se fornecidos
        if filtro_especialidade:
            query = query.contains('especialidades', [filtro_especialidade])
        
        if filtro_estado:
            query = query.ilike('cidadeEstado', f'%{filtro_estado}%')
            
        if filtro_status:
            query = query.eq('status', filtro_status)
            
        if termo_busca:
            query = query.or_(f'nome.ilike.%{termo_busca}%,email.ilike.%{termo_busca}%')
        
        # Executar a contagem para paginação
        count_query = query.execute()
        total_candidatos = len(count_query.data)
        total_pages = (total_candidatos + per_page - 1) // per_page
        
        # Executar a consulta com paginação
        response = query.range(
            (page - 1) * per_page, 
            min(page * per_page - 1, total_candidatos)
        ).order('data_cadastro', desc=True).execute()
        
        candidatos = response.data
        
        # Obter lista de estados únicos para o filtro
        estados_response = supabase.table('candidatos_trabalhe_conosco').select('cidadeEstado').execute()
        estados_raw = [item['cidadeEstado'].split('/')[-1].strip() if '/' in item['cidadeEstado'] else '' for item in estados_response.data]
        estados = sorted(list(set(estado for estado in estados_raw if estado)))
        
    except Exception as e:
        candidatos = []
        estados = []
        total_candidatos = 0
        total_pages = 1
        flash(f'Erro ao buscar candidatos: {str(e)}', 'danger')
    
    return render_template(
        'candidatos.html', 
        candidatos=candidatos,
        user=session['user'],
        estados=estados,
        current_page=page,
        total_pages=total_pages,
        total_candidatos=total_candidatos
    )

# Rota para atualizar status de um candidato
@app.route('/adm/candidatos/<int:id>/status', methods=['POST'])
def atualizar_status_candidato(id):
    if 'user' not in session:
        flash('Você precisa estar logado para realizar esta ação.', 'warning')
        return redirect(url_for('admin_login'))
    
    status = request.form.get('status')
    if not status:
        flash('Status não informado.', 'danger')
        return redirect(url_for('admin_candidatos'))
    
    try:
        supabase.table('candidatos_trabalhe_conosco').update(
            {"status": status, "atualizado_por": session['user']['id']}
        ).eq('id', id).execute()
        
        flash(f'Status do candidato atualizado para {status}.', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar status: {str(e)}', 'danger')
    
    return redirect(url_for('admin_candidatos'))

# Rota para editar um candidato
@app.route('/adm/candidatos/<int:id>/editar', methods=['POST'])
def editar_candidato(id):
    if 'user' not in session:
        flash('Você precisa estar logado para realizar esta ação.', 'warning')
        return redirect(url_for('admin_login'))
    
    try:
        # Construir dados para atualização
        dados = {
            "nome": request.form.get('nome'),
            "email": request.form.get('email'),
            "whatsapp": request.form.get('whatsapp'),
            "cidadeEstado": request.form.get('cidadeEstado'),
            "links": request.form.get('links', ''),
            "experiencia": request.form.get('experiencia', ''),
            "status": request.form.get('status', 'pendente'),
            "atualizado_por": session['user']['id']
        }
        
        # Verificar se especialidades foi enviado
        if 'especialidades[]' in request.form:
            especialidades = request.form.getlist('especialidades[]')
            dados["especialidades"] = especialidades
        
        # Atualizar no banco
        supabase.table('candidatos_trabalhe_conosco').update(dados).eq('id', id).execute()
        flash('Candidato atualizado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar candidato: {str(e)}', 'danger')
    
    return redirect(url_for('admin_candidatos'))

# Rota para excluir um candidato
@app.route('/adm/candidatos/<int:id>/excluir', methods=['POST'])
def excluir_candidato(id):
    if 'user' not in session:
        flash('Você precisa estar logado para realizar esta ação.', 'warning')
        return redirect(url_for('admin_login'))
    
    try:
        supabase.table('candidatos_trabalhe_conosco').delete().eq('id', id).execute()
        flash('Candidato excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir candidato: {str(e)}', 'danger')
    
    return redirect(url_for('admin_candidatos'))

# Rota para exportar candidatos
@app.route('/adm/candidatos/exportar', methods=['POST'])
def exportar_candidatos():
    if 'user' not in session:
        flash('Você precisa estar logado para realizar esta ação.', 'warning')
        return redirect(url_for('admin_login'))
    
    formato = request.form.get('formato', 'excel')
    escopo = request.form.get('escopo', 'todos')
    
    # Implementação simplificada - na prática, você criaria os arquivos para download
    flash(f'Exportação de candidatos em {formato} solicitada. Esta funcionalidade será implementada em breve.', 'info')
    return redirect(url_for('admin_candidatos'))

# Rota para enviar email a um candidato
@app.route('/adm/candidatos/<int:id>/email')
def enviar_email_candidato(id):
    if 'user' not in session:
        flash('Você precisa estar logado para realizar esta ação.', 'warning')
        return redirect(url_for('admin_login'))
    
    # Implementação simplificada
    flash('Funcionalidade de envio de e-mail será implementada em breve.', 'info')
    return redirect(url_for('admin_candidatos'))

if __name__ == '__main__':
    app.run(debug=True) # debug=True para desenvolvimento 