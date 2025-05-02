// Função para carregar recursos de forma assíncrona
function loadResource(url, type) {
    return new Promise((resolve, reject) => {
        let element;
        if (type === 'script') {
            element = document.createElement('script');
            element.src = url;
            element.async = true;
        } else if (type === 'style') {
            element = document.createElement('link');
            element.href = url;
            element.rel = 'stylesheet';
        }
        
        element.onload = () => resolve();
        element.onerror = () => reject();
        document.head.appendChild(element);
    });
}

// Carregar recursos não críticos após a página carregar
window.addEventListener('load', () => {
    // Array de recursos para carregar depois
    const deferredResources = [
        { url: '/static/js/charts-config.js', type: 'script' },
        // Adicione outros recursos não críticos aqui
    ];

    // Carregar recursos de forma assíncrona
    Promise.all(deferredResources.map(resource => 
        loadResource(resource.url, resource.type)
    )).then(() => {
        console.log('Todos os recursos foram carregados');
    }).catch(error => {
        console.error('Erro ao carregar recursos:', error);
    });
});

// Otimização de imagens
document.addEventListener('DOMContentLoaded', () => {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback para navegadores que não suportam IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
});

// Otimização de eventos
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Exemplo de uso do debounce em eventos de redimensionamento
const handleResize = debounce(() => {
    // Lógica de redimensionamento aqui
}, 250);

window.addEventListener('resize', handleResize); 