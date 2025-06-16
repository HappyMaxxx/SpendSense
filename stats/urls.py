from django.urls import path
from . import views

urlpatterns = [
	path('reports/', views.reports_view, name='reports'),
    path('chart-data/', views.chart_data, name='chart_data')
]
