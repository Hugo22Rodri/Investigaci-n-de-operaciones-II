from django.urls import path
from . import views

app_name = 'northwest_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('setup/', views.setup_problem, name='setup'),
    path('data-input/', views.data_input, name='data_input'),
    path('results/<int:problem_id>/', views.results, name='results'),
    path('history/', views.history, name='history'),
]