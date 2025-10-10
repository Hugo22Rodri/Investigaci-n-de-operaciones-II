class MinimumCostService:
    @staticmethod
    def solve(problem):
        # Convertir datos a enteros
        supplies = [int(x) for x in problem.supplies]
        demands = [int(x) for x in problem.demands]
        costs = [[int(x) for x in row] for row in problem.costs]
        
        # Verificar balanceo y ajustar si es necesario
        total_supply = sum(supplies)
        total_demand = sum(demands)
        adjusted = False
        adjusted_supplies = supplies.copy()
        adjusted_demands = demands.copy()
        adjusted_costs = [row.copy() for row in costs]
        
        #CASO 1 : oferta > demanda (agregar columna ficticia)
        if total_supply > total_demand:
            adjusted = True
            # Agregar demanda ficticia
            for i in range(len(adjusted_costs)):
                adjusted_costs[i].append(0)  # Costo cero para la columna ficticia
            adjusted_demands.append(total_supply - total_demand)
        #CASO 2 : demanda > oferta (agregar fila ficticia)
        elif total_supply < total_demand:
            adjusted = True
            # Agregar oferta ficticia
            new_row = [0] * len(adjusted_costs[0])  # Costo cero para la fila ficticia
            adjusted_costs.append(new_row)
            adjusted_supplies.append(total_demand - total_supply)
        
        # Usar datos ajustados si fue necesario
        use_supplies = adjusted_supplies.copy()
        use_demands = adjusted_demands.copy()
        use_costs = adjusted_costs.copy()
        rows = len(use_supplies)
        cols = len(use_demands)
        
        # Inicializar matriz de asignaciones y variables de seguimiento
        allocations = [[0] * cols for _ in range(rows)]
        steps = []
        total_cost = 0
        step_count = 1
        remaining_supplies = use_supplies.copy()
        remaining_demands = use_demands.copy()
        
        # Aplicar algoritmo de costo mínimo
        while any(s > 0 for s in remaining_supplies) and any(d > 0 for d in remaining_demands):
            # Buscar la celda con menor costo que tenga oferta y demanda disponibles
            min_cost = float('inf')
            min_i = min_j = None
            
            for i in range(rows):
                for j in range(cols):
                    if (remaining_supplies[i] > 0 and remaining_demands[j] > 0 and 
                        use_costs[i][j] < min_cost):
                        min_cost = use_costs[i][j]
                        min_i, min_j = i, j
            
            # Asignar la cantidad máxima posible a la celda de menor costo
            allocation = min(remaining_supplies[min_i], remaining_demands[min_j])
            allocations[min_i][min_j] = allocation
            cost_for_step = allocation * use_costs[min_i][min_j]
            total_cost += cost_for_step
            
            # Registrar paso
            steps.append({
                'step': step_count,
                'i': min_i,
                'j': min_j,
                'allocation': allocation,
                'cost': use_costs[min_i][min_j],
                'total_cost_step': cost_for_step,
                'remaining_supply_before': remaining_supplies[min_i],
                'remaining_demand_before': remaining_demands[min_j],
                'remaining_supply_after': remaining_supplies[min_i] - allocation,
                'remaining_demand_after': remaining_demands[min_j] - allocation
            })
            
            # Actualizar ofertas y demandas restantes
            remaining_supplies[min_i] -= allocation
            remaining_demands[min_j] -= allocation
            step_count += 1
        
        # Preparar datos de retorno
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