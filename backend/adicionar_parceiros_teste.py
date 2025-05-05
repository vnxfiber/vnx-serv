#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
import argparse
from datetime import datetime
from supabase import create_client

# Configurações de conexão do Supabase
SUPABASE_URL = 'https://cwrxdjfmxntmplwdbnpg.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cnhkamZteG50bXBsd2RibnBnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjAwMjQzOSwiZXhwIjoyMDYxNTc4NDM5fQ.wUCecHTnyEwSVoH_-ruIV4fIGibr0vNkGZPbTVBM8uY'

def conectar_supabase():
    """Estabelece conexão com o Supabase"""
    print("[1] Conectando ao Supabase...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[✓] Conexão estabelecida com sucesso!")
        return supabase
    except Exception as e:
        print(f"[✗] Erro ao conectar: {e}")
        sys.exit(1)

def obter_exemplo_valido(supabase):
    """Obtém um exemplo válido do banco de dados"""
    try:
        # Tentar obter uma amostra para descobrir quais valores são aceitos
        response = supabase.table('parceiros_tecnicos').select("*").limit(1).execute()
        
        # Se tiver dados de exemplo, usá-los como referência
        if response.data and len(response.data) > 0:
            sample = response.data[0]
            print(f"[✓] Registro de exemplo encontrado: {sample.get('nome_completo')}")
            
            # Extrair valores do exemplo
            nome = "Paulo Silva"
            especialidades = ["Solucoes ISP"]
            
            if 'especialidades' in sample and isinstance(sample['especialidades'], list):
                especialidades = sample['especialidades']
                print(f"[✓] Especialidades encontradas: {especialidades}")
            
            if 'nome_completo' in sample and sample['nome_completo']:
                nome = sample['nome_completo']
                print(f"[✓] Formato de nome encontrado: {nome}")
                
            return {
                'especialidades': especialidades,
                'nome': nome,
                'amostra': sample  # Retorna o objeto completo para referência
            }
    except Exception as e:
        print(f"[!] Erro ao obter exemplo do banco: {e}")
    
    # Se falhar, retornar valores default conhecidos que funcionam
    default = {
        'especialidades': ["Solucoes ISP"],
        'nome': 'Paulo Silva',
        'amostra': None
    }
    print(f"[!] Usando valores padrão: {default}")
    return default

def gerar_telefone_unico():
    """Gera um número de telefone com 11 dígitos que atende à validação"""
    # Gera um número de 11 dígitos (2 DDD + 9 número)
    ddd = random.choice(['11', '21', '31', '41', '51', '61', '71', '81', '91', '98'])
    numero = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return f"{ddd}{numero}"

def adicionar_parceiros(quantidade=5):
    """Adiciona parceiros de teste ao banco de dados"""
    # Conectar ao Supabase
    supabase = conectar_supabase()
    
    # Obter exemplo válido do banco
    exemplo = obter_exemplo_valido(supabase)
    
    # Dados para geração aleatória
    estados_cidades = [
        ('MA', 'Sao Luis'),
        ('MA', 'Imperatriz'),
        ('PI', 'Teresina'),
        ('CE', 'Fortaleza'),
        ('PE', 'Recife'),
        ('PA', 'Belem')
    ]
    
    # Lista de nomes válidos (seguindo o padrão de validação)
    nomes_validos = [
        "Paulo Silva",
        "Maria Santos", 
        "Joao Oliveira",
        "Ana Costa",
        "Carlos Souza",
        "Juliana Lima",
        "Pedro Alves",
        "Fernanda Pereira",
        "Roberto Gomes",
        "Lucia Ferreira"
    ]
    
    # Lista de especialidades válidas - usando apenas valores do enum specialty_type
    especialidades_validas = [
        ["Solucoes ISP"],
        ["Telefonia VoIP"],
        ["Solucoes ISP", "Telefonia VoIP"],
        ["Fibra Óptica"],
        ["Servidores TI"],
        ["Wi-Fi Corporativo"],
        ["Infraestrutura Fisica"],
        ["Radio Comunicacao"],
        ["Consultoria"]
    ]
    
    print(f"\n[2] Gerando {quantidade} parceiros técnicos de teste...")
    
    # Verificar telefones já existentes para evitar duplicação
    existentes = set()
    try:
        response = supabase.table('parceiros_tecnicos').select("whatsapp").execute()
        if response.data:
            for item in response.data:
                if 'whatsapp' in item and item['whatsapp']:
                    existentes.add(item['whatsapp'])
        print(f"[✓] {len(existentes)} números de telefone já cadastrados")
    except Exception as e:
        print(f"[!] Erro ao verificar telefones: {e}")
    
    parceiros_inseridos = 0
    for i in range(quantidade):
        try:
            # Gerar dados aleatórios
            estado, cidade = random.choice(estados_cidades)
            nome = random.choice(nomes_validos)
            especialidades = random.choice(especialidades_validas)
            
            # Gerar um número de telefone único que não existe no banco
            whatsapp = gerar_telefone_unico()
            while whatsapp in existentes:
                whatsapp = gerar_telefone_unico()
            existentes.add(whatsapp)  # adiciona à lista de existentes para não repetir
            
            # Gerar email único
            random_id = random.randint(10000, 99999)
            nome_email = nome.lower().replace(" ", ".")
            email = f"{nome_email}.{random_id}@exemplo.com"
            
            # Dados do parceiro
            parceiro = {
                'nome_completo': nome,
                'email': email,
                'whatsapp': whatsapp,
                'estado': estado,
                'cidade': cidade,
                'especialidades': especialidades,
                'experiencia': 'Testando instalacao e configuracao de equipamentos de rede', 
                'status': 'Pendente',
                'is_test_data': True
            }
            
            print(f"   - Inserindo parceiro {i+1}: {parceiro['nome_completo']} ({parceiro['email']})")
            print(f"     WhatsApp: {parceiro['whatsapp']}")
            print(f"     Especialidades: {parceiro['especialidades']}")
            
            # Inserir no banco de dados
            response = supabase.table('parceiros_tecnicos').insert(parceiro).execute()
            
            if hasattr(response, 'data') and response.data:
                parceiros_inseridos += 1
                parceiro_id = response.data[0].get('id', 'ID desconhecido')
                print(f"     [✓] Inserido com sucesso! ID: {parceiro_id}")
            else:
                error = response.error if hasattr(response, 'error') else "Erro desconhecido"
                print(f"     [✗] Erro ao inserir parceiro: {error}")
                
        except Exception as e:
            print(f"     [✗] Erro: {e}")
            continue
            
    print(f"\n[3] Resultado: {parceiros_inseridos} parceiros inseridos com sucesso.")
    
    # Verificar parceiros inseridos
    try:
        response = supabase.table('parceiros_tecnicos').select('count', count='exact').eq('is_test_data', True).execute()
        total_teste = response.count if hasattr(response, 'count') else 0
        
        print(f"[✓] Total de parceiros de teste no banco: {total_teste}")
    except Exception as e:
        print(f"[✗] Erro ao verificar total: {e}")

