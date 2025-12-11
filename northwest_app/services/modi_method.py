def compute_potentials_and_deltas(costs, allocations):
    """Dado `costs` y `allocations` (matrices), calcula los potenciales u, v
    usando las celdas básicas (allocations>0), y devuelve u, v y la matriz de deltas:
    delta[i][j] = cost[i][j] - (u[i] + v[j])
    """
    rows = len(costs)
    cols = len(costs[0]) if rows > 0 else 0

    # Inicializar u y v con None
    u = [None] * rows
    v = [None] * cols

    # Lista de posiciones básicas (alloc>0)
    basics = [(i, j) for i in range(rows) for j in range(cols) if allocations[i][j] > 0]

    # Si no hay celdas básicas, devolver u/v ceros
    if not basics:
        u = [0] * rows
        v = [0] * cols
    else:
        # Fijar arbitrariamente u[0] = 0 y propagar
        u[0] = 0
        changed = True
        while changed:
            changed = False
            for i, j in basics:
                if u[i] is not None and v[j] is None:
                    v[j] = costs[i][j] - u[i]
                    changed = True
                if v[j] is not None and u[i] is None:
                    u[i] = costs[i][j] - v[j]
                    changed = True

        # Si hay filas/columnas sin potencial asignado, asignar 0 para evitar None
        for idx in range(rows):
            if u[idx] is None:
                u[idx] = 0
        for idx in range(cols):
            if v[idx] is None:
                v[idx] = 0
    # Aplicar redondeo a dos decimales
    u = [round(val, 2) for val in u]
    v = [round(val, 2) for val in v]

    # Calcular deltas
    deltas = [[None] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            # redondear delta a dos decimales
            delta_value = costs[i][j] - (u[i] + v[j])
            deltas[i][j] = round(delta_value, 2)

    # Encontrar el delta más negativo (si existe)
    most_negative = 0
    entering = None
    for i in range(rows):
        for j in range(cols):
            if allocations[i][j] == 0 and deltas[i][j] < most_negative:
                most_negative = deltas[i][j]
                entering = (i, j)

    return {
        'u': u,
        'v': v,
        'deltas': deltas,
        'entering': entering,
        'most_negative': most_negative,
        'is_optimal': entering is None
    }


def find_cycle(occupied_set, start):
    """Busca un ciclo cerrado alternando movimientos por filas y columnas
    entre las celdas ocupadas más la celda `start` (tupla (r,c)).
    Devuelve la lista de posiciones del ciclo en orden, o None si no se encuentra.
    """
    # Preparar índices por fila y columna
    rows = {}
    cols = {}
    for (i, j) in occupied_set:
        rows.setdefault(i, []).append((i, j))
        cols.setdefault(j, []).append((i, j))

    target = start

    path = [start]

    def dfs(pos, visited, look_in_row):
        # look_in_row True -> mover en la misma fila (cambiar columna)
        i, j = pos
        neighbors = rows.get(i, []) if look_in_row else cols.get(j, [])
        for nb in neighbors:
            if nb == pos:
                continue
            if nb == start and len(visited) >= 4:
                return visited + [start]
            if nb in visited:
                continue
            # alternar búsqueda
            res = dfs(nb, visited + [nb], not look_in_row)
            if res:
                return res
        return None

    # Intentar empezar moviendo por fila y por columna
    cycle = dfs(start, [start], True)
    if cycle:
        return cycle
    cycle = dfs(start, [start], False)
    return cycle


def apply_modi_improvement(costs, allocations):
    """Calcula u,v,deltas y, si no es óptimo, intenta aplicar una mejora simple:
    - Encuentra la celda entrante (más negativo)
    - Busca un ciclo entre celdas básicas + entrante
    - Ajusta las cantidades alternando + y -
    Devuelve un dict con los datos y la nueva matriz de allocations (si hubo mejora).
    """
    # Copiar matrices para no mutar externas
    import copy
    alloc = copy.deepcopy(allocations)
    rows = len(costs)
    cols = len(costs[0]) if rows > 0 else 0

    info = compute_potentials_and_deltas(costs, alloc)
    if info['is_optimal']:
        info.update({'new_allocations': alloc, 'improved': False})
        return info

    entering = info['entering']

    # Construir conjunto de posiciones ocupadas (alloc>0) + entering
    occupied = {(i, j) for i in range(rows) for j in range(cols) if alloc[i][j] > 0}
    occupied.add(entering)

    cycle = find_cycle(occupied, entering)
    if not cycle:
        # No se encontró ciclo: no se puede mejorar automáticamente
        info.update({'new_allocations': alloc, 'improved': False, 'cycle': None})
        return info

    # El ciclo incluye start al final; eliminar duplicación final para alternar signos
    cycle_nodes = cycle[:-1]

    # Alternar signos: + en la entering, luego -, +, - ...
    signs = []
    for idx in range(len(cycle_nodes)):
        signs.append(1 if idx % 2 == 0 else -1)

    # Identificar las posiciones con signo - y encontrar el mínimo para ajustar
    minus_positions = [cycle_nodes[i] for i, s in enumerate(signs) if s == -1]
    min_value = min((alloc[i][j] for (i, j) in minus_positions)) if minus_positions else 0

    # Aplicar ajuste
    for (i, j), s in zip(cycle_nodes, signs):
        alloc[i][j] = alloc[i][j] + s * min_value

    # Asegurar que no haya valores negativos (por seguridad)
    for i in range(rows):
        for j in range(cols):
            if alloc[i][j] < 0:
                alloc[i][j] = 0

    # Recalcular totales
    total_cost = sum(alloc[i][j] * costs[i][j] for i in range(rows) for j in range(cols))
    total_cost = round(total_cost, 2)
    #asegurar redondeo a dos decimales
    for i in range(rows):
        for j in range(cols):
            alloc[i][j] = round(alloc[i][j], 2)
            
    info.update({'new_allocations': alloc, 'improved': True, 'cycle': cycle_nodes, 'min_adjust': min_value, 'new_total_cost': total_cost})
    return info
