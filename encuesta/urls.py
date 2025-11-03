from django.urls import path

from . import views

urlpatterns = [
    # --- URLs de Admin (SECPLA) ---
    path('main_encuesta/', views.main_encuesta, name='main_encuesta'),
    path('nueva_encuesta/', views.nueva_encuesta, name='nueva_encuesta'),
    path('ver_encuesta/<int:id>/', views.ver_encuesta, name='ver_encuesta'),
    path('editar_encuesta/<int:id>/', views.editar_encuesta, name='editar_encuesta'),
    path('toggle_encuesta/<int:id>/', views.toggle_encuesta, name='toggle_encuesta'),
    path('eliminar_encuesta/<int:id>/', views.eliminar_encuesta, name='eliminar_encuesta'),
    
    # --- NUEVAS URLs PARA TERRITORIAL (Responder Encuesta) ---
    
    # 1. Lista de encuestas (plantillas) disponibles para responder
    path('responder/listado/', views.listar_encuestas_responder, name='listar_encuestas_responder'),
    
    # 2. Vista para rellenar (responder) una encuesta específica y crear la Solicitud
    path('responder/nueva/<int:id_encuesta>/', views.responder_encuesta, name='responder_encuesta'),
]