"""Reports app URL configuration."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('state/<str:state_name>/', views.state_detail, name='state_detail'),
    path('clusters/', views.clusters, name='clusters'),
    path('insights/', views.insights, name='insights'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
]
