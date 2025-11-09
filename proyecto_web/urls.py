"""
URL configuration for proyecto_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from dashboard import views as dashboard_views


urlpatterns = [
    path('', include('core.urls')),
    path('encuesta/', include('encuesta.urls')),
    path('accounts/', include('register.urls')),
    path('user/', include('usuarios.urls')),
    path('admin/', admin.site.urls),
    path('direccion/', include('direccion.urls')),
    path('incidencia/', include('incidencia.urls')),
    path('encuesta/', include('encuesta.urls')),
    path('departamento/', include('departamento.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('dashboard/territorial/', dashboard_views.dashboard_territorial, name='dashboard_territorial'),
    path('dashboard/departamento/', dashboard_views.dashboard_departamento, name='dashboard_departamento'),
    path('dashboard/cuadrilla/', dashboard_views.dashboard_cuadrilla, name='dashboard_cuadrilla'),
    path('', dashboard_views.dashboard_main, name='dashboard_main'),
    path('', dashboard_views.dashboard_main, name='home'),

]