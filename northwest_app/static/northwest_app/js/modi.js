// modi.js - utilidades para mostrar ciclos MODI y marcar celdas entrantes
document.addEventListener('DOMContentLoaded', function(){
    var table = document.querySelector('.table-results');
    if (!table) return;

    window.modiShowEntering = function(i,j){
        var row = table.rows[i+1];
        if (row){
            var cell = row.cells[j+1];
            if (cell) cell.classList.add('modi-entering');
        }
    };

    // Demo: si la tabla tiene atributo data-entering='[i,j]'
    var raw = table.getAttribute('data-entering');
    if (raw){
        try{
            var coords = JSON.parse(raw);
            if (Array.isArray(coords) && coords.length==2){
                modiShowEntering(coords[0], coords[1]);
            }
        }catch(e){/* ignore */}
    }
});
