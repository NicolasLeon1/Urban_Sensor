from django.urls import path
from . import views

urlpatterns = [
    path('main_usuario/', views.main_usuario, name='main_usuario'),
    path('nuevo_usuario/', views.nuevo_usuario, name='nuevo_usuario'),
    path('editar_usuario/<int:id>', views.editar_usuario, name='editar_usuario'),
    path('ver_usuario/<int:id>', views.ver_usuario, name='ver_usuario'),
    path('toggle_usuario/<int:id>', views.toggle_usuario, name='toggle_usuario'),
    path('eliminar_usuario/<int:id>', views.eliminar_usuario, name='eliminar_usuario'),
]