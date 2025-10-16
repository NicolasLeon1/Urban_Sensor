from django.contrib import admin
from .models import Departamento, Cuadrilla, TipoIncidencia, Incidencia

admin.site.register(Departamento)
admin.site.register(Cuadrilla)
admin.site.register(TipoIncidencia)
admin.site.register(Incidencia)
