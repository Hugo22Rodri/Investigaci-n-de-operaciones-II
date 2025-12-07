// setup.js - comportamiento específico de la página de configuración (setup)
document.addEventListener('DOMContentLoaded', function(){
    try{
        const originsSelect = document.getElementById('id_origins');
        const destinationsSelect = document.getElementById('id_destinations');
        const balancedCheckbox = document.getElementById('id_is_balanced');

        if (originsSelect) originsSelect.classList.add('form-select');
        if (destinationsSelect) destinationsSelect.classList.add('form-select');
        if (balancedCheckbox) {
            balancedCheckbox.classList.add('form-check-input');
            balancedCheckbox.addEventListener('change', function(){
                const infoBox = document.querySelector('.info-box');
                if (!infoBox) return;
                if (this.checked) {
                    infoBox.querySelector('p').textContent = 'Un problema está balanceado cuando la oferta total es igual a la demanda total.';
                } else {
                    infoBox.querySelector('p').textContent = 'El problema no está balanceado. El método agregará automáticamente un origen o destino ficticio para equilibrar oferta y demanda.';
                }
            });
        }
    }catch(e){ console.error('setup.js error', e); }
});
