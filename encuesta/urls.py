from django.urls import path

from . import views

urlpatterns = [
    path('main_encuesta/', views.main_encuesta, name='main_encuesta'),
    path('encuesta_crear/', views.encuesta_crear, name='encuesta_crear'),
    path('encuesta_guardar/', views.encuesta_guardar, name='encuesta_guardar'),
    path('encuesta_ver/<int:encuesta_id>/', views.encuesta_ver, name='encuesta_ver'),
    path('encuesta_actualiza/<int:encuesta_id>/', views.encuesta_actualiza, name='encuesta_actualiza'),
    path('encuesta_bloquea/<int:encuesta_id>/', views.encuesta_bloquea, name='encuesta_bloquea'),
    path('encuesta_activa/<int:encuesta_id>/', views.encuesta_activa, name='encuesta_activa'),
]