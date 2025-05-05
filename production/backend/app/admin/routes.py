import os
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, Response
from supabase import create_client, Client
import logging
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import hashlib
import base64
from .logger_config import setup_logger
import sys
import os
import random
import io
import csv
import pytz
from ..utils.supabase import SupabaseClient
from ..utils.logger import logger

# Adiciona o diretório pai ao path para permitir importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

# Configuração do logger
logger = setup_logger()

# Blueprint do Admin
admin_bp = Blueprint('admin', __name__,
                    url_prefix='/admin',
                    template_folder='../templates',
                    static_folder='../static',
                    static_url_path='/static')

# Filtros para templates
@admin_bp.app_template_filter('datetime')
def format_datetime(value):
    if not value:
        return ''
    try:
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            dt = value
        return dt.strftime('%d/%m/%Y %H:%M')
    except Exception as e:
        logger.error(f"Erro ao formatar data: {str(e)}")
        return value

@admin_bp.app_template_filter('todatetime')
def to_datetime(value):
    if not value:
        return datetime.now(pytz.UTC)
    try:
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value
    except Exception as e:
        logger.error(f"Erro ao converter data: {str(e)}")
        return datetime.now(pytz.UTC)

@admin_bp.app_template_filter('nl2br')
def nl2br(value):
    if not value:
        return ''
    return value.replace('\n', '<br>')

# Filtro para ícones de notificação
@admin_bp.app_template_filter('notification_icon')
def notification_icon(type):
    icons = {
        'success': 'check-circle',
        'danger': 'times-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    }
    return icons.get(type, 'info-circle')

# Filtro para formatar o número do WhatsApp
@admin_bp.app_template_filter('format_whatsapp')
def format_whatsapp(number):
    """Formata o número do WhatsApp para o formato internacional."""
    if not number:
        return ''
    
    # Remove todos os caracteres não numéricos
    clean_number = ''.join(filter(str.isdigit, number))
    
    # Se o número começar com 0, remove o 0
    if clean_number.startswith('0'):
        clean_number = clean_number[1:]
    
    # Se não começar com 55 (código do Brasil), adiciona
    if not clean_number.startswith('55'):
        clean_number = '55' + clean_number
    
    return clean_number

# Configuração do Supabase
class SupabaseClient:
    _instance = None
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                logger.debug("Inicializando cliente Supabase...")
                cls._client = create_client(
                    'https://cwrxdjfmxntmplwdbnpg.supabase.co',
                    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjAwMjQzOSwiZXhwIjoyMDYxNTc4NDM5fQ.wUCecHTnyEwSVoH_-ruIV4fIGibr0vNkGZPbTVBM8uY'
                )
                # Teste de conexão
                test = cls._client.table('admin_users').select("*").limit(1).execute()
                logger.debug(f"Teste de conexão Supabase bem-sucedido: {test}")
            except Exception as e:
                logger.error(f"Erro ao inicializar Supabase: {str(e)}", exc_info=True)
                cls._client = None
        return cls._client

def verify_password(password: str, hash_string: str) -> bool:
    """Verifica a senha com suporte a múltiplos formatos de hash."""
    try:
        # Formato pbkdf2 do Flask/Werkzeug
        if hash_string.startswith('pbkdf2:sha256:'):
            return check_password_hash(hash_string, password)
        
        # Formato scrypt do Supabase
        elif hash_string.startswith('scrypt:'):
            try:
                # Formato: scrypt:N:r:p$salt$hash
                parts = hash_string.split('$')
                if len(parts) != 3:
                    return False
                
                algo_params, salt, stored_hash = parts
                algo_parts = algo_params.split(':')
                if len(algo_parts) != 4 or algo_parts[0] != 'scrypt':
                    return False
                
                N, r, p = map(int, algo_parts[1:])
                
                # Gera o hash da senha fornecida
                derived_key = hashlib.scrypt(
                    password.encode(),
                    salt=salt.encode(),
                    n=N,
                    r=r,
                    p=p,
                    maxmem=2000000000,  # 2GB max memory
                    dklen=64  # 64 bytes output
                )
                
                # Converte para base64 para comparar
                derived_hash = base64.b64encode(derived_key).decode('utf-8')
                
                return derived_hash == stored_hash
            except Exception as e:
                logger.error(f"Erro ao verificar hash scrypt: {str(e)}", exc_info=True)
                return False
        
        # Formato sha256 simples
        elif hash_string.startswith('sha256$SALT$'):
            try:
                _, _, stored_hash = hash_string.split('$')
                # Gera um hash SHA-256 da senha
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                return password_hash == stored_hash
            except Exception as e:
                logger.error(f"Erro ao verificar hash sha256: {str(e)}", exc_info=True)
                return False
        
        # Formato desconhecido
        else:
            logger.warning(f"Formato de hash desconhecido: {hash_string[:20]}...")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {str(e)}", exc_info=True)
        return False

# --- Decorator para verificar login ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"Verificando login - session: {session}")
        if 'user_id' not in session:
            logger.warning("Tentativa de acesso sem login")
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('admin.login'))
        logger.debug(f"Usuário autenticado: {session['user_id']}")
        return f(*args, **kwargs)
    return decorated_function

# --- Rotas de Autenticação ---

