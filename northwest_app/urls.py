from django.urls import path
from . import views

app_name = 'northwest_app'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('esquina_noroeste/', views.EsquinaNoroesteView.as_view(), name='esquina_noroeste'),
    path('costo_minimo/', views.CostoMinimoView.as_view(), name='costo_minimo'),
    path('hungaro/', views.MetodoHungaroView.as_view(), name='hungaro'),
    path('vogel/', views.MetodoVogelView.as_view(), name='vogel'),
    path('setup/', views.SetupProblemView.as_view(), name='setup'),
    path('data-input/', views.DataInputView.as_view(), name='data_input'),
    path('results/<int:problem_id>/', views.ResultsView.as_view(), name='results'),
    path('diagram/<int:problem_id>/', views.DiagramResultsView.as_view(), name='diagram_results'),
    path('modi/<int:problem_id>/', views.ModiResultsView.as_view(), name='modi_results'),
    path('history/', views.HistoryView.as_view(), name='history'),
]