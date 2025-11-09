from django.urls import path
from . import views

urlpatterns = [
    # --- URLs SECPLA (Gestión de Tipos de Incidencia) ---
    path('main_incidencia/', views.main_incidencia, name='main_incidencia'),
    path('nueva_incidencia/', views.nueva_incidencia, name='nueva_incidencia'),
    path('ver_incidencia/<int:id>/', views.ver_incidencia, name='ver_incidencia'),
    path('editar_incidencia/<int:id>/', views.editar_incidencia, name='editar_incidencia'),
    path('toggle_incidencia/<int:id>/', views.toggle_incidencia, name='toggle_incidencia'),
    path('solicitud/<int:pk>/derivar-territorial/',views.derivar_solicitud_territorial,name='derivar_solicitud_territorial'),
    path('solicitud/<int:pk>/territorial/',views.detalle_solicitud_territorial,name='detalle_solicitud_territorial'),
    path('solicitud/<int:pk>/cuadrilla/',views.detalle_solicitud_cuadrilla, name='detalle_solicitud_cuadrilla'
    ),

    # --- NUEVAS URLs (Gestión de Solicitudes de Incidencia) ---
            
    # Vista de detalle (para todos los perfiles)
    path('solicitud/detalle/<int:id_solicitud>/', views.detalle_solicitud, name='detalle_solicitud'),

    # Acción POST (Departamento) para derivar a cuadrilla
    path('solicitud/derivar/<int:id_solicitud>/', views.derivar_solicitud, name='derivar_solicitud'),

    # Acción POST (Cuadrilla) para marcar como finalizada
    path('solicitud/resolver/<int:id_solicitud>/', views.resolver_solicitud, name='resolver_solicitud'),
]