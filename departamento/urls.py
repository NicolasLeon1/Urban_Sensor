from django.urls import path

from . import views

urlpatterns = [
    path('main_departamento/', views.main_departamento, name='main_departamento'),
    path('crear_departamento/', views.crear_departamento, name='crear_departamento'),
    path('ver_departamento/<int:id>/', views.ver_departamento, name='ver_departamento'),
    path('editar_departamento/<int:id>/', views.editar_departamento, name='editar_departamento'),
    path('bloquear_departamento/<int:id>/', views.bloquear_departamento, name='bloquear_departamento'),
    path('activar_departamento/<int:id>/', views.activar_departamento, name='activar_departamento'),
    path('eliminar_departamento/<int:id>', views.eliminar_departamento, name='eliminar_departamento'),
]