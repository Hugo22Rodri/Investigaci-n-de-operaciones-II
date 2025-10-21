# hungarian_method.py - VERSIÓN COMPLETA CORREGIDA

class HungarianMethod:
    @staticmethod
    def _validate_and_prepare_costs(problem):
        """Valida que el `problem` contenga una matriz de costos cuadrada y la normaliza a enteros."""
        if not hasattr(problem, 'costs'):
            raise ValueError("El problema debe incluir la matriz 'costs' para el Método Húngaro")

        try:
            costs = [[int(x) for x in row] for row in problem.costs]
        except Exception:
            raise ValueError("La matriz de costos contiene valores no numéricos o estructura inválida")
        rows = len(costs)
        if rows == 0:
            raise ValueError("La matriz de costos está vacía")

        # Verificar que todas las filas tengan la misma longitud
        cols = len(costs[0])
        for row in costs:
            if len(row) != cols:
                raise ValueError("Todas las filas de la matriz de costos deben tener la misma longitud")

        # Si el problema declara dimensiones, comprobar consistencia (pero no forzar cuadrado)
        if hasattr(problem, 'origins') and hasattr(problem, 'destinations'):
            declared_rows = int(problem.origins)
            declared_cols = int(problem.destinations)
            if rows != declared_rows or cols != declared_cols:
                raise ValueError("La matriz de costos no coincide con las dimensiones declaradas en el problema")

        # Guardar copia original sin padding
        original_costs = [row.copy() for row in costs]

        # Si no es cuadrada, crear filas o columnas ficticias (rellenando con 0)
        n = max(rows, cols)
        if rows != cols:
            # Crear matriz cuadrada de tamaño n x n
            padded = [[0] * n for _ in range(n)]
            for i in range(rows):
                for j in range(cols):
                    padded[i][j] = costs[i][j]
            costs = padded

        return costs, n, rows, cols, original_costs

    @staticmethod
    def solve(problem):
        costs, n, orig_rows, orig_cols, original_costs = HungarianMethod._validate_and_prepare_costs(problem)
        matrix = [row.copy() for row in costs]
        steps = []
        step_count = 1
        
        # PASO 1: Restar el mínimo de cada fila
        step1_data = {
            'step': step_count,
            'description': 'Restar el mínimo de cada fila',
            'row_minima': [],
            'matrix_before': [row.copy() for row in matrix],
            'matrix_after': None
        }
        
        for i in range(n):
            row_min = min(matrix[i])
            step1_data['row_minima'].append(row_min)
            for j in range(n):
                matrix[i][j] -= row_min
        
        step1_data['matrix_after'] = [row.copy() for row in matrix]
        steps.append(step1_data)
        step_count += 1
        
        # PASO 2: Restar el mínimo de cada columna
        step2_data = {
            'step': step_count,
            'description': 'Restar el mínimo de cada columna',
            'col_minima': [],
            'matrix_before': [row.copy() for row in matrix],
            'matrix_after': None
        }
        
        for j in range(n):
            col_min = min(matrix[i][j] for i in range(n))
            step2_data['col_minima'].append(col_min)
            for i in range(n):
                matrix[i][j] -= col_min
        
        step2_data['matrix_after'] = [row.copy() for row in matrix]
        steps.append(step2_data)
        step_count += 1

        # PASO 3+: Iterar hasta encontrar solución óptima
        iteration = 1
        max_iterations = n * 3  # Prevenir loops infinitos
        
        while iteration <= max_iterations:
            # Encontrar asignación máxima de ceros
            assignment = HungarianMethod._find_max_assignment(matrix)
            
            # Si tenemos asignación completa, terminamos
            if len(assignment) == n:
                steps.append({
                    'step': step_count,
                    'description': f'Asignación óptima encontrada - {len(assignment)} asignaciones',
                    'matrix': [row.copy() for row in matrix],
                    'assignment': assignment,
                    'num_lines': n,
                    'required_lines': n
                })
                step_count += 1
                break
            
            # Cubrir ceros con líneas
            covered_rows, covered_cols, lines_info = HungarianMethod._cover_zeros(matrix, assignment)
            num_lines = len(covered_rows) + len(covered_cols)
            
            steps.append({
                'step': step_count,
                'description': f'Cubrir ceros con líneas (iteración {iteration})',
                'matrix': [row.copy() for row in matrix],
                'lines_info': lines_info,
                'num_lines': num_lines,
                'required_lines': n,
                'assignment': assignment
            })
            step_count += 1
            
            # Si tenemos suficientes líneas, deberíamos tener solución
            if num_lines >= n:
                # Forzar encontrar asignación completa
                final_assignment = HungarianMethod._find_complete_assignment_backtracking(matrix)
                if len(final_assignment) == n:
                    steps.append({
                        'step': step_count,
                        'description': f'Asignación óptima encontrada después de cobertura',
                        'matrix': [row.copy() for row in matrix],
                        'assignment': final_assignment,
                        'num_lines': num_lines,
                        'required_lines': n
                    })
                    step_count += 1
                    assignment = final_assignment
                    break
                else:
                    # Si no encontramos asignación completa, continuar con ajuste
                    pass
            
            # Encontrar valor mínimo no cubierto
            min_uncovered = HungarianMethod._find_min_uncovered(matrix, covered_rows, covered_cols)
            
            if min_uncovered == 0:
                break
                
            # Ajustar matriz
            matrix_before = [row.copy() for row in matrix]
            matrix = HungarianMethod._adjust_matrix(matrix, covered_rows, covered_cols, min_uncovered)
            
            steps.append({
                'step': step_count,
                'description': f'Ajustar matriz con valor mínimo no cubierto: {min_uncovered}',
                'matrix_before': matrix_before,
                'matrix_after': [row.copy() for row in matrix],
                'min_uncovered_value': min_uncovered,
                'lines_info': lines_info
            })
            step_count += 1
            
            iteration += 1
        
        # Encontrar asignación final si no se encontró en el loop
        if iteration > max_iterations or len(assignment) < n:
            assignment = HungarianMethod._find_complete_assignment_backtracking(matrix)

        # Calcular costo total solo con asignaciones dentro de las dimensiones originales
        total_cost = 0
        filtered_assignment = []
        for i, j in assignment:
            if i < orig_rows and j < orig_cols:
                total_cost += original_costs[i][j]
                filtered_assignment.append((i, j))

        # Preparar resultados acorde a las dimensiones originales
        allocations = [[0] * orig_cols for _ in range(orig_rows)]
        allocation_mask = [[False] * orig_cols for _ in range(orig_rows)]
        for i, j in filtered_assignment:
            allocations[i][j] = original_costs[i][j]
            allocation_mask[i][j] = True

        return {
            'allocations': allocations,
            'allocation_mask': allocation_mask,
            'total_cost': total_cost,
            'assignment': filtered_assignment,
            'raw_assignment': assignment,
            'steps': steps,
            'original_costs': original_costs,
            'padded_costs': costs,
            'reduced_matrix': matrix
        }

    @staticmethod
    def _find_max_assignment(matrix):
        """Encuentra la máxima asignación posible de ceros usando enfoque greedy"""
        n = len(matrix)
        assignment = []
        used_cols = set()
        
        # Primera pasada: asignar ceros únicos por fila
        for i in range(n):
            zero_cols = [j for j in range(n) if matrix[i][j] == 0 and j not in used_cols]
            if len(zero_cols) == 1:  # Solo un cero disponible en esta fila
                j = zero_cols[0]
                assignment.append((i, j))
                used_cols.add(j)
        
        # Segunda pasada: asignar ceros restantes
        for i in range(n):
            if any(assign[0] == i for assign in assignment):
                continue  # Fila ya asignada
            for j in range(n):
                if matrix[i][j] == 0 and j not in used_cols:
                    assignment.append((i, j))
                    used_cols.add(j)
                    break
        
        return assignment

    @staticmethod
    def _cover_zeros(matrix, assignment):
        """Cubre todos los ceros con el mínimo número de líneas - VERSIÓN CORREGIDA"""
        n = len(matrix)
        
        # ENFOQUE ALTERNATIVO: Encontrar el mínimo número de líneas
        # Esto es más eficiente y da resultados consistentes con el método clásico
        
        # Marcar ceros en la matriz
        zeros = []
        for i in range(n):
            for j in range(n):
                if matrix[i][j] == 0:
                    zeros.append((i, j))
        
        # Estrategia greedy para encontrar cobertura mínima
        covered_rows = set()
        covered_cols = set()
        
        # Primero cubrir filas/columnas con más ceros
        row_zero_count = [0] * n
        col_zero_count = [0] * n
        
        for i, j in zeros:
            row_zero_count[i] += 1
            col_zero_count[j] += 1
        
        remaining_zeros = zeros.copy()
        
        while remaining_zeros:
            # Encontrar fila o columna con más ceros no cubiertos
            max_row = -1
            max_row_count = -1
            max_col = -1
            max_col_count = -1
            
            for i in range(n):
                if i not in covered_rows:
                    count = sum(1 for (r, c) in remaining_zeros if r == i)
                    if count > max_row_count:
                        max_row_count = count
                        max_row = i
            
            for j in range(n):
                if j not in covered_cols:
                    count = sum(1 for (r, c) in remaining_zeros if c == j)
                    if count > max_col_count:
                        max_col_count = count
                        max_col = j
            
            # Cubrir la fila o columna que elimina más ceros
            if max_row_count >= max_col_count and max_row_count > 0:
                covered_rows.add(max_row)
                # Remover ceros de esta fila
                remaining_zeros = [(r, c) for (r, c) in remaining_zeros if r != max_row]
            elif max_col_count > 0:
                covered_cols.add(max_col)
                # Remover ceros de esta columna
                remaining_zeros = [(r, c) for (r, c) in remaining_zeros if c != max_col]
            else:
                break
        
        lines_info = {
            'horizontal_lines': list(covered_rows),
            'vertical_lines': list(covered_cols)
        }
        
        return covered_rows, covered_cols, lines_info

    @staticmethod
    def _find_min_uncovered(matrix, covered_rows, covered_cols):
        """Encuentra el valor mínimo no cubierto"""
        n = len(matrix)
        min_val = float('inf')
        
        for i in range(n):
            if i not in covered_rows:
                for j in range(n):
                    if j not in covered_cols:
                        if matrix[i][j] < min_val:
                            min_val = matrix[i][j]
        
        return min_val if min_val != float('inf') else 0

    @staticmethod
    def _adjust_matrix(matrix, covered_rows, covered_cols, min_val):
        """Ajusta la matriz según el método húngaro - VERSIÓN CORREGIDA"""
        n = len(matrix)
        new_matrix = [row.copy() for row in matrix]
        
        # RESTAR el valor mínimo a los elementos NO CUBIERTOS
        for i in range(n):
            for j in range(n):
                if i not in covered_rows and j not in covered_cols:
                    new_matrix[i][j] -= min_val
        
        # SUMAR el valor mínimo a los elementos en la INTERSECCIÓN de líneas
        for i in covered_rows:
            for j in covered_cols:
                new_matrix[i][j] += min_val
        
        return new_matrix

    @staticmethod
    def _find_complete_assignment_backtracking(matrix):
        """Encuentra asignación completa usando backtracking (fallback)"""
        n = len(matrix)
        best_assignment = []
        
        def backtrack(row, current, used_cols):
            nonlocal best_assignment
            if row == n:
                if len(current) == n:
                    best_assignment = current.copy()
                return
            
            if len(current) + (n - row) <= len(best_assignment):
                return  # Podar
            
            for col in range(n):
                if matrix[row][col] == 0 and col not in used_cols:
                    used_cols.add(col)
                    current.append((row, col))
                    backtrack(row + 1, current, used_cols)
                    current.pop()
                    used_cols.remove(col)
                    if len(best_assignment) == n:
                        return
            
            # También intentar no asignar esta fila (solo si es necesario)
            if len(current) < n:
                backtrack(row + 1, current, used_cols)
        
        backtrack(0, [], set())
        return best_assignment

    @staticmethod
    def solve_minimization(problem):
        """Método específico para minimización (caso estándar). Alias de solve."""
        return HungarianMethod.solve(problem)

    @staticmethod
    def solve_maximization(problem):
        """Método para problemas de maximización convirtiéndolos a minimización"""
        costs, n, orig_rows, orig_cols, original_costs = HungarianMethod._validate_and_prepare_costs(problem)
        max_val = max(max(row) for row in costs)
        converted_costs = [[max_val - val for val in row] for row in costs]
        
        class TempProblem:
            def __init__(self, costs):
                self.costs = costs

        temp_problem = TempProblem(converted_costs)
        result = HungarianMethod.solve(temp_problem)

        # `result` ya contiene 'original_costs' y 'total_cost' calculados por solve (minimización)
        # Ajustar metadatos para maximización
        result['converted_costs'] = converted_costs
        result['max_value_used'] = max_val
        # Guardar copia de los costos originales (antes de padding)
        result['original_costs_conventional'] = original_costs

        return result

    @staticmethod
    def validate_solution(assignment, n):
        """Valida que una asignación sea válida"""
        if len(assignment) != n:
            return False
        
        rows = set()
        cols = set()
        
        for i, j in assignment:
            if i in rows or j in cols:
                return False
            rows.add(i)
            cols.add(j)
        
        return len(rows) == n and len(cols) == n