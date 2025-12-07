// global.js - funciones globales para la app
document.addEventListener('DOMContentLoaded', function() {
    // Preloader hide (si existe). Fallback si otros scripts fallan: fade out tras 3s
    try {
        var pre = document.getElementById('preloader');
        if (pre) {
            // Intentar ocultar con fade si el preloader sigue presente
            setTimeout(function(){
                try {
                    pre.style.transition = 'opacity 0.4s ease';
                    pre.style.opacity = '0';
                    setTimeout(function(){
                        pre.style.display = 'none';
                        pre.style.visibility = 'hidden';
                    }, 450);
                } catch(e) {
                    pre.style.display = 'none';
                }
            }, 3000);
        }
    } catch(e) {
        // no-op
    }

    // Inicialización general
    window.appUtils = {
        formatCurrency: function(val){ return '$' + (Number(val) || 0); }
    };
});
