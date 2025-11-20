from django.urls import path
from . import views

urlpatterns = [
    path('main_direccion/', views.main_direccion, name='main_direccion'),
    path('nueva_direccion/', views.nueva_direccion, name='nueva_direccion'),
    path('ver_direccion/<int:id>', views.ver_direccion, name='ver_direccion'),
    path('editar_direccion/<int:id>/', views.editar_direccion, name='editar_direccion'),
    path('toggle_direccion/<int:id>/', views.toggle_direccion, name='toggle_direccion'),
    path('eliminar_direccion/<int:id>/', views.eliminar_direccion, name='eliminar_direccion'),
]