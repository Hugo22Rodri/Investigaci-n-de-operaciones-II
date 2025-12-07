// page-nav.js - comportamiento común de navegación entre páginas (smooth scroll, navbar scroll, backups)
document.addEventListener('DOMContentLoaded', function() {
    console.log('page-nav initialized');

    // Saber más - scroll hacia sección
    const saberMasBtn = document.getElementById('saberMasBtn');
    if (saberMasBtn) {
        saberMasBtn.addEventListener('click', function(e){
            e.preventDefault();
            const target = document.getElementById('introduccion');
            if (target){
                const offsetTop = target.offsetTop - 80;
                window.scrollTo({ top: offsetTop, behavior: 'smooth' });
            }
        });
    }

    // Calcular ahora - deja que el enlace funcione (no preventDefault)
    const calcularBtn = document.getElementById('calcularBtn');
    if (calcularBtn){
        calcularBtn.addEventListener('click', function(){
            console.log('calcularBtn clicked');
        });
    }

    // Smooth scrolling para enlaces en la navbar
    document.querySelectorAll('.navbar-nav a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e){
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement){
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')){
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
                const offsetTop = targetElement.offsetTop - 80;
                window.scrollTo({ top: offsetTop, behavior: 'smooth' });
            }
        });
    });

    // Cambiar fondo de navbar al hacer scroll
    window.addEventListener('scroll', function(){
        const navbar = document.querySelector('.custom-navbar');
        if (navbar){
            if (window.scrollY > 100) navbar.classList.add('navbar-scrolled'); else navbar.classList.remove('navbar-scrolled');
        }
    });

    // Forzar cursor pointer en botones y enlaces
    document.querySelectorAll('.btn, a[href]').forEach(el => el.style.cursor = 'pointer');
});

// Backup para navegacion si DOMContentLoaded falla
function backupNavigation() {
    const calcularBtn = document.getElementById('calcularBtn');
    if (calcularBtn) calcularBtn.onclick = function(){ window.location.href = ""; return false; };
    const saberMasBtn = document.getElementById('saberMasBtn');
    if (saberMasBtn) saberMasBtn.onclick = function(){ const t = document.getElementById('introduccion'); if (t) t.scrollIntoView({behavior:'smooth'}); return false; };
}

setTimeout(backupNavigation, 200);
