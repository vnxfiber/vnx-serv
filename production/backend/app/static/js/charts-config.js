// Configuração padrão para todos os gráficos
Chart.defaults.font.family = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#596775';

// Configurações de animação global
Chart.defaults.animation = {
    duration: 1000,
    easing: 'easeInOutQuart'
};

// Configurações de responsividade
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;

// Configurações de tooltips
Chart.defaults.plugins.tooltip = {
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    titleFont: {
        size: 13,
        weight: 'bold'
    },
    bodyFont: {
        size: 12
    },
    padding: 10,
    cornerRadius: 4,
    displayColors: true
};

// Configurações de legendas
Chart.defaults.plugins.legend = {
    position: 'top',
    align: 'start',
    labels: {
        boxWidth: 12,
        padding: 15
    }
};

// Configurações para gráficos de linha
Chart.defaults.elements.line = {
    tension: 0.4,
    borderWidth: 2,
    fill: false
};

// Configurações para pontos em gráficos
Chart.defaults.elements.point = {
    radius: 4,
    hoverRadius: 6
};

// Configurações para barras
Chart.defaults.elements.bar = {
    borderRadius: 4
}; 