[file name]: modi-scripts.js
[file content begin]
document.addEventListener('DOMContentLoaded', function() {
    // Crear partículas flotantes
    function createParticles() {
        const container = document.getElementById('particles-container');
        if (!container) return;
        
        // Limpiar partículas existentes
        container.innerHTML = '';
        
        for (let i = 0; i < 15; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            // Tamaño y posición aleatoria
            const size = Math.random() * 60 + 20;
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            
            // Color aleatorio del gradiente
            const colors = [
                'rgba(67, 97, 238, 0.1)',
                'rgba(114, 9, 183, 0.1)',
                'rgba(247, 37, 133, 0.1)',
                'rgba(76, 201, 240, 0.1)'
            ];
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}vw`;
            particle.style.top = `${posY}vh`;
            particle.style.background = color;
            particle.style.animation = `floatBubble ${Math.random() * 30 + 20}s infinite linear`;
            particle.style.animationDelay = `${Math.random() * 5}s`;
            
            container.appendChild(particle);
        }
    }

    // Efecto hover para celdas especiales
    function initCellHoverEffects() {
        document.querySelectorAll('.delta-negative, .cell-cycle, .cell-entering').forEach(cell => {
            cell.addEventListener('mouseenter', function() {
                this.style.zIndex = '10';
                this.style.transform = 'scale(1.05)';
            });
            
            cell.addEventListener('mouseleave', function() {
                this.style.zIndex = '1';
                this.style.transform = 'scale(1)';
            });
        });
    }

    // Efecto de ripple para botones
    function initButtonRippleEffects() {
        document.querySelectorAll('.btn-mod, .btn-outline-mod').forEach(btn => {
            btn.addEventListener('click', function(event) {
                // Crear efecto ripple solo si es un botón clickeable
                if (this.tagName === 'BUTTON' || this.tagName === 'A') {
                    const rect = this.getBoundingClientRect();
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;
                    
                    const ripple = document.createElement('span');
                    ripple.style.position = 'absolute';
                    ripple.style.borderRadius = '50%';
                    ripple.style.background = 'rgba(255, 255, 255, 0.3)';
                    ripple.style.transform = 'scale(0)';
                    ripple.style.animation = 'ripple 0.6s linear';
                    ripple.style.left = `${x}px`;
                    ripple.style.top = `${y}px`;
                    ripple.style.width = '100px';
                    ripple.style.height = '100px';
                    ripple.style.marginLeft = '-50px';
                    ripple.style.marginTop = '-50px';
                    ripple.style.pointerEvents = 'none';
                    
                    this.style.position = 'relative';
                    this.style.overflow = 'hidden';
                    this.appendChild(ripple);
                    
                    setTimeout(() => {
                        if (ripple.parentNode === this) {
                            this.removeChild(ripple);
                        }
                    }, 600);
                }
            });
        });
    }

    // Expandir automáticamente el primer paso del acordeón
    function initAccordion() {
        const firstAccordion = document.querySelector('#modiStep1c');
        if (firstAccordion) {
            // Usar Bootstrap Collapse
            const bsCollapse = new bootstrap.Collapse(firstAccordion, {
                toggle: true
            });
        }
        
        // Añadir efectos a todos los botones del acordeón
        document.querySelectorAll('.accordion-button-mod').forEach(button => {
            button.addEventListener('click', function() {
                // Añadir pequeña animación al hacer click
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            });
        });
    }

    // Resaltar la celda entrante
    function highlightEnteringCell() {
        const enteringCell = document.querySelector('.cell-entering');
        if (enteringCell) {
            // Asegurar que la animación esté activa
            enteringCell.style.animation = 'enteringGlow 2s infinite';
            
            // Añadir tooltip
            enteringCell.setAttribute('title', 'Celda entrante seleccionada para mejora');
            enteringCell.setAttribute('data-bs-toggle', 'tooltip');
            enteringCell.setAttribute('data-bs-placement', 'top');
            
            // Inicializar tooltip de Bootstrap
            new bootstrap.Tooltip(enteringCell);
        }
    }

    // Inicializar tooltips de Bootstrap
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Efecto de scroll suave para enlaces internos
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                if (targetId !== '#') {
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }

    // Animación para números que cuentan
    function animateNumbers() {
        const numbers = document.querySelectorAll('.potential-badge');
        numbers.forEach(badge => {
            const originalText = badge.textContent;
            if (!isNaN(parseFloat(originalText))) {
                const number = parseFloat(originalText);
                let current = 0;
                const increment = number / 30;
                const interval = setInterval(() => {
                    current += increment;
                    if (current >= number) {
                        current = number;
                        clearInterval(interval);
                    }
                    badge.textContent = current.toFixed(2);
                }, 30);
            }
        });
    }

    // Efecto de parallax para el fondo
    function initParallax() {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const particles = document.querySelectorAll('.particle');
            
            particles.forEach((particle, index) => {
                const speed = 0.5 + (index * 0.1);
                const yPos = -(scrolled * speed);
                particle.style.transform = `translateY(${yPos}px) rotate(${scrolled * 0.1}deg)`;
            });
        });
    }

    // Inicializar todas las funciones
    function init() {
        createParticles();
        initCellHoverEffects();
        initButtonRippleEffects();
        initAccordion();
        highlightEnteringCell();
        initTooltips();
        initSmoothScroll();
        animateNumbers();
        initParallax();
        
        // Re-crear partículas cuando cambia el tamaño de la ventana
        window.addEventListener('resize', createParticles);
    }

    // Ejecutar inicialización
    init();
});
[file content end]