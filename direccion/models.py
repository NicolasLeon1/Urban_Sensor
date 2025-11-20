from django.db import models

class Direccion(models.Model):
    id_direccion = models.AutoField(primary_key=True)
    nombre_direccion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'direccion'
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return self.nombre_direccion