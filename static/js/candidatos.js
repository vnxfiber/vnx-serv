// Funções para a página de Candidatos (Trabalhe Conosco)
document.addEventListener('DOMContentLoaded', function() {
    // Aplicar mascara de telefone
    const telefoneInputs = document.querySelectorAll('input[type="tel"]');
    if (telefoneInputs.length) {
        telefoneInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                if (value.length > 11) value = value.substring(0, 11);
                
                // Formatar como (XX) XXXXX-XXXX
                if (value.length > 2) {
                    value = `(${value.substring(0, 2)}) ${value.substring(2)}`;
                }
                if (value.length > 10) {
                    value = `${value.substring(0, 10)}-${value.substring(10)}`;
                }
                
                e.target.value = value;
            });
        });
    }
    
    // Limpar formulário de filtro
    const limparFiltroBtn = document.querySelector('a[href*="limpar"]');
    if (limparFiltroBtn) {
        limparFiltroBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Limpar todos os campos do formulário
            const form = document.getElementById('filter-form');
            const inputs = form.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.type === 'text' || input.type === 'search' || input.tagName === 'SELECT') {
                    input.value = '';
                }
            });
            
            // Enviar o formulário
            form.submit();
        });
    }
    
    // Função para atualizar a contagem de filtros ativos
    function updateFilterCount() {
        const filterCount = document.getElementById('filter-count');
        if (!filterCount) return;
        
        const form = document.getElementById('filter-form');
        let count = 0;
        
        // Contar filtros ativos
        form.querySelectorAll('select, input[type="text"]').forEach(el => {
            if (el.value && el.value !== '') {
                count++;
            }
        });
        
        // Atualizar a contagem
        filterCount.textContent = count;
        filterCount.style.display = count > 0 ? 'inline-flex' : 'none';
    }
    
    // Inicializar contagem e atualizar quando mudar
    updateFilterCount();
    document.querySelectorAll('#filter-form select, #filter-form input[type="text"]').forEach(el => {
        el.addEventListener('change', updateFilterCount);
    });
    
    // Função para abrir modais de detalhes/edição
    const viewButtons = document.querySelectorAll('.btn[data-bs-toggle="modal"]');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-bs-target');
            const modal = document.querySelector(modalId);
            if (modal) {
                const myModal = new bootstrap.Modal(modal);
                myModal.show();
            }
        });
    });
}); 