/**
 * Validação e envio de formulários
 * VNX FIBER SERVICE
 */

document.addEventListener('DOMContentLoaded', function() {
    // Formulário de contato na página principal
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validar formulário
            if (!validateForm(contactForm)) {
                return false;
            }
            
            // Campo honeypot para proteção contra spam (invisível para humanos)
            const honeypotValue = document.getElementById('website').value;
            if (honeypotValue) {
                console.log('Possível submissão de spam detectada');
                return false;
            }
            
            // Coleta os dados do formulário
            const formData = new FormData(contactForm);
            
            // Adiciona token CSRF
            formData.append('csrf_token', getCsrfToken());
            
            // Envia para o servidor
            submitFormData(formData, 'contato')
                .then(response => {
                    if (response.success) {
                        // Limpa o formulário
                        contactForm.reset();
                        
                        // Mostra mensagem de sucesso
                        showAlert('success', 'Mensagem enviada com sucesso! Entraremos em contato em breve.');
                    } else {
                        // Mostra mensagem de erro
                        showAlert('danger', response.message || 'Erro ao enviar mensagem. Por favor, tente novamente.');
                    }
                })
                .catch(error => {
                    console.error('Erro ao enviar formulário:', error);
                    showAlert('danger', 'Erro ao enviar mensagem. Por favor, tente novamente.');
                });
        });
    }
    
    // Formulário de agendamento
    const scheduleForm = document.getElementById('schedule-form');
    if (scheduleForm) {
        // Adicionar listener para o botão de agendamento
        const scheduleButton = document.querySelector('button[onclick="submitScheduleForm()"]');
        if (scheduleButton) {
            scheduleButton.onclick = function() {
                if (!validateForm(scheduleForm)) {
                    return false;
                }
                
                const formData = new FormData(scheduleForm);
                formData.append('csrf_token', getCsrfToken());
                
                submitFormData(formData, 'agendamento')
                    .then(response => {
                        if (response.success) {
                            scheduleForm.reset();
                            // Fechar modal
                            const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleModal'));
                            if (modal) {
                                modal.hide();
                            }
                            showAlert('success', 'Agendamento solicitado com sucesso! Entraremos em contato para confirmar.');
                        } else {
                            showAlert('danger', response.message || 'Erro ao solicitar agendamento. Por favor, tente novamente.');
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao enviar agendamento:', error);
                        showAlert('danger', 'Erro ao solicitar agendamento. Por favor, tente novamente.');
                    });
            };
        }
    }
    
    // Formulário de parceiros (trabalhe-conosco.html)
    const partnerForm = document.getElementById('partner-form');
    if (partnerForm) {
        partnerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validateForm(partnerForm)) {
                return false;
            }
            
            const formData = new FormData(partnerForm);
            formData.append('csrf_token', getCsrfToken());
            
            submitFormData(formData, 'parceiro')
                .then(response => {
                    if (response.success) {
                        partnerForm.reset();
                        // Mostrar modal de sucesso se existir
                        const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                        if (successModal) {
                            successModal.show();
                        } else {
                            showAlert('success', 'Cadastro realizado com sucesso! Entraremos em contato em breve.');
                        }
                    } else {
                        showAlert('danger', response.message || 'Erro ao realizar cadastro. Por favor, tente novamente.');
                    }
                })
                .catch(error => {
                    console.error('Erro ao enviar formulário de parceiro:', error);
                    showAlert('danger', 'Erro ao realizar cadastro. Por favor, tente novamente.');
                });
        });
    }
});

/**
 * Valida os campos do formulário
 * @param {HTMLFormElement} form - Formulário a ser validado
 * @returns {boolean} - Indica se o formulário é válido
 */
function validateForm(form) {
    let valid = true;
    
    // Adiciona classe para ativar validação visual do Bootstrap
    form.classList.add('was-validated');
    
    // Validar campos obrigatórios
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            valid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    });
    
    // Validar emails
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !validateEmail(field.value)) {
            field.classList.add('is-invalid');
            valid = false;
        }
    });
    
    // Validar telefones
    const phoneFields = form.querySelectorAll('input[type="tel"]');
    phoneFields.forEach(field => {
        if (field.value && !validatePhone(field.value)) {
            field.classList.add('is-invalid');
            valid = false;
        }
    });
    
    return valid && form.checkValidity();
}

/**
 * Valida endereço de email
 * @param {string} email - Email a ser validado
 * @returns {boolean} - Indica se o email é válido
 */
function validateEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

/**
 * Valida número de telefone brasileiro
 * @param {string} phone - Telefone a ser validado
 * @returns {boolean} - Indica se o telefone é válido
 */
function validatePhone(phone) {
    // Remove caracteres não numéricos
    const numericPhone = phone.replace(/\D/g, '');
    // Verifica se tem entre 10 e 11 dígitos (com ou sem 9 no celular)
    return numericPhone.length >= 10 && numericPhone.length <= 11;
}

/**
 * Envia os dados do formulário para o servidor
 * @param {FormData} formData - Dados do formulário
 * @param {string} type - Tipo de formulário (contato, agendamento, parceiro)
 * @returns {Promise} - Promise com a resposta do servidor
 */
async function submitFormData(formData, type) {
    // Aqui você deve implementar a lógica real de envio para seu backend
    // Este é apenas um exemplo simulado
    
    // Simula envio para API
    return new Promise((resolve) => {
        console.log(`Enviando formulário de ${type}:`, Object.fromEntries(formData));
        
        // Simulação de resposta do servidor (sucesso)
        setTimeout(() => {
            resolve({
                success: true,
                message: 'Dados recebidos com sucesso!'
            });
        }, 1000);
        
        // Para simular erro, descomente o código abaixo
        /*
        setTimeout(() => {
            resolve({
                success: false,
                message: 'Erro ao processar solicitação. Tente novamente.'
            });
        }, 1000);
        */
    });
}

/**
 * Obtém token CSRF para proteger contra ataques CSRF
 * @returns {string} - Token CSRF
 */
function getCsrfToken() {
    // Em um ambiente real, este token seria gerado e validado pelo servidor
    // Esta é apenas uma simulação para demonstração
    return 'csrf_token_' + Math.random().toString(36).substr(2);
}

/**
 * Mostra alerta na página
 * @param {string} type - Tipo de alerta (success, danger, warning, info)
 * @param {string} message - Mensagem a ser exibida
 */
function showAlert(type, message) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.setAttribute('role', 'alert');
    
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
    `;
    
    // Adiciona o alerta ao início do corpo da página
    const firstElement = document.body.firstChild;
    document.body.insertBefore(alertContainer, firstElement);
    
    // Remove o alerta após 5 segundos
    setTimeout(() => {
        alertContainer.classList.remove('show');
        setTimeout(() => alertContainer.remove(), 300);
    }, 5000);
} 