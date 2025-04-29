/**
 * Menu Mobile - VNX FIBER SERVICE
 * Script para gerenciar comportamentos do menu mobile em todas as páginas
 */

document.addEventListener('DOMContentLoaded', function() {
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
    window.addEventListener('scroll', function() {
        if (window.scrollY > 10) {
            document.querySelector('.navbar').classList.add('navbar-scrolled');
        } else {
            document.querySelector('.navbar').classList.remove('navbar-scrolled');
        }
    });
}); 