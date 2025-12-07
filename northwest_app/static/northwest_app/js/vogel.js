// vogel.js - interacciones específicas para el Método Vogel
document.addEventListener('DOMContentLoaded', function(){
    // Resaltar penalidades cuando exista tabla con clase 'table-results'
    var table = document.querySelector('.table-results');
    if (!table) return;

    // Función simple para marcar celdas con clase 'vogel-penalty' (puede usarse con back-end)
    window.vogelHighlight = function(cells){
        // cells: array de [i,j]
        cells.forEach(function(pos){
            var i = pos[0], j = pos[1];
            var row = table.rows[i+1]; // asumiendo header
            if (row){
                var cell = row.cells[j+1];
                if (cell) cell.classList.add('vogel-penalty');
            }
        });
    };

    // demo: pulsador que resalta las celdas con mayor penalidad (si existe elemento data)
    var demoBtn = document.getElementById('vogel-highlight-demo');
    if (demoBtn){
        demoBtn.addEventListener('click', function(){
            // buscar atributos data-penalties en la tabla (JSON)
            var raw = table.getAttribute('data-penalties');
            if (!raw) return alert('No hay penalidades en el DOM');
            try{
                var penalties = JSON.parse(raw);
                vogelHighlight(penalties);
            }catch(e){ console.error(e); alert('Formato de penalidades inválido'); }
        });
    }
});
