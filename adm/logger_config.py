import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    # Criar o diretório de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configurar o logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Formato detalhado para os logs
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s'
    )

    # Handler para arquivo
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # Limpar handlers existentes
    logger.handlers = []

    # Adicionar os novos handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Configurar logging para bibliotecas terceiras
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)

    return logger 