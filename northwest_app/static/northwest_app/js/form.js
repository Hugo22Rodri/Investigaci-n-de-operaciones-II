// form.js - mejoras UX para formularios de entrada
document.addEventListener('DOMContentLoaded', function(){
    // Añadir listener para campos numéricos: seleccionar todo al focusear
    document.querySelectorAll('input[type="number"]').forEach(function(input){
        input.addEventListener('focus', function(e){ e.target.select(); });
    });

    // Validación antes de submit: asegurar que todos los campos requeridos estén llenos
    var form = document.querySelector('form');
    if (form){
        form.addEventListener('submit', function(e){
            // Verificar que todos los inputs requeridos tengan valores
            var allInputs = document.querySelectorAll('input[required]');
            var emptyFields = [];
            
            allInputs.forEach(function(input){
                var value = input.value.trim();
                // Un campo está vacío si su valor es cadena vacía
                if (value === ''){
                    emptyFields.push(input.name);
                }
            });
            
            console.log('Total campos requeridos:', allInputs.length);
            console.log('Campos vacíos:', emptyFields);
            
            if (emptyFields.length > 0){
                e.preventDefault();
                alert('Por favor complete todos los campos requeridos:\n- Ofertas de orígenes\n- Demandas de destinos\n- Costos de transporte');
            }
        });
    }
});
