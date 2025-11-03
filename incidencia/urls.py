from django.urls import path
from . import views

urlpatterns = [
    path('main_incidencia/', views.main_incidencia, name='main_incidencia'),
    path('nueva_incidencia/', views.nueva_incidencia, name='nueva_incidencia'),
    path('ver_incidencia/<int:id>/', views.ver_incidencia, name='ver_incidencia'),
    path('editar_incidencia/<int:id>/', views.editar_incidencia, name='editar_incidencia'),
    path('toggle_incidencia/<int:id>/', views.toggle_incidencia, name='toggle_incidencia'),
]