def main():
    """Função principal"""
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Inserir parceiros técnicos de teste no banco de dados')
    parser.add_argument('-q', '--quantidade', type=int, default=5, help='Quantidade de parceiros a inserir (padrão: 5)')
    parser.add_argument('-y', '--yes', action='store_true', help='Executar sem confirmação')
    args = parser.parse_args()
    
    quantidade = args.quantidade
    
    # Limitar quantidade por segurança
    if quantidade > 50:
        print("Por segurança, limitando a 50 parceiros.")
        quantidade = 50
    
    print("\n========================================================")
    print("=== INSERÇÃO DE PARCEIROS TÉCNICOS DE TESTE ===")
    print("========================================================")
    print(f"Quantidade a inserir: {quantidade}")
    
    # Confirmar antes de prosseguir, a menos que --yes tenha sido especificado
    if not args.yes:
        confirmacao = input("Deseja continuar? (s/n): ")
        if confirmacao.lower() not in ['s', 'sim', 'y', 'yes']:
            print("Operação cancelada.")
            return
    
    # Adicionar parceiros
    adicionar_parceiros(quantidade)
    
    print("\nOperação concluída com sucesso!")

def limpar_dados_teste():
    """Remove todos os dados de teste do banco"""
    # Conectar ao Supabase
    supabase = conectar_supabase()
    
    print("\n[2] Removendo parceiros técnicos marcados como teste...")
    
    try:
        # Primeiro verificar quantos registros existem
        response = supabase.table('parceiros_tecnicos').select('count', count='exact').eq('is_test_data', True).execute()
        total = response.count if hasattr(response, 'count') else 0
        
        if total == 0:
            print("[!] Nenhum parceiro de teste encontrado para remover.")
            return
            
        print(f"[!] Serão removidos {total} parceiros de teste.")
        
        # Perguntar confirmação
        confirmacao = input("Deseja continuar com a remoção? (s/n): ")
        if confirmacao.lower() not in ['s', 'sim', 'y', 'yes']:
            print("[!] Operação cancelada.")
            return
            
        # Executar a remoção
        response = supabase.table('parceiros_tecnicos').delete().eq('is_test_data', True).execute()
        
        if hasattr(response, 'data'):
            removed = len(response.data) if response.data else 0
            print(f"[✓] {removed} parceiros de teste removidos com sucesso!")
        else:
            print(f"[✗] Erro na remoção: {response}")
            
    except Exception as e:
        print(f"[✗] Erro ao remover dados: {e}")

# Verificar se o script está sendo executado diretamente
if __name__ == "__main__":
    # Verificar se foi solicitada a limpeza de dados
    if len(sys.argv) > 1 and sys.argv[1] == 'limpar':
        limpar_dados_teste()
    else:
        main() 