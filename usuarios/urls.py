from django.urls import path
from . import views

urlpatterns = [
    path('main_usuario/', views.main_usuario, name='main_usuario'),
    path('usuario_crear/', views.usuario_crear, name='usuario_crear'),
    path('usuario_guardar/', views.usuario_guardar, name='usuario_guardar'),
    path('usuario_ver/<int:usuario_id>/', views.usuario_ver, name='usuario_ver'),
    path('usuario_actualiza/<int:usuario_id>/', views.usuario_actualiza, name='usuario_actualiza'),
    path('usuario_actualiza/', views.usuario_actualiza, name='usuario_actualiza_post'),
    path('usuario_bloquea/<int:usuario_id>/', views.usuario_bloquea, name='usuario_bloquea'),
]