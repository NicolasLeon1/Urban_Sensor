from django.db import models
from direccion.models import Direccion  # Asumiendo módulo 'direccion'
from departamento.models import Departamento  # Asumiendo módulo 'departamento'

class TipoIncidencia(models.Model):
    nombre_incidencia = models.CharField(max_length=240, blank=False, unique=True)
    id_direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='incidencias')
    id_departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='incidencias')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'tipo_incidencia_incidencia'  # Nombre distinto para evitar conflicto
        verbose_name = 'Tipo de Incidencia'
        verbose_name_plural = 'Tipos de Incidencia'
    
    def __str__(self):
        return self.nombre_incidencia