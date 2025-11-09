from django.urls import path
from dashboard import views

urlpatterns = [
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
    path('departamento/', views.dashboard_departamento, name='dashboard_departamento'),
    path('direccion/', views.dashboard_direccion, name='dashboard_direccion'),
    path('territorial/', views.dashboard_territorial, name='dashboard_territorial'),
    path('cuadrilla/', views.dashboard_cuadrilla, name='dashboard_cuadrilla'),
    path('', views.dashboard_main, name='dashboard_main'),
    path('departamento/derivar-cuadrilla/<int:pk>/', views.derivar_a_cuadrilla, name='derivar_a_cuadrilla'),
    path('to_dashboard/', views.to_dashboard, name='to_dashboard'),
]
