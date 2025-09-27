from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProblemSetupForm, DataInputForm
from .models import TransportationProblem, Solution
import json

def index(request):
    return render(request, 'northwest_app/index.html')

def setup_problem(request):
    if request.method == 'POST':
        form = ProblemSetupForm(request.POST)
        if form.is_valid():
            origins = form.cleaned_data['origins']
            destinations = form.cleaned_data['destinations']
            is_balanced = form.cleaned_data['is_balanced']
            
            request.session['problem_data'] = {
                'origins': origins,
                'destinations': destinations,
                'is_balanced': is_balanced
            }
            
            return redirect('northwest_app:data_input')
    else:
        form = ProblemSetupForm()
    
    return render(request, 'northwest_app/setup.html', {'form': form})

def data_input(request):
    problem_data = request.session.get('problem_data')
    if not problem_data:
        return redirect('northwest_app:setup')
    
    origins = problem_data['origins']
    destinations = problem_data['destinations']
    is_balanced = problem_data['is_balanced']
    
    if request.method == 'POST':
        form = DataInputForm(origins, destinations, request.POST)
        if form.is_valid():
            # Recoger datos del formulario
            supplies = []
            for i in range(origins):
                supplies.append(form.cleaned_data[f'supply_{i}'])
            
            demands = []
            for j in range(destinations):
                demands.append(form.cleaned_data[f'demand_{j}'])
            
            costs = []
            for i in range(origins):
                row = []
                for j in range(destinations):
                    row.append(form.cleaned_data[f'cost_{i}_{j}'])
                costs.append(row)
            
            # Guardar el problema
            problem = TransportationProblem(
                origins=origins,
                destinations=destinations,
                supplies=supplies,
                demands=demands,
                costs=costs,
                balanced=is_balanced
            )
            problem.save()
            
            # Resolver el problema
            solution_data = solve_northwest_corner(problem)
            
            # Guardar la solución
            solution = Solution(
                problem=problem,
                allocations=solution_data['allocations'],
                total_cost=solution_data['total_cost'],
                steps=solution_data['steps'],
                adjusted_supplies=solution_data.get('adjusted_supplies'),
                adjusted_demands=solution_data.get('adjusted_demands'),
                adjusted_costs=solution_data.get('adjusted_costs')
            )
            solution.save()
            
            return redirect('northwest_app:results', problem_id=problem.id)
    else:
        form = DataInputForm(origins, destinations)
    
    return render(request, 'northwest_app/data_input.html', {
        'form': form,
        'origins': origins,
        'destinations': destinations,
        'is_balanced': is_balanced
    })

def solve_northwest_corner(problem):
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
        adjusted_demands.append(total_supply - total_demand)    #diferencia
    #CASO 2 : demanda > oferta (agregar fila ficticia)
    elif total_supply < total_demand:
        adjusted = True
        # Agregar oferta ficticia
        new_row = [0] * len(adjusted_costs[0])  # Costo cero para la fila ficticia
        adjusted_costs.append(new_row)
        adjusted_supplies.append(total_demand - total_supply)    #diferencia    
    
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

def results(request, problem_id):
    problem = get_object_or_404(TransportationProblem, id=problem_id)
    solution = get_object_or_404(Solution, problem=problem)
    
    # Calcular totales originales y verificar si está balanceado
    total_supply = sum(int(x) for x in problem.supplies)
    total_demand = sum(int(x) for x in problem.demands)
    is_balanced = total_supply == total_demand

    # Usar datos ajustados si están disponibles
    if solution.adjusted_supplies and not is_balanced:
        supplies = solution.adjusted_supplies
        demands = solution.adjusted_demands
        costs = solution.adjusted_costs
        rows = len(supplies)
        cols = len(demands)
        has_adjusted_data = True
        # Calcular totales ajustados
        if problem.total_supply > problem.total_demand:
            # Si hay destino ficticio, la demanda total debe ser igual a la oferta total
            total_supply = problem.total_supply
            total_demand = problem.total_supply  # Incluye el destino ficticio
        else:
            # Si hay origen ficticio, la oferta total debe ser igual a la demanda total
            total_demand = problem.total_demand
            total_supply = problem.total_demand  # Incluye el origen ficticio
        real_destinations = problem.destinations
        fictitious_destinations = cols - real_destinations
    else:
        supplies = problem.supplies
        demands = problem.demands
        costs = problem.costs
        rows = problem.origins
        cols = problem.destinations
        has_adjusted_data = False
        real_destinations = cols
        fictitious_destinations = 0
    
    # Preparar datos para la tabla
    table_data = []
    for i in range(rows):
        row_data = []
        for j in range(cols):
            # Buscar si esta celda fue operada en algún paso
            step_operated = None
            for step in solution.steps:
                if step['i'] == i and step['j'] == j:
                    step_operated = step['step']
                    break
        
            # Determinar si es celda ficticia
            is_fictitious = False
            
            if has_adjusted_data:
                # Si es una columna ficticia
                if j >= problem.destinations:
                    is_fictitious = True
            
            row_data.append({
                'allocation': solution.allocations[i][j],
                'cost': costs[i][j],
                'step_operated': step_operated,
                'is_zero': solution.allocations[i][j] == 0,
                'is_fictitious': is_fictitious,
                'is_balanced': is_balanced
            })
        table_data.append(row_data)
    
    return render(request, 'northwest_app/results.html', {
        'problem': problem,
        'solution': solution,
        'table_data': table_data,
        'supplies': supplies,
        'demands': demands,
        'costs': costs,
        'rows': rows,
        'cols': cols,
        'has_adjusted_data': has_adjusted_data,
        'origins_range': range(rows),
        'destinations_range': range(cols),
        'range_real_origins': range(problem.origins),
        'range_real_destinations': range(problem.destinations),
        'real_destinations': real_destinations,
        'fictitious_destinations': fictitious_destinations,
        'total_supply': total_supply,
        'total_demand': total_demand
    })

def history(request):
    problems = TransportationProblem.objects.all().order_by('-created_at')
    return render(request, 'northwest_app/history.html', {'problems': problems})