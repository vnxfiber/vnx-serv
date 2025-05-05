import os
import logging
from logging.handlers import RotatingFileHandler

# Configurar o diretório de logs
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Criar o logger
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

# Configurar formato do log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configurar handler para arquivo
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Configurar handler para console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Função para alterar o nível de log
def set_log_level(level):
    """
    Altera o nível de log.
    
    Args:
        level: Nível de log (logging.DEBUG, logging.INFO, etc.)
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level) 