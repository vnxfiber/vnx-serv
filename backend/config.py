import os

class Config:
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    
    # Configurações do Supabase
    SUPABASE_URL = 'https://cwrxdjfmxntmplwdbnpg.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    # Configurações de logging - uso simplificado para evitar problemas com permissões
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')  # Reduzido para WARNING para menos logs
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'  # Formato simplificado
    LOG_FILE = 'logs/app.log'
    LOG_MODE = 'a'  # Modo de anexação simples em vez de RotatingFileHandler
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # Ativar ou desativar logs
    LOG_TO_FILE = False  # Desabilitando completamente logs em arquivo
    LOG_TO_CONSOLE = True
    
    @staticmethod
    def init_app(app):
        # Criar diretório de logs se não existir
        if Config.LOG_TO_FILE:
            os.makedirs('logs', exist_ok=True) 