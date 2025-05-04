import logging
import sys
import os
import sys

# Adicionar o diretório raiz ao sys.path para permitir importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from backend.config import Config
except ImportError:
    # Fallback para importação relativa se a absoluta falhar
    import importlib.util
    import os
    
    # Carregar o módulo config.py diretamente
    spec = importlib.util.spec_from_file_location(
        "config", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config.py'))
    )
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    Config = config_module.Config

def setup_logger():
    # Criar o diretório de logs se não existir
    if Config.LOG_TO_FILE and not os.path.exists('logs'):
        os.makedirs('logs')

    # Configurar o logger principal
    logger = logging.getLogger()
    
    # Definir nível de log a partir da configuração
    log_level = getattr(logging, Config.LOG_LEVEL)
    logger.setLevel(log_level)

    # Formato simplificado para os logs
    formatter = logging.Formatter(Config.LOG_FORMAT)

    # Limpar handlers existentes
    logger.handlers = []

    # Handler para arquivo (se ativado)
    if Config.LOG_TO_FILE:
        # Usar FileHandler simples em vez de RotatingFileHandler para evitar problemas
        file_handler = logging.FileHandler(
            Config.LOG_FILE,
            mode=Config.LOG_MODE
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Handler para console (se ativado)
    if Config.LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Configurar logging para bibliotecas terceiras (níveis mais altos para reduzir logs)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('h2').setLevel(logging.WARNING)
    logging.getLogger('hpack').setLevel(logging.WARNING)

    return logger 