@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    logger.debug("Iniciando rota de registro")
    logger.debug(f"Método da requisição: {request.method}")
    
    if request.method == 'POST':
        logger.debug("Recebido POST para registro")
        logger.debug(f"Dados do formulário completos: {request.form}")
        email = request.form.get('email')
        password = request.form.get('password')
        nome = request.form.get('nome')
        
        logger.debug(f"Dados recebidos - Email: {email}, Nome: {nome}")

        if not all([email, password, nome]):
            logger.warning("Dados incompletos no formulário")
            flash('Por favor, preencha todos os campos.', 'warning')
            return render_template('admin/register.html')

        supabase = SupabaseClient.get_client()
        if not supabase:
            logger.error("Cliente Supabase não está inicializado")
            flash('Erro na conexão com o banco de dados.', 'danger')
            return render_template('admin/register.html')

        try:
            logger.debug("Verificando se o email já existe")
            existing_user = supabase.table('admin_users').select("id").eq('email', email).execute()
            logger.debug(f"Resposta da verificação de email: {existing_user}")
            
            if existing_user.data:
                logger.warning(f"Email {email} já está cadastrado")
                flash('Este e-mail já está cadastrado.', 'warning')
                return render_template('admin/register.html')

            # Criar hash da senha usando método simples
            logger.debug("Gerando hash da senha")
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # Inserir novo usuário
            user_data = {
                'email': email,
                'password_hash': hashed_password,
                'nome': nome
            }
            logger.debug("Tentando inserir novo usuário")
            logger.debug(f"Dados a serem inseridos: {user_data}")
            
            try:
                response = supabase.table('admin_users').insert(user_data).execute()
                logger.debug(f"Resposta completa da inserção: {response}")
                
                if hasattr(response, 'data') and response.data:
                    logger.info(f"Usuário {email} registrado com sucesso")
                    flash('Conta criada com sucesso! Faça o login.', 'success')
                    return redirect(url_for('admin.login'))
                else:
                    error_msg = getattr(response, 'error', 'Erro desconhecido')
                    logger.error(f"Erro ao registrar usuário: {error_msg}")
                    flash('Erro ao criar conta. Tente novamente.', 'danger')
            except Exception as insert_error:
                logger.error(f"Erro durante a inserção: {str(insert_error)}", exc_info=True)
                flash('Erro ao inserir usuário no banco de dados.', 'danger')

        except Exception as e:
            logger.error(f"Erro excepcional durante o registro: {str(e)}", exc_info=True)
            flash('Ocorreu um erro inesperado. Tente novamente.', 'danger')

    return render_template('admin/register.html')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    logger.debug("Iniciando rota de login")
    
    if request.method == 'POST':
        logger.debug("Recebido POST para login")
        email = request.form.get('email')
        password = request.form.get('password')
        
        logger.debug(f"Tentando login com email: {email}")

        supabase = SupabaseClient.get_client()
        if not supabase:
            logger.error("Cliente Supabase não está inicializado")
            flash('Erro na conexão com o banco de dados.', 'danger')
            return render_template('admin/login.html')

        try:
            logger.debug("Buscando usuário no banco de dados")
            response = supabase.table('admin_users').select("*").eq('email', email).execute()
            logger.debug(f"Resposta da busca de usuário: {response}")
            
            if response.data and len(response.data) > 0:
                user = response.data[0]
                logger.debug(f"Usuário encontrado: {user}")
                
                if verify_password(password, user['password_hash']):
                    logger.info(f"Login bem-sucedido para o usuário: {email}")
                    session['user_id'] = user['id']
                    session['user_name'] = user['nome']
                    session['user_email'] = user['email']
                    session['is_authenticated'] = True
                    return redirect(url_for('admin.dashboard'))
                else:
                    logger.warning(f"Senha incorreta para o usuário: {email}")
                    flash('Email ou senha incorretos.', 'danger')
            else:
                logger.warning(f"Usuário não encontrado: {email}")
                flash('Email ou senha incorretos.', 'danger')
                
        except Exception as e:
            logger.error(f"Erro ao tentar fazer login: {e}", exc_info=True)
            flash('Erro ao tentar fazer login.', 'danger')
            
        return render_template('admin/login.html')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('admin.login'))

# --- Rota do Dashboard ---

