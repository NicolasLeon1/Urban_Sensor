from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main_direccion, name='main_direccion'),
    path('actualiza/<int:id_direccion>/', views.direccion_actualiza, name='direccion_actualiza'),
    path('bloquea_activa/<int:id_direccion>/', views.direccion_bloquea_activa, name='direccion_bloquea_activa'),
    path('main_bloqueadas/', views.main_direccion_bloqueadas, name='main_direccion_bloqueadas'),
    path('desbloquea/<int:id_direccion>/', views.direccion_desbloqueadas, name='direccion_desbloquea'),
]