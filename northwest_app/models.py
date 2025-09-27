from django.db import models

class TransportationProblem(models.Model):
    name = models.CharField(max_length=100, blank=True)
    origins = models.IntegerField()
    destinations = models.IntegerField()
    supplies = models.JSONField()  # Almacena las ofertas
    demands = models.JSONField()   # Almacena las demandas
    costs = models.JSONField()     # Almacena la matriz de costos
    balanced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Problema {self.id} - {self.name}"
    
    @property
    def total_supply(self):
        return sum(int(x) for x in self.supplies)
    
    @property
    def total_demand(self):
        return sum(int(x) for x in self.demands)
        
    @property
    def fictitious_value(self):
        return abs(self.total_supply - self.total_demand)

class Solution(models.Model):
    problem = models.ForeignKey(TransportationProblem, on_delete=models.CASCADE)
    allocations = models.JSONField()  # Almacena las asignaciones
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    steps = models.JSONField()  # Almacena los pasos del algoritmo
    adjusted_supplies = models.JSONField(null=True, blank=True)  # Ofertas ajustadas
    adjusted_demands = models.JSONField(null=True, blank=True)   # Demandas ajustadas
    adjusted_costs = models.JSONField(null=True, blank=True)     # Costos ajustados
    solved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Solución para {self.problem}"