document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS (Animate On Scroll)
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false,
        offset: 50
    });

    // Initialize Bootstrap modals
    const scheduleModal = new bootstrap.Modal(document.getElementById('scheduleModal'));
    
    // Initialize input masks
    initializeInputMasks();
    
    // Setup contact form validation
    setupContactFormValidation();
    
    // Expose the function to open the modal in global scope
    window.openScheduleModal = function() {
        scheduleModal.show();
    };
    
    // Input masking function
    function initializeInputMasks() {
        // Phone number mask
        const phoneInputs = document.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach(input => {
            input.addEventListener('input', function(e) {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length <= 11) {
                    // Format as (XX) X XXXX-XXXX or (XX) XXXX-XXXX
                    if (value.length > 2) {
                        value = '(' + value.substring(0, 2) + ') ' + value.substring(2);
                    }
                    if (value.length > 10) {
                        value = value.substring(0, 10) + '-' + value.substring(10);
                    }
                    if (value.length > 5 && value.length <= 10) {
                        value = value.substring(0, 9) + '-' + value.substring(9);
                    }
                }
                
                e.target.value = value;
            });
        });
        
        // Date formatting - enforce Brazilian date format DD/MM/YYYY when manually typing
        const dateInputs = document.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            // This ensures when the built-in date picker is used, we don't interfere
            input.addEventListener('blur', function(e) {
                if (e.target.value) {
                    const date = new Date(e.target.value);
                    if (!isNaN(date.getTime())) {
                        // The input already has a valid date from the date picker
                        return;
                    }
                }
            });
        });
    }
    
    // Advanced form validation setup
    function setupContactFormValidation() {
        const contactForm = document.getElementById('contact-form');
        if (!contactForm) return;
        
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form elements
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const phone = document.getElementById('phone');
            const subject = document.getElementById('subject');
            const message = document.getElementById('message');
            
            // Reset validation state
            resetValidationState([name, email, phone, subject, message]);
            
            // Validate each field
            let isValid = true;
            
            // Name validation (required, min 3 chars)
            if (!name.value.trim() || name.value.trim().length < 3) {
                setInvalidState(name, 'Por favor, informe seu nome completo');
                isValid = false;
            }
            
            // Email validation
            if (!validateEmail(email.value)) {
                setInvalidState(email, 'Por favor, informe um e-mail válido');
                isValid = false;
            }
            
            // Phone validation (optional but if provided must follow pattern)
            if (phone.value && !validatePhone(phone.value)) {
                setInvalidState(phone, 'Por favor, informe um telefone válido');
                isValid = false;
            }
            
            // Subject validation
            if (subject.options[subject.selectedIndex].disabled) {
                setInvalidState(subject, 'Por favor, selecione um assunto');
                isValid = false;
            }
            
            // Message validation (required, min 10 chars)
            if (!message.value.trim() || message.value.trim().length < 10) {
                setInvalidState(message, 'Por favor, digite uma mensagem com pelo menos 10 caracteres');
                isValid = false;
            }
            
            if (isValid) {
                // Simulate form submission (replace with actual submission in production)
                const submitBtn = contactForm.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;
                
                // Show loading state
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
                
                // Simulated success (would be replaced with actual API call)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                    
                    // Show success message
                    showFormMessage('success', 'Mensagem enviada com sucesso! Entraremos em contato em breve.');
                    
                    // Reset form
                    contactForm.reset();
                }, 1500);
            }
        });
    }
    
    // Helper validation functions
    function validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    function validatePhone(phone) {
        // Basic Brazilian phone validation
        return phone.replace(/\D/g, '').length >= 10;
    }
    
    function resetValidationState(elements) {
        elements.forEach(element => {
            element.classList.remove('is-invalid');
            element.classList.remove('is-valid');
            
            // Remove existing feedback elements
            const parent = element.parentNode;
            const feedback = parent.querySelector('.invalid-feedback');
            if (feedback) {
                parent.removeChild(feedback);
            }
        });
    }
    
    function setInvalidState(element, message) {
        element.classList.add('is-invalid');
        
        // Add feedback message
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        element.parentNode.appendChild(feedback);
        
        // Focus the first invalid element
        if (document.querySelectorAll('.is-invalid').length === 1) {
            element.focus();
        }
    }
    
    function showFormMessage(type, message) {
        // Remove any existing messages
        const existingMessage = document.getElementById('form-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.id = 'form-message';
        messageEl.className = `alert alert-${type === 'success' ? 'success' : 'danger'} mt-3`;
        messageEl.innerHTML = message;
        
        // Add to form
        const form = document.getElementById('contact-form');
        form.after(messageEl);
        
        // Auto-remove message after 5 seconds
        setTimeout(() => {
            messageEl.classList.add('fade');
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.parentNode.removeChild(messageEl);
                }
            }, 500);
        }, 5000);
    }
    
    // Expose the function to submit the schedule form
    window.submitScheduleForm = function() {
        const form = document.getElementById('schedule-form');
        
        // Basic validation
        const inputs = form.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                // Special validation for email field
                if (input.type === 'email' && !validateEmail(input.value)) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            }
        });
        
        if (!isValid) {
            // Add feedback message for invalid form
            const errorFeedback = document.getElementById('schedule-form-feedback');
            if (!errorFeedback) {
                const feedbackDiv = document.createElement('div');
                feedbackDiv.id = 'schedule-form-feedback';
                feedbackDiv.className = 'alert alert-danger mt-3';
                feedbackDiv.innerHTML = 'Por favor, corrija os campos destacados.';
                form.appendChild(feedbackDiv);
                
                // Remove the feedback after 5 seconds
                setTimeout(() => {
                    if (feedbackDiv.parentNode) {
                        feedbackDiv.parentNode.removeChild(feedbackDiv);
                    }
                }, 5000);
            }
            return;
        }
        
        // Clean up any previous feedback
        const existingFeedback = document.getElementById('schedule-form-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Get form data
        const name = document.getElementById('scheduleName').value;
        const email = document.getElementById('scheduleEmail').value;
        const phone = document.getElementById('schedulePhone').value;
        const date = document.getElementById('scheduleDate').value;
        const time = document.getElementById('scheduleTime').value;
        const service = document.getElementById('scheduleService').value;
        const message = document.getElementById('scheduleMessage').value || "Sem mensagem adicional";
        
        // Format date
        const formattedDate = new Date(date).toLocaleDateString('pt-BR');
        
        // Create WhatsApp message
        const whatsappMessage = `*Agendamento VNX FIBER*%0A%0A*Nome:* ${name}%0A*Email:* ${email}%0A*Telefone:* ${phone}%0A*Data:* ${formattedDate}%0A*Horário:* ${time}%0A*Serviço:* ${service}%0A*Mensagem:* ${message}`;
        
        // WhatsApp URL
        const whatsappUrl = `https://wa.me/5598999882215?text=${whatsappMessage}`;
        
        // Open WhatsApp
        window.open(whatsappUrl, '_blank');
        
        // Close modal and reset form
        form.reset();
        scheduleModal.hide();
    };

    // Initialize Swiper for client logos
    const clientSwiper = new Swiper('.swiper-container', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: false,
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
            pauseOnMouseEnter: true
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        breakpoints: {
            640: {
                slidesPerView: 1,
            },
            768: {
                slidesPerView: 2,
            },
            1024: {
                slidesPerView: 3,
            },
        }
    });

    // Counter Animation
    const counters = document.querySelectorAll('.counter');
    
    const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.innerText);
                let count = 0;
                const speed = 2000 / target;
                
                const updateCount = () => {
                    if (count < target) {
                        count++;
                        counter.innerText = count;
                        setTimeout(updateCount, speed);
                    }
                };
                
                updateCount();
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => {
        counterObserver.observe(counter);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 75,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Contact form handling
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Mostrar feedback visual
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            submitBtn.disabled = true;
            
            try {
                // Get form data
                const name = document.getElementById('name').value;
                const email = document.getElementById('email').value;
                const phone = document.getElementById('phone').value || "Não informado";
                const subject = document.getElementById('subject').value || "Contato geral";
                const message = document.getElementById('message').value;
                
                // Create WhatsApp message
                const whatsappMessage = `*Contato via site - VNX FIBER*%0A%0A*Nome:* ${name}%0A*Email:* ${email}%0A*Telefone:* ${phone}%0A*Assunto:* ${subject}%0A*Mensagem:* ${message}`;
                
                // Open WhatsApp in new window
                window.open(`https://wa.me/5598999882215?text=${whatsappMessage}`, '_blank');
                
                // Mostrar sucesso
                showFormMessage('success', 'Mensagem enviada com sucesso! Entraremos em contato em breve.');
                contactForm.reset();
            } catch (error) {
                console.error('Erro ao enviar mensagem:', error);
                showFormMessage('error', 'Ocorreu um erro ao enviar a mensagem. Por favor, tente novamente.');
            } finally {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    }

    // Função para mostrar mensagem após submissão do formulário
    function showFormMessage(type, message) {
        const formMessage = document.createElement('div');
        formMessage.className = `alert alert-${type === 'success' ? 'success' : 'danger'} mt-3 animate__animated animate__fadeIn`;
        formMessage.innerHTML = message;
        
        const form = document.getElementById('contact-form');
        form.parentNode.appendChild(formMessage);
        
        setTimeout(() => {
            formMessage.classList.remove('animate__fadeIn');
            formMessage.classList.add('animate__fadeOut');
            setTimeout(() => {
                formMessage.remove();
            }, 500);
        }, 5000);
    }

    // Navbar background change on scroll
    const navbar = document.querySelector('.navbar');

    function updateNavbar() {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    }

    window.addEventListener('scroll', updateNavbar);
    updateNavbar(); // Call once to set initial state

    // Service category hover effect with improved performance
    const serviceCategories = document.querySelectorAll('.service-category');

    serviceCategories.forEach(category => {
        category.addEventListener('mouseenter', function() {
            this.classList.add('hovered');
        });
        
        category.addEventListener('mouseleave', function() {
            this.classList.remove('hovered');
        });
    });

    // Add parallax effect to hero section
    window.addEventListener('scroll', function() {
        const hero = document.querySelector('.hero');
        if (hero) {
            const scrollPosition = window.scrollY;
            hero.style.backgroundPosition = `center ${scrollPosition * 0.4}px`;
        }
    });

    // Toggle mobile menu close when clicking nav-link
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (navbarCollapse.classList.contains('show')) {
                navbarCollapse.classList.remove('show');
            }
        });
    });

    // Add active class to nav item based on scroll position
    function setActiveNavItem() {
        const scrollPosition = window.scrollY + 150; // Offset for navbar height
        
        document.querySelectorAll('section').forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', setActiveNavItem);
    setActiveNavItem();
});