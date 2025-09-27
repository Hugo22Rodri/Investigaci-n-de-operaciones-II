from django.contrib import admin
from .models import TransportationProblem, Solution

@admin.register(TransportationProblem)
class TransportationProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'origins', 'destinations', 'balanced', 'created_at')
    list_filter = ('balanced', 'created_at')
    search_fields = ('name',)

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'total_cost', 'solved_at')
    list_filter = ('solved_at',)
    search_fields = ('problem__name',)