import os
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from supabase import create_client, Client
import logging
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import hashlib
import base64
from .logger_config import setup_logger
from config import Config

# Configuração do logger
logger = setup_logger()

# Blueprint do Admin
admin_bp = Blueprint('admin', __name__,
                    url_prefix='/adm',
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='/adm/static')

# Filtros para templates
@admin_bp.app_template_filter('datetime')
def format_datetime(value):
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
    return value.strftime('%d/%m/%Y %H:%M')

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
            return render_template('adm/register.html')

        supabase = SupabaseClient.get_client()
        if not supabase:
            logger.error("Cliente Supabase não está inicializado")
            flash('Erro na conexão com o banco de dados.', 'danger')
            return render_template('adm/register.html')

        try:
            logger.debug("Verificando se o email já existe")
            existing_user = supabase.table('admin_users').select("id").eq('email', email).execute()
            logger.debug(f"Resposta da verificação de email: {existing_user}")
            
            if existing_user.data:
                logger.warning(f"Email {email} já está cadastrado")
                flash('Este e-mail já está cadastrado.', 'warning')
                return render_template('adm/register.html')

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

    return render_template('adm/register.html')

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
            return render_template('adm/login.html')

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
    
    return render_template('adm/login.html')

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
    parceiros_data = []
    total_parceiros = 0
    parceiros_pendentes = 0
    parceiros_aprovados = 0
    parceiros_rejeitados = 0
    novos_parceiros_mes = 0
    ultimos_6_meses = []
    dados_cadastros_mes = []
    dados_status = [0, 0, 0]  # [pendentes, aprovados, rejeitados]
    especialidades = []
    cidades = []

    supabase = SupabaseClient.get_client()
    logger.debug(f"Iniciando dashboard - user_id: {session.get('user_id')}")

    if not supabase:
        logger.error("Cliente Supabase não está inicializado")
        flash('Erro na conexão com o banco de dados.', 'danger')
        return render_template('adm/dashboard.html',
                             parceiros=parceiros_data,
                             total_parceiros=total_parceiros,
                             parceiros_pendentes=parceiros_pendentes,
                             parceiros_aprovados=parceiros_aprovados,
                             novos_parceiros_mes=novos_parceiros_mes,
                             labels_meses=ultimos_6_meses,
                             dados_cadastros_mes=dados_cadastros_mes,
                             dados_status=dados_status,
                             especialidades=especialidades,
                             cidades=cidades,
                             error_db=True,
                             current_year=2024)

    try:
        # Aplicar filtros se existirem
        status_filter = request.args.get('status')
        especialidade_filter = request.args.get('especialidade')
        cidade_filter = request.args.get('cidade')
        search = request.args.get('search')

        logger.debug(f"Filtros aplicados - Status: {status_filter}, Especialidade: {especialidade_filter}, Cidade: {cidade_filter}, Busca: {search}")

        # Consulta base
        query = supabase.table('parceiros_tecnicos').select("*")
        
        # Aplicar filtros
        if status_filter:
            query = query.eq('status', status_filter)
        if especialidade_filter:
            query = query.contains('especialidades', [especialidade_filter])
        if cidade_filter:
            query = query.eq('cidade', cidade_filter)
        if search:
            query = query.or_(f"nome.ilike.%{search}%,email.ilike.%{search}%,cidade.ilike.%{search}%")

        # Executar consulta
        response = query.execute()
        logger.debug(f"Resposta do Supabase (parceiros): {response}")

        if not hasattr(response, 'data'):
            logger.error("Resposta do Supabase não contém 'data'")
            raise Exception("Formato de resposta inválido")

        parceiros_data = response.data or []
        logger.debug(f"Número de parceiros encontrados: {len(parceiros_data)}")
        
        # Log detalhado dos dados de cada parceiro
        for parceiro in parceiros_data:
            logger.debug(f"Dados do parceiro: {json.dumps(parceiro, indent=2, ensure_ascii=False)}")
        
        # Garantir que todos os campos necessários existam e tenham valores padrão
        for parceiro in parceiros_data:
            if not parceiro.get('status'):
                parceiro['status'] = 'Pendente'
            if not parceiro.get('nome'):
                parceiro['nome'] = parceiro.get('nome_completo', 'Nome não informado')
            if not parceiro.get('email'):
                parceiro['email'] = 'Email não informado'
            if not parceiro.get('cidade'):
                parceiro['cidade'] = 'Cidade não informada'
            if not parceiro.get('especialidades') or not isinstance(parceiro['especialidades'], list):
                parceiro['especialidades'] = []
            if not parceiro.get('created_at'):
                parceiro['created_at'] = datetime.now().isoformat()
        
            parceiros_data.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Calcular estatísticas
        total_parceiros = len(parceiros_data)
        parceiros_pendentes = len([p for p in parceiros_data if p.get('status', '').lower() == 'pendente'])
        parceiros_aprovados = len([p for p in parceiros_data if p.get('status', '').lower() == 'aprovado'])
        parceiros_rejeitados = len([p for p in parceiros_data if p.get('status', '').lower() == 'rejeitado'])

        logger.debug(f"Estatísticas calculadas:")
        logger.debug(f"Total: {total_parceiros}")
        logger.debug(f"Pendentes: {parceiros_pendentes}")
        logger.debug(f"Aprovados: {parceiros_aprovados}")
        logger.debug(f"Rejeitados: {parceiros_rejeitados}")

        # Calcular novos parceiros este mês
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        inicio_mes = inicio_mes.astimezone()  # Converter para timezone-aware
        
        novos_parceiros_mes = len([
            p for p in parceiros_data 
            if p.get('created_at') and 
            datetime.fromisoformat(p.get('created_at').replace('Z', '+00:00')) >= inicio_mes
        ])

        # Preparar dados para o gráfico de cadastros por mês
        meses_ptbr = {
            'January': 'Janeiro',
            'February': 'Fevereiro',
            'March': 'Março',
            'April': 'Abril',
            'May': 'Maio',
            'June': 'Junho',
            'July': 'Julho',
            'August': 'Agosto',
            'September': 'Setembro',
            'October': 'Outubro',
            'November': 'Novembro',
            'December': 'Dezembro'
        }
        
        # Calcular os últimos 6 meses corretamente
        hoje = datetime.now()
        ultimos_6_meses = []
        dados_cadastros_mes = []
        
        for i in range(5, -1, -1):
            # Calcular o primeiro dia do mês
            data = hoje.replace(day=1) - timedelta(days=1)  # Último dia do mês anterior
            data = data.replace(day=1)  # Primeiro dia do mês
            data = data - timedelta(days=30*i)  # Voltar i meses
            
            mes_en = data.strftime('%B')
            mes_ptbr = meses_ptbr.get(mes_en, mes_en)
            ultimos_6_meses.append(f"{mes_ptbr}/{data.strftime('%y')}")
            
            inicio_mes = data.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i > 0:
                fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            else:
                fim_mes = hoje  # Para o mês atual, usar a data atual como fim
            
            # Converter para timezone-aware
            inicio_mes = inicio_mes.astimezone()
            fim_mes = fim_mes.astimezone()
            
            count = len([
                p for p in parceiros_data 
                if p.get('created_at') and 
                inicio_mes <= datetime.fromisoformat(p.get('created_at').replace('Z', '+00:00')) <= fim_mes
            ])
            dados_cadastros_mes.append(count)
            logger.debug(f"Mês: {mes_ptbr}, Início: {inicio_mes}, Fim: {fim_mes}, Contagem: {count}")

        # Coletar todas as especialidades únicas
        especialidades = set()
        for parceiro in parceiros_data:
            if isinstance(parceiro.get('especialidades'), list):
                especialidades.update(esp for esp in parceiro.get('especialidades') if esp)

        especialidades = sorted(list(especialidades))
        logger.debug(f"Especialidades encontradas: {especialidades}")

        # Coletar todas as cidades únicas
        cidades = sorted(list(set(p.get('cidade') for p in parceiros_data if p.get('cidade'))))
        logger.debug(f"Cidades encontradas: {cidades}")

        # Preparar dados para o gráfico de status
        dados_status = [parceiros_pendentes, parceiros_aprovados, parceiros_rejeitados]
        logger.debug(f"Dados de status: Pendentes={parceiros_pendentes}, Aprovados={parceiros_aprovados}, Rejeitados={parceiros_rejeitados}")

        return render_template('adm/dashboard.html',
                             parceiros=parceiros_data,
                             total_parceiros=total_parceiros,
                             parceiros_pendentes=parceiros_pendentes,
                             parceiros_aprovados=parceiros_aprovados,
                             novos_parceiros_mes=novos_parceiros_mes,
                             labels_meses=ultimos_6_meses,
                             dados_cadastros_mes=dados_cadastros_mes,
                             dados_status=dados_status,
                             especialidades=especialidades,
                             cidades=cidades,
                             error_db=False,
                             current_year=2024)

    except Exception as e:
        logger.error(f"Erro ao buscar dados dos parceiros: {str(e)}", exc_info=True)
        flash(f'Erro ao carregar dados: {str(e)}', 'danger')
    return render_template('adm/dashboard.html',
                         parceiros=parceiros_data,
                             total_parceiros=total_parceiros,
                             parceiros_pendentes=parceiros_pendentes,
                             parceiros_aprovados=parceiros_aprovados,
                             novos_parceiros_mes=novos_parceiros_mes,
                             labels_meses=ultimos_6_meses,
                             dados_cadastros_mes=dados_cadastros_mes,
                             dados_status=dados_status,
                             especialidades=especialidades,
                             cidades=cidades,
                             error_db=True,
                         current_year=2024)

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
            return render_template('adm/partner_details.html', parceiro=parceiro)
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
                error_message = f"Erro ao atualizar status: {response.error.message}"
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
        user_id = session.get('user_id')
        
        # Atualizar status do parceiro
        response = supabase.table('parceiros_tecnicos') \
            .update({'status': 'Aprovado'}) \
            .eq('id', partner_id) \
            .execute()
            
        if response.data:
            # Criar notificação
            create_notification(
                user_id=user_id,
                title='Parceiro Aprovado',
                message=f'O parceiro técnico foi aprovado com sucesso.',
                type='success'
            )
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Parceiro não encontrado'}), 404
    except Exception as e:
        logger.error(f"Erro ao aprovar parceiro: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/rejeitar-parceiro/<partner_id>', methods=['POST'])
@login_required
def rejeitar_parceiro(partner_id):
    try:
        supabase = SupabaseClient.get_client()
        user_id = session.get('user_id')
        
        # Atualizar status do parceiro
        response = supabase.table('parceiros_tecnicos') \
            .update({'status': 'Rejeitado'}) \
            .eq('id', partner_id) \
            .execute()
            
        if response.data:
            # Criar notificação
            create_notification(
                user_id=user_id,
                title='Parceiro Rejeitado',
                message=f'O parceiro técnico foi rejeitado.',
                type='danger'
            )
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Parceiro não encontrado'}), 404
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
        
        return render_template('adm/notifications.html', notifications=notifications)
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
        user_id = session.get('user_id')
        notification_ids = request.json.get('notification_ids', [])
        
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
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Erro ao marcar notificações como lidas: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

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