from django.db import models
from direccion.models import Direccion

class Departamento(models.Model):
    nombre_departamento = models.CharField(max_length=200)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
    
    def __str__(self):
        return self.nombre_departamento