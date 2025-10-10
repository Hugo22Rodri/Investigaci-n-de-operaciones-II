class NorthwestCornerService:
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
        use_supplies = adjusted_supplies if adjusted else supplies
        use_demands = adjusted_demands if adjusted else demands
        use_costs = adjusted_costs if adjusted else costs
        rows = len(use_supplies)
        cols = len(use_demands)
        
        # Inicializar matriz de asignaciones
        allocations = [[0] * cols for _ in range(rows)]
        steps = []
        total_cost = 0
        i, j = 0, 0
        step_count = 1
        
        # Aplicar algoritmo de la esquina noroeste
        while i < rows and j < cols:
            allocation = min(use_supplies[i], use_demands[j])
            allocations[i][j] = allocation
            cost_for_step = allocation * use_costs[i][j]
            total_cost += cost_for_step
            
            # Registrar paso
            steps.append({
                'step': step_count,
                'i': i,
                'j': j,
                'allocation': allocation,
                'cost': use_costs[i][j],
                'total_cost_step': cost_for_step,
                'remaining_supply_before': use_supplies[i],
                'remaining_demand_before': use_demands[j],
                'remaining_supply_after': use_supplies[i] - allocation,
                'remaining_demand_after': use_demands[j] - allocation
            })
            
            # Actualizar ofertas y demandas
            use_supplies[i] -= allocation
            use_demands[j] -= allocation
            
            # Determinar siguiente celda
            if use_supplies[i] == 0:
                i += 1
            if use_demands[j] == 0:
                j += 1
                
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