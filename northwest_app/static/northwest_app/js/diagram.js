// diagram.js - dibuja diagrama usando D3 leyendo datos desde atributos data-*
document.addEventListener('DOMContentLoaded', function(){
    try{
        const container = document.getElementById('transport-diagram');
        if (!container) return;

        const supplies = JSON.parse(container.getAttribute('data-supplies') || '[]');
        const demands = JSON.parse(container.getAttribute('data-demands') || '[]');
        const costs = JSON.parse(container.getAttribute('data-costs') || '[]');
        const allocations = JSON.parse(container.getAttribute('data-allocations') || '[]');

        const width = container.clientWidth;
        const height = 500;

        const svg = d3.select(container).append('svg').attr('width', width).attr('height', height);

        const origins = supplies.map((s,i)=>({ id: 'O'+(i+1), group:'origin', supply:s }));
        const destinations = demands.map((d,j)=>({ id:'D'+(j+1), group:'destination', demand:d }));
        const nodes = origins.concat(destinations);

        const links = [];
        for (let i=0;i<origins.length;i++){
            for (let j=0;j<destinations.length;j++){
                if ((allocations[i]||[])[j] > 0){
                    links.push({ source: origins[i].id, target: destinations[j].id, allocation: allocations[i][j], cost: costs[i][j] });
                }
            }
        }

        origins.forEach((o,i)=>{ o.x=150; o.y=(i+1)*(height/(origins.length+1)); });
        destinations.forEach((d,j)=>{ d.x=width-150; d.y=(j+1)*(height/(destinations.length+1)); });

        svg.append('defs').append('marker').attr('id','arrow').attr('viewBox','0 0 10 10').attr('refX',10).attr('refY',5).attr('markerWidth',6).attr('markerHeight',6).attr('orient','auto')
            .append('path').attr('d','M 0 0 L 10 5 L 0 10 z').attr('fill','#007bff');

        svg.selectAll('line').data(links).enter().append('line')
            .attr('x1', d => nodes.find(n=>n.id===d.source).x)
            .attr('y1', d => nodes.find(n=>n.id===d.source).y)
            .attr('x2', d => nodes.find(n=>n.id===d.target).x)
            .attr('y2', d => nodes.find(n=>n.id===d.target).y)
            .attr('stroke','#007bff').attr('stroke-width',2).attr('marker-end','url(#arrow)');

        svg.selectAll('.link-label').data(links).enter().append('text')
            .attr('x', d => (nodes.find(n=>n.id===d.source).x + nodes.find(n=>n.id===d.target).x)/2)
            .attr('y', d => (nodes.find(n=>n.id===d.source).y + nodes.find(n=>n.id===d.target).y)/2 - 10)
            .attr('text-anchor','middle').attr('font-size','12px').attr('fill','#333')
            .text(d => `${d.allocation} u @ $${d.cost}`);

        svg.selectAll('circle').data(nodes).enter().append('circle')
            .attr('cx', d=>d.x).attr('cy', d=>d.y).attr('r',30).attr('fill', d => d.group==='origin' ? '#28a745' : '#ffc107');

        svg.selectAll('.label').data(nodes).enter().append('text')
            .attr('x', d=>d.x).attr('y', d=>d.y+5).attr('text-anchor','middle').attr('fill','#fff').attr('font-weight','bold')
            .text(d => d.id);
    }catch(e){ console.error('diagram.js error', e); }
});
