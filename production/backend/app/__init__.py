from flask import Flask
from .admin.routes import admin_bp
from .admin.logger_config import setup_logger

# Configurar logger
logger = setup_logger()

# Criar a aplicação Flask
def create_app():
    app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')

    # Configurar chave secreta para cookies e sessões
    import os
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

    # Registrar o blueprint do admin
    logger.debug("Registrando blueprint do admin")
    app.register_blueprint(admin_bp)

    return app 