@admin_bp.route('/') # Rota raiz do admin
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Inicializar variáveis com valores padrão
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    especialidade = request.args.get('especialidade', '')
    cidade = request.args.get('cidade', '')
    
    # Verificar se é uma requisição AJAX
    is_ajax = request.args.get('ajax', 'false') == 'true'
    
    try:
        supabase = SupabaseClient.get_client()
        
        # Verificar se os dados do usuário estão na sessão
        user_id = session.get('user_id')
        if user_id:
            try:
                # Buscar dados atualizados do usuário
                user_response = supabase.table('admin_users').select("*").eq('id', user_id).limit(1).execute()
                if user_response.data and len(user_response.data) > 0:
                    user = user_response.data[0]
                    session['user_name'] = user.get('nome', 'Usuário')
                    session['user_email'] = user.get('email', '')
            except Exception as user_error:
                logger.error(f"Erro ao buscar dados do usuário: {str(user_error)}")
                # Não interromper o fluxo se essa verificação falhar
        
        # Verificar novos cadastros desde o último acesso
        if user_id and not is_ajax:
            try:
                # Buscar a última vez que o usuário verificou por novos cadastros
                last_check_response = supabase.table('user_last_checks').select('*').eq('user_id', user_id).limit(1).execute()
                last_check_time = None
                
                if last_check_response.data and len(last_check_response.data) > 0:
                    last_check_time = last_check_response.data[0].get('last_check_time')
                    
                    # Convertemos o timestamp para o formato correto antes de comparar
                    if isinstance(last_check_time, str):
                        try:
                            last_check_time = datetime.fromisoformat(last_check_time.replace('Z', '+00:00'))
                            last_check_iso = last_check_time.isoformat()
                            
                            # Consultar novos cadastros desde a última verificação - usando o formato ISO correto
                            new_partners_response = supabase.table('parceiros_tecnicos') \
                                .select('id') \
                                .filter('created_at', 'gt', last_check_iso) \
                                .execute()
                                
                            if new_partners_response.data and len(new_partners_response.data) > 0:
                                # Criar notificação apenas se houver novos parceiros
                                logger.debug(f"Encontrados {len(new_partners_response.data)} novos parceiros desde {last_check_iso}")
                                create_notification(
                                    user_id=user_id,
                                    title='Novos Parceiros',
                                    message=f'Há {len(new_partners_response.data)} novo(s) cadastro(s) de parceiro(s) técnico(s).',
                                    type='info'
                                )
                        except Exception as date_error:
                            logger.error(f"Erro na conversão de data: {str(date_error)}")
                
                # Atualizar o timestamp da última verificação
                current_time = datetime.now().isoformat()
                if last_check_time:
                    supabase.table('user_last_checks') \
                        .update({'last_check_time': current_time}) \
                        .eq('user_id', user_id) \
                        .execute()
                else:
                    # Se não houver registro anterior, criar um
                    supabase.table('user_last_checks').insert({
                        'user_id': user_id,
                        'last_check_time': current_time
                    }).execute()
                    
            except Exception as check_error:
                logger.error(f"Erro ao verificar novos cadastros: {str(check_error)}", exc_info=True)
                # Não interromper o fluxo se essa verificação falhar
        
        # Iniciar com uma consulta básica
        query = supabase.table('parceiros_tecnicos').select("*")
        
        # Aplicar filtros, se fornecidos
        if status:
            query = query.eq('status', status)
        if especialidade:
            query = query.contains('especialidades', [especialidade])
        if cidade:
            query = query.eq('cidade', cidade)
        if search:
            search_term = f"%{search}%".lower()
            query = query.or_(f"nome.ilike.{search_term},email.ilike.{search_term}")
        
        # Executar a consulta para obter o número total de registros
        result = query.execute()
        all_parceiros = result.data
        total_records = len(all_parceiros)
        
        # Calcular total de páginas
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        
        # Ajustar a página atual se estiver fora dos limites
        page = min(max(1, page), total_pages)
        
        # Calcular índices de início e fim para paginação
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_records)
        
        # Obter parceiros da página atual
        parceiros = all_parceiros[start_idx:end_idx]
        
        # Verificar e corrigir valores nulos em parceiros
        for p in parceiros:
            if not p.get('status'):
                p['status'] = 'Pendente'
            if not p.get('especialidades'):
                p['especialidades'] = []
            if not p.get('cidade'):
                p['cidade'] = 'Não informada'
            if not p.get('nome_completo'):
                p['nome_completo'] = 'Nome não informado'
            if not p.get('created_at'):
                p['created_at'] = datetime.now().isoformat()
        
        # Contar parceiros por status
        parceiros_pendentes = len([p for p in all_parceiros if not p.get('status') or p['status'] == 'Pendente'])
        parceiros_aprovados = len([p for p in all_parceiros if p.get('status') == 'Aprovado'])
        parceiros_rejeitados = len([p for p in all_parceiros if p.get('status') == 'Rejeitado'])
        
        # Calcular a especialidade mais comum
        especialidades_count = {}
        for p in all_parceiros:
            if p.get('especialidades'):
                for esp in p['especialidades']:
                    if esp not in especialidades_count:
                        especialidades_count[esp] = 0
                    especialidades_count[esp] += 1
        
        # Encontrar a especialidade com mais ocorrências
        especialidade_principal = "Nenhuma" if not especialidades_count else max(especialidades_count.items(), key=lambda x: x[1])[0]
        
        # Obter listas de especialidades e cidades para os filtros
        especialidades = sorted(list(set([esp for p in all_parceiros if 'especialidades' in p and p['especialidades'] for esp in p['especialidades']])))
        cidades = sorted(list(set([p['cidade'] for p in all_parceiros if 'cidade' in p and p['cidade']])))
        
        # Preparar dados para os gráficos
        # 1. Gráfico de distribuição por especialidade
        dados_especialidades = [especialidades_count.get(esp, 0) for esp in especialidades]
        
        # 2. Gráfico de distribuição por status
        dados_status = [parceiros_pendentes, parceiros_aprovados, parceiros_rejeitados]
        
        # Criar ranking de especialidades
        especialidades_ranking = [
            {"nome": esp, "total": total}
            for esp, total in especialidades_count.items()
        ]
        especialidades_ranking.sort(key=lambda x: x["total"], reverse=True)
        
        # Obter informações do usuário logado da sessão
        user_data = {
            'nome': session.get('user_name', 'Usuário'),
            'email': session.get('user_email', ''),
            'id': session.get('user_id')
        }

        # Se for uma requisição AJAX, retornar JSON
        if is_ajax:
            return jsonify({
                'parceiros': parceiros,
                'stats': {
                    'total': total_records,
                    'pendentes': parceiros_pendentes,
                    'aprovados': parceiros_aprovados,
                    'rejeitados': parceiros_rejeitados,
                    'especialidade_principal': especialidade_principal
                },
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'total_records': total_records
                }
            })

        return render_template('admin/dashboard.html',
                             current_user=user_data,
                             pending_security_updates=False,  # Você pode ajustar isso conforme necessário
                             parceiros=parceiros,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             total_parceiros=total_records,
                             parceiros_pendentes=parceiros_pendentes,
                             parceiros_aprovados=parceiros_aprovados,
                             parceiros_rejeitados=parceiros_rejeitados,
                             especialidade_principal=especialidade_principal,
                             especialidades=especialidades,
                             cidades=cidades,
                             labels_especialidades=especialidades,
                             dados_especialidades=dados_especialidades,
                             dados_status=dados_status,
                             especialidades_ranking=especialidades_ranking)

    except Exception as e:
        logger.error(f"Erro ao listar parceiros: {str(e)}", exc_info=True)
        
        if is_ajax:
            return jsonify({
                'error': 'Erro ao carregar dados',
                'message': str(e)
            }), 500
            
        flash('Erro ao carregar dados. Tente novamente.', 'danger')
        
    return render_template('admin/dashboard.html',
                         parceiros=[],
                         page=1, 
                         total_pages=1,
                         total_records=0,
                         per_page=per_page,
                         total_parceiros=0,
                         parceiros_pendentes=0,
                         parceiros_aprovados=0,
                         parceiros_rejeitados=0,
                         especialidade_principal="Nenhuma",
                         especialidades=[],
                         cidades=[],
                         labels_especialidades=[],
                         dados_especialidades=[],
                         dados_status=[0, 0, 0],
                         especialidades_ranking=[])

@admin_bp.route('/parceiro/<partner_id>')
@login_required
def view_partner(partner_id):
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
        response = supabase.table('parceiros_tecnicos').select("*").eq('id', partner_id).limit(1).execute()
        if response.data:
            parceiro = response.data[0]
            return render_template('admin/partner_details.html', parceiro=parceiro)
        else:
            flash('Parceiro não encontrado.', 'warning')
            return redirect(url_for('admin.dashboard'))
    except Exception as e:
        logger.error(f"Erro ao carregar detalhes do parceiro {partner_id}: {str(e)}")
        flash(f'Erro ao carregar detalhes: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/parceiro/<partner_id>/status', methods=['POST'])
@login_required
def update_status(partner_id):
    try:
        logger.debug(f"Iniciando atualização de status - Partner ID: {partner_id}")
        logger.debug(f"Dados recebidos: {request.form}")
        
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        new_status = request.form.get('status')
        if not new_status:
            logger.warning("Status não fornecido na requisição")
            flash('Status inválido.', 'warning')
            return redirect(url_for('admin.dashboard'))
            
        # Validar se o status é válido
        valid_statuses = ['Pendente', 'Aprovado', 'Rejeitado']
        new_status = new_status.capitalize()  # Garantir primeira letra maiúscula
        
        if new_status not in valid_statuses:
            logger.warning(f"Status inválido fornecido: {new_status}")
            flash('Status inválido fornecido.', 'warning')
            return redirect(url_for('admin.dashboard'))
            
        logger.debug(f"Atualizando status do parceiro {partner_id} para {new_status}")
        response = supabase.table('parceiros_tecnicos').update({'status': new_status}).eq('id', partner_id).execute()
        logger.debug(f"Resposta completa da atualização: {response}")
        
        if response.data:
            logger.info(f"Status atualizado com sucesso para {new_status}")
            flash('Status atualizado com sucesso!', 'success')
            
            # Criar notificação
            user_id = session.get('user_id')
            notification_created = create_notification(
                user_id=user_id,
                title=f'Status Atualizado',
                message=f'O status do parceiro foi atualizado para {new_status}.',
                type='success'
            )
            logger.debug(f"Notificação criada: {notification_created}")
            
        else:
            error_message = "Erro desconhecido ao atualizar status."
            if hasattr(response, 'error') and response.error:
                error_message = f"Erro ao atualizar status: {response.error}"
            elif not response.data:
                error_message = "Nenhum dado retornado após a tentativa de atualização."
            
            logger.error(error_message)
            flash(error_message, 'danger')
            
    except Exception as e:
        logger.error(f"Erro excepcional ao atualizar status: {str(e)}", exc_info=True)
        flash(f'Erro ao atualizar status: {str(e)}', 'danger')
        
    return redirect(url_for('admin.dashboard'))

