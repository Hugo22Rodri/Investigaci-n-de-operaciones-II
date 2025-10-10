from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, FormView, DetailView, ListView
from django.http import JsonResponse
from .forms import ProblemSetupForm, DataInputForm
from .models import TransportationProblem, Solution
from .services.northwest_corner_service import NorthwestCornerService
from .services.minimum_cost_service import MinimumCostService
import json
class IndexView(TemplateView):
    template_name = 'northwest_app/index.html'
    form_class = ProblemSetupForm
class EsquinaNoroesteView(TemplateView):
    template_name = 'northwest_app/esquina_noroeste.html'

class CostoMinimoView(TemplateView):
    template_name = 'northwest_app/costo_minimo.html'

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

        })
        return context
    
    def form_valid(self, form):
        origins = self.problem_data['origins']
        destinations = self.problem_data['destinations']
        method = self.problem_data.get('method','northwest')
        
        # Recoger datos del formulario
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
        else:
            solution_data = NorthwestCornerService.solve(problem)
        
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
        else:
            return ['northwest_app/results.html']
    
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
        solution_steps = []
        for step in solution.steps:
            i, j = step['i'], step['j']
            solution_steps.append({
                'step': step['step'],
                'i': i,
                'j': j,
                'allocation': step['allocation'],
                'cost': step['cost'],
                'total_cost_step': step['total_cost_step'],
                'remaining_supply_before': step['remaining_supply_before'],
                'remaining_demand_before': step['remaining_demand_before'],
                'remaining_supply_after': step['remaining_supply_after'],
                'remaining_demand_after': step['remaining_demand_after'],
                'is_fictitious': j >= problem.destinations if total_supply > total_demand else i >= problem.origins
            })
        
        # Preparar matriz de resultados
        matrix = []
        for i in range(rows):
            row = []
            for j in range(cols):
                # Buscar si esta celda fue operada en algún paso
                step_operated = None
                for step in solution.steps:
                    if step['i'] == i and step['j'] == j:
                        step_operated = step['step']
                        break
                
                cell = {
                    'allocation': solution.allocations[i][j],
                    'cost': costs[i][j],
                    'step_operated': step_operated,
                    'is_fictitious': j >= problem.destinations if total_supply > total_demand else i >= problem.origins,
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