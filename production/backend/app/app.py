from flask import redirect, url_for
from . import create_app, logger

app = create_app()

# Rota raiz redireciona para o login do admin
@app.route('/')
def index():
    logger.debug("Acessando rota raiz")
    return redirect(url_for('admin.login'))

# Executa o servidor quando o arquivo é executado diretamente
if __name__ == '__main__':
    logger.info("Iniciando servidor Flask")
    # Inicia o servidor em modo debug
    print("Servidor iniciado! Acesse http://localhost:5000/admin")
    app.run(debug=True, host='0.0.0.0', port=5000) 