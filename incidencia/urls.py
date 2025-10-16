from django.urls import path, include 
from . import views

urlpatterns = [
    path('', views.lista_incidencias, name='lista_incidencias'),
    path('<int:id>/', views.detalle_incidencia, name='detalle_incidencia'),
    path('admin/', admin.site.urls),
    path('incidencias/', include('incidencia.urls')), 
]
