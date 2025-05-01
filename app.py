from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from datetime import datetime
from adm.routes import admin_bp
from adm.logger_config import setup_logger

# Configurar logger
logger = setup_logger()

# Criar a aplicação Flask
# Removido template_folder='.' para permitir que os Blueprints gerenciem seus templates
app = Flask(__name__, 
           static_folder='static',
           static_url_path='/static')

# Configurar chave secreta para cookies e sessões
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here') # É crucial ter uma chave secreta!

# Registrar o blueprint do admin
logger.debug("Registrando blueprint do admin")
app.register_blueprint(admin_bp)

# Rota raiz redireciona para o login do admin
@app.route('/')
def index():
    logger.debug("Acessando rota raiz")
    return redirect(url_for('admin.login'))

# Executa o servidor quando o arquivo é executado diretamente
if __name__ == '__main__':
    logger.info("Iniciando servidor Flask")
    # Inicia o servidor em modo debug
    print("Servidor iniciado! Acesse http://localhost:5000/adm")
    app.run(debug=True, host='0.0.0.0', port=5000) 