# Rotas para aprovar/rejeitar parceiros
@admin_bp.route('/aprovar-parceiro/<partner_id>', methods=['POST'])
@login_required
def aprovar_parceiro(partner_id):
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        user_id = session.get('user_id')
        
        # Atualizar status do parceiro
        response = supabase.table('parceiros_tecnicos') \
            .update({'status': 'Aprovado'}) \
            .eq('id', partner_id) \
            .execute()
            
        if response.data:
            # Criar notificação
            try:
                create_notification(
                    user_id=user_id,
                    title='Parceiro Aprovado',
                    message=f'O parceiro técnico foi aprovado com sucesso.',
                    type='success'
                )
            except Exception as notif_error:
                logger.error(f"Erro ao criar notificação: {str(notif_error)}")
                # Não interromper o fluxo se a notificação falhar
                
            logger.info(f"Parceiro {partner_id} aprovado com sucesso")
            return jsonify({'success': True})
        else:
            error_message = "Erro ao aprovar parceiro"
            if hasattr(response, 'error') and response.error:
                error_message = f"Erro ao aprovar parceiro: {response.error}"
            logger.error(error_message)
            return jsonify({'success': False, 'error': error_message}), 500
    except Exception as e:
        logger.error(f"Erro ao aprovar parceiro: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/rejeitar-parceiro/<partner_id>', methods=['POST'])
@login_required
def rejeitar_parceiro(partner_id):
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        user_id = session.get('user_id')
        
        # Atualizar status do parceiro
        response = supabase.table('parceiros_tecnicos') \
            .update({'status': 'Rejeitado'}) \
            .eq('id', partner_id) \
            .execute()
            
        if response.data:
            # Criar notificação
            try:
                create_notification(
                    user_id=user_id,
                    title='Parceiro Rejeitado',
                    message=f'O parceiro técnico foi rejeitado.',
                    type='warning'
                )
            except Exception as notif_error:
                logger.error(f"Erro ao criar notificação: {str(notif_error)}")
                # Não interromper o fluxo se a notificação falhar
                
            logger.info(f"Parceiro {partner_id} rejeitado com sucesso")
            return jsonify({'success': True})
        else:
            error_message = "Erro ao rejeitar parceiro"
            if hasattr(response, 'error') and response.error:
                error_message = f"Erro ao rejeitar parceiro: {response.error}"
            logger.error(error_message)
            return jsonify({'success': False, 'error': error_message}), 500
    except Exception as e:
        logger.error(f"Erro ao rejeitar parceiro: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Rotas de Notificações ---

@admin_bp.route('/notifications')
@login_required
def notifications():
    """Rota para exibir todas as notificações do usuário."""
    try:
        supabase = SupabaseClient.get_client()
        user_id = session.get('user_id')
        
        # Buscar notificações do usuário, ordenadas por data (mais recentes primeiro)
        response = supabase.table('notifications') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True) \
            .execute()
            
        notifications = response.data if response.data else []
        
        # Marcar todas como lidas
        if notifications:
            supabase.table('notifications') \
                .update({'read': True}) \
                .eq('user_id', user_id) \
                .eq('read', False) \
                .execute()
        
        return render_template('admin/notifications.html', notifications=notifications)
    except Exception as e:
        logger.error(f"Erro ao buscar notificações: {str(e)}", exc_info=True)
        flash('Erro ao carregar notificações.', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/notifications/count')
@login_required
def get_notifications_count():
    """Rota para obter o número de notificações não lidas."""
    try:
        supabase = SupabaseClient.get_client()
        user_id = session.get('user_id')
        
        # Contar notificações não lidas
        response = supabase.table('notifications') \
            .select('id', count='exact') \
            .eq('user_id', user_id) \
            .eq('read', False) \
            .execute()
            
        count = len(response.data) if response.data else 0
        return jsonify({'count': count})
    except Exception as e:
        logger.error(f"Erro ao contar notificações: {str(e)}", exc_info=True)
        return jsonify({'count': 0})

@admin_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    """Rota para marcar notificações como lidas."""
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            return jsonify({'success': False, 'error': 'Erro de conexão com o banco de dados'}), 500
            
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Usuário não autenticado'}), 401
        
        # Obter dados da requisição
        data = request.get_json()
        notification_ids = data.get('notification_ids', []) if data else []
        
        logger.debug(f"Marcando notificações como lidas - User ID: {user_id}, Notification IDs: {notification_ids}")
        
        try:
            if not notification_ids:
                # Se não foram especificados IDs, marca todas como lidas
                response = supabase.table('notifications') \
                    .update({'read': True}) \
                    .eq('user_id', user_id) \
                    .eq('read', False) \
                    .execute()
            else:
                # Marca apenas as notificações específicas como lidas
                response = supabase.table('notifications') \
                    .update({'read': True}) \
                    .eq('user_id', user_id) \
                    .in_('id', notification_ids) \
                    .execute()
            
            if not response.data and not response.count:
                logger.warning("Nenhuma notificação foi atualizada")
                return jsonify({'success': True, 'message': 'Nenhuma notificação para atualizar'})
            
            logger.info(f"Notificações marcadas como lidas com sucesso - User ID: {user_id}")
            return jsonify({'success': True})
            
        except Exception as db_error:
            logger.error(f"Erro ao atualizar notificações no banco: {str(db_error)}", exc_info=True)
            return jsonify({'success': False, 'error': 'Erro ao atualizar notificações'}), 500
            
    except Exception as e:
        logger.error(f"Erro ao marcar notificações como lidas: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/notifications/clear-all', methods=['POST'])
@login_required
def clear_all_notifications():
    """Rota para limpar todas as notificações do usuário."""
    try:
        supabase = SupabaseClient.get_client()
        user_id = session.get('user_id')
        
        # Deleta todas as notificações do usuário
        supabase.table('notifications') \
            .delete() \
            .eq('user_id', user_id) \
            .execute()
        
        # Se chegou aqui, a operação foi bem-sucedida
        return jsonify({'status': 'success'}), 200
            
    except Exception as e:
        logger.error(f"Erro ao limpar notificações: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@admin_bp.route('/notifications/recent')
@login_required
def get_recent_notifications():
    """Rota para obter as notificações mais recentes para o dropdown."""
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            return jsonify({
                'error': 'Erro de conexão com o banco de dados',
                'notifications': []
            }), 500
            
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'error': 'Usuário não autenticado',
                'notifications': []
            }), 401
        
        # Buscar as 5 notificações mais recentes
        response = supabase.table('notifications') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True) \
            .limit(5) \
            .execute()
            
        if not hasattr(response, 'data'):
            return jsonify({
                'error': 'Resposta inválida do banco de dados',
                'notifications': []
            }), 500
            
        notifications = response.data if response.data else []
        
        # Log para debug
        logger.debug(f"Notificações encontradas: {notifications}")
        
        return jsonify({
            'success': True,
            'notifications': notifications
        })
    except Exception as e:
        logger.error(f"Erro ao buscar notificações recentes: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'notifications': []
        }), 500

