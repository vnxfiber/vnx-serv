/**
 * Script para animar elementos SVG nas páginas de serviços
 * VNX FIBER SERVICE
 */

// Função para animar elementos SVG
function animateSvgElements() {
    // Verificar se a ilustração SVG está presente na página
    const svgIllustration = document.querySelector('.hero-decorative-image');
    if (!svgIllustration) return;

    // Carregar evento quando o SVG estiver completamente carregado
    svgIllustration.addEventListener('load', function() {
        // Acessar o documento SVG
        const svgDoc = svgIllustration.contentDocument;
        if (!svgDoc) return;

        // Adicionar classes de animação aos elementos LEDs
        const leds = svgDoc.querySelectorAll('.led-green, .led-red, .led-yellow');
        leds.forEach(led => {
            led.style.animation = led.classList.contains('led-green') 
                ? 'blink 2s infinite' 
                : led.classList.contains('led-red') 
                    ? 'blink 1.5s infinite' 
                    : 'blink 3s infinite';
        });

        // Adicionar efeitos de dados flutuantes
        const dataPoints = svgDoc.querySelectorAll('.data-point');
        dataPoints.forEach((point, index) => {
            const delay = (index % 5) * 0.3;
            point.style.animation = `pulse 4s ${delay}s infinite`;
        });

        // Animar linhas de conexão
        const connectionLines = svgDoc.querySelectorAll('.connection-line');
        connectionLines.forEach((line, index) => {
            const delay = (index % 3) * 0.5;
            line.style.animation = `dataMove 2s ${delay}s infinite alternate`;
        });
    });
}

// Função para melhorar a visualização em dispositivos móveis
function enhanceMobileExperience() {
    const heroSection = document.querySelector('.hero-page');
    if (!heroSection) return;

    // Detectar orientação e ajustar elementos
    const handleOrientationChange = () => {
        const isLandscape = window.innerWidth > window.innerHeight;
        const illustration = document.querySelector('.hero-decorative-image');
        
        if (illustration) {
            if (isLandscape && window.innerWidth < 992) {
                illustration.style.opacity = '0.5'; // Aumentar opacidade em modo paisagem
                illustration.style.maxWidth = '40%'; // Reduzir tamanho
            } else {
                // Restaurar valores padrão (mantidos no CSS)
                illustration.style.opacity = '';
                illustration.style.maxWidth = '';
            }
        }
    };

    // Verificar ao carregar e quando redimensionar/mudar orientação
    handleOrientationChange();
    window.addEventListener('resize', handleOrientationChange);
    window.addEventListener('orientationchange', handleOrientationChange);
}

// Função para ativar navegação suave para o menu de serviços
function setupServiceNavigation() {
    const serviceLinks = document.querySelectorAll('.services-nav .nav-link');
    if (serviceLinks.length === 0) return;

    // Adicionar efeito de hover nos itens do menu
    serviceLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 2px 8px rgba(var(--color-primary-rgb), 0.15)';
            }
        });
        
        link.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = '';
                this.style.boxShadow = '';
            }
        });
    });
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    animateSvgElements();
    enhanceMobileExperience();
    setupServiceNavigation();
}); 