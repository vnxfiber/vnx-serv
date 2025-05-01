import os

class Config:
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    
    # Configurações do Supabase
    SUPABASE_URL = 'https://cwrxdjfmxntmplwdbnpg.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    # Configurações de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
    LOG_FILE = 'logs/app.log'
    
    @staticmethod
    def init_app(app):
        # Criar diretório de logs se não existir
        os.makedirs('logs', exist_ok=True) 