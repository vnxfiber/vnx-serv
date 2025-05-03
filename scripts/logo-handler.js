/**
 * VNX FIBER SERVICE - Logo Handler
 * Este script substitui automaticamente todas as referências à logo padrão pela logo animada
 */

document.addEventListener('DOMContentLoaded', function() {
    // O código abaixo foi desativado para não substituir a logo estática pela animada
    /*
    // Substituir todas as referências da logo estática pela animada
    const logoImages = document.querySelectorAll('img[src*="logo-white.svg"]');
    
    logoImages.forEach(img => {
        // Substituir o src para o novo arquivo de logo
        img.src = img.src.replace('logo-white.svg', 'logo-animated.svg');
        
        // Garantir que a altura e largura estejam definidas
        if (!img.getAttribute('width')) {
            img.setAttribute('width', '280');
        }
        
        if (!img.getAttribute('height')) {
            img.setAttribute('height', '90');
        }
        
        // Adicionar classe para aplicar estilos do logo.css
        if (img.closest('footer')) {
            img.classList.add('footer-logo');
        } else {
            img.classList.add('site-logo');
        }
    });
    
    console.log('Logo replacement complete. Animated logos: ' + logoImages.length);
    */
    console.log('Logo replacement disabled.');
}); 