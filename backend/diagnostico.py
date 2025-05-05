import os
import sys
import json
from datetime import datetime

# Adiciona o diretório atual ao path para permitir importações locais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client
    print("[OK] Biblioteca Supabase instalada")
except ImportError:
    print("[ERRO] Biblioteca Supabase não encontrada. Execute: pip install supabase")
    sys.exit(1)

# Dados de conexão do Supabase
SUPABASE_URL = 'https://cwrxdjfmxntmplwdbnpg.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjAwMjQzOSwiZXhwIjoyMDYxNTc4NDM5fQ.wUCecHTnyEwSVoH_-ruIV4fIGibr0vNkGZPbTVBM8uY'

def main():
    print("\n=== Diagnóstico de Conexão e Tabelas do Supabase ===")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-----------------------------------------------------")
    
    # Tentar criar cliente Supabase
    try:
        print("\n1. Testando conexão com Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[OK] Conexão com Supabase estabelecida")
    except Exception as e:
        print(f"[ERRO] Erro ao conectar ao Supabase: {str(e)}")
        sys.exit(1)
    
    # Verificar tabela parceiros_tecnicos
    try:
        print("\n2. Verificando tabela parceiros_tecnicos...")
        response = supabase.table('parceiros_tecnicos').select('count', count='exact').execute()
        count = response.count if hasattr(response, 'count') else 0
        print(f"[OK] Tabela parceiros_tecnicos encontrada com {count} registros")
        
        # Verificar um registro existente para descobrir valores válidos de especialidades
        sample = supabase.table('parceiros_tecnicos').select('*').limit(1).execute()
        if sample.data and len(sample.data) > 0:
            registro = sample.data[0]
            print("\n3. Amostra de registro encontrado:")
            print(f"   ID: {registro.get('id')}")
            print(f"   Nome: {registro.get('nome_completo')}")
            print(f"   WhatsApp: {registro.get('whatsapp')} (Formato exato)")
            print(f"   Especialidades: {registro.get('especialidades')}")
            
            # Usar os valores do registro existente
            especialidades_validas = registro.get('especialidades', [])
            whatsapp_valido = registro.get('whatsapp')
            nome_valido = registro.get('nome_completo')
            
            if not especialidades_validas:
                especialidades_validas = ["Fibra Óptica"]  # valor padrão se não encontrar
            
            print(f"\n   Usando especialidades encontradas: {especialidades_validas}")
        else:
            print("\n   Nenhum registro encontrado para analisar especialidades")
            especialidades_validas = ["Fibra Óptica"]  # valor padrão
    except Exception as e:
        print(f"[ERRO] Erro ao acessar tabela parceiros_tecnicos: {str(e)}")
        sys.exit(1)
    
    # Testar inserção de um registro
    try:
        print("\n4. Testando inserção na tabela parceiros_tecnicos...")
        # Gerar um WhatsApp único baseado no formato válido
        hora_atual = datetime.now().strftime("%H%M%S")
        # Tentar um WhatsApp com o mesmo comprimento e formato do exemplo válido
        # Formato do exemplo: 98985503360
        if whatsapp_valido:
            comprimento = len(whatsapp_valido)
            prefixo = whatsapp_valido[:2]  # Código de área
            # Gerar um número com o mesmo tamanho, iniciando com o mesmo código de área
            ultimo_digitos = hora_atual + "123456789"
            whatsapp_unico = prefixo + ultimo_digitos[:comprimento-2]
        else:
            whatsapp_unico = "98985512345"  # Fallback similar ao exemplo
            
        # Garantir que o WhatsApp tenha exatamente o mesmo tamanho do exemplo
        if whatsapp_valido:
            whatsapp_unico = whatsapp_unico[:len(whatsapp_valido)]
        else:
            whatsapp_unico = whatsapp_unico[:11]  # 11 dígitos, o padrão brasileiro
        
        print(f"   WhatsApp original: {whatsapp_valido}")
        print(f"   WhatsApp gerado para teste: {whatsapp_unico}")
        print(f"   Comprimentos: original={len(whatsapp_valido) if whatsapp_valido else 'N/A'}, gerado={len(whatsapp_unico)}")
        
        test_data = {
            'nome_completo': nome_valido,
            'email': f'teste.{hora_atual}@exemplo.com',
            'whatsapp': whatsapp_unico,  # WhatsApp único
            'cidade': 'Sao Paulo',
            'estado': 'SP',
            'especialidades': especialidades_validas,
            'is_test_data': True
        }
        
        print(f"   Dados a inserir: {json.dumps(test_data, indent=2)}")
        
        insert_response = supabase.table('parceiros_tecnicos').insert(test_data).execute()
        
        if insert_response.data and len(insert_response.data) > 0:
            inserted_id = insert_response.data[0].get('id')
            print(f"[OK] Registro inserido com sucesso! ID: {inserted_id}")
            
            # Remover o registro de teste
            print("\n5. Removendo registro de teste...")
            delete_response = supabase.table('parceiros_tecnicos').delete().eq('id', inserted_id).execute()
            print(f"[OK] Registro removido com sucesso!")
        else:
            if hasattr(insert_response, 'error') and insert_response.error:
                print(f"[ERRO] Erro na inserção: {insert_response.error}")
            else:
                print(f"[ERRO] Erro desconhecido na inserção, sem detalhes disponíveis")
    except Exception as e:
        print(f"[ERRO] Erro ao testar inserção: {str(e)}")
    
    print("\n=== Diagnóstico concluído ===")

if __name__ == "__main__":
    main() 