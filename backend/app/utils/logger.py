import logging
import os
from datetime import datetime

# Criar diretório de logs se não existir
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configurar o logger
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# Criar formatador
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler para arquivo
log_file = os.path.join(log_dir, f'app.log')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Adicionar handlers ao logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Evitar propagação de logs duplicados
logger.propagate = False 