class VogelMethod:
    @staticmethod
    def solve(problem):
        """Aplica el método de aproximaciones de Vogel (VAM) para obtener una solución inicial.

        Retorna un dict con keys: allocations, total_cost, steps, adjusted_supplies, adjusted_demands, adjusted_costs
        """
        # Preparar datos
        supplies = [float(x) for x in problem.supplies]
        demands = [float(x) for x in problem.demands]
        costs = [[float(x) for x in row] for row in problem.costs]

        total_supply = sum(supplies)
        total_demand = sum(demands)
        adjusted = False
        adjusted_supplies = supplies.copy()
        adjusted_demands = demands.copy()
        adjusted_costs = [row.copy() for row in costs]

        # Ajustar si no balanceado
        if total_supply > total_demand:
            adjusted = True
            for i in range(len(adjusted_costs)):
                adjusted_costs[i].append(0)
            adjusted_demands.append(total_supply - total_demand)
        elif total_supply < total_demand:
            adjusted = True
            new_row = [0] * len(adjusted_costs[0])
            adjusted_costs.append(new_row)
            adjusted_supplies.append(total_demand - total_supply)

        supplies = adjusted_supplies.copy()
        demands = adjusted_demands.copy()
        costs = adjusted_costs.copy()

        rows = len(supplies)
        cols = len(demands)

        allocations = [[0] * cols for _ in range(rows)]
        steps = []
        total_cost = 0
        step_count = 1

        # Marcar filas/columnas activas
        remaining_supplies = supplies.copy()
        remaining_demands = demands.copy()
        active_rows = set(range(rows))
        active_cols = set(range(cols))

        def compute_penalties():
            row_pen = {}
            col_pen = {}
            # además guardamos los dos menores (cost, index) por fila/col para explicar elección
            row_vals = {}
            col_vals = {}
            for i in list(active_rows):
                # obtener dos menores costos en columnas activas
                vals = sorted([[costs[i][j], j] for j in active_cols], key=lambda x: x[0])
                row_vals[i] = vals
                if len(vals) >= 2:
                    row_pen[i] = vals[1][0] - vals[0][0]
                elif len(vals) == 1:
                    row_pen[i] = vals[0][0]
                else:
                    row_pen[i] = 0

            for j in list(active_cols):
                vals = sorted([[costs[i][j], i] for i in active_rows], key=lambda x: x[0])
                col_vals[j] = vals
                if len(vals) >= 2:
                    col_pen[j] = vals[1][0] - vals[0][0]
                elif len(vals) == 1:
                    col_pen[j] = vals[0][0]
                else:
                    col_pen[j] = 0

            return row_pen, col_pen, row_vals, col_vals

        # Algoritmo VAM
        while active_rows and active_cols:
            row_pen, col_pen, row_vals, col_vals = compute_penalties()

            # elegir la mayor penalidad
            max_row = max(row_pen.items(), key=lambda x: x[1]) if row_pen else (None, -1)
            max_col = max(col_pen.items(), key=lambda x: x[1]) if col_pen else (None, -1)

            if max_row[1] >= max_col[1]:
                chosen_type = 'row'
                i = max_row[0]
                # seleccionar columna con menor costo en fila i
                j = min([(costs[i][j], j) for j in active_cols], key=lambda x: x[0])[1]
                chosen_penalty = max_row[1]
                tie = (max_row[1] == max_col[1])
            else:
                chosen_type = 'col'
                j = max_col[0]
                i = min([(costs[i][j], i) for i in active_rows], key=lambda x: x[0])[1]
                chosen_penalty = max_col[1]
                tie = False

            allocation = min(remaining_supplies[i], remaining_demands[j])
            allocations[i][j] = allocation
            cost_step = allocation * costs[i][j]
            total_cost += cost_step

            # construir expresión de asignación (ej. x_{2,1} = min(25,25) = 25)
            alloc_expr = f"x_{{{i+1},{j+1}}} = min({remaining_supplies[i]},{remaining_demands[j]}) = {allocation}"

            # min cost in the chosen line (for explanation)
            if chosen_type == 'row':
                vals_line = row_vals.get(i, [])
                if vals_line:
                    min_cost_in_line = vals_line[0][0]
                    min_cost_pos = vals_line[0][1]
                else:
                    min_cost_in_line = None
                    min_cost_pos = None
            else:
                vals_line = col_vals.get(j, [])
                if vals_line:
                    min_cost_in_line = vals_line[0][0]
                    min_cost_pos = vals_line[0][1]
                else:
                    min_cost_in_line = None
                    min_cost_pos = None

            # registrar paso con detalles de penalizaciones y razonamiento
            steps.append({
                'step': step_count,
                'chosen_type': chosen_type,
                'i': i,
                'j': j,
                'allocation': allocation,
                'cost': costs[i][j],
                'total_cost_step': cost_step,
                'allocation_expr': alloc_expr,
                'row_penalties': row_pen,
                'col_penalties': col_pen,
                'row_vals': row_vals,
                'col_vals': col_vals,
                'chosen_penalty': chosen_penalty,
                'tie': tie,
                'min_cost_in_line': min_cost_in_line,
                'min_cost_pos': min_cost_pos,
                'remaining_supply_before': remaining_supplies[i],
                'remaining_demand_before': remaining_demands[j],
                'remaining_supply_after': remaining_supplies[i] - allocation,
                'remaining_demand_after': remaining_demands[j] - allocation
            })

            remaining_supplies[i] -= allocation
            remaining_demands[j] -= allocation

            if remaining_supplies[i] == 0:
                active_rows.discard(i)
            if remaining_demands[j] == 0:
                active_cols.discard(j)

            step_count += 1

        result = {
            'allocations': allocations,
            'total_cost': total_cost,
            'steps': steps
        }

        if adjusted:
            result['adjusted_supplies'] = adjusted_supplies
            result['adjusted_demands'] = adjusted_demands
            result['adjusted_costs'] = adjusted_costs

        return result
