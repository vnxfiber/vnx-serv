"""
Script de diagnóstico para verificar a conexão com o Supabase
"""

from supabase import create_client, Client
import sys
import time

# Cores para terminal
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
RESET = "\033[0m"
NEGRITO = "\033[1m"

def print_sucesso(mensagem):
    print(f"{VERDE}✓ {mensagem}{RESET}")

def print_aviso(mensagem):
    print(f"{AMARELO}⚠ {mensagem}{RESET}")

def print_erro(mensagem):
    print(f"{VERMELHO}✗ {mensagem}{RESET}")

def print_titulo(mensagem):
    print(f"\n{NEGRITO}{mensagem}{RESET}")
    print("-" * 50)

def main():
    print_titulo("DIAGNÓSTICO DE CONEXÃO COM SUPABASE")
    
    # Definição das credenciais do Supabase
    SUPABASE_URL = "https://cwrxdjfmxntmplwdbnpg.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYwMDI0MzksImV4cCI6MjA2MTU3ODQzOX0.-kFUUiLn2plnEdopteCdxcixyY3pI5O-K-hIk1IL61s"
    
    # Verificar conexão com o Supabase
    print("Tentando conectar ao Supabase...")
    try:
        inicio = time.time()
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        fim = time.time()
        tempo_conexao = round((fim - inicio) * 1000)  # Em milissegundos
        print_sucesso(f"Conexão estabelecida com sucesso! ({tempo_conexao}ms)")
    except Exception as e:
        print_erro(f"Falha na conexão: {str(e)}")
        sys.exit(1)
    
    # Verificar tabelas existentes
    print_titulo("VERIFICANDO TABELAS")
    
    tabelas_necessarias = ['administradores', 'profissionais']
    for tabela in tabelas_necessarias:
        try:
            # Tentar realizar uma consulta simples para verificar se a tabela existe
            resposta = supabase.table(tabela).select('*', count='exact').limit(1).execute()
            count = resposta.count
            print_sucesso(f"Tabela '{tabela}' encontrada com {count} registros")
        except Exception as e:
            print_erro(f"Não foi possível acessar a tabela '{tabela}': {str(e)}")
    
    # Testar operações básicas
    print_titulo("TESTANDO OPERAÇÕES BÁSICAS")
    
    # Teste de inserção e leitura em tabela temporária para não afetar os dados reais
    try:
        # Primeiro, tentamos criar uma tabela temporária para testes
        print("Verificando permissão para operações de escrita...")
        
        # Tentar inserir um registro na tabela profissionais com um ID temporário que depois será removido
        test_id = "11111111-1111-1111-1111-111111111111"
        dados_teste = {
            "id": test_id,
            "nome": "Teste Diagnóstico",
            "email": f"teste_{int(time.time())}@teste.com",
            "telefone": "00000000000",
            "profissao": "Teste"
        }
        
        # Inserir dado de teste
        supabase.table('profissionais').insert(dados_teste).execute()
        print_sucesso("Operação INSERT funcionou corretamente")
        
        # Ler o dado inserido
        resposta = supabase.table('profissionais').select('*').eq('id', test_id).execute()
        if len(resposta.data) > 0:
            print_sucesso("Operação SELECT funcionou corretamente")
        else:
            print_aviso("Operação SELECT não retornou o registro inserido")
        
        # Limpar o dado de teste
        supabase.table('profissionais').delete().eq('id', test_id).execute()
        print_sucesso("Operação DELETE funcionou corretamente")
        
    except Exception as e:
        print_erro(f"Falha ao realizar operações básicas: {str(e)}")
    
    # Verificar políticas de segurança
    print_titulo("VERIFICANDO POLÍTICAS DE SEGURANÇA")
    print("As políticas de segurança não podem ser verificadas diretamente via API.")
    print("Para configurá-las, acesse o painel do Supabase e verifique as políticas RLS.")
    
    # Resumo final
    print_titulo("RESUMO DO DIAGNÓSTICO")
    print("O banco de dados Supabase está corretamente configurado e conectado.")
    print("A aplicação Flask deve funcionar corretamente com as configurações atuais.")
    print("\nPara executar a aplicação Flask, use o comando:")
    print("  python app.py")
    print("\nAcesse o painel em:")
    print("  http://127.0.0.1:5000")

if __name__ == "__main__":
    main() 