def create_notification(user_id, title, message, type='info'):
    """Função auxiliar para criar uma nova notificação."""
    try:
        supabase = SupabaseClient.get_client()
        
        # Verificar se já existe uma notificação recente com o mesmo título e mensagem
        # para evitar duplicações em atualizações de página
        recent_time = (datetime.now() - timedelta(minutes=10)).isoformat()
        
        existing_response = supabase.table('notifications') \
            .select('id') \
            .eq('user_id', user_id) \
            .eq('title', title) \
            .eq('message', message) \
            .gte('created_at', recent_time) \
            .execute()
            
        # Se já existir uma notificação recente similar, não criar outra
        if existing_response.data and len(existing_response.data) > 0:
            logger.debug(f"Notificação similar recente encontrada, evitando duplicação: {title}")
            return False
        
        notification_data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': type,
            'read': False
        }
        
        response = supabase.table('notifications').insert(notification_data).execute()
        return True if response.data else False
    except Exception as e:
        logger.error(f"Erro ao criar notificação: {str(e)}", exc_info=True)
        return False

@admin_bp.route('/terms')
def terms():
    """Rota para exibir os termos de uso."""
    current_date = datetime.now().strftime('%d/%m/%Y')
    return render_template('admin/terms.html', current_date=current_date)

@admin_bp.route('/criar-dados-teste')
@login_required
def criar_dados_teste():
    """Funcionalidade removida."""
    flash('A funcionalidade de geração de dados de teste foi removida', 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/parceiros')
@login_required
def manage_partners():
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")

        # Parâmetros de paginação e filtros
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        especialidade_filter = request.args.get('especialidade')
        cidade_filter = request.args.get('cidade')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # Consulta base para contar total de registros
        count_query = supabase.table('parceiros_tecnicos').select("count", count='exact')
        
        # Aplicar filtros na consulta de contagem
        if status_filter:
            count_query = count_query.eq('status', status_filter)
        if especialidade_filter:
            count_query = count_query.contains('especialidades', [especialidade_filter])
        if cidade_filter:
            count_query = count_query.eq('cidade', cidade_filter)
        if search:
            count_query = count_query.or_(f"nome_completo.ilike.%{search}%,email.ilike.%{search}%,cidade.ilike.%{search}%")
            
        # Executar consulta de contagem
        count_response = count_query.execute()
        total_records = count_response.count if hasattr(count_response, 'count') else 0
        total_pages = (total_records + per_page - 1) // per_page
        
        # Ajustar página atual se necessário
        page = max(1, min(page, total_pages or 1))
        offset = (page - 1) * per_page

        # Consulta principal com paginação
        query = supabase.table('parceiros_tecnicos').select("*")
        
        # Aplicar filtros
        if status_filter:
            query = query.eq('status', status_filter)
        if especialidade_filter:
            query = query.contains('especialidades', [especialidade_filter])
        if cidade_filter:
            query = query.eq('cidade', cidade_filter)
        if search:
            query = query.or_(f"nome_completo.ilike.%{search}%,email.ilike.%{search}%,cidade.ilike.%{search}%")
            
        # Aplicar ordenação e paginação
        query = query.order(sort_by, desc=(sort_order == 'desc'))
        query = query.range(offset, offset + per_page - 1)

        # Executar consulta
        response = query.execute()
        parceiros = response.data or []

        # Coletar todas as especialidades e cidades únicas
        all_data = supabase.table('parceiros_tecnicos').select("especialidades,cidade").execute()
        especialidades = set()
        cidades = set()
        
        if all_data.data:
            for p in all_data.data:
                if isinstance(p.get('especialidades'), list):
                    especialidades.update(esp for esp in p.get('especialidades') if esp)
                if p.get('cidade'):
                    cidades.add(p.get('cidade'))

        return render_template('admin/manage_partners.html',
                             parceiros=parceiros,
                             page=page,
                             per_page=per_page,
                             total_pages=total_pages,
                             total_records=total_records,
                             especialidades=sorted(list(especialidades)),
                             cidades=sorted(list(cidades)),
                             current_filters={
                                 'status': status_filter,
                                 'especialidade': especialidade_filter,
                                 'cidade': cidade_filter,
                                 'search': search,
                                 'sort_by': sort_by,
                                 'sort_order': sort_order
                             })

    except Exception as e:
        logger.error(f"Erro ao gerenciar parceiros: {str(e)}", exc_info=True)
        flash(f'Erro ao carregar dados: {str(e)}', 'danger')
        return render_template('admin/manage_partners.html',
                             parceiros=[],
                             page=1,
                             per_page=10,
                             total_pages=1,
                             total_records=0,
                             especialidades=[],
                             cidades=[],
                             current_filters={})

@admin_bp.route('/parceiros/exportar')
@login_required
def export_partners():
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")

        # Buscar todos os parceiros
        response = supabase.table('parceiros_tecnicos').select("*").execute()
        parceiros = response.data or []

        # Criar CSV em memória
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escrever cabeçalho
        headers = ['ID', 'Nome Completo', 'Email', 'WhatsApp', 'Cidade', 'Estado', 
                  'Especialidades', 'Status', 'Data de Cadastro', 'Última Atualização']
        writer.writerow(headers)
        
        # Escrever dados
        for p in parceiros:
            writer.writerow([
                p.get('id'),
                p.get('nome_completo'),
                p.get('email'),
                p.get('whatsapp'),
                p.get('cidade'),
                p.get('estado'),
                ', '.join(p.get('especialidades', [])),
                p.get('status'),
                p.get('created_at'),
                p.get('updated_at')
            ])
        
        # Preparar resposta
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=parceiros_tecnicos.csv',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )

    except Exception as e:
        logger.error(f"Erro ao exportar parceiros: {str(e)}", exc_info=True)
        flash('Erro ao exportar dados dos parceiros.', 'danger')
        return redirect(url_for('admin.manage_partners'))

@admin_bp.route('/parceiro/<partner_id>/delete', methods=['DELETE'])
@login_required
def delete_partner(partner_id):
    """Rota para deletar um parceiro individual."""
    try:
        logger.debug(f"Iniciando deleção do parceiro {partner_id}")
        
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        # Verificar se o parceiro existe
        response = supabase.table('parceiros_tecnicos').select("*").eq('id', partner_id).execute()
        if not response.data:
            logger.warning(f"Parceiro {partner_id} não encontrado")
            return jsonify({'success': False, 'error': 'Parceiro não encontrado'}), 404
            
        # Deletar o parceiro
        response = supabase.table('parceiros_tecnicos').delete().eq('id', partner_id).execute()
        
        if response.data:
            logger.info(f"Parceiro {partner_id} deletado com sucesso")
            
            # Criar notificação
            user_id = session.get('user_id')
            create_notification(
                user_id=user_id,
                title='Parceiro Deletado',
                message=f'O parceiro foi removido com sucesso.',
                type='warning'
            )
            
            return jsonify({'success': True})
        else:
            error_message = "Erro ao deletar parceiro"
            if hasattr(response, 'error') and response.error:
                error_message = f"Erro ao deletar parceiro: {response.error}"
            logger.error(error_message)
            return jsonify({'success': False, 'error': error_message}), 500
            
    except Exception as e:
        logger.error(f"Erro ao deletar parceiro: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/parceiros/delete-batch', methods=['POST'])
@login_required
def delete_partners_batch():
    """Rota para deletar múltiplos parceiros em lote."""
    try:
        logger.debug("Iniciando deleção em lote de parceiros")
        
        # Obter IDs dos parceiros do JSON da requisição
        data = request.get_json()
        partner_ids = data.get('partner_ids', [])
        
        if not partner_ids:
            return jsonify({'success': False, 'error': 'Nenhum parceiro selecionado'}), 400
            
        logger.debug(f"IDs dos parceiros a serem deletados: {partner_ids}")
        
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        # Deletar parceiros em lote
        response = supabase.table('parceiros_tecnicos').delete().in_('id', partner_ids).execute()
        
        if response.data:
            deleted_count = len(response.data)
            logger.info(f"{deleted_count} parceiros deletados com sucesso")
            
            # Criar notificação
            user_id = session.get('user_id')
            create_notification(
                user_id=user_id,
                title='Parceiros Deletados',
                message=f'{deleted_count} parceiros foram removidos com sucesso.',
                type='warning'
            )
            
            return jsonify({
                'success': True,
                'deleted_count': deleted_count
            })
        else:
            error_message = "Erro ao deletar parceiros"
            if hasattr(response, 'error') and response.error:
                error_message = f"Erro ao deletar parceiros: {response.error}"
            logger.error(error_message)
            return jsonify({'success': False, 'error': error_message}), 500
            
    except Exception as e:
        logger.error(f"Erro ao deletar parceiros em lote: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500 

# Função para garantir que as tabelas necessárias existam
def ensure_tables_exist():
    """Verifica e cria as tabelas necessárias se não existirem."""
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            logger.error("Cliente Supabase não está inicializado")
            return False
            
        # Verificar e criar tabela user_last_checks se não existir
        try:
            # Verificar se a tabela existe executando uma consulta simples
            supabase.table('user_last_checks').select('*').limit(1).execute()
        except Exception as table_error:
            # Se a tabela não existir, criar
            if "relation \"user_last_checks\" does not exist" in str(table_error):
                logger.info("Criando tabela user_last_checks...")
                
                # Usar SQL direto para criar a tabela
                sql = """
                CREATE TABLE IF NOT EXISTS user_last_checks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL,
                    last_check_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                """
                
                supabase.rpc('exec_sql', {'query': sql}).execute()
                logger.info("Tabela user_last_checks criada com sucesso")
                
        return True
    except Exception as e:
        logger.error(f"Erro ao verificar/criar tabelas: {str(e)}", exc_info=True)
        return False

# Variável para controlar se a inicialização já foi executada
_initialization_done = False

@admin_bp.before_request
def initialize_app():
    """Inicializa o aplicativo, garantindo que as tabelas necessárias existam."""
    global _initialization_done
    
    # Executar apenas uma vez
    if not _initialization_done:
        ensure_tables_exist()
        _initialization_done = True 

# --- Rotas de Configuração do Usuário ---

@admin_bp.route('/perfil')
@login_required
def perfil():
    """Rota para exibir e editar o perfil do usuário."""
    try:
        supabase = SupabaseClient.get_client()
        user_id = session.get('user_id')
        
        # Buscar dados atualizados do usuário
        user_response = supabase.table('admin_users').select("*").eq('id', user_id).limit(1).execute()
        if user_response.data and len(user_response.data) > 0:
            user = user_response.data[0]
            return render_template('admin/perfil.html', user=user)
        else:
            flash('Erro ao carregar dados do usuário.', 'danger')
            return redirect(url_for('admin.dashboard'))
            
    except Exception as e:
        logger.error(f"Erro ao carregar perfil: {str(e)}", exc_info=True)
        flash('Erro ao carregar perfil.', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/seguranca')
@login_required
def seguranca():
    """Rota para configurações de segurança."""
    return render_template('admin/seguranca.html')

@admin_bp.route('/notificacoes-config')
@login_required
def notificacoes_config():
    """Rota para configurações de notificações."""
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Usuário não autenticado.', 'danger')
            return redirect(url_for('admin.login'))

        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
        
        # Buscar preferências do usuário
        response = supabase.table('user_preferences').select("*").eq('user_id', user_id).limit(1).execute()
        
        # Se não existir preferências, criar um registro padrão
        if not response.data:
            default_preferences = {
                'user_id': user_id,
                'notification_preferences': ['novos_parceiros', 'atualizacoes_status', 'notif_popup', 'notif_barra_lateral'],
                'theme': 'claro'
            }
            response = supabase.table('user_preferences').insert(default_preferences).execute()
            preferences = default_preferences
        else:
            preferences = response.data[0]
        
        return render_template('admin/notificacoes_config.html', preferences=preferences)
    except Exception as e:
        logger.error(f"Erro ao carregar configurações de notificações: {str(e)}", exc_info=True)
        flash('Erro ao carregar configurações.', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/atualizar-notificacoes', methods=['POST'])
@login_required
def atualizar_notificacoes():
    """Rota para atualizar as preferências de notificação do usuário."""
    try:
        user_id = session.get('user_id')
        if not user_id:
            flash('Usuário não autenticado.', 'danger')
            return redirect(url_for('admin.login'))

        notificacoes = request.form.getlist('notificacoes[]')
        logger.debug(f"Notificações recebidas: {notificacoes}")

        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")

        # Buscar preferências existentes
        response = supabase.table('user_preferences').select("*").eq('user_id', user_id).limit(1).execute()
        
        if response.data:
            # Atualizar preferências existentes
            update_data = {
                'notification_preferences': notificacoes,
                'updated_at': datetime.now().isoformat()
            }
            response = supabase.table('user_preferences').update(update_data).eq('user_id', user_id).execute()
        else:
            # Criar novas preferências
            insert_data = {
                'user_id': user_id,
                'notification_preferences': notificacoes,
                'theme': 'claro'  # valor padrão
            }
            response = supabase.table('user_preferences').insert(insert_data).execute()

        if response.data:
            logger.info(f"Preferências de notificação atualizadas para o usuário {user_id}")
            flash('Preferências de notificação atualizadas com sucesso!', 'success')
        else:
            error_message = "Erro desconhecido ao atualizar preferências."
            if hasattr(response, 'error') and response.error:
                error_message = f"Erro ao atualizar preferências: {response.error}"
            raise Exception(error_message)

    except Exception as e:
        logger.error(f"Erro ao atualizar notificações: {str(e)}", exc_info=True)
        flash('Erro ao atualizar preferências de notificação.', 'danger')

    return redirect(url_for('admin.notificacoes_config'))

@admin_bp.route('/atualizar-perfil', methods=['POST'])
@login_required
def atualizar_perfil():
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        user_id = session.get('user_id')

        if not all([nome, email, user_id]):
            flash('Por favor, preencha todos os campos.', 'warning')
            return redirect(url_for('admin.perfil'))

        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")

        # Atualizar dados do usuário
        response = supabase.table('admin_users').update({
            'nome': nome,
            'email': email
        }).eq('id', user_id).execute()

        if response.data:
            # Atualizar dados na sessão
            session['user_name'] = nome
            session['user_email'] = email
            flash('Perfil atualizado com sucesso!', 'success')
        else:
            flash('Erro ao atualizar perfil.', 'danger')

    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {str(e)}", exc_info=True)
        flash('Erro ao atualizar perfil.', 'danger')

    return redirect(url_for('admin.perfil'))

@admin_bp.route('/atualizar-senha', methods=['POST'])
@login_required
def atualizar_senha():
    try:
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        user_id = session.get('user_id')

        if not all([senha_atual, nova_senha, confirmar_senha]):
            flash('Por favor, preencha todos os campos.', 'warning')
            return redirect(url_for('admin.seguranca'))

        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'warning')
            return redirect(url_for('admin.seguranca'))

        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")

        # Verificar senha atual
        user_response = supabase.table('admin_users').select("password_hash").eq('id', user_id).execute()
        if not user_response.data:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('admin.seguranca'))

        password_hash = user_response.data[0]['password_hash']
        if not verify_password(senha_atual, password_hash):
            flash('Senha atual incorreta.', 'danger')
            return redirect(url_for('admin.seguranca'))

        # Atualizar senha
        new_password_hash = generate_password_hash(nova_senha, method='pbkdf2:sha256')
        response = supabase.table('admin_users').update({
            'password_hash': new_password_hash
        }).eq('id', user_id).execute()

        if response.data:
            flash('Senha atualizada com sucesso!', 'success')
        else:
            flash('Erro ao atualizar senha.', 'danger')

    except Exception as e:
        logger.error(f"Erro ao atualizar senha: {str(e)}", exc_info=True)
        flash('Erro ao atualizar senha.', 'danger')

    return redirect(url_for('admin.seguranca'))

@admin_bp.route('/notifications/list')
@login_required
def list_notifications():
    """Rota para obter a lista de notificações em formato JSON."""
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            return jsonify({'error': 'Erro de conexão com o banco de dados', 'notifications': []}), 500
            
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuário não autenticado', 'notifications': []}), 401
        
        # Buscar notificações não lidas do usuário, ordenadas por data
        response = supabase.table('notifications') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('read', False) \
            .order('created_at', desc=True) \
            .limit(5) \
            .execute()
            
        if not hasattr(response, 'data'):
            return jsonify({'error': 'Resposta inválida do banco de dados', 'notifications': []}), 500
            
        notifications = response.data if response.data else []
        
        # Log para debug
        logger.debug(f"Notificações encontradas: {notifications}")
        
        return jsonify(notifications)
    except Exception as e:
        logger.error(f"Erro ao listar notificações: {str(e)}", exc_info=True)
        return jsonify({'error': str(e), 'notifications': []}), 500 

# --- Rotas do Modo Desenvolvedor ---

@admin_bp.route('/developer')
@login_required
def developer():
    """Rota para a página de ferramentas de desenvolvimento."""
    return render_template('admin/developer.html')

@admin_bp.route('/developer/status')
@login_required
def developer_status():
    """Retorna o status atual do modo debug."""
    return jsonify({
        'debug': logger.getEffectiveLevel() == logging.DEBUG
    })

@admin_bp.route('/developer/toggle-debug', methods=['POST'])
@login_required
def toggle_debug():
    """Ativa/desativa o modo debug."""
    try:
        data = request.get_json()
        debug = data.get('debug', False)
        
        # Configurar nível de log
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao alternar modo debug: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/developer/gerar-dados', methods=['POST'])
@login_required
def gerar_dados_teste():
    """Funcionalidade removida."""
    return jsonify({
        'success': False,
        'message': 'Funcionalidade de geração de dados de teste foi removida'
    }), 404

@admin_bp.route('/developer/gerar-parceiros-teste', methods=['POST'])
@login_required
def gerar_parceiros_teste():
    """Gera parceiros técnicos de teste para desenvolvimento e testes."""
    try:
        # Validar dados da requisição
        data = request.get_json()
        if not data or 'parceiros' not in data:
            return jsonify({
                'success': False,
                'message': 'Dados inválidos na requisição'
            }), 400
            
        parceiros = data.get('parceiros', [])
        if not parceiros or not isinstance(parceiros, list):
            return jsonify({
                'success': False,
                'message': 'Lista de parceiros inválida'
            }), 400
            
        if len(parceiros) > 20:
            return jsonify({
                'success': False,
                'message': 'Número máximo de parceiros excedido (máx: 20)'
            }), 400
            
        # Conectar ao Supabase
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        # Converter dados e inserir no banco
        parceiros_inseridos = 0
        for parceiro in parceiros:
            # Marcar como dado de teste
            parceiro['is_test_data'] = True
            
            # Inserir no banco
            response = supabase.table('parceiros_tecnicos').insert(parceiro).execute()
            if response.data:
                parceiros_inseridos += 1
                logger.debug(f"Parceiro de teste inserido: {parceiro['nome_completo']}")
            else:
                logger.warning(f"Falha ao inserir parceiro de teste: {parceiro['nome_completo']}")
                
        # Registrar no log
        logger.info(f"{parceiros_inseridos} parceiros de teste inseridos com sucesso")
        
        # Criar notificação para o usuário
        user_id = session.get('user_id')
        create_notification(
            user_id=user_id,
            title='Dados de Teste Gerados',
            message=f'{parceiros_inseridos} parceiros técnicos de teste foram gerados com sucesso.',
            type='info'
        )
        
        return jsonify({
            'success': True,
            'message': f'{parceiros_inseridos} parceiros de teste inseridos com sucesso',
            'count': parceiros_inseridos
        })
    except Exception as e:
        logger.error(f"Erro ao gerar parceiros de teste: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar parceiros de teste: {str(e)}'
        }), 500

@admin_bp.route('/developer/limpar-dados', methods=['POST'])
@login_required
def limpar_dados_teste():
    """Funcionalidade removida."""
    return jsonify({
        'success': False,
        'message': 'Funcionalidade de limpeza de dados de teste foi removida'
    }), 404

@admin_bp.route('/developer/limpar-parceiros-teste', methods=['POST'])
@login_required
def limpar_parceiros_teste():
    """Remove todos os parceiros técnicos marcados como dados de teste."""
    try:
        # Conectar ao Supabase
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        # Deletar todos os parceiros marcados como teste
        response = supabase.table('parceiros_tecnicos').delete().eq('is_test_data', True).execute()
        
        if response.data:
            registros_removidos = len(response.data)
            logger.info(f"{registros_removidos} parceiros de teste removidos com sucesso")
            
            # Criar notificação para o usuário
            user_id = session.get('user_id')
            create_notification(
                user_id=user_id,
                title='Dados de Teste Removidos',
                message=f'{registros_removidos} parceiros técnicos de teste foram removidos com sucesso.',
                type='warning'
            )
            
            return jsonify({
                'success': True,
                'message': f'{registros_removidos} parceiros de teste removidos com sucesso',
                'count': registros_removidos
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Nenhum parceiro de teste encontrado para remover',
                'count': 0
            })
    except Exception as e:
        logger.error(f"Erro ao limpar parceiros de teste: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro ao limpar parceiros de teste: {str(e)}'
        }), 500

@admin_bp.route('/developer/configurar-logs', methods=['POST'])
@login_required
def configurar_logs():
    """Configura o nível dos logs do sistema."""
    try:
        data = request.get_json()
        level = data.get('level', 'INFO')
        
        # Mapear nível de log
        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        
        logger.setLevel(log_levels.get(level, logging.INFO))
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao configurar logs: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/developer/visualizar-logs')
@login_required
def visualizar_logs():
    """Retorna os logs mais recentes do sistema."""
    try:
        # Implementar lógica para ler logs do arquivo
        log_file = 'logs/app.log'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.readlines()[-50:]  # Últimas 50 linhas
        
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        logger.error(f"Erro ao visualizar logs: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/developer/testar-db')
@login_required
def testar_db():
    """Testa a conexão com o banco de dados."""
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        # Fazer uma consulta simples
        response = supabase.table('admin_users').select("count", count='exact').execute()
        
        return jsonify({
            'success': True,
            'total_users': response.count if hasattr(response, 'count') else 0
        })
    except Exception as e:
        logger.error(f"Erro ao testar banco de dados: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/developer/verificar-estrutura')
@login_required
def verificar_estrutura():
    """Verifica a estrutura das tabelas no banco de dados."""
    try:
        supabase = SupabaseClient.get_client()
        if not supabase:
            raise Exception("Cliente Supabase não inicializado")
            
        tabelas = [
            'admin_users',
            'parceiros_tecnicos',
            'notifications',
            'user_preferences',
            'user_last_checks'
        ]
        
        status_tabelas = []
        for tabela in tabelas:
            try:
                response = supabase.table(tabela).select("count", count='exact').execute()
                status = 'OK' if hasattr(response, 'count') else 'Erro'
            except Exception as table_error:
                status = f'Erro: {str(table_error)}'
            
            status_tabelas.append({
                'nome': tabela,
                'status': status
            })
        
        return jsonify({
            'success': True,
            'tabelas': status_tabelas
        })
    except Exception as e:
        logger.error(f"Erro ao verificar estrutura: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/developer/verificar-cache')
@login_required
def verificar_cache():
    """Verifica o status do cache."""
    try:
        # Implementar verificação de cache
        return jsonify({
            'success': True,
            'uso': random.randint(20, 80),  # Exemplo
            'itens': random.randint(100, 1000)  # Exemplo
        })
    except Exception as e:
        logger.error(f"Erro ao verificar cache: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/developer/limpar-cache', methods=['POST'])
@login_required
def limpar_cache():
    """Limpa o cache do sistema."""
    try:
        # Implementar limpeza de cache
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/developer/verificar-sessoes')
@login_required
def verificar_sessoes():
    """Verifica as sessões ativas no sistema."""
    try:
        # Implementar verificação de sessões
        sessoes_exemplo = [
            {
                'usuario': session.get('user_name', 'Usuário'),
                'ultima_atividade': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        
        return jsonify({
            'success': True,
            'total': len(sessoes_exemplo),
            'sessoes': sessoes_exemplo
        })
    except Exception as e:
        logger.error(f"Erro ao verificar sessões: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/developer/listar-rotas')
@login_required
def listar_rotas():
    """Lista todas as rotas registradas no sistema."""
    try:
        from flask import current_app
        rotas = []
        
        for rule in current_app.url_map.iter_rules():
            # Filtrar apenas as rotas do admin
            if rule.rule.startswith('/admin'):
                rotas.append({
                    'url': rule.rule,
                    'metodo': ','.join(rule.methods),
                    'funcao': rule.endpoint
                })
        
        return jsonify({
            'success': True,
            'total': len(rotas),
            'rotas': rotas
        })
    except Exception as e:
        logger.error(f"Erro ao listar rotas: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500 