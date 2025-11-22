from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views      
from . import api_views  


router = DefaultRouter()
router.register(r'users', api_views.UserViewSet, basename='api_users')
router.register(r'options', api_views.DataOptionsViewSet, basename='api_options')
router.register(r'dashboard-stats', api_views.DashboardStatsViewSet, basename='api_dashboard')


urlpatterns = [
   
    path('api/', include(router.urls)), 

 
    path('main_usuario/', views.main_usuario, name='main_usuario'),
    path('nuevo_usuario/', views.nuevo_usuario, name='nuevo_usuario'),
    path('editar_usuario/<int:id>', views.editar_usuario, name='editar_usuario'),
    path('ver_usuario/<int:id>', views.ver_usuario, name='ver_usuario'),
    path('toggle_usuario/<int:id>', views.toggle_usuario, name='toggle_usuario'),
    path('eliminar_usuario/<int:id>', views.eliminar_usuario, name='eliminar_usuario'),
]