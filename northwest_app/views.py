from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, FormView, DetailView, ListView
from django.http import JsonResponse
from .forms import ProblemSetupForm, DataInputForm
from .models import TransportationProblem, Solution
from .services.northwest_corner_service import NorthwestCornerService
from .services.minimum_cost_service import MinimumCostService
from .services.hungarian_method import HungarianMethod
from types import SimpleNamespace
import json
class IndexView(TemplateView):
    template_name = 'northwest_app/index.html'
    form_class = ProblemSetupForm
class EsquinaNoroesteView(TemplateView):
    template_name = 'northwest_app/esquina_noroeste.html'

class CostoMinimoView(TemplateView):
    template_name = 'northwest_app/costo_minimo.html'

class MetodoHungaroView(TemplateView):
    template_name = 'northwest_app/hungaro.html'

class SetupProblemView(FormView):
    template_name = 'northwest_app/setup.html'
    form_class = ProblemSetupForm
    
    def form_valid(self, form):
        self.request.session['problem_data'] = {
            'origins': form.cleaned_data['origins'],
            'destinations': form.cleaned_data['destinations'],
            'is_balanced': form.cleaned_data['is_balanced'],
            'method': form.cleaned_data['method']
        }
        self.request.session.modified = True
        return redirect('northwest_app:data_input')
    


class DataInputView(FormView):
    """
    Vista para ingresar datos del problema de transporte
    """
    template_name = 'northwest_app/data_input.html'
    form_class = DataInputForm
    
    def dispatch(self, request, *args, **kwargs):
        self.problem_data = request.session.get('problem_data')
        if not self.problem_data:
            return redirect('northwest_app:setup')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['origins'] = self.problem_data['origins']
        kwargs['destinations'] = self.problem_data['destinations']
        # Si el método seleccionado es Húngaro, no incluir campos de ofertas/demandas
        method = self.problem_data.get('method')
        kwargs['include_supplies_demands'] = False if method == 'hungarian' else True
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'origins': self.problem_data['origins'],
            'destinations': self.problem_data['destinations'],
            'is_balanced': self.problem_data['is_balanced'],
            # Rangos
            'range_rows': range(self.problem_data['origins']),
            'range_cols': range(self.problem_data['destinations']),
            # Indica si mostrar inputs de ofertas y demandas
            'include_supplies_demands': False if self.problem_data.get('method') == 'hungarian' else True,

        })
        return context
    
    def form_valid(self, form):
        origins = self.problem_data['origins']
        destinations = self.problem_data['destinations']
        method = self.problem_data.get('method','northwest')
        
        # Recoger datos del formulario
        # Si el método es Húngaro, no esperamos campos supply/demand
        if method == 'hungarian':
            supplies = []
            demands = []
        else:
            supplies = [form.cleaned_data[f'supply_{i}'] for i in range(origins)]
            demands = [form.cleaned_data[f'demand_{j}'] for j in range(destinations)]

        costs = [[form.cleaned_data[f'cost_{i}_{j}'] for j in range(destinations)] 
                for i in range(origins)]
        
        # Guardar el problema
        if 'method' not in self.problem_data:
            self.problem_data['method'] = 'northwest'
            self.request.session['problem_data'] = self.problem_data
        
        # Guardar el problema
        problem = TransportationProblem.objects.create(
            name=f"Problema {TransportationProblem.objects.count() + 1}",
            origins=origins,
            destinations=destinations,
            supplies=supplies,
            demands=demands,
            costs=costs,
            balanced=self.problem_data['is_balanced'],
            method=self.problem_data['method']
        )
        
        # Resolver el problema usando el servicio apropiado
        if method == 'minimum_cost':
            solution_data = MinimumCostService.solve(problem)
        elif method == 'northwest':
            solution_data = NorthwestCornerService.solve(problem)
        elif method == 'hungarian':
            # El método Húngaro devuelve pasos detallados (restas por fila/columna, trazado de líneas,
            # etc). Guardamos tal cual para la plantilla específica del Método Húngaro.
            solution_data = HungarianMethod.solve(problem)

        # Guardar la solución
        Solution.objects.create(
            problem=problem,
            allocations=solution_data['allocations'],
            total_cost=solution_data['total_cost'],
            steps=solution_data['steps'],
            adjusted_supplies=solution_data.get('adjusted_supplies',[]),
            adjusted_demands=solution_data.get('adjusted_demands',[]),
            adjusted_costs=solution_data.get('adjusted_costs',[])
            
        )
        
        return redirect('northwest_app:results', problem_id=problem.id)

    def get_template_names(self):
        """Seleccionar plantilla según el método almacenado en session problem_data"""
        method = None
        if hasattr(self, 'problem_data') and self.problem_data:
            method = self.problem_data.get('method')

        if method == 'minimum_cost':
            return ['northwest_app/data_input_costo_minimo.html']
        elif method == 'hungarian':
            return ['northwest_app/data_input_hungaro.html']
        else:
            return ['northwest_app/data_input.html']

