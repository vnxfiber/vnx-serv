/**
 * Menu Mobile - VNX FIBER SERVICE
 * Script para gerenciar comportamentos do menu mobile em todas as páginas
 * @version 1.1.0
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    try {
        // Elementos do menu
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        let bsCollapse = null;
        
        // Inicializa o objeto Collapse apenas se o elemento navbar-collapse existir
        if (navbarCollapse) {
            try {
                bsCollapse = new bootstrap.Collapse(navbarCollapse, {toggle: false});
            } catch (error) {
                console.error('Erro ao inicializar collapse do Bootstrap:', error);
            }
        }
        
        // Seleciona todos os links no navbar
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        // Adiciona evento de clique para cada link
        navLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                if (window.innerWidth < 992 && bsCollapse) {
                    // Pequeno atraso para garantir que a navegação ocorra antes de fechar o menu
                    setTimeout(function() {
                        bsCollapse.hide();
                    }, 150);
                }
            });
        });
        
        // Fecha o menu quando clica fora dele
        document.addEventListener('click', function(e) {
            // Verifica se o menu está aberto
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                // Verifica se o clique foi fora do menu e não no toggler
                if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                    if (bsCollapse) {
                        bsCollapse.hide();
                    } else {
                        // Fallback para browsers sem suporte total ao Bootstrap
                        navbarCollapse.classList.remove('show');
                    }
                }
            }
        });
        
        // Adiciona suporte para browsers que não suportam completamente o Bootstrap
        if (navbarToggler && !bsCollapse) {
            navbarToggler.addEventListener('click', function() {
                navbarCollapse.classList.toggle('show');
            });
        }

        // Adiciona classe ao scrollar
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            const scrollListener = function() {
                if (window.scrollY > 10) {
                    navbar.classList.add('navbar-scrolled');
                } else {
                    navbar.classList.remove('navbar-scrolled');
                }
            };
            
            // Adiciona o listener e executa imediatamente para definir o estado inicial
            window.addEventListener('scroll', scrollListener);
            scrollListener();
        }
        
        // Adiciona navegação com teclado para acessibilidade
        if (navbarToggler) {
            navbarToggler.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    navbarToggler.click();
                }
            });
        }
        
        // Ajusta o modal de agendamento
        const scheduleModal = document.getElementById('scheduleModal');
        if (scheduleModal) {
            scheduleModal.addEventListener('shown.bs.modal', function() {
                // Ajusta o tamanho do modal em dispositivos móveis
                if (window.innerWidth < 576) {
                    const modalDialog = this.querySelector('.modal-dialog');
                    if (modalDialog) modalDialog.style.margin = '0.5rem';
                    
                    // Garante que o modal esteja visível dentro da tela
                    const viewportHeight = window.innerHeight;
                    const modalContent = this.querySelector('.modal-content');
                    if (modalContent && modalContent.offsetHeight > viewportHeight - 20) {
                        modalContent.style.height = (viewportHeight - 20) + 'px';
                    }
                }
                
                // Foca o primeiro campo para acessibilidade
                const firstInput = scheduleModal.querySelector('input, select, textarea');
                if (firstInput) {
                    setTimeout(() => {
                        firstInput.focus();
                    }, 100);
                }
            });
        }
        
        // Adiciona melhoria para navegação em dispositivos móveis
        if ('ontouchstart' in window) {
            document.body.classList.add('touch-device');
            
            // Melhora a área de toque para menus em dispositivos móveis
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(item => {
                item.style.padding = '0.5rem 0';
            });
        }
        
    } catch (error) {
        console.error('Erro no script de menu mobile:', error);
    }
}); 