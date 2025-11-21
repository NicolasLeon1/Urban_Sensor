from django.urls import path
from . import views

urlpatterns = [
    # --- URLs SECPLA (Gestión de Tipos de Incidencia) ---
    path('main_incidencia/', views.main_incidencia, name='main_incidencia'),
    path('nueva_incidencia/', views.nueva_incidencia, name='nueva_incidencia'),
    path('ver_incidencia/<int:id>/', views.ver_incidencia, name='ver_incidencia'),
    path('editar_incidencia/<int:id>/', views.editar_incidencia, name='editar_incidencia'),
    path('toggle_incidencia/<int:id>/', views.toggle_incidencia, name='toggle_incidencia'),
    path('eliminar/<int:id>/', views.eliminar_incidencia, name='eliminar_incidencia'),


    # --- URLs (Gestión de Solicitudes de Incidencia) ---
    path('solicitud/rechazar/<int:id_solicitud>/', views.rechazar_incidencia, name='rechazar_incidencia'),
    path('solicitud/derivar/<int:id_solicitud>/', views.derivar_incidencia, name='derivar_incidencia'),
    path('solicitud/resolver/<int:id_solicitud>/', views.resolver_incidencia, name='resolver_incidencia'),
    path('solicitud/cancelar/<int:id_solicitud>/', views.cancelar_incidencia, name='cancelar_incidencia'),
    path('solicitud/reabrir/<int:id_solicitud>/', views.reabrir_incidencia, name='reabrir_incidencia'),
    path('solciitud/revertir/<int:id_solicitud>/', views.revertir_derivacion, name='revertir_incidencia')
]