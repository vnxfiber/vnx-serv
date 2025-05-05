#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import random
from datetime import datetime

# Adiciona o diretório pai ao path para permitir importações locais
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
    print("[✓] Biblioteca Supabase instalada")
except ImportError:
    print("[✗] Biblioteca Supabase não encontrada. Execute: pip install supabase")
    sys.exit(1)

# Dados de conexão do Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://cwrxdjfmxntmplwdbnpg.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjAwMjQzOSwiZXhwIjoyMDYxNTc4NDM5fQ.wUCecHTnyEwSVoH_-ruIV4fIGibr0vNkGZPbTVBM8uY')

def conectar_supabase():
    """Estabelece uma conexão com o Supabase e executa um teste básico."""
    try:
        print("\n[1] Testando conexão com Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Testar a conexão com uma consulta simples
        response = supabase.table('admin_users').select("count", count='exact').limit(1).execute()
        count = response.count if hasattr(response, 'count') else 0
        
        print(f"[✓] Conexão estabelecida com sucesso! ({count} usuários encontrados)")
        return supabase
    except Exception as e:
        print(f"[✗] Erro ao conectar ao Supabase: {str(e)}")
        sys.exit(1)

def verificar_tabela_parceiros(supabase):
    """Verifica se a tabela parceiros_tecnicos existe e sua estrutura."""
    try:
        print("\n[2] Verificando tabela de parceiros...")
        
        # Testar se a tabela existe
        response = supabase.table('parceiros_tecnicos').select("count", count='exact').limit(1).execute()
        
        total_parceiros = response.count if hasattr(response, 'count') else 0
        print(f"[✓] Tabela parceiros_tecnicos encontrada ({total_parceiros} registros)")
        
        # Obter um registro para analisar a estrutura
        if total_parceiros > 0:
            response = supabase.table('parceiros_tecnicos').select("*").limit(1).execute()
            if response.data:
                campos = list(response.data[0].keys())
                print(f"[✓] Campos encontrados: {', '.join(campos)}")
                return True, campos
            else:
                print("[!] Nenhum registro encontrado para analisar estrutura")
        
        # Se não há dados, verificar apenas se a tabela existe
        return True, []
        
    except Exception as e:
        print(f"[✗] Erro ao verificar tabela parceiros_tecnicos: {str(e)}")
        return False, []

def criar_parceiro_teste(supabase):
    """Cria um parceiro técnico de teste para diagnóstico."""
    try:
        print("\n[3] Criando parceiro técnico de teste...")
        
        # Primeiro, verificar exemplos válidos no banco de dados
        response_sample = supabase.table('parceiros_tecnicos').select("*").limit(1).execute()
        especialidades_validas = []
        whatsapp_exemplo = ""
        nome_exemplo = ""
        
        if response_sample.data and len(response_sample.data) > 0:
            # Usar dados de um registro existente como referência
            parceiro_exemplo = response_sample.data[0]
            
            # Verificar especialidades
            especialidades_amostra = parceiro_exemplo.get('especialidades', [])
            if especialidades_amostra:
                print(f"[→] Especialidades válidas encontradas: {especialidades_amostra}")
                especialidades_validas = especialidades_amostra[:2]  # Usar até 2 especialidades da amostra
            
            # Verificar formato WhatsApp
            whatsapp_exemplo = parceiro_exemplo.get('whatsapp', '')
            if whatsapp_exemplo:
                print(f"[→] Formato WhatsApp válido encontrado: {whatsapp_exemplo}")
                
            # Verificar formato de nome válido
            nome_exemplo = parceiro_exemplo.get('nome_completo', '')
            if nome_exemplo:
                print(f"[→] Nome válido encontrado: {nome_exemplo}")
        
        # Se não encontrou nenhuma especialidade válida, usar valores padrão
        if not especialidades_validas:
            especialidades_validas = ["Solucoes ISP", "Telefonia VoIP"]
            print(f"[→] Usando especialidades padrão: {especialidades_validas}")
        
        # Gerar um WhatsApp no formato correto
        if whatsapp_exemplo:
            # Usar o mesmo formato/comprimento do exemplo encontrado
            timestamp = datetime.now().strftime("%H%M%S")
            whatsapp_digitos = ''.join(c for c in whatsapp_exemplo if c.isdigit())
            whatsapp_formato = whatsapp_digitos[:5] + timestamp.ljust(len(whatsapp_digitos) - 5, '9')
            whatsapp_formato = whatsapp_formato[:len(whatsapp_digitos)]
        else:
            # Fallback para um formato que parece funcionar na maioria dos casos
            whatsapp_formato = "98985503360"  # Formato encontrado anteriormente no diagnóstico
        
        # Gerar dados aleatórios para o teste
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_id = random.randint(1000, 9999)
        
        # Usar um nome simples sem caracteres especiais
        nome_teste = "Teste API"
        
        # Criar parceiro com dados válidos
        parceiro_teste = {
            'nome_completo': nome_teste,
            'email': f"diagnostico.{random_id}@teste.com",
            'whatsapp': whatsapp_formato,
            'estado': 'MA',
            'cidade': 'São Luís',
            'especialidades': especialidades_validas,
            'experiencia': f"Teste gerado pelo diagnóstico",
            'is_test_data': True,
            'status': 'Pendente'
        }
        
        print(f"[→] Tentando inserir: {json.dumps(parceiro_teste, indent=2, ensure_ascii=False)}")
        
        # Inserir no banco
        response = supabase.table('parceiros_tecnicos').insert(parceiro_teste).execute()
        
        if response.data:
            print(f"[✓] Parceiro criado com sucesso! ID: {response.data[0].get('id')}")
            return True, response.data[0].get('id')
        else:
            print(f"[✗] Erro ao criar parceiro: Nenhum dado retornado")
            if hasattr(response, 'error'):
                print(f"[✗] Erro: {response.error}")
            return False, None
            
    except Exception as e:
        print(f"[✗] Exceção ao criar parceiro: {str(e)}")
        return False, None

def verificar_insercao(supabase, parceiro_id):
    """Verifica se o parceiro foi inserido corretamente."""
    try:
        if not parceiro_id:
            print("\n[4] Verificação de inserção: falhou (ID não fornecido)")
            return False
            
        print(f"\n[4] Verificando inserção do parceiro ID: {parceiro_id}...")
        
        # Buscar o parceiro pelo ID
        response = supabase.table('parceiros_tecnicos').select("*").eq('id', parceiro_id).execute()
        
        if response.data and len(response.data) > 0:
            parceiro = response.data[0]
            print(f"[✓] Parceiro encontrado no banco de dados!")
            print(f"    Nome: {parceiro.get('nome_completo')}")
            print(f"    Email: {parceiro.get('email')}")
            print(f"    Status: {parceiro.get('status')}")
            return True
        else:
            print(f"[✗] Parceiro não encontrado no banco de dados!")
            return False
            
    except Exception as e:
        print(f"[✗] Erro ao verificar inserção: {str(e)}")
        return False

def testar_elementos_html():
    """Verifica se os elementos HTML necessários existem na página developer.html"""
    try:
        print("\n[5] Verificando elementos HTML na página developer.html...")
        
        html_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates', 'admin', 'developer.html')
        
        if not os.path.exists(html_caminho):
            print(f"[✗] Arquivo developer.html não encontrado em {html_caminho}")
            return False
            
        # Ler o conteúdo do arquivo
        with open(html_caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        # Verificar elementos importantes
        elementos = [
            ('alertaResultado', conteudo.find('id="alertaResultado"') >= 0),
            ('mensagemResultado', conteudo.find('id="mensagemResultado"') >= 0),
            ('formInsercao', conteudo.find('id="formInsercao"') >= 0 or conteudo.find('id="formParceiroTeste"') >= 0),
            ('botaoSubmit', conteudo.find('type="submit"') >= 0)
        ]
        
        for elemento, existe in elementos:
            status = "[✓]" if existe else "[✗]"
            print(f"{status} Elemento '{elemento}': {'encontrado' if existe else 'não encontrado'}")
            
        todos_encontrados = all(existe for _, existe in elementos)
        
        if not todos_encontrados:
            print("\n[!] Alguns elementos HTML necessários estão ausentes!")
            print("    Isso pode causar erros ao inserir parceiros na interface web.")
            print("    Considere adicionar os elementos ausentes à página developer.html.")
            
        return todos_encontrados
            
    except Exception as e:
        print(f"[✗] Erro ao verificar elementos HTML: {str(e)}")
        return False

def diagnosticar_problemas_potenciais():
    """Lista problemas potenciais que podem afetar a inserção de parceiros."""
    print("\n[6] Diagnóstico de problemas potenciais...")
    
    problemas = [
        ("Formato de WhatsApp", "O WhatsApp deve ter exatamente 11 dígitos numéricos. Verifique se o valor está sendo formatado corretamente antes de enviar ao banco."),
        ("Especialidades inválidas", "As especialidades devem ser uma lista válida de valores aceitos pelo banco. Verifique se os valores estão na lista permitida."),
        ("Elementos HTML ausentes", "Se a página developer.html não tiver elementos como 'alertaResultado' e 'mensagemResultado', pode falhar silenciosamente."),
        ("CORS ou Permissões", "Verifique se há problemas de CORS ou permissões no Supabase que possam impedir a inserção."),
        ("Validações no frontend", "O frontend pode estar validando os dados de forma diferente do backend, causando rejeição silenciosa."),
        ("Console do navegador", "Verifique o console do navegador (F12) para erros de JavaScript durante o envio do formulário.")
    ]
    
    for problema, descricao in problemas:
        print(f"[!] {problema}: {descricao}")

def limpar_dados_teste(supabase, parceiro_id=None):
    """Limpa os dados de teste criados durante o diagnóstico."""
    try:
        if parceiro_id:
            print(f"\n[7] Limpando parceiro de teste ID: {parceiro_id}...")
            response = supabase.table('parceiros_tecnicos').delete().eq('id', parceiro_id).execute()
            if response.data:
                print(f"[✓] Parceiro de teste removido com sucesso")
            else:
                print(f"[!] Não foi possível remover o parceiro de teste")
        else:
            print("\n[7] Nenhum parceiro de teste para limpar")
    except Exception as e:
        print(f"[✗] Erro ao limpar dados de teste: {str(e)}")

def consertar_html_developer():
    """Tenta corrigir o arquivo developer.html se os elementos estiverem ausentes."""
    try:
        html_caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates', 'admin', 'developer.html')
        
        if not os.path.exists(html_caminho):
            print("[✗] Arquivo developer.html não encontrado")
            return False
            
        # Ler o conteúdo do arquivo
        with open(html_caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        # Verificar se os elementos já existem
        elementos_ausentes = []
        if conteudo.find('id="alertaResultado"') < 0:
            elementos_ausentes.append('alertaResultado')
        if conteudo.find('id="mensagemResultado"') < 0:
            elementos_ausentes.append('mensagemResultado')
            
        if not elementos_ausentes:
            print("[✓] Arquivo developer.html já possui os elementos necessários")
            return True
            
        print(f"\n[8] Tentando corrigir elementos ausentes: {', '.join(elementos_ausentes)}")
        
        # Encontrar onde adicionar os elementos (após algum formulário ou botão de submit)
        pos = conteudo.find('</form>')
        if pos < 0:
            pos = conteudo.find('type="submit"')
        if pos < 0:
            pos = conteudo.find('</div>')
            
        if pos < 0:
            print("[✗] Não foi possível encontrar um local adequado para adicionar os elementos")
            return False
            
        # Avançar até o final da tag
        while pos < len(conteudo) and conteudo[pos] != '>':
            pos += 1
        if pos < len(conteudo):
            pos += 1
            
        # Criar HTML para os elementos ausentes
        html_elementos = '\n'
        if 'alertaResultado' in elementos_ausentes:
            html_elementos += '        <div id="alertaResultado" class="alert mt-3" style="display: none;"></div>\n'
        if 'mensagemResultado' in elementos_ausentes:
            html_elementos += '        <div id="mensagemResultado" class="mt-3" style="display: none;"></div>\n'
            
        # Inserir os elementos no conteúdo
        novo_conteudo = conteudo[:pos] + html_elementos + conteudo[pos:]
        
        # Fazer backup do arquivo original
        backup_caminho = html_caminho + '.bak'
        with open(backup_caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
            
        # Salvar o novo conteúdo
        with open(html_caminho, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
            
        print(f"[✓] Elementos adicionados ao arquivo developer.html")
        print(f"[i] Backup salvo em: {backup_caminho}")
        return True
        
    except Exception as e:
        print(f"[✗] Erro ao consertar arquivo HTML: {str(e)}")
        return False

def verificar_cadastros_recentes(supabase, minutos=30):
    """Verifica se há cadastros recentes no sistema."""
    try:
        from datetime import datetime, timedelta
        
        print(f"\n[9] Verificando cadastros nos últimos {minutos} minutos...")
        
        # Calcular timestamp de corte
        agora = datetime.now()
        corte = agora - timedelta(minutes=minutos)
        corte_iso = corte.isoformat()
        
        # Buscar cadastros recentes
        response = supabase.table('parceiros_tecnicos').select("*").filter('created_at', 'gte', corte_iso).execute()
        
        cadastros = response.data if response.data else []
        
        if cadastros:
            print(f"[✓] Encontrados {len(cadastros)} cadastros recentes:")
            for i, c in enumerate(cadastros[:5]):  # Mostrar até 5 cadastros
                print(f"   {i+1}. {c.get('nome_completo')} ({c.get('email')}) - {c.get('created_at')}")
                
            if len(cadastros) > 5:
                print(f"   ... e mais {len(cadastros) - 5} cadastro(s)")
        else:
            print(f"[!] Nenhum cadastro encontrado nos últimos {minutos} minutos")
            
    except Exception as e:
        print(f"[✗] Erro ao verificar cadastros recentes: {str(e)}")

def main():
    """Função principal que executa o diagnóstico."""
    print("\n========================================================")
    print("=== DIAGNÓSTICO DE INSERÇÃO DE PARCEIROS TÉCNICOS ===")
    print("========================================================")
    print(f"Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("--------------------------------------------------------")
    
    # Testes de diagnóstico
    supabase = conectar_supabase()
    sucesso_tabela, campos = verificar_tabela_parceiros(supabase)
    
    # Se a tabela existir, tentar inserir um parceiro de teste
    parceiro_id = None
    if sucesso_tabela:
        criar_sucesso, parceiro_id = criar_parceiro_teste(supabase)
        if criar_sucesso:
            time.sleep(1)  # Pequena pausa para garantir que os dados sejam gravados
            verificar_insercao(supabase, parceiro_id)
    
    # Verificar elementos HTML
    testar_elementos_html()
    
    # Diagnóstico de problemas potenciais
    diagnosticar_problemas_potenciais()
    
    # Verificar cadastros recentes
    verificar_cadastros_recentes(supabase)
    
    # Tenta corrigir automaticamente elementos HTML ausentes
    consertar_html_developer()
    
    # Limpar dados de teste automaticamente
    if parceiro_id:
        limpar_dados_teste(supabase, parceiro_id)
    
    print("\n--------------------------------------------------------")
    print("Diagnóstico concluído!")
    print("--------------------------------------------------------")

if __name__ == "__main__":
    main() 