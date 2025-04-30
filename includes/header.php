<?php
/**
 * VNX FIBER SERVICE - Header Component
 * Este arquivo contém o cabeçalho padronizado que deve ser incluído em todas as páginas
 */
?>
<!-- Header -->
<header class="fixed-top">
    <nav class="navbar navbar-expand-lg navbar-dark" aria-label="Navegação principal">
        <div class="container">
            <a class="navbar-brand" href="<?php echo $base_url; ?>">
                <img src="<?php echo $base_url; ?>assets/logo-animated.svg" alt="VNX FIBER SERVICE" width="280" height="90" class="site-logo">
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Alternar navegação">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link<?php echo ($current_page === 'home') ? ' active' : ''; ?>" href="<?php echo $base_url; ?>#home">Início</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link<?php echo ($current_page === 'quem-somos') ? ' active' : ''; ?>" href="<?php echo $base_url; ?>#quem-somos">Quem Somos</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link<?php echo ($current_page === 'servicos') ? ' active' : ''; ?>" href="<?php echo $base_url; ?>#servicos">Serviços</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link<?php echo ($current_page === 'tecnologias') ? ' active' : ''; ?>" href="<?php echo $base_url; ?>#tecnologias">Tecnologias</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link<?php echo ($current_page === 'contato') ? ' active' : ''; ?>" href="<?php echo $base_url; ?>#contato">Contato</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link ms-lg-2 animated-underline<?php echo ($current_page === 'trabalhe-conosco') ? ' active' : ''; ?>" href="<?php echo $base_url; ?>trabalhe-conosco.html">Trabalhe Conosco</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</header> 