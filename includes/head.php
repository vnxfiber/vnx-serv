<?php
/**
 * VNX FIBER SERVICE - Header Include
 * Este arquivo contém os elementos comuns que devem ser incluídos no <head> de todas as páginas
 */
?>
<!-- Meta tags básicas -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

<!-- Favicon e ícones -->
<link rel="icon" href="<?php echo $base_url; ?>assets/favicon.ico" type="image/x-icon">
<link rel="apple-touch-icon" href="<?php echo $base_url; ?>assets/icons/apple-touch-icon.svg">
<meta name="theme-color" content="#0a3d62">

<!-- Preload da logo animada -->
<link rel="preload" href="<?php echo $base_url; ?>assets/logo-animated.svg" as="image">

<!-- Fontes -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

<!-- Bootstrap CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- Font Awesome -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">

<!-- AOS -->
<link href="https://unpkg.com/aos@2.3.4/dist/aos.css" rel="stylesheet">

<!-- Swiper -->
<link href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" rel="stylesheet">

<!-- CSS Personalizado -->
<link rel="stylesheet" href="<?php echo $base_url; ?>styles/main.css">
<link rel="stylesheet" href="<?php echo $base_url; ?>styles/logo.css">

<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script> 