def solve_northwest_corner(problem):
    """
    @deprecated: Use NorthwestCornerService.solve() instead
    """
    return NorthwestCornerService.solve(problem)

class ResultsView(DetailView):
    model = TransportationProblem
    template_name = 'northwest_app/results.html'  # Valor por defecto
    context_object_name = 'problem'
    pk_url_kwarg = 'problem_id'
    
    def get_template_names(self):
        """
        Selecciona la plantilla según el método de solución
        """
        problem = self.get_object()
        if problem.method == 'minimum_cost':
            return ['northwest_app/minimum_cost_results.html']
        elif problem.method == 'northwest':
            # No hay una plantilla dedicada llamada 'northwest_results.html' en el proyecto.
            # Reutilizamos la plantilla genérica `results.html` para mostrar resultados de esquina noroeste.
            return ['northwest_app/results.html']
        elif problem.method == 'hungarian':
            return ['northwest_app/hungarian_results.html'] 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problem = self.object
        solution = get_object_or_404(Solution, problem=problem)
        
        # Calcular totales originales y verificar si está balanceado
        total_supply = sum(int(x) for x in problem.supplies)
        total_demand = sum(int(x) for x in problem.demands)
        is_balanced = total_supply == total_demand
        
        # Preparar datos para la plantilla
        supplies = problem.supplies
        demands = problem.demands
        costs = problem.costs
        rows = problem.origins
        cols = problem.destinations
        has_adjusted_data = False
        
        # Usar datos ajustados si están disponibles
        if solution.adjusted_supplies and not is_balanced:
            has_adjusted_data = True
            supplies = solution.adjusted_supplies
            demands = solution.adjusted_demands
            costs = solution.adjusted_costs
            rows = len(supplies)
            cols = len(demands)
            
            # Calcular datos de destinos ficticios
            real_destinations = problem.destinations
            fictitious_destinations = cols - real_destinations
        else:
            real_destinations = cols
            fictitious_destinations = 0
        
        # Preparar datos de la solución paso a paso
        # Nota: El método Húngaro almacena pasos con una estructura distinta (row_minima, col_minima, matrix_before, lines_info, assignment, ...)
        # por lo que NO debemos procesarlos aquí como si tuvieran claves 'i' y 'j'. Solo construir `solution_steps` y la `matrix` genérica
        # cuando el método NO sea 'hungarian'.
        matrix = []
        solution_steps = []
        if problem.method != 'hungarian':
            for step in solution.steps:
                # Algunos pasos de otros métodos usan claves i/j
                if 'i' in step and 'j' in step:
                    i, j = step['i'], step['j']
                    solution_steps.append({
                        'step': step.get('step'),
                        'i': i,
                        'j': j,
                        'allocation': step.get('allocation'),
                        'cost': step.get('cost'),
                        'total_cost_step': step.get('total_cost_step'),
                        'remaining_supply_before': step.get('remaining_supply_before'),
                        'remaining_demand_before': step.get('remaining_demand_before'),
                        'remaining_supply_after': step.get('remaining_supply_after'),
                        'remaining_demand_after': step.get('remaining_demand_after'),
                        'is_fictitious': (j >= problem.destinations) if total_supply > total_demand else (i >= problem.origins)
                    })

            # Preparar matriz de resultados para métodos tradicionales
            for i in range(rows):
                row = []
                for j in range(cols):
                    # Buscar si esta celda fue operada en algún paso
                    step_operated = None
                    for step in solution.steps:
                        if isinstance(step, dict) and 'i' in step and 'j' in step and step['i'] == i and step['j'] == j:
                            step_operated = step.get('step')
                            break

                    cell = {
                        'allocation': solution.allocations[i][j],
                        'cost': costs[i][j],
                        'step_operated': step_operated,
                        'is_fictitious': (j >= problem.destinations) if total_supply > total_demand else (i >= problem.origins),
                        'is_zero': solution.allocations[i][j] == 0,
                        'is_balanced': is_balanced
                    }
                    row.append(cell)
                matrix.append(row)
        
        context.update({
            'solution': solution,
            'matrix': matrix,
            'solution_steps': solution_steps,
            'supplies': supplies,
            'demands': demands,
            'costs': costs,
            'rows': rows,
            'cols': cols,
            'has_adjusted_data': has_adjusted_data,
            'real_origins': problem.origins,
            'real_destinations': real_destinations,
            'range_rows': range(rows),
            'range_cols': range(cols),
            'range_real_origins': range(rows),
            'range_real_destinations': range(cols),
            'table_data': matrix,
            'is_balanced': is_balanced,
            'total_supply': total_supply,
            'total_demand': total_demand,
        })

        # Ajustes específicos para plantilla del Método Húngaro
        if problem.method == 'hungarian':
            # Obtener matriz de costos original
            original_costs = solution.adjusted_costs if solution.adjusted_costs else problem.costs

            # Asegurar estructuras y tamaños
            allocations = solution.allocations if solution.allocations else [[0]*cols for _ in range(rows)]
            # Calcular assignment a partir de allocations (celdas con 1)
            assignment = []
            try:
                for i in range(len(allocations)):
                    for j in range(len(allocations[i])):
                        if allocations[i][j]:
                            assignment.append((i, j))
            except Exception:
                assignment = []

            # Pasos: usar los pasos guardados en la solución (asegurar lista)
            steps = solution.steps if isinstance(solution.steps, list) else (list(solution.steps) if solution.steps is not None else [])

            # Total cost
            total_cost = solution.total_cost

            # Preparar un objeto `problem` ligero con los atributos que la plantilla Húngaro espera
            hungarian_problem = SimpleNamespace()
            # Por defecto asumimos minimización; si se reconociera maximización habría que marcarlo aquí
            hungarian_problem.type = getattr(solution, 'method', 'minimization') if hasattr(solution, 'method') else 'minimization'
            hungarian_problem.size = len(original_costs)

            # Actualizar el contexto con las claves esperadas por la plantilla Húngaro
            context.update({
                'original_costs': original_costs,
                'steps': steps,
                'allocations': allocations,
                'assignment': assignment,
                'total_cost': total_cost,
                'problem': hungarian_problem,
                'range_rows': range(len(original_costs)),
                'range_cols': range(len(original_costs[0]) if original_costs and len(original_costs) > 0 else 0),
            })
        return context

class DiagramResultsView(DetailView):
    """Vista simple para mostrar diagrama"""
    model = TransportationProblem
    template_name = 'northwest_app/diagram_results.html'
    context_object_name = 'problem'
    pk_url_kwarg = 'problem_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problem = self.object
        solution = get_object_or_404(Solution, problem=problem)
        
        # Datos básicos para el template
        context.update({
            'solution': solution,
            'supplies': problem.supplies,
            'demands': problem.demands,
            'costs': problem.costs,
            'allocations': solution.allocations,
            'range_origins': range(problem.origins),
            'range_destinations': range(problem.destinations),
        })
        
        return context
class HistoryView(ListView):
    model = TransportationProblem
    template_name = 'northwest_app/history.html'
    context_object_name = 'problems'
    ordering = ['-created_at']