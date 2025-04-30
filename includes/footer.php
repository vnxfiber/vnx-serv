<?php
/**
 * VNX FIBER SERVICE - Footer Include
 * Este arquivo contém os elementos comuns que devem ser incluídos no final de todas as páginas
 */
?>
<!-- Scripts -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
<script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>

<!-- Script para substituição da logo -->
<script src="<?php echo $base_url; ?>scripts/logo-handler.js"></script>

<!-- AOS Initialization -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        AOS.init({
            duration: 800,
            once: true
        });
    });
</script>

<!-- WhatsApp Flutuante -->
<a href="https://wa.me/5598999882215?text=Olá!%20Gostaria%20de%20mais%20informações%20sobre%20os%20serviços%20da%20VNX%20FIBER%20SERVICE." class="whatsapp-float" target="_blank" aria-label="Fale conosco pelo WhatsApp">
    <i class="fab fa-whatsapp"></i>
</a>

<!-- Atualização do Ano no Copyright -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const yearElements = document.querySelectorAll('.current-year');
        const currentYear = new Date().getFullYear();
        
        yearElements.forEach(el => {
            el.textContent = currentYear;
        });
    });
</script> 