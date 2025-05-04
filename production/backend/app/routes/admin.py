from flask import jsonify
from flask_login import login_required
from sqlalchemy import func
from backend.models import Parceiro
from backend import app, db

@admin_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """Retorna estatísticas atualizadas para o dashboard via AJAX."""
    try:
        # Reduzir o número de consultas ao banco usando uma única consulta
        # e processamento em memória
        parceiros = Parceiro.query.all()
        
        # Inicializar contadores
        total_parceiros = len(parceiros)
        parceiros_pendentes = 0
        parceiros_aprovados = 0
        parceiros_rejeitados = 0
        
        # Coletar dados de especialidades
        especialidades_count = {}
        
        # Uma única iteração para preencher todos os dados
        for parceiro in parceiros:
            # Contar por status
            status = parceiro.status or 'Pendente'
            if status == 'Pendente':
                parceiros_pendentes += 1
            elif status == 'Aprovado':
                parceiros_aprovados += 1
            elif status == 'Rejeitado':
                parceiros_rejeitados += 1
            
            # Contar especialidades
            if parceiro.especialidades:
                for esp in parceiro.especialidades:
                    if esp in especialidades_count:
                        especialidades_count[esp] += 1
                    else:
                        especialidades_count[esp] = 1
        
        # Determinar especialidade principal
        especialidade_principal = "Nenhuma"
        if especialidades_count:
            especialidade_principal = max(especialidades_count.items(), key=lambda x: x[1])[0]
        
        # Preparar dados para gráficos
        dados_status = [parceiros_pendentes, parceiros_aprovados, parceiros_rejeitados]
        
        # Dados para o gráfico de especialidades (limitar a 10 itens)
        especialidades_sorted = sorted(especialidades_count.items(), key=lambda x: x[1], reverse=True)
        labels_especialidades = [esp[0] for esp in especialidades_sorted[:10]]
        dados_especialidades = [esp[1] for esp in especialidades_sorted[:10]]
        
        # Retornar os resultados em formato JSON
        return jsonify({
            "stats": {
                "total": total_parceiros,
                "pendentes": parceiros_pendentes,
                "aprovados": parceiros_aprovados,
                "rejeitados": parceiros_rejeitados,
                "especialidade_principal": especialidade_principal
            },
            "charts": {
                "status": dados_status,
                "labels_especialidades": labels_especialidades,
                "dados_especialidades": dados_especialidades
            },
            "ranking": [{"nome": esp[0], "total": esp[1]} for esp in especialidades_sorted[:10]]
        })
    
    except Exception as e:
        # Log simplificado para evitar sobrecarga
        app.logger.error(f"Erro stats: {str(e)}")
        return jsonify({"error": "Erro ao obter estatísticas"}), 500 