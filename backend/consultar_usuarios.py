import os
import sys
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
    print("\n=== Diagnóstico e Gestão de Usuários ===")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("----------------------------------------")
    
    # Tentar criar cliente Supabase
    try:
        print("\n1. Testando conexão com Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[OK] Conexão com Supabase estabelecida")
    except Exception as e:
        print(f"[ERRO] Erro ao conectar ao Supabase: {str(e)}")
        sys.exit(1)
    
    # Verificar tabela admin_users
    try:
        print("\n2. Verificando tabela admin_users...")
        response = supabase.table('admin_users').select('*').execute()
        users = response.data if response.data else []
        
        print(f"[OK] Encontrados {len(users)} usuários cadastrados:")
        for i, user in enumerate(users):
            print(f"   {i+1}. ID: {user.get('id')}, Email: {user.get('email')}, Criado em: {user.get('created_at')}")
        
        # Identificar usuários de teste
        test_users = [u for u in users if u.get('email', '').startswith('teste') or 
                     'teste' in u.get('email', '').lower() or 
                     u.get('email', '') in ['teste1@exemplo.com', 'teste2@exemplo.com', 'teste3@exemplo.com', 'teste4@exemplo.com', 'teste5@exemplo.com']]
        
        print(f"\n3. Identificados {len(test_users)} usuários de teste:")
        for i, user in enumerate(test_users):
            print(f"   {i+1}. ID: {user.get('id')}, Email: {user.get('email')}")
        
        if not test_users:
            print("   Nenhum usuário de teste identificado.")
            return
            
        # Verificar notificações
        print("\n4. Verificando notificações relacionadas aos usuários de teste...")
        has_notifications = False
        
        for user in test_users:
            user_id = user.get('id')
            notif_response = supabase.table('notifications').select('count', count='exact').eq('user_id', user_id).execute()
            notif_count = notif_response.count if hasattr(notif_response, 'count') else 0
            
            if notif_count > 0:
                has_notifications = True
                print(f"   [AVISO] Usuário {user.get('email')} (ID: {user_id}) tem {notif_count} notificações")
        
        if not has_notifications:
            print("   [OK] Nenhuma notificação encontrada para os usuários de teste")
        
        # Perguntar se deseja excluir os usuários de teste
        if test_users:
            choice = input("\nDeseja excluir os usuários de teste identificados? (s/n): ").lower()
            
            if choice == 's':
                print("\n5. Excluindo usuários de teste...")
                
                # Primeiro, excluir notificações relacionadas
                for user in test_users:
                    user_id = user.get('id')
                    
                    # Excluir notificações primeiro devido à restrição de chave estrangeira
                    notif_delete = supabase.table('notifications').delete().eq('user_id', user_id).execute()
                    deleted_notif = len(notif_delete.data) if notif_delete.data else 0
                    
                    if deleted_notif > 0:
                        print(f"   [OK] Excluídas {deleted_notif} notificações do usuário {user.get('email')}")
                    
                    # Agora excluir o usuário
                    user_delete = supabase.table('admin_users').delete().eq('id', user_id).execute()
                    
                    if user_delete.data and len(user_delete.data) > 0:
                        print(f"   [OK] Usuário {user.get('email')} excluído com sucesso!")
                    else:
                        print(f"   [ERRO] Falha ao excluir o usuário {user.get('email')}")
                
                print("\n[OK] Processo de limpeza concluído!")
            else:
                print("\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"[ERRO] Erro ao acessar dados: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 