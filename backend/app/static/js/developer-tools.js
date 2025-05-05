/**
 * developer-tools.js
 * Funções auxiliares para o modo desenvolvedor
 */

// Objeto para gerenciar as ferramentas de desenvolvimento
const DevTools = {
    // Função para formatar o WhatsApp para o formato esperado pelo banco
    formatarWhatsApp: function(whatsapp) {
        // Remover todos os caracteres não numéricos
        const numeroLimpo = whatsapp.replace(/\D/g, '');
        
        // Garantir que tenha exatamente 11 dígitos
        if (numeroLimpo.length !== 11) {
            console.error(`WhatsApp inválido: ${whatsapp} (após limpeza: ${numeroLimpo}). Deve ter exatamente 11 dígitos.`);
            return null;
        }
        
        return numeroLimpo;
    },
    
    // Função para garantir que os elementos HTML necessários existam
    verificarElementosHTML: function() {
        console.log('Verificando elementos HTML necessários...');
        
        // Lista de elementos obrigatórios
        const elementos = [
            { id: 'alertaResultado', criar: true },
            { id: 'mensagemResultado', criar: true }
        ];
        
        // Verificar cada elemento
        elementos.forEach(elem => {
            const elemento = document.getElementById(elem.id);
            
            if (!elemento && elem.criar) {
                console.warn(`Elemento #${elem.id} não encontrado. Criando dinamicamente...`);
                
                // Criar o elemento
                const novoElemento = document.createElement('div');
                novoElemento.id = elem.id;
                novoElemento.className = elem.id === 'alertaResultado' ? 'alert mt-3' : 'mt-3';
                novoElemento.style.display = 'none';
                
                // Encontrar onde inserir o elemento (após o formulário)
                const form = document.getElementById('formParceiroTeste') || document.getElementById('formInsercao');
                if (form) {
                    form.parentNode.insertBefore(novoElemento, form.nextSibling);
                    console.log(`Elemento #${elem.id} criado com sucesso!`);
                } else {
                    // Se não encontrar o formulário, adicionar ao final do body
                    document.body.appendChild(novoElemento);
                    console.warn(`Formulário não encontrado. Elemento #${elem.id} adicionado ao final da página.`);
                }
            }
        });
        
        return true;
    },
    
    // Função para mostrar alertas
    mostrarAlerta: function(elementId, mensagem, tipo) {
        // Verificar se o elemento existe, se não, criar
        let elemento = document.getElementById(elementId);
        if (!elemento) {
            console.warn(`Elemento #${elementId} não encontrado. Criando...`);
            elemento = document.createElement('div');
            elemento.id = elementId;
            elemento.className = 'alert mt-3';
            elemento.style.display = 'none';
            
            // Adicionar após o formulário ou no final da página
            const form = document.getElementById('formParceiroTeste') || document.getElementById('formInsercao');
            if (form && form.parentNode) {
                form.parentNode.insertBefore(elemento, form.nextSibling);
            } else {
                document.body.appendChild(elemento);
            }
        }
        
        // Atualizar conteúdo e classe
        elemento.innerHTML = mensagem;
        elemento.className = `alert alert-${tipo} mt-3`;
        elemento.style.display = 'block';
        
        // Scroll até o alerta
        elemento.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        return elemento;
    },
    
    // Função para enviar parceiro de teste
    enviarParceiro: function(event, formId = 'formParceiroTeste') {
        // Evitar comportamento padrão do formulário
        if (event) {
            event.preventDefault();
        }
        
        console.log("Iniciando envio de parceiro de teste");
        
        // Garantir que os elementos necessários existam
        this.verificarElementosHTML();
        
        // Limpar alertas anteriores
        const alertaResultado = document.getElementById('alertaResultado');
        const mensagemResultado = document.getElementById('mensagemResultado');
        
        if (alertaResultado) alertaResultado.style.display = 'none';
        if (mensagemResultado) mensagemResultado.style.display = 'none';
        
        // Obter dados do formulário
        const form = document.getElementById(formId);
        if (!form) {
            console.error(`Formulário #${formId} não encontrado!`);
            this.mostrarAlerta('alertaResultado', `Erro: Formulário #${formId} não encontrado!`, 'danger');
            return false;
        }
        
        const formData = new FormData(form);
        
        // Verificar WhatsApp (exatamente 11 dígitos)
        let whatsapp = formData.get('whatsapp');
        whatsapp = this.formatarWhatsApp(whatsapp);
        
        if (!whatsapp) {
            this.mostrarAlerta('alertaResultado', 'O WhatsApp deve conter exatamente 11 dígitos numéricos', 'danger');
            return false;
        }
        
        // Não adicionar prefixo 55 - o banco espera exatamente 11 dígitos sem o código do país
        
        // Extrair especialidades (múltiplas)
        const especialidadesSelect = document.getElementById('especialidadesParceiro');
        let especialidades = [];
        
        // Valores válidos de especialidades conforme descobertos no diagnóstico
        const especialidadesValidas = ["Solucoes ISP", "Telefonia VoIP", "Redes", "Seguranca"];
        
        if (especialidadesSelect) {
            // Obter valores selecionados
            const selecionadas = Array.from(especialidadesSelect.selectedOptions).map(option => option.value);
            
            // Filtrar apenas especialidades válidas ou mapear para valores válidos
            especialidades = selecionadas.map(esp => {
                // Tenta mapear para um valor válido
                switch(esp) {
                    case 'Infraestrutura': return 'Solucoes ISP';
                    case 'Servidores': return 'Solucoes ISP';
                    case 'Wi-Fi Corporativo': return 'Redes';
                    case 'Fibra Óptica': return 'Solucoes ISP';
                    case 'Telefonia VoIP': return 'Telefonia VoIP';
                    case 'Segurança da Informação': return 'Seguranca';
                    default: return esp;
                }
            });
            
            // Se após a conversão não houver especialidades válidas, usar um valor padrão
            if (especialidades.length === 0) {
                especialidades = ['Solucoes ISP'];
            }
            
            console.log("Especialidades originais:", selecionadas);
            console.log("Especialidades convertidas:", especialidades);
        } else {
            // Valor padrão se não encontrar o seletor
            especialidades = ['Solucoes ISP'];
        }
        
        // Se nenhuma especialidade selecionada, mostrar erro
        if (especialidades.length === 0) {
            this.mostrarAlerta('alertaResultado', 'Selecione pelo menos uma especialidade', 'danger');
            return false;
        }
        
        // Montar objeto com os dados do parceiro
        const parceiro = {
            nome_completo: formData.get('nome_completo') || 'Parceiro Teste',
            email: formData.get('email') || 'teste@exemplo.com',
            whatsapp: whatsapp,
            cidade: formData.get('cidade') || 'São Luís',
            estado: formData.get('estado') || 'MA',
            especialidades: especialidades,
            experiencia: formData.get('experiencia') || 'Parceiro de teste para validação do sistema.',
            is_test_data: true,
            status: 'Pendente'
        };
        
        console.log("Dados do parceiro:", parceiro);
        
        // Exibir mensagem de carregamento
        this.mostrarAlerta('alertaResultado', 'Enviando dados...', 'info');
        
        // Enviar requisição para o endpoint de geração de parceiros de teste
        fetch('/admin/developer/gerar-parceiros-teste', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                parceiros: [parceiro]
            })
        })
        .then(response => {
            console.log("Resposta recebida:", response);
            if (!response.ok) {
                throw new Error(`Erro HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Dados da resposta:", data);
            
            if (data.success) {
                // Sucesso
                this.mostrarAlerta('alertaResultado', 'Parceiro inserido com sucesso na tabela parceiros_tecnicos!', 'success');
                
                // Exibir detalhes do parceiro inserido
                const msgResultado = document.getElementById('mensagemResultado');
                if (msgResultado) {
                    msgResultado.innerHTML = `
                        <div class="card">
                            <div class="card-header bg-success text-white">
                                <strong>Parceiro Inserido</strong>
                            </div>
                            <div class="card-body">
                                <p><strong>Nome:</strong> ${parceiro.nome_completo}</p>
                                <p><strong>Email:</strong> ${parceiro.email}</p>
                                <p><strong>WhatsApp:</strong> ${parceiro.whatsapp}</p>
                                <p><strong>Cidade/Estado:</strong> ${parceiro.cidade}/${parceiro.estado}</p>
                                <p><strong>Especialidades:</strong> ${parceiro.especialidades.join(', ')}</p>
                            </div>
                        </div>
                    `;
                    msgResultado.style.display = 'block';
                }
                
                // Limpar o formulário
                form.reset();
                
                return true;
            } else {
                // Erro
                let mensagemErro = data.message || 'Erro desconhecido ao inserir parceiro';
                
                // Exibir erros detalhados se disponíveis
                if (data.erros && data.erros.length > 0) {
                    mensagemErro += '<ul>';
                    data.erros.forEach(erro => {
                        mensagemErro += `<li>${erro}</li>`;
                    });
                    mensagemErro += '</ul>';
                }
                
                this.mostrarAlerta('alertaResultado', mensagemErro, 'danger');
                
                // Log detalhado no console para debugging
                console.error("Erro na inserção:", data);
                
                return false;
            }
        })
        .catch(error => {
            console.error('Erro ao enviar parceiro:', error);
            this.mostrarAlerta('alertaResultado', 'Erro ao enviar parceiro: ' + error, 'danger');
            return false;
        });
    },
    
    // Função auxiliar para obter o token CSRF
    getCSRFToken: function() {
        // Tentar obter de meta tag
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }
        
        // Tentar obter de input hidden
        const inputToken = document.querySelector('input[name="csrf_token"]');
        if (inputToken) {
            return inputToken.value;
        }
        
        // Tentar obter de cookie
        const csrfCookie = document.cookie.split('; ')
            .find(row => row.startsWith('csrf_token='));
        if (csrfCookie) {
            return csrfCookie.split('=')[1];
        }
        
        console.warn("CSRF token não encontrado!");
        return '';
    }
};

// Adicionar ao escopo global
window.DevTools = DevTools;

// Inicializar quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    console.log('Developer Tools carregadas');
    
    // Verificar e criar elementos necessários
    DevTools.verificarElementosHTML();
    
    // Adicionar event listener para o formulário
    const form = document.getElementById('formParceiroTeste');
    if (form) {
        form.addEventListener('submit', function(event) {
            DevTools.enviarParceiro(event);
        });
        console.log('Event listener adicionado ao formulário de parceiro');
    }
}); 