from app.app import app

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")
    print("Acesse http://localhost:5000 para utilizar a aplicação")
    app.run(debug=True, port=5000) 